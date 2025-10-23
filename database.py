import sqlite3
import json
from datetime import datetime
import os

class Database:
    def __init__(self, db_name='bot_store.db'):
        self.db_name = db_name
        self.init_db()
    
    def get_connection(self):
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_db(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                price REAL NOT NULL,
                image_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                active INTEGER DEFAULT 1
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                username TEXT,
                product_id INTEGER NOT NULL,
                product_name TEXT NOT NULL,
                price REAL NOT NULL,
                crypto_address TEXT NOT NULL,
                payment_hash TEXT,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                approved_at TIMESTAMP,
                FOREIGN KEY (product_id) REFERENCES products(id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_product(self, name, description, price, image_path=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO products (name, description, price, image_path) VALUES (?, ?, ?, ?)',
            (name, description, price, image_path)
        )
        product_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return product_id
    
    def get_all_products(self, active_only=True):
        conn = self.get_connection()
        cursor = conn.cursor()
        if active_only:
            cursor.execute('SELECT * FROM products WHERE active = 1 ORDER BY created_at DESC')
        else:
            cursor.execute('SELECT * FROM products ORDER BY created_at DESC')
        products = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return products
    
    def get_product(self, product_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM products WHERE id = ?', (product_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    
    def update_product(self, product_id, name, description, price, image_path=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        if image_path:
            cursor.execute(
                'UPDATE products SET name = ?, description = ?, price = ?, image_path = ? WHERE id = ?',
                (name, description, price, image_path, product_id)
            )
        else:
            cursor.execute(
                'UPDATE products SET name = ?, description = ?, price = ? WHERE id = ?',
                (name, description, price, product_id)
            )
        conn.commit()
        conn.close()
    
    def delete_product(self, product_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE products SET active = 0 WHERE id = ?', (product_id,))
        conn.commit()
        conn.close()
    
    def create_order(self, user_id, username, product_id, crypto_address):
        product = self.get_product(product_id)
        if not product:
            return None
        
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO orders (user_id, username, product_id, product_name, price, crypto_address) VALUES (?, ?, ?, ?, ?, ?)',
            (user_id, username, product_id, product['name'], product['price'], crypto_address)
        )
        order_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return order_id
    
    def get_order(self, order_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM orders WHERE id = ?', (order_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    
    def get_pending_orders(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM orders WHERE status = "pending" ORDER BY created_at DESC')
        orders = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return orders
    
    def get_all_orders(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM orders ORDER BY created_at DESC')
        orders = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return orders
    
    def approve_order(self, order_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE orders SET status = "approved", approved_at = ? WHERE id = ?',
            (datetime.now(), order_id)
        )
        conn.commit()
        conn.close()
    
    def reject_order(self, order_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE orders SET status = "rejected" WHERE id = ?', (order_id,))
        conn.commit()
        conn.close()
    
    def mark_payment_received(self, order_id, payment_hash):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE orders SET payment_hash = ?, status = "payment_received" WHERE id = ?',
            (payment_hash, order_id)
        )
        conn.commit()
        conn.close()
