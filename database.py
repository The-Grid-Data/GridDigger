import os
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def create_connection():
    """Create a database connection."""
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST'),
            database=os.getenv('DB_DATABASE'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            port=os.getenv('DB_PORT')
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print("Error while connecting to MySQL", e)
    return None



def create_users_table():
    """Create or alter the users table to include user_id and user_name."""
    try:
        connection = create_connection()
        if connection:
            with connection.cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        user_id INT PRIMARY KEY
                    );
                """)
                cursor.execute("""
                    SELECT COLUMN_NAME
                    FROM INFORMATION_SCHEMA.COLUMNS
                    WHERE TABLE_NAME = 'users' AND COLUMN_NAME = 'user_name';
                """)
                result = cursor.fetchone()
                if not result:
                    cursor.execute("""
                        ALTER TABLE users 
                        ADD COLUMN user_name VARCHAR(255);
                    """)
                connection.commit()
                print("Table 'users' created or updated successfully.")
    except Error as e:
        print("Error while creating or updating table", e)
    finally:
        if connection and connection.is_connected():
            connection.close()


def create_user_stats_table():
    """Create a user_stats table with user_id as the primary key."""
    try:
        connection = create_connection()
        if connection:
            with connection.cursor() as cursor:
                # Drop the table if it already exists to recreate it without stat_id
                cursor.execute("DROP TABLE IF EXISTS user_stats;")

                cursor.execute("""
                    CREATE TABLE user_stats (
                        user_id INT PRIMARY KEY,
                        fetch_count INT DEFAULT 0,
                        expand_count INT DEFAULT 0,
                        FOREIGN KEY (user_id) REFERENCES users(user_id)
                    );
                """)
                connection.commit()
                print("Table 'user_stats' created successfully.")
    except Error as e:
        print("Error while creating user_stats table", e)
    finally:
        if connection and connection.is_connected():
            connection.close()


def add_user(user_id, user_name=None):
    """Add a user to the users table or update their name if they already exist."""
    try:
        connection = create_connection()
        if connection:
            cursor = connection.cursor()
            if user_name:
                cursor.execute("""
                    INSERT INTO users (user_id, user_name)
                    VALUES (%s, %s)
                    ON DUPLICATE KEY UPDATE user_name = VALUES(user_name);
                """, (user_id, user_name))
            else:
                cursor.execute("INSERT IGNORE INTO users (user_id) VALUES (%s);", (user_id,))
            connection.commit()
            print(f"User {user_id} added or updated successfully.")
    except Error as e:
        print("Error while adding or updating user", e)
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


def show_user_data(user_id):
    """Show user data including ID, name, and stats."""
    try:
        connection = create_connection()
        if connection:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT u.user_id, u.user_name, 
                       IFNULL(us.fetch_count, 0) AS fetch_count, 
                       IFNULL(us.expand_count, 0) AS expand_count
                FROM users u
                LEFT JOIN user_stats us ON u.user_id = us.user_id
                WHERE u.user_id = %s;
            """, (user_id,))
            record = cursor.fetchone()
            if record:
                print(f"ID: {record['user_id']}, Name: {record['user_name']}, Fetch Count: {record['fetch_count']}, Expand Count: {record['expand_count']}")
            else:
                print(f"No user found with ID: {user_id}")
    except Error as e:
        print("Error while fetching user data", e)
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


def generate_database_design():
    """Generate the database design in a readable format."""
    try:
        connection = create_connection()
        if connection:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT table_name, column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_schema = DATABASE()
                    ORDER BY table_name, ordinal_position;
                """)

                current_table = ''
                for row in cursor.fetchall():
                    table_name, column_name, data_type = row
                    if table_name != current_table:
                        if current_table:
                            print('}')
                        print(f'Table: {table_name} {{')
                        current_table = table_name
                    print(f'    {column_name} ({data_type})')
                if current_table:
                    print('}')
    except Error as e:
        print("Error while generating database design", e)
    finally:
        if connection and connection.is_connected():
            connection.close()


def display_users():
    """Display all users from the users table."""
    try:
        connection = create_connection()
        if connection:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT user_id, user_name FROM users;")
            records = cursor.fetchall()
            print("Users:")
            for row in records:
                print(f"ID: {row['user_id']}, Name: {row['user_name']}")
    except Error as e:
        print("Error while fetching users", e)
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

def increment_fetch_count(user_id):
    """Increment the fetch_count for the specified user_id."""
    try:
        connection = create_connection()
        if connection:
            with connection.cursor() as cursor:
                # Check if user_id exists in users table
                cursor.execute("SELECT 1 FROM users WHERE user_id = %s;", (user_id,))
                if cursor.fetchone():
                    # Ensure the user exists in user_stats
                    cursor.execute("""
                        INSERT INTO user_stats (user_id) 
                        VALUES (%s) 
                        ON DUPLICATE KEY UPDATE user_id=user_id;
                    """, (user_id,))
                    # Increment the fetch_count
                    cursor.execute("""
                        UPDATE user_stats
                        SET fetch_count = fetch_count + 1
                        WHERE user_id = %s;
                    """, (user_id,))
                    connection.commit()
                    print(f"Fetch count incremented for user_id: {user_id}")
                else:
                    print(f"User ID {user_id} does not exist in users table.")
    except Error as e:
        print("Error while incrementing fetch_count", e)
    finally:
        if connection and connection.is_connected():
            connection.close()

def increment_expand_count(user_id):
    """Increment the expand_count for the specified user_id."""
    try:
        connection = create_connection()
        if connection:
            with connection.cursor() as cursor:
                # Check if user_id exists in users table
                cursor.execute("SELECT 1 FROM users WHERE user_id = %s;", (user_id,))
                if cursor.fetchone():
                    # Ensure the user exists in user_stats
                    cursor.execute("""
                        INSERT INTO user_stats (user_id) 
                        VALUES (%s) 
                        ON DUPLICATE KEY UPDATE user_id=user_id;
                    """, (user_id,))
                    # Increment the expand_count
                    cursor.execute("""
                        UPDATE user_stats
                        SET expand_count = expand_count + 1
                        WHERE user_id = %s;
                    """, (user_id,))
                    connection.commit()
                    print(f"Expand count incremented for user_id: {user_id}")
                else:
                    print(f"User ID {user_id} does not exist in users table.")
    except Error as e:
        print("Error while incrementing expand_count", e)
    finally:
        if connection and connection.is_connected():
            connection.close()



#create_user_stats_table()
#generate_database_design()
#add_user(1823406139, "hehe boi")
increment_fetch_count(1823406139)
increment_expand_count(1823406139)
show_user_data(1823406139)
#create_table()
#add_user(0)  # Add a specific user ID to test
# display_users()  # Display all users
