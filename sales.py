from flask import Blueprint, jsonify, request
from datetime import datetime
from src.services.database_service import db_service
from src.models.inventory import SalesOrder, SalesOrderItem

sales_bp = Blueprint('sales', __name__)

@sales_bp.route('/sales', methods=['GET'])
def get_sales_orders():
    """Get all sales orders with optional filtering"""
    try:
        # Get query parameters
        start_date = request.args.get('start_date', '')
        end_date = request.args.get('end_date', '')
        customer_id = request.args.get('customer_id', '')
        warehouse_id = request.args.get('warehouse_id', '')
        status = request.args.get('status', '')
        limit = int(request.args.get('limit', 100))
        skip = int(request.args.get('skip', 0))
        
        if start_date and end_date:
            # Get sales by date range
            sales_orders = db_service.get_sales_by_date_range(start_date, end_date)
        else:
            # Get all sales orders
            selector = {}
            if customer_id:
                selector['customer_id'] = customer_id
            if warehouse_id:
                selector['warehouse_id'] = warehouse_id
            if status:
                selector['status'] = status
                
            sales_orders = db_service.find_documents('sales_order', limit, skip, selector)
        
        # Sort by order date (most recent first)
        sales_orders.sort(key=lambda x: x.get('order_date', ''), reverse=True)
        
        return jsonify({
            'success': True,
            'data': sales_orders,
            'count': len(sales_orders)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@sales_bp.route('/sales', methods=['POST'])
def create_sales_order():
    """Create a new sales order"""
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['items', 'warehouse_id']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        if not data['items']:
            return jsonify({
                'success': False,
                'error': 'Sales order must have at least one item'
            }), 400
        
        # Validate and process items
        processed_items = []
        total_amount = 0.0
        
        for item_data in data['items']:
            # Validate item fields
            if not all(k in item_data for k in ['product_id', 'quantity', 'unit_price']):
                return jsonify({
                    'success': False,
                    'error': 'Each item must have product_id, quantity, and unit_price'
                }), 400
            
            # Get product details
            product = db_service.get_document(item_data['product_id'])
            if not product or product.get('type') != 'product':
                return jsonify({
                    'success': False,
                    'error': f'Product not found: {item_data["product_id"]}'
                }), 400
            
            # Check stock availability
            warehouse_id = data['warehouse_id']
            current_stock = product.get('current_stock', {})
            available_stock = current_stock.get(warehouse_id, 0)
            
            if available_stock < item_data['quantity']:
                return jsonify({
                    'success': False,
                    'error': f'Insufficient stock for product {product.get("name", "")}. Available: {available_stock}, Requested: {item_data["quantity"]}'
                }), 400
            
            # Create order item
            item = SalesOrderItem(
                product_id=item_data['product_id'],
                product_name=product.get('name', ''),
                sku=product.get('sku', ''),
                quantity=int(item_data['quantity']),
                unit_price=float(item_data['unit_price']),
                discount=float(item_data.get('discount', 0)),
                batch_no=item_data.get('batch_no', ''),
                expiry_date=item_data.get('expiry_date', '')
            )
            
            processed_items.append(item.to_dict())
            
            # Calculate item total
            item_total = item.quantity * item.unit_price - item.discount
            total_amount += item_total
        
        # Create sales order
        sales_order = SalesOrder(
            order_date=data.get('order_date', datetime.utcnow().isoformat()),
            customer_id=data.get('customer_id', ''),
            customer_name=data.get('customer_name', ''),
            items=processed_items,
            total_amount=total_amount,
            payment_status=data.get('payment_status', 'pending'),
            payment_method=data.get('payment_method', 'cash'),
            notes=data.get('notes', ''),
            warehouse_id=data['warehouse_id'],
            status=data.get('status', 'completed')
        )
        
        # Save the sales order
        order_id = db_service.create_document(sales_order)
        if not order_id:
            return jsonify({
                'success': False,
                'error': 'Failed to create sales order'
            }), 500
        
        # Update stock for each item
        for item in processed_items:
            success = db_service.update_product_stock(
                product_id=item['product_id'],
                warehouse_id=data['warehouse_id'],
                quantity_change=-item['quantity'],  # Negative for sale
                movement_type='SALE',
                reference_id=order_id,
                reference_type='sales_order'
            )
            
            if not success:
                # If stock update fails, we should ideally rollback the order
                # For now, we'll log the error
                print(f"Failed to update stock for product {item['product_id']}")
        
        # Get the created order to return
        created_order = db_service.get_document(order_id)
        return jsonify({
            'success': True,
            'data': created_order
        }), 201
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@sales_bp.route('/sales/<order_id>', methods=['GET'])
def get_sales_order(order_id):
    """Get a specific sales order by ID"""
    try:
        order = db_service.get_document(order_id)
        if not order or order.get('type') != 'sales_order':
            return jsonify({
                'success': False,
                'error': 'Sales order not found'
            }), 404
        
        return jsonify({
            'success': True,
            'data': order
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@sales_bp.route('/sales/<order_id>', methods=['PUT'])
def update_sales_order(order_id):
    """Update a sales order (limited fields)"""
    try:
        data = request.json
        
        # Get existing order
        existing_order = db_service.get_document(order_id)
        if not existing_order or existing_order.get('type') != 'sales_order':
            return jsonify({
                'success': False,
                'error': 'Sales order not found'
            }), 404
        
        # Only allow updating certain fields for completed orders
        order = SalesOrder.from_dict(existing_order)
        
        # Update allowed fields
        if 'payment_status' in data:
            order.payment_status = data['payment_status']
        if 'payment_method' in data:
            order.payment_method = data['payment_method']
        if 'notes' in data:
            order.notes = data['notes']
        if 'customer_id' in data:
            order.customer_id = data['customer_id']
        if 'customer_name' in data:
            order.customer_name = data['customer_name']
        
        # Update the order
        if db_service.update_document(order):
            updated_order = db_service.get_document(order_id)
            return jsonify({
                'success': True,
                'data': updated_order
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to update sales order'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@sales_bp.route('/sales/<order_id>/cancel', methods=['POST'])
def cancel_sales_order(order_id):
    """Cancel a sales order and restore stock"""
    try:
        # Get existing order
        existing_order = db_service.get_document(order_id)
        if not existing_order or existing_order.get('type') != 'sales_order':
            return jsonify({
                'success': False,
                'error': 'Sales order not found'
            }), 404
        
        if existing_order.get('status') == 'cancelled':
            return jsonify({
                'success': False,
                'error': 'Sales order is already cancelled'
            }), 400
        
        # Update order status
        order = SalesOrder.from_dict(existing_order)
        order.status = 'cancelled'
        
        if not db_service.update_document(order):
            return jsonify({
                'success': False,
                'error': 'Failed to cancel sales order'
            }), 500
        
        # Restore stock for each item
        for item in existing_order.get('items', []):
            success = db_service.update_product_stock(
                product_id=item['product_id'],
                warehouse_id=existing_order['warehouse_id'],
                quantity_change=item['quantity'],  # Positive to restore stock
                movement_type='ADJUSTMENT',
                reference_id=order_id,
                reference_type='sales_order_cancellation'
            )
            
            if not success:
                print(f"Failed to restore stock for product {item['product_id']}")
        
        # Get the updated order
        updated_order = db_service.get_document(order_id)
        return jsonify({
            'success': True,
            'data': updated_order
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@sales_bp.route('/sales/reports/summary', methods=['GET'])
def get_sales_summary():
    """Get sales summary for a date range"""
    try:
        start_date = request.args.get('start_date', '')
        end_date = request.args.get('end_date', '')
        warehouse_id = request.args.get('warehouse_id', '')
        
        if not start_date or not end_date:
            return jsonify({
                'success': False,
                'error': 'start_date and end_date are required'
            }), 400
        
        # Get sales orders for the date range
        sales_orders = db_service.get_sales_by_date_range(start_date, end_date)
        
        # Filter by warehouse if specified
        if warehouse_id:
            sales_orders = [order for order in sales_orders if order.get('warehouse_id') == warehouse_id]
        
        # Calculate summary
        total_orders = len(sales_orders)
        total_revenue = sum(order.get('total_amount', 0) for order in sales_orders if order.get('status') != 'cancelled')
        completed_orders = len([order for order in sales_orders if order.get('status') == 'completed'])
        cancelled_orders = len([order for order in sales_orders if order.get('status') == 'cancelled'])
        
        # Payment status breakdown
        paid_orders = len([order for order in sales_orders if order.get('payment_status') == 'paid'])
        pending_orders = len([order for order in sales_orders if order.get('payment_status') == 'pending'])
        
        # Top selling products
        product_sales = {}
        for order in sales_orders:
            if order.get('status') != 'cancelled':
                for item in order.get('items', []):
                    product_id = item.get('product_id')
                    if product_id not in product_sales:
                        product_sales[product_id] = {
                            'product_name': item.get('product_name', ''),
                            'sku': item.get('sku', ''),
                            'total_quantity': 0,
                            'total_revenue': 0
                        }
                    product_sales[product_id]['total_quantity'] += item.get('quantity', 0)
                    product_sales[product_id]['total_revenue'] += (item.get('quantity', 0) * item.get('unit_price', 0) - item.get('discount', 0))
        
        # Sort by quantity sold
        top_products = sorted(product_sales.values(), key=lambda x: x['total_quantity'], reverse=True)[:10]
        
        summary = {
            'date_range': {
                'start_date': start_date,
                'end_date': end_date
            },
            'totals': {
                'total_orders': total_orders,
                'completed_orders': completed_orders,
                'cancelled_orders': cancelled_orders,
                'total_revenue': total_revenue
            },
            'payment_status': {
                'paid_orders': paid_orders,
                'pending_orders': pending_orders
            },
            'top_products': top_products
        }
        
        return jsonify({
            'success': True,
            'data': summary
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

