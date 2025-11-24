import mysql.connector

class Database:
    def __init__(self):
        self.config = {
            'user': 'root',
            'password': '',
            'host': 'localhost',
            'database': 'soft605_pos'
        }

    def get_connection(self):
        try:
            return mysql.connector.connect(**self.config)
        except mysql.connector.Error as err:
            print(f"DB Connection Error: {err}")
            return None

    def login(self, username, password):
        conn = self.get_connection()
        if not conn: return None
        try:
            cursor = conn.cursor(dictionary=True, buffered=True)
            cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
            return cursor.fetchone()
        finally:
            if conn.is_connected(): cursor.close(); conn.close()

    def get_all_products(self):
        conn = self.get_connection()
        if not conn: return []
        try:
            cursor = conn.cursor(dictionary=True, buffered=True)
            cursor.execute("SELECT id, name, price, image_path, stock_level FROM products")
            return cursor.fetchall()
        finally:
            if conn.is_connected(): cursor.close(); conn.close()

    def add_product(self, name, price, image_path, stock):
        conn = self.get_connection()
        if not conn: return False
        try:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO products (name, price, image_path, stock_level) VALUES (%s, %s, %s, %s)", 
                           (name, round(float(price), 2), image_path, int(stock)))
            conn.commit()
            return True
        finally:
            if conn.is_connected(): cursor.close(); conn.close()

    def update_product(self, pid, name, price, image_path, stock):
        conn = self.get_connection()
        if not conn: return False
        try:
            cursor = conn.cursor()
            cursor.execute("UPDATE products SET name=%s, price=%s, image_path=%s, stock_level=%s WHERE id=%s",
                           (name, round(float(price), 2), image_path, int(stock), int(pid)))
            conn.commit()
            return True
        finally:
            if conn.is_connected(): cursor.close(); conn.close()

    def delete_product(self, pid):
        conn = self.get_connection()
        if not conn: return False
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM products WHERE id = %s", (int(pid),))
            conn.commit()
            return True
        finally:
            if conn.is_connected(): cursor.close(); conn.close()

    def get_all_customers(self):
        conn = self.get_connection()
        if not conn: return []
        try:
            cursor = conn.cursor(dictionary=True, buffered=True)
            cursor.execute("SELECT * FROM customers")
            return cursor.fetchall()
        finally:
            if conn.is_connected(): cursor.close(); conn.close()

    def add_customer(self, name, phone, email, c_type="Standard"):
        conn = self.get_connection()
        if not conn: return False
        try:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO customers (name, phone, email, customer_type, loyalty_points) VALUES (%s, %s, %s, %s, 0)",
                           (name, phone, email, c_type))
            conn.commit()
            return True
        finally:
            if conn.is_connected(): cursor.close(); conn.close()

    def update_customer(self, cid, name, phone, email, c_type):
        conn = self.get_connection()
        if not conn: return False
        try:
            cursor = conn.cursor()
            cursor.execute("UPDATE customers SET name=%s, phone=%s, email=%s, customer_type=%s WHERE id=%s",
                           (name, phone, email, c_type, int(cid)))
            conn.commit()
            return True
        finally:
            if conn.is_connected(): cursor.close(); conn.close()

    def delete_customer(self, cid):
        conn = self.get_connection()
        if not conn: return False
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM customers WHERE id = %s", (int(cid),))
            conn.commit()
            return True
        finally:
            if conn.is_connected(): cursor.close(); conn.close()

    def process_transaction(self, customer_id, user_id, cart_items, total_cost):
        conn = self.get_connection()
        if not conn: return False
        try:
            cursor = conn.cursor()
            conn.start_transaction()

            cursor.execute("INSERT INTO orders (customer_id, user_id, total_amount) VALUES (%s, %s, %s)",
                           (customer_id, user_id, round(float(total_cost), 2)))
            order_id = cursor.lastrowid

            for p_id, qty in cart_items.items():
                p_id_int = int(p_id)
                cursor.execute("SELECT price FROM products WHERE id = %s", (p_id_int,))
                price_res = cursor.fetchone()
                current_price = float(price_res[0] if isinstance(price_res, tuple) else price_res['price'])

                cursor.execute("INSERT INTO order_items (order_id, product_id, quantity, price_at_time) VALUES (%s, %s, %s, %s)",
                               (order_id, p_id_int, qty, current_price))
                cursor.execute("UPDATE products SET stock_level = stock_level - %s WHERE id = %s", (qty, p_id_int))

            if customer_id:
                points = int(total_cost / 10)
                if points > 0:
                    cursor.execute("UPDATE customers SET loyalty_points = loyalty_points + %s WHERE id = %s", (points, customer_id))

            conn.commit()
            return order_id
        except Exception as e:
            print(f"Transaction Failed: {e}")
            conn.rollback()
            return False
        finally:
            if conn.is_connected(): cursor.close(); conn.close()

    def get_order_items(self, order_id):
        conn = self.get_connection()
        if not conn: return []
        try:
            cursor = conn.cursor(dictionary=True)
            query = """
                SELECT p.name, oi.quantity, oi.price_at_time 
                FROM order_items oi
                JOIN products p ON oi.product_id = p.id
                WHERE oi.order_id = %s
            """
            cursor.execute(query, (order_id,))
            return cursor.fetchall()
        finally:
            if conn.is_connected(): cursor.close(); conn.close()

    def get_all_orders(self):
        conn = self.get_connection()
        if not conn: return []
        try:
            cursor = conn.cursor(dictionary=True)
            query = """
                SELECT o.id, c.name as customer, u.username as staff, o.total_amount, o.order_date 
                FROM orders o
                LEFT JOIN customers c ON o.customer_id = c.id
                LEFT JOIN users u ON o.user_id = u.id
                ORDER BY o.order_date DESC
            """
            cursor.execute(query)
            return cursor.fetchall()
        finally:
            if conn.is_connected(): cursor.close(); conn.close()