import sqlite3
from flask import flash
import hashlib
import random
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

    # Create token table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reset_token (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            token INTEGER NOT NULL,
            customer_id INTEGER NOT NULL UNIQUE,
            generation_time DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (customer_id) REFERENCES customers(id)
        )
    ''')

    # Create cart_item table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cart_items (
            id INTEGER PRIMARY KEY,
            customer_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            FOREIGN KEY (customer_id) REFERENCES customers(id),
            FOREIGN KEY (product_id) REFERENCES products(id)
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

def get_password_hash(customer):
    password_hash = get_user_password_from_db(customer['email'])
    return password_hash

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

def search_products(name):
    with create_sqlite_connection() as conn:
        cursor = conn.cursor()
        if name:
            query = 'SELECT products.id, products.name, products.price, products.quantity, categories.name, products.description FROM products JOIN categories ON products.cat_id = categories.id WHERE products.name LIKE ?'
            params = ("%" + name + "%",)
        else:
            return None  # Invalid parameters provided

        result = cursor.execute(query, params)
        rows = result.fetchall()
        print(rows)
        if rows:
            products = []
            for product in rows:
                product_detials = {
                    'id': product[0],
                    'name': product[1],
                    'price': product[2],
                    'quantity': product[3],
                    'categorie': product[4],
                    'description': product[5]
                }
                products.append(product_detials)
            return products
        else:
            return None

def create_reset_token(email):
    with create_sqlite_connection() as conn:
        cursor = conn.cursor()
        if email:
            query = 'SELECT id FROM customers WHERE email = ?'
            params = (email,)
        else:
            return None  # Invalid parameters provided

        result = cursor.execute(query, params)
        row = result.fetchone()
        if row:
            customer_id = row[0]
        else:
            return None
        print(customer_id)
        if customer_id:
            query = 'SELECT * FROM reset_token WHERE customer_id = ?'
            result = cursor.execute(query, (customer_id,))
            row = result.fetchone()
            if row:
                query = 'DELETE FROM reset_token WHERE id = ?'
                cursor.execute(query, (row[0],))
            token = random.randint(100000, 999999)
            query = 'INSERT INTO reset_token(token, customer_id) VALUES (?, ?)'
            cursor.execute(query, (token, customer_id))
            return token
        else:
            return None

def delete_recovery_token(token_id):
    with create_sqlite_connection() as conn:
        cursor = conn.cursor()
        query = 'DELETE FROM reset_token WHERE id = ?'
        cursor.execute(query, (token_id,))

def get_customer_recovery_token(email):
    with create_sqlite_connection() as conn:
        cursor = conn.cursor()
        if email:
            query = 'SELECT id FROM customers WHERE email = ?'
            params = (email,)
        else:
            return None  # Invalid parameters provided

        result = cursor.execute(query, params)
        row = result.fetchone()
        customer_id = row[0]
        print(customer_id)
        if customer_id:
            query = 'SELECT * FROM reset_token WHERE customer_id = ?'
            result = cursor.execute(query, (customer_id,))
            row = result.fetchone()
            if row:
                return row
        else:
            return None

def get_product_quantity(product_id):
    with create_sqlite_connection() as conn:
        cursor = conn.cursor()

        if product_id:
            query = 'SELECT quantity FROM products WHERE id = ?'
            params = (product_id,)
        else:
            return None

        result = cursor.execute(query, params)
        row = result.fetchone()
        if row:
            return row[0]
        else:
            return None

def update_password(email, password):
    with create_sqlite_connection() as conn:
        cursor = conn.cursor()

        if email and password:
            query = 'UPDATE customers SET password = ? WHERE email = ?'
            params = (password, email)
        else:
            return None

        try:
            result = cursor.execute(query, params)
            return True
        except Exception as e:
            return False

def add_product_to_cart_items(email, product_id, quantity):
    with create_sqlite_connection() as conn:
        cursor = conn.cursor()
        if email:
            query = 'SELECT id FROM customers WHERE email = ?'
            params = (email,)
        else:
            return False  # Invalid parameters provided

        result = cursor.execute(query, params)
        row = result.fetchone()
        customer_id = row[0]

        query = '''
            INSERT INTO cart_items(customer_id, product_id, quantity)
            VALUES (?, ?, ?)
        '''
        print("added")
        try:
            cursor.execute(query, (customer_id, product_id, quantity))
            conn.commit()
            print("added")
            return True
        except Exception as e:
            return False
