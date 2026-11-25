USE grocery_db;
INSERT IGNORE INTO categories(category_name,description) VALUES
('Fruits','Fresh seasonal fruits'),('Vegetables','Fresh vegetables'),
('Dairy','Milk and dairy products'),('Staples','Rice, pulses and grains'),
('Beverages','Drinks and beverages'),('Snacks','Packaged snacks');

INSERT INTO suppliers(supplier_name,phone,email,address)
SELECT 'Green Farm Traders','9876543210','greenfarm@example.com','Namakkal'
WHERE NOT EXISTS (SELECT 1 FROM suppliers WHERE supplier_name='Green Farm Traders');
INSERT INTO suppliers(supplier_name,phone,email,address)
SELECT 'Daily Needs Wholesale','9876501234','dailyneeds@example.com','Salem'
WHERE NOT EXISTS (SELECT 1 FROM suppliers WHERE supplier_name='Daily Needs Wholesale');

INSERT INTO products(product_name,category_id,supplier_id,unit_price,quantity,reorder_level)
SELECT 'Apple',category_id,(SELECT supplier_id FROM suppliers WHERE supplier_name='Green Farm Traders' LIMIT 1),160,25,8
FROM categories WHERE category_name='Fruits'
AND NOT EXISTS(SELECT 1 FROM products WHERE product_name='Apple');
INSERT INTO products(product_name,category_id,supplier_id,unit_price,quantity,reorder_level)
SELECT 'Banana',category_id,(SELECT supplier_id FROM suppliers WHERE supplier_name='Green Farm Traders' LIMIT 1),60,7,10
FROM categories WHERE category_name='Fruits'
AND NOT EXISTS(SELECT 1 FROM products WHERE product_name='Banana');
INSERT INTO products(product_name,category_id,supplier_id,unit_price,quantity,reorder_level)
SELECT 'Milk 1L',category_id,(SELECT supplier_id FROM suppliers WHERE supplier_name='Daily Needs Wholesale' LIMIT 1), 55,20,5
FROM categories WHERE category_name='Dairy'
AND NOT EXISTS(SELECT 1 FROM products WHERE product_name='Milk 1L');
