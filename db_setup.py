import sqlite3
import os

# --- This finds the 'db' folder automatically ---
DB_DIR = os.path.dirname(__file__)
DB_NAME = 'bijulitech.db'
DB_PATH = os.path.join(DB_DIR, DB_NAME)

def setup_database():
    """
    Creates and populates all necessary tables for the Bijuli Tech app.
    This function is idempotent (safe to run multiple times).
    
    This is your "Script of Tables +data" for your assignment.
    """
    
    # Delete old database file if it exists, to start fresh
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print(f"Removed old database '{DB_NAME}'.")

    # This creates the blank 'bijulitech.db' file
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    print(f"Database '{DB_NAME}' created at '{DB_PATH}'.")

    # --- Create Tables ---
    print("Creating tables...")
    
    # 1. Users Table (for authentication)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Users (
        username TEXT PRIMARY KEY,
        password TEXT NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('customer', 'admin'))
    );
    """)

    # 2. Products Table (the inventory)
    # --- UPDATED: Added stock_level ---
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Products (
      product_id TEXT PRIMARY KEY,
      name TEXT NOT NULL,
      price REAL NOT NULL,
      stock_level INTEGER DEFAULT 10, -- NEW COLUMN
      description TEXT,
      image TEXT
    );
    """)

    # 3. Customers Table (for saving checkout details)
    # --- UPDATED: Added ON DELETE CASCADE ---
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Customers (
        customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL, -- Links to Users table
        name TEXT NOT NULL,
        phone TEXT,
        email TEXT,
        address TEXT,
        country TEXT,
        FOREIGN KEY(username) REFERENCES Users(username) ON DELETE CASCADE
    );
    """)
    
    # 4. Orders Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Orders (
      order_id INTEGER PRIMARY KEY AUTOINCREMENT,
      customer_username TEXT,
      order_date TEXT DEFAULT CURRENT_TIMESTAMP,
      total_amount REAL,
      status TEXT DEFAULT 'Pending',
      shipping_address TEXT,
      FOREIGN KEY(customer_username) REFERENCES Users(username)
    );
    """)
    
    # 5. OrderItems Table (links Products to Orders)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS OrderItems (
      order_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
      order_id INTEGER,
      product_id TEXT,
      quantity INTEGER,
      price_per_unit REAL,
      FOREIGN KEY(order_id) REFERENCES Orders(order_id),
      FOREIGN KEY(product_id) REFERENCES Products(product_id)
    );
    """)
    print("Tables created successfully.")

    # --- Insert Sample Data ---
    print("Inserting sample data...")
    
    # 1. Sample Users (as per your spec)
    try:
        users = [
            ('saba', 'saba123', 'customer'),
            ('admin', 'admin123', 'admin')
        ]
        cursor.executemany("INSERT INTO Users (username, password, role) VALUES (?,?,?)", users)
    except sqlite3.IntegrityError:
        print("Users already exist.")

    # 2. Sample Products (10 items as requested)
    # --- UPDATED: Added stock_level values ---
    try:
        products = [
            ('GPC-MID', 'Mid-tier Gaming PC', 1899.99, 15, 'A solid 1440p gaming machine. Ryzen 5, RTX 4060, 32GB RAM.', 'gpc-mid.png'),
            ('GPC-HIGH', 'Overpowered Gaming PC', 4499.99, 5, 'Ultimate 4K gaming rig. Intel i9, RTX 4090, 64GB RAM.', 'gpc-high.png'),
            ('RPI-5', 'Raspberry Pi 5', 149.00, 50, '8GB RAM model. Perfect for hobbyists and projects.', 'rpi-5.png'),
            ('PHONE-S24', 'Flagship Smartphone', 1999.00, 20, 'The latest model with 200MP camera and AI features.', 'phone-s24.png'),
            ('SCOOT-XIPRO', 'Xiaomi Scooter Pro 4', 899.00, 0, 'Electric scooter with 45km range. (OUT OF STOCK)', 'scoot-xipro.png'), # Out of stock
            ('JBL-CH5', 'JBL Charge 5 Speaker', 249.99, 30, 'Portable Bluetooth speaker with deep bass and waterproof design.', 'jbl-ch5.png'),
            ('JBL-T760', 'JBL Tune 760NC Headphone', 199.99, 25, 'Wireless Active Noise-Cancelling headphones.', 'jbl-t760.png'),
            ('LAP-M3P', 'Pro Laptop 14"', 3299.00, 10, 'M3 Pro chip, 18GB RAM, 1TB SSD. For professional creators.', 'lap-m3p.png'),
            ('MON-DW', '34" Ultrawide Monitor', 799.00, 12, 'Curved 144Hz WQHD monitor for immersive gaming.', 'mon-dw.png'),
            ('KEY-MECH', 'Mechanical Keyboard', 219.00, 40, 'RGB Mechanical Keyboard with Cherry MX Brown switches.', 'key-mech.png')
        ]
        cursor.executemany("INSERT INTO Products (product_id, name, price, stock_level, description, image) VALUES (?,?,?,?,?,?)", products)
    except sqlite3.IntegrityError:
        print("Products already exist.")
        
    # 3. Sample Customer profile for 'saba'
    try:
        cursor.execute("""
        INSERT INTO Customers (username, name, phone, email, address, country) 
        VALUES ('saba', 'Saba', '021 123 4567', 'saba@example.com', '123 Queen St, Auckland', 'New Zealand')
        """)
    except sqlite3.IntegrityError:
        print("Customer 'saba' already exists.")

    conn.commit()
    conn.close()
    print("Database setup complete!")

if __name__ == "__main__":
    setup_database()