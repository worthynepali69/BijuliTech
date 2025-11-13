import sqlite3
import os
from datetime import datetime

# --- This finds the 'db' folder automatically ---
DB_DIR = os.path.dirname(__file__)
DB_NAME = 'bijulitech.db'
DB_PATH = os.path.join(DB_DIR, DB_NAME)

class Database:
    """
    OOP - ABSTRACTION & ENCAPSULATION
    This class handles ALL database interactions.
    The rest of the app doesn't know SQL. It just calls methods
    like 'validate_user' or 'fetch_products'. This hides the
    complexity of the database (Abstraction) and protects the
    database connection (Encapsulation).
    
    This is your "Database Script" for your assignment.
    """
    
    def __init__(self, db_path=DB_PATH):
        """Initializes a connection to the SQLite database."""
        try:
            self.conn = sqlite3.connect(db_path)
            # Use Row factory to get results as dictionaries
            # This lets us access columns by name (e.g., row['name'])
            self.conn.row_factory = sqlite3.Row
            print(f"Successfully connected to database at {db_path}")
        except sqlite3.Error as e:
            print(f"Error connecting to database: {e}")
            raise

    def close(self):
        """Closes the database connection."""
        if self.conn:
            self.conn.close()
            # print("Database connection closed.") # Can be noisy

    def execute_query(self, query, params=(), fetch_one=False, fetch_all=False, commit=False):
        """A generic method to execute any SQL query."""
        try:
            cursor = self.conn.cursor()
            cursor.execute(query, params)

            if commit:
                self.conn.commit()
                # Return the last inserted row's ID (useful for creating orders)
                return cursor.lastrowid

            if fetch_one:
                return cursor.fetchone()
            
            if fetch_all:
                return cursor.fetchall()
                
        except sqlite3.Error as e:
            print(f"SQL Error: {e}")
            print(f"Query: {query}")
            print(f"Params: {params}")
            return None

    # --- User Authentication (Functional Requirement c.1) ---
    def validate_user(self, username, password):
        """Checks if a username and password are valid."""
        query = "SELECT role FROM Users WHERE username = ? AND password = ?"
        user = self.execute_query(query, (username, password), fetch_one=True)
        if user:
            return user['role']
        return None

    # --- NEW: Register User (for Admin Panel) ---
    def register_user(self, username, password, name, phone, email, address, country, role="customer"):
        """
        Registers a new user. Adds to Users table AND Customers table.
        This is a transaction.
        """
        cursor = self.conn.cursor()
        try:
            # 1. Insert into Users table
            user_query = "INSERT INTO Users (username, password, role) VALUES (?, ?, ?)"
            cursor.execute(user_query, (username, password, role))
            
            # 2. Insert into Customers table
            customer_query = """
            INSERT INTO Customers (username, name, phone, email, address, country)
            VALUES (?, ?, ?, ?, ?, ?)
            """
            customer_params = (username, name, phone, email, address, country)
            cursor.execute(customer_query, customer_params)
            
            # 3. Commit the transaction
            self.conn.commit()
            print(f"User {username} registered successfully.")
            return True
        except sqlite3.IntegrityError:
            self.conn.rollback() # Roll back changes
            print(f"Error: Username {username} already exists.")
            return "duplicate"
        except sqlite3.Error as e:
            self.conn.rollback()
            print(f"SQL Error during registration: {e}")
            return False

    # --- Product/Inventory (Functional Requirement c.3) ---
    def fetch_products(self):
        """Fetches all products from the inventory."""
        query = "SELECT * FROM Products"
        return self.execute_query(query, fetch_all=True)

    # --- NEW FEATURE: Search ---
    def search_products(self, search_term):
        """Fetches products where the name matches the search term."""
        query = "SELECT * FROM Products WHERE name LIKE ?"
        params = (f"%{search_term}%",)
        return self.execute_query(query, params, fetch_all=True)
        
    def fetch_product_by_id(self, product_id):
        """Fetches a single product by its ID."""
        query = "SELECT * FROM Products WHERE product_id = ?"
        return self.execute_query(query, (product_id,), fetch_one=True)
    
    # --- NEW: Includes stock_level ---
    def add_product(self, product_id, name, price, stock, description, image):
        """Adds a new product to the database."""
        query = """
        INSERT INTO Products (product_id, name, price, stock_level, description, image)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        try:
            self.execute_query(query, (product_id, name, price, stock, description, image), commit=True)
            print(f"Product {product_id} added.")
            return True
        except sqlite3.IntegrityError:
            print(f"Error: Product ID {product_id} already exists.")
            return "duplicate"
        except Exception as e:
            print(f"Error adding product: {e}")
            return False

    # --- NEW: Includes stock_level ---
    def update_product(self, product_id, name, price, stock, description):
        """Updates an existing product in the database."""
        query = """
        UPDATE Products
        SET name = ?, price = ?, stock_level = ?, description = ?
        WHERE product_id = ?
        """
        self.execute_query(query, (name, price, stock, description, product_id), commit=True)
        print(f"Product {product_id} updated.")
        return True
    
    # --- NEW: Get product stock ---
    def get_product_stock(self, product_id):
        """Gets the current stock level for a single product."""
        query = "SELECT stock_level FROM Products WHERE product_id = ?"
        result = self.execute_query(query, (product_id,), fetch_one=True)
        return result['stock_level'] if result else 0

    # --- NEW: Delete Product (for Admin Panel) ---
    def delete_product(self, product_id):
        """
        Deletes a product.
        Note: Will fail if the product is in an order.
        A better long-term solution is to set product as 'inactive'.
        For this assignment, delete is fine.
        """
        try:
            query = "DELETE FROM Products WHERE product_id = ?"
            self.execute_query(query, (product_id,), commit=True)
            print(f"Product {product_id} deleted.")
            return True
        except sqlite3.IntegrityError as e:
            print(f"Error deleting product {product_id}: {e}. It might be part of an existing order.")
            return False

    # --- Customer Management (Functional Requirement c.2) ---
    def fetch_customers(self):
        """Fetches all customer details."""
        query = "SELECT * FROM Customers"
        return self.execute_query(query, fetch_all=True)
        
    def fetch_customer_by_username(self, username):
        """Gets a customer's saved details by their username."""
        query = "SELECT * FROM Customers WHERE username = ?"
        return self.execute_query(query, (username,), fetch_one=True)
        
    # --- UPDATED: To accept a dictionary from the admin panel ---
    def update_customer_details(self, username, data):
        """Updates a customer's profile information from a dictionary."""
        
        # Update Customers table
        customer_query = """
        UPDATE Customers
        SET name = ?, phone = ?, email = ?, address = ?, country = ?
        WHERE username = ?
        """
        customer_params = (
            data['name'], data['phone'], data['email'], 
            data['address'], data['country'], username
        )
        self.execute_query(customer_query, customer_params, commit=True)
        
        # Update Users table (if password was changed)
        if data['password']:
            password_query = "UPDATE Users SET password = ? WHERE username = ?"
            self.execute_query(password_query, (data['password'], username), commit=True)
            print(f"Customer {username} password updated.")

        print(f"Customer {username} details updated.")
        return True

    # --- NEW: Delete User (for Admin Panel) ---
    def delete_user(self, username):
        """
        Deletes a user from the system.
        Requires "ON DELETE CASCADE" in the database schema.
        """
        try:
            # By deleting from "Users", the ON DELETE CASCADE
            # will automatically delete from "Customers".
            query = "DELETE FROM Users WHERE username = ?"
            self.execute_query(query, (username,), commit=True)
            print(f"User {username} deleted.")
            return True
        except sqlite3.IntegrityError as e:
            # This might fire if the user has orders
            print(f"Error deleting user {username}: {e}. User may have existing orders.")
            return False

    # --- Transaction Processing (Functional Requirement c.4 & c.5) ---
    def create_order(self, username, cart, customer_details):
        """
        Creates a new order and associated order items in the database.
        This is a transaction. It now also decrements stock.
        """
        cursor = self.conn.cursor()
        try:
            # 1. Check stock levels *before* doing anything
            for product_id, item in cart.items():
                current_stock = self.get_product_stock(product_id)
                if current_stock < item['quantity']:
                    print(f"Error: Not enough stock for {item['name']}.")
                    return None # Stock check failed
            
            # 2. Update customer details
            # --- UPDATED: This now uses the new method signature ---
            self.update_customer_details(
                username,
                {
                    "name": customer_details['name'],
                    "phone": customer_details['phone'],
                    "email": customer_details['email'],
                    "address": customer_details['address'],
                    "country": customer_details['country'],
                    "password": None # Don't change password on checkout
                }
            )

            # 3. Create the order
            total_amount = sum(item['price'] * item['quantity'] for item in cart.values())
            order_query = """
            INSERT INTO Orders (customer_username, total_amount, status, shipping_address)
            VALUES (?, ?, ?, ?)
            """
            full_address = f"{customer_details['address']}, {customer_details['country']}"
            order_params = (username, total_amount, 'Paid', full_address)
            
            cursor.execute(order_query, order_params)
            order_id = cursor.lastrowid
            
            # 4. Add items to OrderItems and Decrement Stock
            items_data = []
            decrement_stock_query = "UPDATE Products SET stock_level = stock_level - ? WHERE product_id = ?"
            
            for product_id, item in cart.items():
                # Add to order items list
                items_data.append((
                    order_id,
                    product_id,
                    item['quantity'],
                    item['price']
                ))
                # Execute stock decrement
                cursor.execute(decrement_stock_query, (item['quantity'], product_id))
            
            items_query = """
            INSERT INTO OrderItems (order_id, product_id, quantity, price_per_unit)
            VALUES (?, ?, ?, ?)
            """
            cursor.executemany(items_query, items_data)
            
            # 5. Commit the entire transaction
            self.conn.commit()
            print(f"Successfully created Order #{order_id}")
            return order_id
            
        except sqlite3.Error as e:
            self.conn.rollback() # Roll back all changes if any part failed
            print(f"Error creating order: {e}")
            return None

    # --- Reporting (Functional Requirement c.6) & Admin ---
    def fetch_all_orders_summary(self):
        """Fetches all orders with customer name for the admin panel."""
        query = """
        SELECT o.order_id, o.order_date, c.name, o.total_amount, o.status
        FROM Orders o
        JOIN Customers c ON o.customer_username = c.username
        """
        return self.execute_query(query, fetch_all=True)

    def fetch_order_details(self, order_id):
        """Fetches details for a single order (customer, address, items)."""
        order_query = """
        SELECT o.order_id, o.order_date, o.total_amount, o.status, o.shipping_address,
               c.name, c.email, c.phone
        FROM Orders o
        JOIN Customers c ON o.customer_username = c.username
        WHERE o.order_id = ?
        """
        order_details = self.execute_query(order_query, (order_id,), fetch_one=True)
        
        items_query = """
        SELECT p.name, oi.quantity, oi.price_per_unit
        FROM OrderItems oi
        JOIN Products p ON oi.product_id = p.product_id
        WHERE oi.order_id = ?
        """
        items_details = self.execute_query(items_query, (order_id,), fetch_all=True)
        
        return order_details, items_details
        
    def update_order_status(self, order_id, new_status):
        """Updates the status of an order (e.g., 'Shipped', 'Delivered')."""
        query = "UPDATE Orders SET status = ? WHERE order_id = ?"
        self.execute_query(query, (new_status, order_id), commit=True)
        print(f"Order {order_id} status updated to {new_status}")
        return True
        
    def get_daily_sales_report(self):
        """Generates a simple daily sales report."""
        query = """
        SELECT 
            DATE(order_date) as 'Date', 
            COUNT(order_id) as 'Total Orders', 
            SUM(total_amount) as 'Total Revenue'
        FROM Orders
        WHERE status != 'Cancelled'
        GROUP BY DATE(order_date)
        ORDER BY DATE(order_date) DESC
        """
        return self.execute_query(query, fetch_all=True)
        
    def get_inventory_report(self):
        """Generates a simple inventory report."""
        query = """
        SELECT
            p.product_id,
            p.name,
            p.stock_level,
            p.price,
            COALESCE(SUM(oi.quantity), 0) as 'Total Units Sold'
        FROM Products p
        LEFT JOIN OrderItems oi ON p.product_id = oi.product_id
        GROUP BY p.product_id, p.name, p.price, p.stock_level
        ORDER BY 'Total Units Sold' DESC
        """
        return self.execute_query(query, fetch_all=True)

    def __del__(self):
        """Destructor to ensure the connection is closed when the app exits."""
        self.close()