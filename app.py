import os
import sys
import sqlite3
import json
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS

# Create Flask app
app = Flask(__name__)
CORS(app)

# Database setup
DATABASE = 'inventory.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        # Create tables
        conn.executescript('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                _id TEXT UNIQUE,
                name TEXT NOT NULL,
                description TEXT,
                sku TEXT UNIQUE NOT NULL,
                price REAL NOT NULL,
                unit TEXT NOT NULL,
                category_id TEXT,
                supplier_id TEXT,
                reorder_point INTEGER DEFAULT 10,
                current_stock TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                _id TEXT UNIQUE,
                name TEXT NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS suppliers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                _id TEXT UNIQUE,
                name TEXT NOT NULL,
                contact_person TEXT,
                email TEXT,
                phone TEXT,
                address TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                _id TEXT UNIQUE,
                name TEXT NOT NULL,
                email TEXT,
                phone TEXT,
                address TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS warehouses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                _id TEXT UNIQUE,
                name TEXT NOT NULL,
                location TEXT,
                manager TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        ''')
        
        # Insert sample data
        sample_products = [
            ('prod_1', 'Paracetamol 500mg', 'Pain relief and fever reducer', 'PAR500', 150, 'tablet', 'cat_1', 'sup_1', 50, '{"warehouse_1": 200}'),
            ('prod_2', 'Vitamin C 1000mg', 'Immune system support', 'VITC1000', 500, 'tablet', 'cat_1', 'sup_1', 30, '{"warehouse_1": 100}'),
            ('prod_3', 'Hand Sanitizer 250ml', 'Alcohol-based hand sanitizer', 'HANSAN250', 800, 'bottle', 'cat_2', 'sup_2', 20, '{"warehouse_1": 75}'),
            ('prod_4', 'Baby Diapers Size M', 'Soft and absorbent baby diapers', 'DIAPER-M', 2500, 'pack', 'cat_3', 'sup_3', 10, '{"warehouse_1": 25}')
        ]
        
        sample_categories = [
            ('cat_1', 'Pharmaceuticals', 'Medical and pharmaceutical products'),
            ('cat_2', 'Personal Care', 'Personal hygiene and care products'),
            ('cat_3', 'Baby Care', 'Baby and infant care products')
        ]
        
        sample_suppliers = [
            ('sup_1', 'MedSupply Nigeria', 'John Doe', 'john@medsupply.ng', '+234-801-234-5678', 'Lagos, Nigeria'),
            ('sup_2', 'HealthCare Distributors', 'Jane Smith', 'jane@healthcare.ng', '+234-802-345-6789', 'Abuja, Nigeria'),
            ('sup_3', 'BabyCare Imports', 'Mike Johnson', 'mike@babycare.ng', '+234-803-456-7890', 'Port Harcourt, Nigeria')
        ]
        
        sample_customers = [
            ('cust_1', 'Sunshine Pharmacy', 'info@sunshine.ng', '+234-901-234-5678', 'Victoria Island, Lagos'),
            ('cust_2', 'City Hospital', 'procurement@cityhospital.ng', '+234-902-345-6789', 'Garki, Abuja'),
            ('cust_3', 'Family Clinic', 'admin@familyclinic.ng', '+234-903-456-7890', 'GRA, Port Harcourt')
        ]
        
        sample_warehouses = [
            ('warehouse_1', 'Main Warehouse', 'Ikeja, Lagos', 'Ahmed Bello')
        ]
        
        # Insert sample data
        conn.executemany('INSERT OR IGNORE INTO products (_id, name, description, sku, price, unit, category_id, supplier_id, reorder_point, current_stock) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', sample_products)
        conn.executemany('INSERT OR IGNORE INTO categories (_id, name, description) VALUES (?, ?, ?)', sample_categories)
        conn.executemany('INSERT OR IGNORE INTO suppliers (_id, name, contact_person, email, phone, address) VALUES (?, ?, ?, ?, ?, ?)', sample_suppliers)
        conn.executemany('INSERT OR IGNORE INTO customers (_id, name, email, phone, address) VALUES (?, ?, ?, ?, ?)', sample_customers)
        conn.executemany('INSERT OR IGNORE INTO warehouses (_id, name, location, manager) VALUES (?, ?, ?, ?)', sample_warehouses)

# API Routes
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'success': True,
        'message': 'Melapro API is running',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/products', methods=['GET'])
def get_products():
    try:
        with get_db() as conn:
            cursor = conn.execute('SELECT * FROM products ORDER BY name')
            products = []
            for row in cursor.fetchall():
                product = dict(row)
                product['current_stock'] = json.loads(product['current_stock']) if product['current_stock'] else {}
                products.append(product)
            
        return jsonify({
            'success': True,
            'data': products
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/products', methods=['POST'])
def create_product():
    try:
        data = request.get_json()
        
        with get_db() as conn:
            conn.execute('''
                INSERT INTO products (_id, name, description, sku, price, unit, category_id, supplier_id, reorder_point, current_stock)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data.get('_id', f"prod_{datetime.now().timestamp()}"),
                data['name'],
                data.get('description', ''),
                data['sku'],
                data['price'],
                data['unit'],
                data.get('category_id'),
                data.get('supplier_id'),
                data.get('reorder_point', 10),
                json.dumps(data.get('current_stock', {}))
            ))
            
        return jsonify({
            'success': True,
            'message': 'Product created successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/categories', methods=['GET'])
def get_categories():
    try:
        with get_db() as conn:
            cursor = conn.execute('SELECT * FROM categories ORDER BY name')
            categories = [dict(row) for row in cursor.fetchall()]
            
        return jsonify({
            'success': True,
            'data': categories
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/suppliers', methods=['GET'])
def get_suppliers():
    try:
        with get_db() as conn:
            cursor = conn.execute('SELECT * FROM suppliers ORDER BY name')
            suppliers = [dict(row) for row in cursor.fetchall()]
            
        return jsonify({
            'success': True,
            'data': suppliers
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/customers', methods=['GET'])
def get_customers():
    try:
        with get_db() as conn:
            cursor = conn.execute('SELECT * FROM customers ORDER BY name')
            customers = [dict(row) for row in cursor.fetchall()]
            
        return jsonify({
            'success': True,
            'data': customers
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/warehouses', methods=['GET'])
def get_warehouses():
    try:
        with get_db() as conn:
            cursor = conn.execute('SELECT * FROM warehouses ORDER BY name')
            warehouses = [dict(row) for row in cursor.fetchall()]
            
        return jsonify({
            'success': True,
            'data': warehouses
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Initialize database on startup
init_db()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

