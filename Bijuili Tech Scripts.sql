CREATE TABLE Roles (
    role_id INT AUTO_INCREMENT PRIMARY KEY,
    role_name VARCHAR(50) NOT NULL
);

CREATE TABLE Employees (
    employee_id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role_id INT,
    FOREIGN KEY (role_id) REFERENCES Roles(role_id)
);


CREATE TABLE Categories (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL
);

CREATE TABLE Products (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    product_name VARCHAR(100) NOT NULL,
    category_id INT,
    quantity_in_stock INT DEFAULT 0,
    reorder_level INT DEFAULT 10,
    price DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (category_id) REFERENCES Categories(category_id)
);

CREATE TABLE StockTransactions (
    transaction_id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    employee_id INT,
    transaction_type ENUM('IN', 'OUT') NOT NULL,
    quantity INT NOT NULL,
    transaction_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES Products(product_id),
    FOREIGN KEY (employee_id) REFERENCES Employees(employee_id)
);

CREATE TABLE StockAlerts (
    alert_id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    alert_message VARCHAR(255),
    alert_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    status ENUM('Active','Resolved') DEFAULT 'Active',
    FOREIGN KEY (product_id) REFERENCES Products(product_id)
);


CREATE TABLE Customers (
    customer_id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    contact_number VARCHAR(20),
    email VARCHAR(100),
    registration_date DATE DEFAULT (CURRENT_DATE),
    registered_by INT,
    FOREIGN KEY (registered_by) REFERENCES Employees(employee_id)
);

CREATE TABLE LoyaltyPoints (
    loyalty_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    total_points INT DEFAULT 0,
    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES Customers(customer_id)
);


CREATE TABLE Sales (
    sale_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT,
    cashier_id INT,
    sale_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    total_amount DECIMAL(10,2) DEFAULT 0.00,
    FOREIGN KEY (customer_id) REFERENCES Customers(customer_id),
    FOREIGN KEY (cashier_id) REFERENCES Employees(employee_id)
);

CREATE TABLE SaleDetails (
    detail_id INT AUTO_INCREMENT PRIMARY KEY,
    sale_id INT,
    product_id INT,
    quantity INT,
    price DECIMAL(10,2),
    FOREIGN KEY (sale_id) REFERENCES Sales(sale_id),
    FOREIGN KEY (product_id) REFERENCES Products(product_id)
);


INSERT INTO Roles (role_name) VALUES ('Manager'), ('Staff'), ('Cashier');

INSERT INTO Employees (full_name, username, password_hash, role_id)
VALUES ('John Doe', 'manager1', 'hashed_pwd', 1),
       ('Jane Smith', 'staff1', 'hashed_pwd', 2),
       ('Tom Lee', 'cashier1', 'hashed_pwd', 3);

INSERT INTO Categories (category_name)
VALUES ('Beverages'), ('Food Items'), ('Cleaning Supplies');

INSERT INTO Products (product_name, category_id, quantity_in_stock, reorder_level, price)
VALUES ('Cola Drink', 1, 25, 10, 3.50),
       ('BBQ Sauce', 2, 8, 10, 6.90),
       ('Dish Soap', 3, 12, 5, 4.20);


INSERT INTO StockTransactions (product_id, employee_id, transaction_type, quantity)
VALUES (2, 2, 'OUT', 3);


INSERT INTO StockAlerts (product_id, alert_message)
VALUES (2, 'Low stock alert: BBQ Sauce below reorder level');


INSERT INTO Customers (full_name, contact_number, email, registered_by)
VALUES ('Alice Brown', '0212345678', 'alice@example.com', 3);

INSERT INTO LoyaltyPoints (customer_id, total_points)
VALUES (1, 150);