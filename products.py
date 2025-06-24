from flask import Blueprint, jsonify, request
from src.services.database_service import db_service
from src.models.inventory import Product

product_bp = Blueprint('product', __name__)

@product_bp.route('/products', methods=['GET'])
def get_products():
    """Get all products with optional search and filtering"""
    try:
        # Get query parameters
        search = request.args.get('search', '')
        category_id = request.args.get('category_id', '')
        warehouse_id = request.args.get('warehouse_id', '')
        limit = int(request.args.get('limit', 100))
        skip = int(request.args.get('skip', 0))
        
        if search:
            # Search products by name, SKU, or description
            products = db_service.search_products(search, limit)
        else:
            # Get all products with optional category filter
            selector = {}
            if category_id:
                selector['category_id'] = category_id
                
            products = db_service.find_documents('product', limit, skip, selector)
        
        # Filter by warehouse if specified (products with stock in that warehouse)
        if warehouse_id:
            filtered_products = []
            for product in products:
                current_stock = product.get('current_stock', {})
                if current_stock.get(warehouse_id, 0) > 0:
                    filtered_products.append(product)
            products = filtered_products
        
        return jsonify({
            'success': True,
            'data': products,
            'count': len(products)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@product_bp.route('/products', methods=['POST'])
def create_product():
    """Create a new product"""
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['name', 'sku', 'price']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Check if SKU already exists
        existing_products = db_service.find_documents('product', selector={'sku': data['sku']})
        if existing_products:
            return jsonify({
                'success': False,
                'error': 'Product with this SKU already exists'
            }), 400
        
        # Create product
        product = Product(
            name=data['name'],
            description=data.get('description', ''),
            sku=data['sku'],
            barcode=data.get('barcode', ''),
            category_id=data.get('category_id', ''),
            supplier_id=data.get('supplier_id', ''),
            price=float(data['price']),
            cost_price=float(data.get('cost_price', 0)),
            unit=data.get('unit', 'each'),
            reorder_point=int(data.get('reorder_point', 0)),
            current_stock=data.get('current_stock', {}),
            is_active=data.get('is_active', True)
        )
        
        product_id = db_service.create_document(product)
        if product_id:
            # Get the created product to return
            created_product = db_service.get_document(product_id)
            return jsonify({
                'success': True,
                'data': created_product
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to create product'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@product_bp.route('/products/<product_id>', methods=['GET'])
def get_product(product_id):
    """Get a specific product by ID"""
    try:
        product = db_service.get_document(product_id)
        if not product or product.get('type') != 'product':
            return jsonify({
                'success': False,
                'error': 'Product not found'
            }), 404
        
        return jsonify({
            'success': True,
            'data': product
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@product_bp.route('/products/<product_id>', methods=['PUT'])
def update_product(product_id):
    """Update a product"""
    try:
        data = request.json
        
        # Get existing product
        existing_product = db_service.get_document(product_id)
        if not existing_product or existing_product.get('type') != 'product':
            return jsonify({
                'success': False,
                'error': 'Product not found'
            }), 404
        
        # Check if SKU is being changed and if it conflicts
        if 'sku' in data and data['sku'] != existing_product.get('sku'):
            conflicting_products = db_service.find_documents('product', selector={'sku': data['sku']})
            if conflicting_products:
                return jsonify({
                    'success': False,
                    'error': 'Product with this SKU already exists'
                }), 400
        
        # Update product fields
        product = Product.from_dict(existing_product)
        
        # Update fields if provided
        if 'name' in data:
            product.name = data['name']
        if 'description' in data:
            product.description = data['description']
        if 'sku' in data:
            product.sku = data['sku']
        if 'barcode' in data:
            product.barcode = data['barcode']
        if 'category_id' in data:
            product.category_id = data['category_id']
        if 'supplier_id' in data:
            product.supplier_id = data['supplier_id']
        if 'price' in data:
            product.price = float(data['price'])
        if 'cost_price' in data:
            product.cost_price = float(data['cost_price'])
        if 'unit' in data:
            product.unit = data['unit']
        if 'reorder_point' in data:
            product.reorder_point = int(data['reorder_point'])
        if 'is_active' in data:
            product.is_active = data['is_active']
        
        # Update the product
        if db_service.update_document(product):
            updated_product = db_service.get_document(product_id)
            return jsonify({
                'success': True,
                'data': updated_product
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to update product'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@product_bp.route('/products/<product_id>', methods=['DELETE'])
def delete_product(product_id):
    """Delete a product (soft delete by setting is_active to False)"""
    try:
        # Get existing product
        existing_product = db_service.get_document(product_id)
        if not existing_product or existing_product.get('type') != 'product':
            return jsonify({
                'success': False,
                'error': 'Product not found'
            }), 404
        
        # Soft delete by setting is_active to False
        product = Product.from_dict(existing_product)
        product.is_active = False
        
        if db_service.update_document(product):
            return jsonify({
                'success': True,
                'message': 'Product deleted successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to delete product'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@product_bp.route('/products/low-stock', methods=['GET'])
def get_low_stock_products():
    """Get products that are below their reorder point"""
    try:
        warehouse_id = request.args.get('warehouse_id')
        products = db_service.get_low_stock_products(warehouse_id)
        
        return jsonify({
            'success': True,
            'data': products,
            'count': len(products)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@product_bp.route('/products/<product_id>/stock', methods=['PUT'])
def update_product_stock(product_id):
    """Update product stock for a specific warehouse"""
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['warehouse_id', 'quantity_change', 'movement_type']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Update stock
        success = db_service.update_product_stock(
            product_id=product_id,
            warehouse_id=data['warehouse_id'],
            quantity_change=int(data['quantity_change']),
            movement_type=data['movement_type'],
            reference_id=data.get('reference_id', ''),
            reference_type=data.get('reference_type', '')
        )
        
        if success:
            # Get updated product
            updated_product = db_service.get_document(product_id)
            return jsonify({
                'success': True,
                'data': updated_product
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to update product stock'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@product_bp.route('/products/<product_id>/similar', methods=['GET'])
def get_similar_products(product_id):
    """Get similar products based on category (simple rule-based approach)"""
    try:
        # Get the current product
        product = db_service.get_document(product_id)
        if not product or product.get('type') != 'product':
            return jsonify({
                'success': False,
                'error': 'Product not found'
            }), 404
        
        # Find products in the same category
        similar_products = []
        if product.get('category_id'):
            all_products = db_service.find_documents('product', limit=50)
            for p in all_products:
                if (p.get('category_id') == product.get('category_id') and 
                    p.get('_id') != product_id and 
                    p.get('is_active', True)):
                    similar_products.append(p)
        
        # Limit to 10 similar products
        similar_products = similar_products[:10]
        
        return jsonify({
            'success': True,
            'data': similar_products,
            'count': len(similar_products)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

