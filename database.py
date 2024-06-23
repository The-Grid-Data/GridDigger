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

def create_table():
    """Create a table with user_id."""
    try:
        connection = create_connection()
        if connection:
            cursor = connection.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INT PRIMARY KEY
                );
            """)
            connection.commit()
            print("Table 'users' created successfully.")
    except Error as e:
        print("Error while creating table", e)
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

def add_user(user_id):
    """Add a user to the users table."""
    try:
        connection = create_connection()
        if connection:
            cursor = connection.cursor()
            cursor.execute("INSERT IGNORE INTO users (user_id) VALUES (%s);", (user_id,))
            connection.commit()
            print(f"User {user_id} added successfully or already exists.")
    except Error as e:
        print("Error while adding user", e)
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

def display_users():
    """Display all users from the users table."""
    try:
        connection = create_connection()
        if connection:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users;")
            records = cursor.fetchall()
            print("Users:")
            for row in records:
                print(row)
    except Error as e:
        print("Error while fetching users", e)
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

#create_table()
#add_user(0)  # Add a specific user ID to test
#display_users()  # Display all users
