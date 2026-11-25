USE grocery_db;

-- 1. JOIN: products with category and supplier
SELECT p.product_name,c.category_name,s.supplier_name,p.unit_price,p.quantity
FROM products p JOIN categories c ON p.category_id=c.category_id
LEFT JOIN suppliers s ON p.supplier_id=s.supplier_id;

-- 2. Aggregate: inventory value by category
SELECT c.category_name, SUM(p.quantity*p.unit_price) AS inventory_value
FROM products p JOIN categories c USING(category_id)
WHERE p.is_active=1 GROUP BY c.category_id,c.category_name;

-- 3. Aggregate: best-selling products
SELECT p.product_name,SUM(si.quantity) AS units_sold
FROM sale_items si JOIN products p USING(product_id)
GROUP BY p.product_id,p.product_name ORDER BY units_sold DESC;

-- 4. Views
SELECT * FROM v_low_stock;
SELECT * FROM v_daily_sales;

-- 5. Transaction example: execute as one transaction in MySQL Workbench
START TRANSACTION;
SELECT quantity FROM products WHERE product_id=1 FOR UPDATE;
UPDATE products SET quantity=quantity-2 WHERE product_id=1 AND quantity>=2;
-- Check ROW_COUNT() is 1 before committing.
COMMIT;
-- Use ROLLBACK instead of COMMIT if validation fails.
