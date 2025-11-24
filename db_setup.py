import mysql.connector
from mysql.connector import errorcode

DB_CONFIG = {
    'user': 'root',
    'password': '',
    'host': 'localhost'
}
DB_NAME = 'soft605_pos'

def create_database():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        try:
            cursor.execute(f"CREATE DATABASE {DB_NAME} DEFAULT CHARACTER SET 'utf8'")
            print(f"Database '{DB_NAME}' checked/created.")
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_DB_CREATE_EXISTS:
                print(f"Database '{DB_NAME}' already exists.")
            else:
                print(f"Failed creating database: {err}")
                exit(1)
        conn.close()
    except mysql.connector.Error as err:
        print(f"Connection failed: {err}")
        exit(1)

def create_tables():
    config = DB_CONFIG.copy()
    config['database'] = DB_NAME
    
    try:
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()

        # Clean Slate
        cursor.execute("DROP TABLE IF EXISTS order_items")
        cursor.execute("DROP TABLE IF EXISTS orders")
        cursor.execute("DROP TABLE IF EXISTS users")
        cursor.execute("DROP TABLE IF EXISTS products")
        cursor.execute("DROP TABLE IF EXISTS customers")

        # Create Tables
        cursor.execute("""
            CREATE TABLE users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password VARCHAR(50) NOT NULL,
                role ENUM('admin', 'staff') NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE products (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                price DECIMAL(10, 2) NOT NULL,
                image_path VARCHAR(255),
                stock_level INT NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE customers (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                phone VARCHAR(20),
                email VARCHAR(100),
                customer_type VARCHAR(50) DEFAULT 'Standard',
                loyalty_points INT DEFAULT 0
            )
        """)

        cursor.execute("""
            CREATE TABLE orders (
                id INT AUTO_INCREMENT PRIMARY KEY,
                customer_id INT,
                user_id INT, 
                total_amount DECIMAL(10, 2),
                order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE SET NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE order_items (
                id INT AUTO_INCREMENT PRIMARY KEY,
                order_id INT,
                product_id INT,
                quantity INT,
                price_at_time DECIMAL(10, 2),
                FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
                FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE SET NULL
            )
        """)

        # Seed Data
        users_data = [
            ('nibesh', 'nibesh123', 'admin'),
            ('aayush', 'aayush123', 'admin'),
            ('zimone', 'zimone123', 'staff')
        ]
        cursor.executemany("INSERT INTO users (username, password, role) VALUES (%s, %s, %s)", users_data)

        products_data = [
            ('Gaming PC Mid', 1200.00, 'assets/gpc-mid.png', 10),
            ('High End PC', 2500.00, 'assets/highendpc.png', 5),
            ('JBL Headphone', 150.00, 'assets/jbl headphone.png', 20),
            ('JBL Speaker', 120.00, 'assets/jbl speaker.png', 25),
            ('LG Monitor 27"', 300.00, 'assets/lgmonitor.png', 4),
            ('MacBook Pro', 2100.00, 'assets/macbook pro.png', 8),
            ('Mechanical Keyboard', 110.00, 'assets/mech-key.png', 30),
            ('Samsung S24 Ultra', 1300.00, 'assets/phone-s24.png', 12),
            ('Raspberry Pi 5', 85.00, 'assets/rpi-5.png', 50),
            ('Xiaomi Scooter', 550.00, 'assets/xiaomi.png', 3)
        ]
        cursor.executemany("INSERT INTO products (name, price, image_path, stock_level) VALUES (%s, %s, %s, %s)", products_data)

        customers_data = [
            ('John Doe', '021123456', 'john@example.com', 'Standard', 10),
            ('Jane Smith', '022987654', 'jane@test.com', 'VIP', 150)
        ]
        cursor.executemany("INSERT INTO customers (name, phone, email, customer_type, loyalty_points) VALUES (%s, %s, %s, %s, %s)", customers_data)

        conn.commit()
        print("Database initialized with Loyalty, Staff ID, and Assets.")
        cursor.close()
        conn.close()

    except mysql.connector.Error as err:
        print(f"Error creating tables: {err}")

if __name__ == "__main__":
    create_database()
    create_tables()