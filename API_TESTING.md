# Event Management System API Testing Guide

This file contains sample API requests you can use to test the Event Management System backend.

## Base URL
```
http://localhost:8000/api/
```

## Authentication

### 1. Register a new user
```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpassword123",
    "password_confirm": "testpassword123",
    "first_name": "Test",
    "last_name": "User",
    "role": "user",
    "phone_number": "+91-9876543210"
  }'
```

### 2. Login
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "testpassword123"
  }'
```

### 3. Login with sample users
```bash
# Admin user
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# Vendor user
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "delicious_catering", "password": "vendor123"}'

# Customer user
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "alice_customer", "password": "user123"}'
```

## Products

### 4. Get all products
```bash
curl -X GET http://localhost:8000/api/products/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 5. Get products by category
```bash
curl -X GET "http://localhost:8000/api/products/?category=catering" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 6. Search products
```bash
curl -X GET "http://localhost:8000/api/products/?search=wedding" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 7. Create a new product (Vendor only)
```bash
curl -X POST http://localhost:8000/api/products/ \
  -H "Authorization: Bearer YOUR_VENDOR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Custom Wedding Cake",
    "description": "Beautiful custom wedding cake for your special day",
    "price": "5000.00",
    "category": "catering",
    "stock_quantity": 10
  }'
```

## Shopping Cart

### 8. Add item to cart
```bash
curl -X POST http://localhost:8000/api/products/cart/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": 1,
    "quantity": 2
  }'
```

### 9. Get cart items
```bash
curl -X GET http://localhost:8000/api/products/cart/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 10. Get cart summary
```bash
curl -X GET http://localhost:8000/api/products/cart/summary/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Orders

### 11. Create an order from cart
```bash
curl -X POST http://localhost:8000/api/orders/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "use_cart": true,
    "shipping_address": "123 Main Street, Apt 4B",
    "shipping_city": "Mumbai",
    "shipping_state": "Maharashtra",
    "shipping_postal_code": "400001",
    "contact_phone": "+91-9876543210",
    "contact_email": "test@example.com",
    "payment_method": "cod",
    "notes": "Please handle with care"
  }'
```

### 12. Create an order with specific items
```bash
curl -X POST http://localhost:8000/api/orders/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "items": [
      {"product_id": 1, "quantity": 1},
      {"product_id": 2, "quantity": 2}
    ],
    "shipping_address": "456 Oak Avenue",
    "shipping_city": "Delhi",
    "shipping_state": "Delhi",
    "shipping_postal_code": "110001",
    "contact_phone": "+91-9876543210",
    "contact_email": "test@example.com",
    "payment_method": "online"
  }'
```

### 13. Get user orders
```bash
curl -X GET http://localhost:8000/api/orders/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 14. Get order details
```bash
curl -X GET http://localhost:8000/api/orders/1/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 15. Update order status (Vendor/Admin only)
```bash
curl -X PUT http://localhost:8000/api/orders/1/status/ \
  -H "Authorization: Bearer YOUR_VENDOR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "shipped",
    "notes": "Order shipped via express delivery"
  }'
```

## Vendor Endpoints

### 16. Get vendor products
```bash
curl -X GET http://localhost:8000/api/products/vendor/products/ \
  -H "Authorization: Bearer YOUR_VENDOR_ACCESS_TOKEN"
```

### 17. Get vendor orders
```bash
curl -X GET http://localhost:8000/api/orders/vendor/orders/ \
  -H "Authorization: Bearer YOUR_VENDOR_ACCESS_TOKEN"
```

### 18. Get vendor stats
```bash
curl -X GET http://localhost:8000/api/products/vendor/stats/ \
  -H "Authorization: Bearer YOUR_VENDOR_ACCESS_TOKEN"
```

## Admin Reports

### 19. Get sales report
```bash
curl -X GET "http://localhost:8000/api/reports/sales/?start_date=2024-01-01&end_date=2024-12-31" \
  -H "Authorization: Bearer YOUR_ADMIN_ACCESS_TOKEN"
```

### 20. Get inventory report
```bash
curl -X GET http://localhost:8000/api/reports/inventory/ \
  -H "Authorization: Bearer YOUR_ADMIN_ACCESS_TOKEN"
```

### 21. Get user activity report
```bash
curl -X GET http://localhost:8000/api/reports/user-activity/ \
  -H "Authorization: Bearer YOUR_ADMIN_ACCESS_TOKEN"
```

### 22. Export report as CSV
```bash
curl -X GET "http://localhost:8000/api/reports/export/csv/?type=sales" \
  -H "Authorization: Bearer YOUR_ADMIN_ACCESS_TOKEN" \
  -o sales_report.csv
```

## Utility Endpoints

### 23. Get vendor categories
```bash
curl -X GET http://localhost:8000/api/auth/categories/
```

### 24. Get vendors by category
```bash
curl -X GET "http://localhost:8000/api/auth/vendors/?category=catering" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 25. Get featured products
```bash
curl -X GET http://localhost:8000/api/products/featured/
```

## Notes

1. Replace `YOUR_ACCESS_TOKEN`, `YOUR_VENDOR_ACCESS_TOKEN`, and `YOUR_ADMIN_ACCESS_TOKEN` with actual JWT tokens received from login.

2. The sample data includes:
   - Admin: `admin` / `admin123`
   - Vendors: `delicious_catering`, `blooming_flowers`, `elegant_decor`, `bright_lights` / `vendor123`
   - Customers: `alice_customer`, `bob_customer` / `user123`

3. All authenticated endpoints require the `Authorization: Bearer {token}` header.

4. Tokens expire after 60 minutes by default. Use the refresh token to get a new access token:
```bash
curl -X POST http://localhost:8000/api/auth/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh": "YOUR_REFRESH_TOKEN"}'
```

5. For file uploads (like product images), use `multipart/form-data` instead of JSON:
```bash
curl -X POST http://localhost:8000/api/products/ \
  -H "Authorization: Bearer YOUR_VENDOR_ACCESS_TOKEN" \
  -F "name=Test Product" \
  -F "description=Test description" \
  -F "price=1000.00" \
  -F "category=catering" \
  -F "stock_quantity=5" \
  -F "image=@/path/to/image.jpg"
```
