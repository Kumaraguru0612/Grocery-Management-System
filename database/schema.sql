CREATE DATABASE IF NOT EXISTS grocery_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE grocery_db;

CREATE TABLE IF NOT EXISTS categories (
  category_id INT AUTO_INCREMENT PRIMARY KEY,
  category_name VARCHAR(100) NOT NULL UNIQUE,
  description VARCHAR(255)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS suppliers (
  supplier_id INT AUTO_INCREMENT PRIMARY KEY,
  supplier_name VARCHAR(150) NOT NULL,
  phone VARCHAR(20),
  email VARCHAR(120),
  address VARCHAR(255)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS products (
  product_id INT AUTO_INCREMENT PRIMARY KEY,
  product_name VARCHAR(150) NOT NULL,
  category_id INT NOT NULL,
  supplier_id INT NULL,
  unit_price DECIMAL(10,2) NOT NULL CHECK (unit_price >= 0),
  quantity INT NOT NULL DEFAULT 0 CHECK (quantity >= 0),
  reorder_level INT NOT NULL DEFAULT 10 CHECK (reorder_level >= 0),
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_product_category FOREIGN KEY(category_id) REFERENCES categories(category_id),
  CONSTRAINT fk_product_supplier FOREIGN KEY(supplier_id) REFERENCES suppliers(supplier_id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS purchases (
  purchase_id INT AUTO_INCREMENT PRIMARY KEY,
  product_id INT NOT NULL,
  quantity INT NOT NULL CHECK(quantity > 0),
  unit_cost DECIMAL(10,2) NOT NULL CHECK(unit_cost >= 0),
  total_cost DECIMAL(12,2) NOT NULL,
  purchase_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY(product_id) REFERENCES products(product_id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS sales (
  sale_id INT AUTO_INCREMENT PRIMARY KEY,
  sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  total_amount DECIMAL(12,2) NOT NULL,
  payment_method ENUM('Cash','Card','UPI') NOT NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS sale_items (
  sale_item_id INT AUTO_INCREMENT PRIMARY KEY,
  sale_id INT NOT NULL,
  product_id INT NOT NULL,
  quantity INT NOT NULL CHECK(quantity > 0),
  unit_price DECIMAL(10,2) NOT NULL,
  line_total DECIMAL(12,2) NOT NULL,
  FOREIGN KEY(sale_id) REFERENCES sales(sale_id),
  FOREIGN KEY(product_id) REFERENCES products(product_id)
) ENGINE=InnoDB;

CREATE INDEX idx_products_name ON products(product_name);
CREATE INDEX idx_sales_date ON sales(sale_date);

CREATE OR REPLACE VIEW v_low_stock AS
SELECT p.product_id,p.product_name,c.category_name,p.quantity,p.reorder_level
FROM products p JOIN categories c ON p.category_id=c.category_id
WHERE p.is_active=1 AND p.quantity<=p.reorder_level;

CREATE OR REPLACE VIEW v_daily_sales AS
SELECT DATE(sale_date) AS sale_day, COUNT(*) AS bill_count, SUM(total_amount) AS revenue
FROM sales GROUP BY DATE(sale_date);
