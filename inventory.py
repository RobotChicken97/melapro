from datetime import datetime
from typing import Optional, Dict, Any
import uuid

class BaseModel:
    """Base model class for CouchDB documents"""
    
    def __init__(self, **kwargs):
        self._id = kwargs.get('_id', str(uuid.uuid4()))
        if '_rev' in kwargs and kwargs['_rev']:
            self._rev = kwargs['_rev']
        self.created_at = kwargs.get('created_at', datetime.utcnow().isoformat())
        self.updated_at = kwargs.get('updated_at', datetime.utcnow().isoformat())
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary for CouchDB storage"""
        result = {}
        for key, value in self.__dict__.items():
            if key == '_rev' and not hasattr(self, '_rev'):
                continue
            if not key.startswith('_') or key in ['_id', '_rev']:
                result[key] = value
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Create model instance from CouchDB document"""
        return cls(**data)
    
    def update_timestamp(self):
        """Update the updated_at timestamp"""
        self.updated_at = datetime.utcnow().isoformat()

class Product(BaseModel):
    """Product model for inventory items"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.type = 'product'
        self.name = kwargs.get('name', '')
        self.description = kwargs.get('description', '')
        self.sku = kwargs.get('sku', '')
        self.barcode = kwargs.get('barcode', '')
        self.category_id = kwargs.get('category_id', '')
        self.supplier_id = kwargs.get('supplier_id', '')
        self.price = kwargs.get('price', 0.0)
        self.cost_price = kwargs.get('cost_price', 0.0)
        self.unit = kwargs.get('unit', 'each')
        self.reorder_point = kwargs.get('reorder_point', 0)
        self.current_stock = kwargs.get('current_stock', {})  # warehouse_id -> quantity
        self.is_active = kwargs.get('is_active', True)
    
    def get_total_stock(self) -> int:
        """Get total stock across all warehouses"""
        return sum(self.current_stock.values())
    
    def get_stock_by_warehouse(self, warehouse_id: str) -> int:
        """Get stock for a specific warehouse"""
        return self.current_stock.get(warehouse_id, 0)
    
    def update_stock(self, warehouse_id: str, quantity_change: int):
        """Update stock for a specific warehouse"""
        current = self.current_stock.get(warehouse_id, 0)
        self.current_stock[warehouse_id] = max(0, current + quantity_change)
        self.update_timestamp()

class Category(BaseModel):
    """Category model for product classification"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.type = 'category'
        self.name = kwargs.get('name', '')
        self.description = kwargs.get('description', '')
        self.parent_category_id = kwargs.get('parent_category_id', '')
        self.is_active = kwargs.get('is_active', True)

class Supplier(BaseModel):
    """Supplier model for product vendors"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.type = 'supplier'
        self.name = kwargs.get('name', '')
        self.contact_info = kwargs.get('contact_info', {})
        self.email = kwargs.get('email', '')
        self.phone = kwargs.get('phone', '')
        self.address = kwargs.get('address', '')
        self.payment_terms = kwargs.get('payment_terms', '')
        self.is_active = kwargs.get('is_active', True)

class Customer(BaseModel):
    """Customer model for retail customers"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.type = 'customer'
        self.name = kwargs.get('name', '')
        self.email = kwargs.get('email', '')
        self.phone = kwargs.get('phone', '')
        self.address = kwargs.get('address', '')
        self.loyalty_program_id = kwargs.get('loyalty_program_id', '')
        self.loyalty_points = kwargs.get('loyalty_points', 0)
        self.is_active = kwargs.get('is_active', True)

class Warehouse(BaseModel):
    """Warehouse model for inventory locations"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.type = 'warehouse'
        self.name = kwargs.get('name', '')
        self.location = kwargs.get('location', '')
        self.description = kwargs.get('description', '')
        self.is_active = kwargs.get('is_active', True)

class SalesOrder(BaseModel):
    """Sales order model for customer transactions"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.type = 'sales_order'
        self.order_date = kwargs.get('order_date', datetime.utcnow().isoformat())
        self.customer_id = kwargs.get('customer_id', '')  # Can be empty for walk-in sales
        self.customer_name = kwargs.get('customer_name', '')  # For walk-in customers
        self.items = kwargs.get('items', [])  # List of order items
        self.total_amount = kwargs.get('total_amount', 0.0)
        self.payment_status = kwargs.get('payment_status', 'pending')  # pending, paid, partial
        self.payment_method = kwargs.get('payment_method', 'cash')
        self.notes = kwargs.get('notes', '')
        self.warehouse_id = kwargs.get('warehouse_id', '')
        self.status = kwargs.get('status', 'completed')  # draft, completed, cancelled
    
    def calculate_total(self):
        """Calculate total amount from items"""
        total = 0.0
        for item in self.items:
            item_total = item.get('quantity', 0) * item.get('unit_price', 0.0)
            item_total -= item.get('discount', 0.0)
            total += item_total
        self.total_amount = total
        return total

class SalesOrderItem:
    """Sales order item (embedded in SalesOrder)"""
    
    def __init__(self, **kwargs):
        self.product_id = kwargs.get('product_id', '')
        self.product_name = kwargs.get('product_name', '')
        self.sku = kwargs.get('sku', '')
        self.quantity = kwargs.get('quantity', 0)
        self.unit_price = kwargs.get('unit_price', 0.0)
        self.discount = kwargs.get('discount', 0.0)
        self.batch_no = kwargs.get('batch_no', '')
        self.expiry_date = kwargs.get('expiry_date', '')
    
    def to_dict(self):
        return self.__dict__

class PurchaseOrder(BaseModel):
    """Purchase order model for supplier orders"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.type = 'purchase_order'
        self.order_date = kwargs.get('order_date', datetime.utcnow().isoformat())
        self.supplier_id = kwargs.get('supplier_id', '')
        self.supplier_name = kwargs.get('supplier_name', '')
        self.items = kwargs.get('items', [])
        self.total_cost = kwargs.get('total_cost', 0.0)
        self.status = kwargs.get('status', 'pending')  # pending, ordered, received, cancelled
        self.expected_delivery = kwargs.get('expected_delivery', '')
        self.notes = kwargs.get('notes', '')
        self.warehouse_id = kwargs.get('warehouse_id', '')
    
    def calculate_total(self):
        """Calculate total cost from items"""
        total = 0.0
        for item in self.items:
            total += item.get('quantity', 0) * item.get('cost_price', 0.0)
        self.total_cost = total
        return total

class InventoryMovement(BaseModel):
    """Inventory movement model for tracking stock changes"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.type = 'inventory_movement'
        self.product_id = kwargs.get('product_id', '')
        self.warehouse_id = kwargs.get('warehouse_id', '')
        self.quantity_change = kwargs.get('quantity_change', 0)  # positive for in, negative for out
        self.movement_type = kwargs.get('movement_type', '')  # SALE, PURCHASE, ADJUSTMENT, TRANSFER
        self.reference_id = kwargs.get('reference_id', '')  # ID of related order/transaction
        self.reference_type = kwargs.get('reference_type', '')  # sales_order, purchase_order, etc.
        self.notes = kwargs.get('notes', '')
        self.timestamp = kwargs.get('timestamp', datetime.utcnow().isoformat())

class User(BaseModel):
    """User model for system authentication"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.type = 'user'
        self.username = kwargs.get('username', '')
        self.email = kwargs.get('email', '')
        self.password_hash = kwargs.get('password_hash', '')
        self.full_name = kwargs.get('full_name', '')
        self.roles = kwargs.get('roles', [])  # List of role names
        self.is_active = kwargs.get('is_active', True)
        self.last_login = kwargs.get('last_login', '')

class Role(BaseModel):
    """Role model for access control"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.type = 'role'
        self.name = kwargs.get('name', '')
        self.description = kwargs.get('description', '')
        self.permissions = kwargs.get('permissions', [])  # List of permission strings
        self.is_active = kwargs.get('is_active', True)

class AuditLog(BaseModel):
    """Audit log model for tracking system activities"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.type = 'audit_log'
        self.user_id = kwargs.get('user_id', '')
        self.username = kwargs.get('username', '')
        self.action_type = kwargs.get('action_type', '')  # CREATE, UPDATE, DELETE, LOGIN, etc.
        self.entity_id = kwargs.get('entity_id', '')
        self.entity_type = kwargs.get('entity_type', '')
        self.changes = kwargs.get('changes', {})  # Details of what changed
        self.ip_address = kwargs.get('ip_address', '')
        self.user_agent = kwargs.get('user_agent', '')
        self.timestamp = kwargs.get('timestamp', datetime.utcnow().isoformat())

