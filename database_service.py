from typing import List, Optional, Dict, Any
import couchdb
from src.database_config import db_config
from src.models.inventory import (
    BaseModel, Product, Category, Supplier, Customer, Warehouse,
    SalesOrder, PurchaseOrder, InventoryMovement, User, Role, AuditLog
)

class DatabaseService:
    """Service class for database operations"""
    
    def __init__(self, db_name: str = 'inventory_system'):
        self.db_name = db_name
        self.db = None
        self._connect()
    
    def _connect(self):
        """Connect to the database"""
        self.db = db_config.get_database(self.db_name)
        if self.db:
            db_config.create_indexes(self.db_name)
    
    def create_document(self, model: BaseModel) -> Optional[str]:
        """Create a new document in the database"""
        if not self.db:
            return None
            
        try:
            doc_data = model.to_dict()
            doc_id, doc_rev = self.db.save(doc_data)
            return doc_id
        except Exception as e:
            print(f"Error creating document: {e}")
            return None
    
    def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Get a document by ID"""
        if not self.db:
            return None
            
        try:
            return dict(self.db[doc_id])
        except couchdb.ResourceNotFound:
            return None
        except Exception as e:
            print(f"Error getting document {doc_id}: {e}")
            return None
    
    def update_document(self, model: BaseModel) -> bool:
        """Update an existing document"""
        if not self.db:
            return False
            
        try:
            # Get current document to get the latest _rev
            current_doc = self.get_document(model._id)
            if not current_doc:
                return False
                
            # Update the model's _rev
            model._rev = current_doc['_rev']
            model.update_timestamp()
            
            # Save the updated document
            doc_data = model.to_dict()
            doc_id, doc_rev = self.db.save(doc_data)
            model._rev = doc_rev
            return True
        except Exception as e:
            print(f"Error updating document: {e}")
            return False
    
    def delete_document(self, doc_id: str) -> bool:
        """Delete a document by ID"""
        if not self.db:
            return False
            
        try:
            doc = self.db[doc_id]
            self.db.delete(doc)
            return True
        except couchdb.ResourceNotFound:
            return False
        except Exception as e:
            print(f"Error deleting document {doc_id}: {e}")
            return False
    
    def find_documents(self, doc_type: str, limit: int = 100, skip: int = 0, 
                      selector: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """Find documents by type with optional selector"""
        if not self.db:
            return []
            
        try:
            # Use a simple view-based approach for now
            # In production, you'd want to use Mango queries or views
            results = []
            for doc_id in self.db:
                try:
                    doc = dict(self.db[doc_id])
                    if doc.get('type') == doc_type:
                        # Apply selector if provided
                        if selector:
                            match = True
                            for key, value in selector.items():
                                if doc.get(key) != value:
                                    match = False
                                    break
                            if not match:
                                continue
                        results.append(doc)
                        
                        if len(results) >= limit + skip:
                            break
                except:
                    continue
            
            # Apply skip and limit
            return results[skip:skip + limit]
        except Exception as e:
            print(f"Error finding documents: {e}")
            return []
    
    def search_products(self, query: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Search products by name, SKU, or description"""
        if not self.db:
            return []
            
        try:
            results = []
            query_lower = query.lower()
            
            for doc_id in self.db:
                try:
                    doc = dict(self.db[doc_id])
                    if doc.get('type') == 'product':
                        # Simple text search
                        searchable_text = (
                            doc.get('name', '').lower() + ' ' +
                            doc.get('sku', '').lower() + ' ' +
                            doc.get('description', '').lower()
                        )
                        
                        if query_lower in searchable_text:
                            results.append(doc)
                            
                        if len(results) >= limit:
                            break
                except:
                    continue
                    
            return results
        except Exception as e:
            print(f"Error searching products: {e}")
            return []
    
    def get_low_stock_products(self, warehouse_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get products that are below their reorder point"""
        if not self.db:
            return []
            
        try:
            results = []
            
            for doc_id in self.db:
                try:
                    doc = dict(self.db[doc_id])
                    if doc.get('type') == 'product':
                        reorder_point = doc.get('reorder_point', 0)
                        current_stock = doc.get('current_stock', {})
                        
                        if warehouse_id:
                            stock = current_stock.get(warehouse_id, 0)
                            if stock <= reorder_point:
                                results.append(doc)
                        else:
                            total_stock = sum(current_stock.values())
                            if total_stock <= reorder_point:
                                results.append(doc)
                except:
                    continue
                    
            return results
        except Exception as e:
            print(f"Error getting low stock products: {e}")
            return []
    
    def get_sales_by_date_range(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """Get sales orders within a date range"""
        if not self.db:
            return []
            
        try:
            results = []
            
            for doc_id in self.db:
                try:
                    doc = dict(self.db[doc_id])
                    if doc.get('type') == 'sales_order':
                        order_date = doc.get('order_date', '')
                        if start_date <= order_date <= end_date:
                            results.append(doc)
                except:
                    continue
                    
            # Sort by date
            results.sort(key=lambda x: x.get('order_date', ''), reverse=True)
            return results
        except Exception as e:
            print(f"Error getting sales by date range: {e}")
            return []
    
    def update_product_stock(self, product_id: str, warehouse_id: str, 
                           quantity_change: int, movement_type: str, 
                           reference_id: str = '', reference_type: str = '') -> bool:
        """Update product stock and create inventory movement record"""
        if not self.db:
            return False
            
        try:
            # Get the product
            product_doc = self.get_document(product_id)
            if not product_doc:
                return False
            
            # Update stock
            current_stock = product_doc.get('current_stock', {})
            current_qty = current_stock.get(warehouse_id, 0)
            new_qty = max(0, current_qty + quantity_change)
            current_stock[warehouse_id] = new_qty
            product_doc['current_stock'] = current_stock
            
            # Save updated product
            self.db.save(product_doc)
            
            # Create inventory movement record
            movement = InventoryMovement(
                product_id=product_id,
                warehouse_id=warehouse_id,
                quantity_change=quantity_change,
                movement_type=movement_type,
                reference_id=reference_id,
                reference_type=reference_type
            )
            
            self.create_document(movement)
            return True
            
        except Exception as e:
            print(f"Error updating product stock: {e}")
            return False
    
    def create_audit_log(self, user_id: str, username: str, action_type: str,
                        entity_id: str, entity_type: str, changes: Dict = None,
                        ip_address: str = '', user_agent: str = '') -> bool:
        """Create an audit log entry"""
        try:
            audit_log = AuditLog(
                user_id=user_id,
                username=username,
                action_type=action_type,
                entity_id=entity_id,
                entity_type=entity_type,
                changes=changes or {},
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            return self.create_document(audit_log) is not None
        except Exception as e:
            print(f"Error creating audit log: {e}")
            return False

# Global database service instance
db_service = DatabaseService()

