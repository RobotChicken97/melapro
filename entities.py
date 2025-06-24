from flask import Blueprint, jsonify, request
from src.services.database_service import db_service
from src.models.inventory import Category, Supplier, Customer, Warehouse

# Categories Blueprint
category_bp = Blueprint('category', __name__)

@category_bp.route('/categories', methods=['GET'])
def get_categories():
    """Get all categories"""
    try:
        categories = db_service.find_documents('category', limit=200)
        return jsonify({
            'success': True,
            'data': categories,
            'count': len(categories)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@category_bp.route('/categories', methods=['POST'])
def create_category():
    """Create a new category"""
    try:
        data = request.json
        
        if not data.get('name'):
            return jsonify({
                'success': False,
                'error': 'Category name is required'
            }), 400
        
        category = Category(
            name=data['name'],
            description=data.get('description', ''),
            parent_category_id=data.get('parent_category_id', ''),
            is_active=data.get('is_active', True)
        )
        
        category_id = db_service.create_document(category)
        if category_id:
            created_category = db_service.get_document(category_id)
            return jsonify({
                'success': True,
                'data': created_category
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to create category'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@category_bp.route('/categories/<category_id>', methods=['PUT'])
def update_category(category_id):
    """Update a category"""
    try:
        data = request.json
        
        existing_category = db_service.get_document(category_id)
        if not existing_category or existing_category.get('type') != 'category':
            return jsonify({
                'success': False,
                'error': 'Category not found'
            }), 404
        
        category = Category.from_dict(existing_category)
        
        if 'name' in data:
            category.name = data['name']
        if 'description' in data:
            category.description = data['description']
        if 'parent_category_id' in data:
            category.parent_category_id = data['parent_category_id']
        if 'is_active' in data:
            category.is_active = data['is_active']
        
        if db_service.update_document(category):
            updated_category = db_service.get_document(category_id)
            return jsonify({
                'success': True,
                'data': updated_category
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to update category'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Suppliers Blueprint
supplier_bp = Blueprint('supplier', __name__)

@supplier_bp.route('/suppliers', methods=['GET'])
def get_suppliers():
    """Get all suppliers"""
    try:
        suppliers = db_service.find_documents('supplier', limit=200)
        return jsonify({
            'success': True,
            'data': suppliers,
            'count': len(suppliers)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@supplier_bp.route('/suppliers', methods=['POST'])
def create_supplier():
    """Create a new supplier"""
    try:
        data = request.json
        
        if not data.get('name'):
            return jsonify({
                'success': False,
                'error': 'Supplier name is required'
            }), 400
        
        supplier = Supplier(
            name=data['name'],
            email=data.get('email', ''),
            phone=data.get('phone', ''),
            address=data.get('address', ''),
            contact_info=data.get('contact_info', {}),
            payment_terms=data.get('payment_terms', ''),
            is_active=data.get('is_active', True)
        )
        
        supplier_id = db_service.create_document(supplier)
        if supplier_id:
            created_supplier = db_service.get_document(supplier_id)
            return jsonify({
                'success': True,
                'data': created_supplier
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to create supplier'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@supplier_bp.route('/suppliers/<supplier_id>', methods=['PUT'])
def update_supplier(supplier_id):
    """Update a supplier"""
    try:
        data = request.json
        
        existing_supplier = db_service.get_document(supplier_id)
        if not existing_supplier or existing_supplier.get('type') != 'supplier':
            return jsonify({
                'success': False,
                'error': 'Supplier not found'
            }), 404
        
        supplier = Supplier.from_dict(existing_supplier)
        
        if 'name' in data:
            supplier.name = data['name']
        if 'email' in data:
            supplier.email = data['email']
        if 'phone' in data:
            supplier.phone = data['phone']
        if 'address' in data:
            supplier.address = data['address']
        if 'contact_info' in data:
            supplier.contact_info = data['contact_info']
        if 'payment_terms' in data:
            supplier.payment_terms = data['payment_terms']
        if 'is_active' in data:
            supplier.is_active = data['is_active']
        
        if db_service.update_document(supplier):
            updated_supplier = db_service.get_document(supplier_id)
            return jsonify({
                'success': True,
                'data': updated_supplier
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to update supplier'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Customers Blueprint
customer_bp = Blueprint('customer', __name__)

@customer_bp.route('/customers', methods=['GET'])
def get_customers():
    """Get all customers"""
    try:
        search = request.args.get('search', '')
        limit = int(request.args.get('limit', 100))
        
        if search:
            # Simple search by name, email, or phone
            all_customers = db_service.find_documents('customer', limit=500)
            customers = []
            search_lower = search.lower()
            
            for customer in all_customers:
                searchable_text = (
                    customer.get('name', '').lower() + ' ' +
                    customer.get('email', '').lower() + ' ' +
                    customer.get('phone', '').lower()
                )
                if search_lower in searchable_text:
                    customers.append(customer)
                    if len(customers) >= limit:
                        break
        else:
            customers = db_service.find_documents('customer', limit=limit)
        
        return jsonify({
            'success': True,
            'data': customers,
            'count': len(customers)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@customer_bp.route('/customers', methods=['POST'])
def create_customer():
    """Create a new customer"""
    try:
        data = request.json
        
        if not data.get('name'):
            return jsonify({
                'success': False,
                'error': 'Customer name is required'
            }), 400
        
        # Check if email already exists (if provided)
        if data.get('email'):
            existing_customers = db_service.find_documents('customer', selector={'email': data['email']})
            if existing_customers:
                return jsonify({
                    'success': False,
                    'error': 'Customer with this email already exists'
                }), 400
        
        customer = Customer(
            name=data['name'],
            email=data.get('email', ''),
            phone=data.get('phone', ''),
            address=data.get('address', ''),
            loyalty_program_id=data.get('loyalty_program_id', ''),
            loyalty_points=int(data.get('loyalty_points', 0)),
            is_active=data.get('is_active', True)
        )
        
        customer_id = db_service.create_document(customer)
        if customer_id:
            created_customer = db_service.get_document(customer_id)
            return jsonify({
                'success': True,
                'data': created_customer
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to create customer'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@customer_bp.route('/customers/<customer_id>', methods=['PUT'])
def update_customer(customer_id):
    """Update a customer"""
    try:
        data = request.json
        
        existing_customer = db_service.get_document(customer_id)
        if not existing_customer or existing_customer.get('type') != 'customer':
            return jsonify({
                'success': False,
                'error': 'Customer not found'
            }), 404
        
        # Check email uniqueness if being changed
        if 'email' in data and data['email'] != existing_customer.get('email'):
            conflicting_customers = db_service.find_documents('customer', selector={'email': data['email']})
            if conflicting_customers:
                return jsonify({
                    'success': False,
                    'error': 'Customer with this email already exists'
                }), 400
        
        customer = Customer.from_dict(existing_customer)
        
        if 'name' in data:
            customer.name = data['name']
        if 'email' in data:
            customer.email = data['email']
        if 'phone' in data:
            customer.phone = data['phone']
        if 'address' in data:
            customer.address = data['address']
        if 'loyalty_program_id' in data:
            customer.loyalty_program_id = data['loyalty_program_id']
        if 'loyalty_points' in data:
            customer.loyalty_points = int(data['loyalty_points'])
        if 'is_active' in data:
            customer.is_active = data['is_active']
        
        if db_service.update_document(customer):
            updated_customer = db_service.get_document(customer_id)
            return jsonify({
                'success': True,
                'data': updated_customer
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to update customer'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Warehouses Blueprint
warehouse_bp = Blueprint('warehouse', __name__)

@warehouse_bp.route('/warehouses', methods=['GET'])
def get_warehouses():
    """Get all warehouses"""
    try:
        warehouses = db_service.find_documents('warehouse', limit=100)
        return jsonify({
            'success': True,
            'data': warehouses,
            'count': len(warehouses)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@warehouse_bp.route('/warehouses', methods=['POST'])
def create_warehouse():
    """Create a new warehouse"""
    try:
        data = request.json
        
        if not data.get('name'):
            return jsonify({
                'success': False,
                'error': 'Warehouse name is required'
            }), 400
        
        warehouse = Warehouse(
            name=data['name'],
            location=data.get('location', ''),
            description=data.get('description', ''),
            is_active=data.get('is_active', True)
        )
        
        warehouse_id = db_service.create_document(warehouse)
        if warehouse_id:
            created_warehouse = db_service.get_document(warehouse_id)
            return jsonify({
                'success': True,
                'data': created_warehouse
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to create warehouse'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@warehouse_bp.route('/warehouses/<warehouse_id>', methods=['PUT'])
def update_warehouse(warehouse_id):
    """Update a warehouse"""
    try:
        data = request.json
        
        existing_warehouse = db_service.get_document(warehouse_id)
        if not existing_warehouse or existing_warehouse.get('type') != 'warehouse':
            return jsonify({
                'success': False,
                'error': 'Warehouse not found'
            }), 404
        
        warehouse = Warehouse.from_dict(existing_warehouse)
        
        if 'name' in data:
            warehouse.name = data['name']
        if 'location' in data:
            warehouse.location = data['location']
        if 'description' in data:
            warehouse.description = data['description']
        if 'is_active' in data:
            warehouse.is_active = data['is_active']
        
        if db_service.update_document(warehouse):
            updated_warehouse = db_service.get_document(warehouse_id)
            return jsonify({
                'success': True,
                'data': updated_warehouse
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to update warehouse'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

