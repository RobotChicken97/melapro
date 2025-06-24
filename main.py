import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from src.database_config import db_config
from src.routes.products import product_bp
from src.routes.sales import sales_bp
from src.routes.entities import category_bp, supplier_bp, customer_bp, warehouse_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'

# Enable CORS for all routes
CORS(app, origins="*")

# Register blueprints
app.register_blueprint(product_bp, url_prefix='/api')
app.register_blueprint(sales_bp, url_prefix='/api')
app.register_blueprint(category_bp, url_prefix='/api')
app.register_blueprint(supplier_bp, url_prefix='/api')
app.register_blueprint(customer_bp, url_prefix='/api')
app.register_blueprint(warehouse_bp, url_prefix='/api')

# Initialize database connection on startup
def initialize_database():
    """Initialize database connection and create sample data"""
    if db_config.connect():
        print("Connected to CouchDB successfully")
        create_sample_data()
    else:
        print("Failed to connect to CouchDB")

def create_sample_data():
    """Create sample data for testing"""
    from src.services.database_service import db_service
    from src.models.inventory import Category, Supplier, Warehouse, Product
    
    try:
        # Check if sample data already exists
        existing_categories = db_service.find_documents('category', limit=1)
        if existing_categories:
            print("Sample data already exists")
            return
        
        # Create sample categories
        categories = [
            Category(name="Medicines", description="Pharmaceutical products"),
            Category(name="Personal Care", description="Personal hygiene and care products"),
            Category(name="Vitamins & Supplements", description="Health supplements and vitamins"),
            Category(name="Baby Care", description="Products for babies and infants")
        ]
        
        category_ids = {}
        for category in categories:
            category_id = db_service.create_document(category)
            if category_id:
                category_ids[category.name] = category_id
                print(f"Created category: {category.name}")
        
        # Create sample suppliers
        suppliers = [
            Supplier(
                name="PharmaCorp Ltd",
                email="contact@pharmacorp.com",
                phone="+234-800-1234-567",
                address="123 Medical Street, Lagos, Nigeria",
                payment_terms="Net 30"
            ),
            Supplier(
                name="HealthSupply Nigeria",
                email="orders@healthsupply.ng",
                phone="+234-800-2345-678",
                address="456 Wellness Avenue, Abuja, Nigeria",
                payment_terms="Net 15"
            )
        ]
        
        supplier_ids = {}
        for supplier in suppliers:
            supplier_id = db_service.create_document(supplier)
            if supplier_id:
                supplier_ids[supplier.name] = supplier_id
                print(f"Created supplier: {supplier.name}")
        
        # Create sample warehouse
        warehouse = Warehouse(
            name="Main Store",
            location="Ground Floor, Main Building",
            description="Primary retail location"
        )
        
        warehouse_id = db_service.create_document(warehouse)
        if warehouse_id:
            print(f"Created warehouse: {warehouse.name}")
        
        # Create sample products
        products = [
            Product(
                name="Paracetamol 500mg",
                description="Pain relief and fever reducer",
                sku="PAR500",
                barcode="1234567890123",
                category_id=category_ids.get("Medicines", ""),
                supplier_id=supplier_ids.get("PharmaCorp Ltd", ""),
                price=150.00,
                cost_price=100.00,
                unit="tablet",
                reorder_point=50,
                current_stock={warehouse_id: 200}
            ),
            Product(
                name="Vitamin C 1000mg",
                description="Immune system support",
                sku="VITC1000",
                barcode="2345678901234",
                category_id=category_ids.get("Vitamins & Supplements", ""),
                supplier_id=supplier_ids.get("HealthSupply Nigeria", ""),
                price=500.00,
                cost_price=350.00,
                unit="tablet",
                reorder_point=30,
                current_stock={warehouse_id: 100}
            ),
            Product(
                name="Hand Sanitizer 250ml",
                description="Alcohol-based hand sanitizer",
                sku="HANSAN250",
                barcode="3456789012345",
                category_id=category_ids.get("Personal Care", ""),
                supplier_id=supplier_ids.get("HealthSupply Nigeria", ""),
                price=800.00,
                cost_price=600.00,
                unit="bottle",
                reorder_point=20,
                current_stock={warehouse_id: 75}
            ),
            Product(
                name="Baby Diapers Size M",
                description="Soft and absorbent baby diapers",
                sku="DIAPER-M",
                barcode="4567890123456",
                category_id=category_ids.get("Baby Care", ""),
                supplier_id=supplier_ids.get("PharmaCorp Ltd", ""),
                price=2500.00,
                cost_price=2000.00,
                unit="pack",
                reorder_point=10,
                current_stock={warehouse_id: 25}
            )
        ]
        
        for product in products:
            product_id = db_service.create_document(product)
            if product_id:
                print(f"Created product: {product.name}")
        
        print("Sample data created successfully")
        
    except Exception as e:
        print(f"Error creating sample data: {e}")

# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        db_status = "connected" if db_config.server else "disconnected"
        
        return jsonify({
            'status': 'healthy',
            'database': db_status,
            'message': 'Melapro API is running'
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500

# API info endpoint
@app.route('/api', methods=['GET'])
def api_info():
    """API information endpoint"""
    return jsonify({
        'name': 'Melapro API',
        'version': '1.0.0',
        'description': 'Offline-first inventory management system for small retail businesses',
        'endpoints': {
            'products': '/api/products',
            'sales': '/api/sales',
            'categories': '/api/categories',
            'suppliers': '/api/suppliers',
            'customers': '/api/customers',
            'warehouses': '/api/warehouses',
            'health': '/api/health'
        }
    })

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return jsonify({
                'message': 'Melapro API',
                'version': '1.0.0',
                'api_docs': '/api'
            })

if __name__ == '__main__':
    # Initialize database on startup
    initialize_database()
    app.run(host='0.0.0.0', port=5000, debug=True)

