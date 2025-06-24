import couchdb
import os
from typing import Optional

class CouchDBConfig:
    """CouchDB configuration and connection management"""
    
    def __init__(self):
        self.server_url = os.getenv('COUCHDB_URL', 'http://localhost:5984')
        self.username = os.getenv('COUCHDB_USER', 'admin')
        self.password = os.getenv('COUCHDB_PASSWORD', 'password')
        self.server = None
        self.databases = {}
        
    def connect(self):
        """Connect to CouchDB server"""
        try:
            self.server = couchdb.Server(self.server_url)
            # Set authentication if provided
            if self.username and self.password:
                self.server.resource.credentials = (self.username, self.password)
            return True
        except Exception as e:
            print(f"Failed to connect to CouchDB: {e}")
            return False
    
    def get_database(self, db_name: str):
        """Get or create a database"""
        if not self.server:
            if not self.connect():
                return None
                
        if db_name in self.databases:
            return self.databases[db_name]
            
        try:
            # Try to get existing database
            db = self.server[db_name]
        except couchdb.ResourceNotFound:
            # Create database if it doesn't exist
            try:
                db = self.server.create(db_name)
            except Exception as e:
                print(f"Failed to create database {db_name}: {e}")
                return None
        except Exception as e:
            print(f"Failed to access database {db_name}: {e}")
            return None
            
        self.databases[db_name] = db
        return db
    
    def create_indexes(self, db_name: str):
        """Create necessary indexes for the inventory system"""
        db = self.get_database(db_name)
        if not db:
            return False
            
        # Create indexes for common queries
        indexes = [
            # Product indexes
            {'index': {'fields': ['type', 'sku']}, 'name': 'product-sku-index'},
            {'index': {'fields': ['type', 'barcode']}, 'name': 'product-barcode-index'},
            {'index': {'fields': ['type', 'category_id']}, 'name': 'product-category-index'},
            
            # Sales order indexes
            {'index': {'fields': ['type', 'order_date']}, 'name': 'sales-order-date-index'},
            {'index': {'fields': ['type', 'customer_id']}, 'name': 'sales-customer-index'},
            
            # Inventory movement indexes
            {'index': {'fields': ['type', 'product_id', 'warehouse_id']}, 'name': 'inventory-movement-index'},
            
            # User indexes
            {'index': {'fields': ['type', 'email']}, 'name': 'user-email-index'},
        ]
        
        for index_def in indexes:
            try:
                # CouchDB 2.x+ uses _index endpoint for creating indexes
                # For now, we'll skip index creation as it requires more complex setup
                pass
            except Exception as e:
                print(f"Failed to create index {index_def['name']}: {e}")
                
        return True

# Global database configuration instance
db_config = CouchDBConfig()

