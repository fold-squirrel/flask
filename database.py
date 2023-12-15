import sqlite3
from flask import flash
import hashlib
from datetime import datetime


# Function to create SQLite3 connection
def create_sqlite_connection(name='database.db'):
    return sqlite3.connect(name, check_same_thread=False)


# Initialize SQLite3 database
def init_db(connection):
    cursor = connection.cursor()

    # Create customers table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            gender TEXT NOT NULL,
            birthdate DATE NOT NULL
        )
    ''')

    # Create orders table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date DATETIME DEFAULT CURRENT_TIMESTAMP,
            cust_id TEXT NOT NULL,
            address TEXT NOT NULL,
            FOREIGN KEY (cust_id) REFERENCES customers(id)
        )
    ''')

    # Create categories table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name NOT NULL
        )
    ''')

    # Create products table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price INTEGER,
            quantity INTEGER,
            cat_id INTEGER,
            description TEXT NOT NULL,
            FOREIGN KEY (cat_id) REFERENCES categories(id)
        )
    ''')

    # Create order_details table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS order_details (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prod_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            order_id INTEGER NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders(id)
        )
    ''')

    # Create rate table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS rate (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            stars INTEGER NOT NULL,
            comment TEXT NOT NULL
        )
    ''')

    connection.commit()


def add_customer_to_db(data):
    with create_sqlite_connection() as conn:
        cursor = conn.cursor()
        query = '''
            INSERT INTO customers(name, email, password, gender, birthdate)
            VALUES (?, ?, ?, ?, ?)
        '''
        try:
            cursor.execute(query, (
                data['name'],
                data['email'],
                data['password'],
                data['gender'],
                data['birthdate'],
            ))
            conn.commit()
            return True
        except Exception as e:
            return False

def get_user_password_from_db(email):
    with create_sqlite_connection() as conn:
        cursor = conn.cursor()
        if email:
            query = 'SELECT password FROM customers WHERE email = ?'
            params = (email,)
        else:
            return None  # Invalid parameters provided

        result = cursor.execute(query, params)
        row = result.fetchone()
        if row:
            return row[0]
        else:
            return None

def check_password(customer):
    correct_password_hash = get_user_password_from_db(customer['email'])
    try:
        if correct_password_hash and (correct_password_hash == customer['password']):
            return True
        else:
            return False
    except Exception as e:
        return False

def get_user_data_from_db(email):
    with create_sqlite_connection() as conn:
        cursor = conn.cursor()
        if email:
            query = 'SELECT * FROM customers WHERE email = ?'
            params = (email,)
        else:
            return None  # Invalid parameters provided

        result = cursor.execute(query, params)
        row = result.fetchone()
        if row:
            return row
        else:
            return None


