"""
Enhanced database operations for GridDigger Telegram Bot
Improved connection management, error handling, and performance
"""
import os
import logging
import time
from typing import Optional, Dict, Any, List
from contextlib import contextmanager
import mysql.connector
from mysql.connector import Error, pooling
from mysql.connector.pooling import MySQLConnectionPool

from config import Config

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Enhanced database manager with connection pooling and improved error handling"""
    
    def __init__(self):
        self.pool: Optional[MySQLConnectionPool] = None
        self._initialize_pool()
    
    def _initialize_pool(self):
        """Initialize connection pool"""
        try:
            pool_config = {
                'pool_name': 'griddigger_pool',
                'pool_size': Config.CONNECTION_POOL_SIZE,
                'pool_reset_session': True,
                'host': Config.DB_HOST,
                'database': Config.DB_DATABASE,
                'user': Config.DB_USER,
                'password': Config.DB_PASSWORD,
                'port': Config.DB_PORT,
                'autocommit': False,
                'charset': 'utf8mb4',
                'collation': 'utf8mb4_unicode_ci',
                'time_zone': '+00:00',
                'sql_mode': 'STRICT_TRANS_TABLES,NO_ZERO_DATE,NO_ZERO_IN_DATE,ERROR_FOR_DIVISION_BY_ZERO',
                'connect_timeout': 10,
                'raise_on_warnings': True
            }
            
            self.pool = mysql.connector.pooling.MySQLConnectionPool(**pool_config)
            logger.info(f"Database connection pool initialized with {Config.CONNECTION_POOL_SIZE} connections")
            
            # Test the pool
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                cursor.fetchone()
                logger.info("Database connection pool test successful")
                
        except Error as e:
            logger.error(f"Failed to initialize database connection pool: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error initializing database: {e}")
            raise
    
    @contextmanager
    def get_connection(self):
        """Get database connection from pool with automatic cleanup"""
        connection = None
        try:
            connection = self.pool.get_connection()
            yield connection
        except Error as e:
            if connection:
                connection.rollback()
            logger.error(f"Database error: {e}")
            raise
        except Exception as e:
            if connection:
                connection.rollback()
            logger.error(f"Unexpected database error: {e}")
            raise
        finally:
            if connection and connection.is_connected():
                connection.close()
    
    @contextmanager
    def get_cursor(self, dictionary=False, buffered=True):
        """Get database cursor with automatic connection management"""
        with self.get_connection() as connection:
            cursor = connection.cursor(dictionary=dictionary, buffered=buffered)
            try:
                yield cursor, connection
            finally:
                cursor.close()
    
    def execute_query(self, query: str, params: tuple = None, 
                     fetch_one: bool = False, fetch_all: bool = False,
                     commit: bool = False) -> Any:
        """
        Execute database query with error handling
        
        Args:
            query: SQL query to execute
            params: Query parameters
            fetch_one: Whether to fetch one result
            fetch_all: Whether to fetch all results
            commit: Whether to commit the transaction
            
        Returns:
            Query result or None
        """
        try:
            with self.get_cursor(dictionary=True) as (cursor, connection):
                cursor.execute(query, params or ())
                
                result = None
                if fetch_one:
                    result = cursor.fetchone()
                elif fetch_all:
                    result = cursor.fetchall()
                else:
                    result = cursor.rowcount
                
                if commit:
                    connection.commit()
                
                return result
                
        except Error as e:
            logger.error(f"Database query error: {e}")
            logger.error(f"Query: {query}")
            logger.error(f"Params: {params}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error executing query: {e}")
            raise
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform database health check
        
        Returns:
            Dictionary containing health status
        """
        try:
            start_time = time.time()
            
            with self.get_cursor(dictionary=True) as (cursor, connection):
                # Test basic connectivity
                cursor.execute("SELECT 1 as test")
                result = cursor.fetchone()
                
                # Get connection info
                cursor.execute("SELECT CONNECTION_ID() as connection_id")
                conn_info = cursor.fetchone()
                
                # Try to get database stats (handle case where users table doesn't exist)
                try:
                    cursor.execute("""
                        SELECT
                            COUNT(*) as user_count
                        FROM users
                    """)
                    user_stats = cursor.fetchone()
                    user_count = user_stats['user_count'] if user_stats else 0
                except Exception:
                    # Users table might not exist yet
                    user_count = 0
                
                response_time = time.time() - start_time
                
                return {
                    'status': 'healthy',
                    'response_time_ms': round(response_time * 1000, 2),
                    'connection_id': conn_info['connection_id'] if conn_info else 'unknown',
                    'pool_size': Config.CONNECTION_POOL_SIZE,
                    'user_count': user_count,
                    'timestamp': time.time()
                }
                
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': time.time()
            }


class UserRepository:
    """Repository for user-related database operations"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def create_user(self, user_id: int, user_name: str = None) -> bool:
        """
        Create or update user
        
        Args:
            user_id: Telegram user ID
            user_name: Optional username
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if user_name:
                query = """
                    INSERT INTO users (user_id, user_name)
                    VALUES (%s, %s)
                    ON DUPLICATE KEY UPDATE 
                        user_name = VALUES(user_name),
                        updated_at = CURRENT_TIMESTAMP
                """
                params = (user_id, user_name)
            else:
                query = """
                    INSERT IGNORE INTO users (user_id)
                    VALUES (%s)
                """
                params = (user_id,)
            
            self.db.execute_query(query, params, commit=True)
            logger.info(f"User {user_id} created/updated successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error creating/updating user {user_id}: {e}")
            return False
    
    def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Get user information
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            User data dictionary or None
        """
        try:
            query = """
                SELECT u.user_id, u.user_name, u.created_at, u.updated_at,
                       IFNULL(us.fetch_count, 0) AS fetch_count,
                       IFNULL(us.expand_count, 0) AS expand_count,
                       IFNULL(us.search_count, 0) AS search_count
                FROM users u
                LEFT JOIN user_stats us ON u.user_id = us.user_id
                WHERE u.user_id = %s
            """
            
            result = self.db.execute_query(query, (user_id,), fetch_one=True)
            return result
            
        except Exception as e:
            logger.error(f"Error fetching user {user_id}: {e}")
            return None
    
    def get_all_users(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Get all users with pagination
        
        Args:
            limit: Maximum number of users to return
            offset: Number of users to skip
            
        Returns:
            List of user dictionaries
        """
        try:
            query = """
                SELECT u.user_id, u.user_name, u.created_at,
                       IFNULL(us.fetch_count, 0) AS fetch_count,
                       IFNULL(us.expand_count, 0) AS expand_count,
                       IFNULL(us.search_count, 0) AS search_count
                FROM users u
                LEFT JOIN user_stats us ON u.user_id = us.user_id
                ORDER BY u.created_at DESC
                LIMIT %s OFFSET %s
            """
            
            result = self.db.execute_query(query, (limit, offset), fetch_all=True)
            return result or []
            
        except Exception as e:
            logger.error(f"Error fetching users: {e}")
            return []
    
    def increment_stat(self, user_id: int, stat_type: str) -> bool:
        """
        Increment user statistic
        
        Args:
            user_id: Telegram user ID
            stat_type: Type of statistic (fetch_count, expand_count, search_count)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Validate stat_type
            valid_stats = ['fetch_count', 'expand_count', 'search_count']
            if stat_type not in valid_stats:
                logger.error(f"Invalid stat type: {stat_type}")
                return False
            
            # First ensure user exists in users table
            user_exists_query = "SELECT 1 FROM users WHERE user_id = %s"
            user_exists = self.db.execute_query(user_exists_query, (user_id,), fetch_one=True)
            
            if not user_exists:
                logger.warning(f"User {user_id} does not exist, creating...")
                self.create_user(user_id)
            
            # Insert or update stats
            query = f"""
                INSERT INTO user_stats (user_id, {stat_type})
                VALUES (%s, 1)
                ON DUPLICATE KEY UPDATE 
                    {stat_type} = {stat_type} + 1,
                    updated_at = CURRENT_TIMESTAMP
            """
            
            self.db.execute_query(query, (user_id,), commit=True)
            logger.debug(f"Incremented {stat_type} for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error incrementing {stat_type} for user {user_id}: {e}")
            return False
    
    def get_user_stats_summary(self) -> Dict[str, Any]:
        """
        Get summary statistics for all users
        
        Returns:
            Dictionary containing summary statistics
        """
        try:
            query = """
                SELECT 
                    COUNT(DISTINCT u.user_id) as total_users,
                    COUNT(DISTINCT CASE WHEN us.user_id IS NOT NULL THEN u.user_id END) as active_users,
                    IFNULL(SUM(us.fetch_count), 0) as total_fetches,
                    IFNULL(SUM(us.expand_count), 0) as total_expands,
                    IFNULL(SUM(us.search_count), 0) as total_searches,
                    IFNULL(AVG(us.fetch_count), 0) as avg_fetches_per_user,
                    MAX(u.created_at) as last_user_created
                FROM users u
                LEFT JOIN user_stats us ON u.user_id = us.user_id
            """
            
            result = self.db.execute_query(query, fetch_one=True)
            return result or {}
            
        except Exception as e:
            logger.error(f"Error getting user stats summary: {e}")
            return {}


class DatabaseInitializer:
    """Database schema initialization and migration"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def initialize_schema(self):
        """Initialize database schema"""
        try:
            logger.info("Initializing database schema...")
            
            # Create users table
            self._create_users_table()
            
            # Create user_stats table
            self._create_user_stats_table()
            
            # Create indexes
            self._create_indexes()
            
            logger.info("Database schema initialization completed")
            
        except Exception as e:
            logger.error(f"Error initializing database schema: {e}")
            raise
    
    def _create_users_table(self):
        """Create users table"""
        try:
            # Check if table exists first
            check_query = """
                SELECT COUNT(*) as count
                FROM information_schema.tables
                WHERE table_schema = DATABASE()
                AND table_name = 'users'
            """
            result = self.db.execute_query(check_query, fetch_one=True)
            
            if result and result['count'] == 0:
                # Table doesn't exist, create it
                query = """
                    CREATE TABLE users (
                        user_id BIGINT PRIMARY KEY,
                        user_name VARCHAR(255),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        INDEX idx_created_at (created_at),
                        INDEX idx_user_name (user_name)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """
                self.db.execute_query(query, commit=True)
                logger.info("Users table created successfully")
            else:
                logger.info("Users table already exists")
                
        except Error as e:
            if "already exists" in str(e):
                logger.info("Users table already exists")
            else:
                logger.error(f"Error creating users table: {e}")
                raise
    
    def _create_user_stats_table(self):
        """Create user_stats table"""
        try:
            # Check if table exists first
            check_query = """
                SELECT COUNT(*) as count
                FROM information_schema.tables
                WHERE table_schema = DATABASE()
                AND table_name = 'user_stats'
            """
            result = self.db.execute_query(check_query, fetch_one=True)
            
            if result and result['count'] == 0:
                # Table doesn't exist, create it
                query = """
                    CREATE TABLE user_stats (
                        user_id BIGINT PRIMARY KEY,
                        fetch_count INT DEFAULT 0,
                        expand_count INT DEFAULT 0,
                        search_count INT DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
                        INDEX idx_fetch_count (fetch_count),
                        INDEX idx_expand_count (expand_count),
                        INDEX idx_search_count (search_count),
                        INDEX idx_updated_at (updated_at)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """
                self.db.execute_query(query, commit=True)
                logger.info("User stats table created successfully")
            else:
                logger.info("User stats table already exists")
                
        except Error as e:
            if "already exists" in str(e):
                logger.info("User stats table already exists")
            else:
                logger.error(f"Error creating user_stats table: {e}")
                raise
    
    def _create_indexes(self):
        """Create additional indexes for performance"""
        indexes = [
            {
                'name': 'idx_users_created_at',
                'table': 'users',
                'column': 'created_at'
            },
            {
                'name': 'idx_user_stats_updated_at',
                'table': 'user_stats',
                'column': 'updated_at'
            }
        ]
        
        for index_info in indexes:
            try:
                # Check if index exists first
                check_query = """
                    SELECT COUNT(*) as count
                    FROM information_schema.statistics
                    WHERE table_schema = DATABASE()
                    AND table_name = %s
                    AND index_name = %s
                """
                result = self.db.execute_query(
                    check_query,
                    (index_info['table'], index_info['name']),
                    fetch_one=True
                )
                
                if result and result['count'] == 0:
                    # Index doesn't exist, create it
                    create_query = f"CREATE INDEX {index_info['name']} ON {index_info['table']}({index_info['column']})"
                    self.db.execute_query(create_query, commit=True)
                    logger.info(f"Created index {index_info['name']}")
                else:
                    logger.debug(f"Index {index_info['name']} already exists")
                    
            except Error as e:
                if "Duplicate key name" in str(e) or "already exists" in str(e):
                    logger.debug(f"Index {index_info['name']} already exists: {e}")
                else:
                    logger.warning(f"Index creation warning for {index_info['name']}: {e}")
        
        logger.info("Database indexes created/verified")


# Global instances
db_manager = DatabaseManager()
user_repository = UserRepository(db_manager)
db_initializer = DatabaseInitializer(db_manager)

# Schema initialization is now optional - call manually when needed
# To initialize schema: from database_v2 import db_initializer; db_initializer.initialize_schema()
def initialize_database_schema():
    """Initialize database schema - call this manually when needed"""
    try:
        db_initializer.initialize_schema()
        return True
    except Exception as e:
        logger.error(f"Failed to initialize database schema: {e}")
        return False


# Backward compatibility functions
def add_user(user_id: int, user_name: str = None) -> bool:
    """Backward compatible user creation function"""
    return user_repository.create_user(user_id, user_name)


def increment_fetch_count(user_id: int) -> bool:
    """Backward compatible fetch count increment"""
    return user_repository.increment_stat(user_id, 'fetch_count')


def increment_expand_count(user_id: int) -> bool:
    """Backward compatible expand count increment"""
    return user_repository.increment_stat(user_id, 'expand_count')


def increment_search_count(user_id: int) -> bool:
    """New search count increment function"""
    return user_repository.increment_stat(user_id, 'search_count')


def show_user_data(user_id: int) -> Optional[Dict[str, Any]]:
    """Backward compatible user data retrieval"""
    return user_repository.get_user(user_id)


def get_database_health() -> Dict[str, Any]:
    """Get database health status"""
    return db_manager.health_check()