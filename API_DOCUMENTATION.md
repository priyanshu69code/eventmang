# Event Management System API Documentation

## Table of Contents
1. [Overview](#overview)
2. [Authentication](#authentication)
3. [API Endpoints](#api-endpoints)
   - [Authentication Endpoints](#authentication-endpoints)
   - [User Management](#user-management)
   - [Product Management](#product-management)
   - [Cart Management](#cart-management)
   - [Order Management](#order-management)
   - [Vendor Management](#vendor-management)
   - [Reports & Analytics](#reports--analytics)
4. [Error Handling](#error-handling)
5. [Status Codes](#status-codes)

## Overview

The Event Management System API is a RESTful API built with Django REST Framework that provides comprehensive functionality for managing events, vendors, products, orders, and users.

**Base URL:** `http://localhost:8000/api/`

**Authentication:** JWT (JSON Web Tokens)

**Content Type:** `application/json`

**API Version:** 1.0.0

## Authentication

The API uses JWT (JSON Web Token) for authentication. Include the token in the Authorization header:

```
Authorization: Bearer <access_token>
```

**Token Expiry:**
- Access Token: 60 minutes
- Refresh Token: 7 days

---

## API Endpoints

### Authentication Endpoints

#### 1. User Registration
**Endpoint:** `POST /api/auth/register/`

**Description:** Register a new user (vendor or customer)

**Permissions:** Public (no authentication required)

**Request Body:**
```json
{
  "username": "string (required, unique)",
  "email": "string (required, valid email)",
  "password": "string (required, min 8 chars)",
  "password_confirm": "string (required, must match password)",
  "first_name": "string (optional)",
  "last_name": "string (optional)",
  "role": "string (required, choices: 'vendor', 'user')",
  "phone_number": "string (optional, max 15 chars)",
  "address": "string (optional)",
  "date_of_birth": "date (optional, format: YYYY-MM-DD)",
  "vendor_profile": {
    "shop_name": "string (required if role=vendor)",
    "category": "string (required if role=vendor, choices: catering, florist, decoration, lighting)",
    "description": "string (optional)"
  }
}
```

**Response (201 Created):**
```json
{
  "message": "User registered successfully",
  "tokens": {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
  },
  "user": {
    "id": 1,
    "username": "john_vendor",
    "email": "john@example.com",
    "role": "vendor",
    "vendor_profile": {
      "shop_name": "John's Catering",
      "category": "catering"
    }
  }
}
```

**Validation Errors (400 Bad Request):**
- Username already exists
- Email already exists
- Passwords don't match
- Invalid role (only 'vendor' or 'user' allowed)
- Missing required fields

---

#### 2. User Login
**Endpoint:** `POST /api/auth/login/`

**Description:** Authenticate user and receive JWT tokens

**Permissions:** Public

**Request Body:**
```json
{
  "username": "string (required)",
  "password": "string (required)"
}
```

**Response (200 OK):**
```json
{
  "message": "Login successful",
  "tokens": {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
  },
  "user": {
    "id": 1,
    "username": "john_vendor",
    "email": "john@example.com",
    "role": "vendor"
  }
}
```

**Errors:**
- `400`: Invalid credentials
- `400`: User account is disabled

---

#### 3. User Logout
**Endpoint:** `POST /api/auth/logout/`

**Description:** Blacklist refresh token (logout)

**Permissions:** Authenticated

**Request Body:**
```json
{
  "refresh": "string (required, refresh token)"
}
```

**Response (200 OK):**
```json
{
  "message": "Logout successful"
}
```

---

#### 4. Refresh Token
**Endpoint:** `POST /api/auth/token/refresh/`

**Description:** Get new access token using refresh token

**Permissions:** Public

**Request Body:**
```json
{
  "refresh": "string (required, valid refresh token)"
}
```

**Response (200 OK):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

---

#### 5. User Profile
**Endpoint:** `GET|PUT /api/auth/profile/`

**Description:** Get or update current user's profile

**Permissions:** Authenticated

**GET Response (200 OK):**
```json
{
  "id": 1,
  "username": "john_vendor",
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "role": "vendor",
  "phone_number": "+91-9876543210",
  "address": "123 Main St",
  "is_verified": true,
  "date_joined": "2024-01-15T10:30:00Z",
  "vendor_profile": {
    "shop_name": "John's Catering",
    "category": "catering"
  }
}
```

**PUT Request Body:**
```json
{
  "first_name": "string (optional)",
  "last_name": "string (optional)",
  "email": "string (optional, valid email)",
  "phone_number": "string (optional)",
  "address": "string (optional)",
  "date_of_birth": "date (optional)"
}
```

---

#### 6. Change Password
**Endpoint:** `POST /api/auth/change-password/`

**Description:** Change user's password

**Permissions:** Authenticated

**Request Body:**
```json
{
  "old_password": "string (required)",
  "new_password": "string (required, min 8 chars)",
  "confirm_password": "string (required, must match new_password)"
}
```

**Response (200 OK):**
```json
{
  "message": "Password changed successfully"
}
```

---

### User Management

#### 7. List/Create Users (Admin Only)
**Endpoint:** `GET|POST /api/auth/users/`

**Description:** List all users or create new user

**Permissions:** Admin only

**Query Parameters (GET):**
- `role`: Filter by role (admin, vendor, user)

**GET Response (200 OK):**
```json
{
  "count": 25,
  "next": "http://localhost:8000/api/auth/users/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "username": "john_vendor",
      "email": "john@example.com",
      "role": "vendor",
      "is_verified": true,
      "date_joined": "2024-01-15T10:30:00Z"
    }
  ]
}
```

---

#### 8. User Details (Admin Only)
**Endpoint:** `GET|PUT|DELETE /api/auth/users/{id}/`

**Description:** Retrieve, update, or delete specific user

**Permissions:** Admin only

**GET Response (200 OK):**
```json
{
  "id": 1,
  "username": "john_vendor",
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "role": "vendor",
  "phone_number": "+91-9876543210",
  "is_verified": true,
  "date_joined": "2024-01-15T10:30:00Z",
  "vendor_profile": {
    "shop_name": "John's Catering",
    "category": "catering"
  }
}
```

---

### Product Management

#### 9. List/Create Products
**Endpoint:** `GET|POST /api/products/`

**Description:** List products or create new product (vendors only for POST)

**Permissions:** Authenticated

**Query Parameters (GET):**
- `category`: Filter by category (catering, florist, decoration, lighting)
- `vendor_id`: Filter by vendor ID
- `search`: Search in name, description, tags
- `min_price`: Minimum price filter
- `max_price`: Maximum price filter
- `featured`: Show only featured products (true/false)
- `ordering`: Sort by (price, -price, name, -name, created_at, -created_at)

**GET Response (200 OK):**
```json
{
  "count": 50,
  "next": "http://localhost:8000/api/products/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Wedding Buffet Package",
      "price": "15000.00",
      "category": "catering",
      "vendor": "John's Catering",
      "image": "http://localhost:8000/media/products/buffet.jpg",
      "stock_quantity": 20,
      "status": "active",
      "is_featured": true,
      "average_rating": 4.5,
      "total_reviews": 12,
      "is_available": true,
      "created_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

**POST Request Body (Vendor only):**
```json
{
  "name": "string (required, max 200 chars)",
  "description": "string (optional)",
  "price": "decimal (required, min 0.01)",
  "category": "string (required, choices: catering, florist, decoration, lighting)",
  "stock_quantity": "integer (required, min 0)",
  "sku": "string (optional, unique)",
  "image": "file upload (optional)",
  "weight": "decimal (optional)",
  "dimensions": "string (optional)",
  "tags": "string (optional)",
  "is_featured": "boolean (optional, default: false)"
}
```

---

#### 10. Product Details
**Endpoint:** `GET|PUT|DELETE /api/products/{id}/`

**Description:** Retrieve, update, or delete specific product

**Permissions:**
- GET: Authenticated
- PUT/DELETE: Product owner (vendor) or Admin

**GET Response (200 OK):**
```json
{
  "id": 1,
  "name": "Wedding Buffet Package",
  "description": "Premium catering service for weddings",
  "price": "15000.00",
  "category": "catering",
  "vendor": "John's Catering",
  "stock_quantity": 20,
  "status": "active",
  "sku": "CAT1001",
  "weight": "0.00",
  "dimensions": "",
  "tags": "wedding, catering, buffet",
  "is_featured": true,
  "is_available": true,
  "average_rating": 4.5,
  "total_reviews": 12,
  "images": [
    {
      "id": 1,
      "image": "http://localhost:8000/media/products/buffet1.jpg",
      "is_primary": true
    }
  ],
  "reviews": [
    {
      "id": 1,
      "user": "alice_customer",
      "rating": 5,
      "comment": "Excellent service!",
      "created_at": "2024-01-20T15:30:00Z"
    }
  ],
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-20T12:00:00Z"
}
```

---

#### 11. Vendor Products
**Endpoint:** `GET /api/products/vendor/products/`

**Description:** Get current vendor's products

**Permissions:** Vendor only

**Query Parameters:**
- `status`: Filter by status (active, pending_approval, out_of_stock, inactive)

**Response (200 OK):**
```json
{
  "count": 15,
  "results": [
    {
      "id": 1,
      "name": "Wedding Buffet Package",
      "price": "15000.00",
      "category": "catering",
      "stock_quantity": 20,
      "status": "active",
      "is_featured": true,
      "created_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

---

#### 12. Vendor Statistics
**Endpoint:** `GET /api/products/vendor/stats/`

**Description:** Get vendor's product and sales statistics

**Permissions:** Vendor only

**Response (200 OK):**
```json
{
  "total_products": 15,
  "active_products": 12,
  "pending_products": 2,
  "out_of_stock_products": 1,
  "total_reviews": 45,
  "average_rating": 4.3
}
```

---

#### 13. Featured Products
**Endpoint:** `GET /api/products/featured/`

**Description:** Get featured products

**Permissions:** Public

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "name": "Wedding Buffet Package",
    "price": "15000.00",
    "category": "catering",
    "vendor": "John's Catering",
    "average_rating": 4.5,
    "total_reviews": 12,
    "is_available": true
  }
]
```

---

#### 14. Product Reviews
**Endpoint:** `GET|POST /api/products/{product_id}/reviews/`

**Description:** List or create product reviews

**Permissions:** Authenticated

**POST Request Body:**
```json
{
  "rating": "integer (required, 1-5)",
  "comment": "string (optional)"
}
```

**GET Response (200 OK):**
```json
[
  {
    "id": 1,
    "user": "alice_customer",
    "rating": 5,
    "comment": "Excellent service! Highly recommended.",
    "is_verified_purchase": true,
    "created_at": "2024-01-20T15:30:00Z"
  }
]
```

---

### Cart Management

#### 15. Cart Items
**Endpoint:** `GET|POST /api/products/cart/`

**Description:** Get cart items or add item to cart

**Permissions:** Authenticated

**POST Request Body:**
```json
{
  "product_id": "integer (required)",
  "quantity": "integer (required, min 1)"
}
```

**GET Response (200 OK):**
```json
[
  {
    "id": 1,
    "product": {
      "id": 1,
      "name": "Wedding Buffet Package",
      "price": "15000.00",
      "vendor": "John's Catering",
      "is_available": true
    },
    "quantity": 2,
    "total_price": "30000.00",
    "added_at": "2024-01-20T10:30:00Z"
  }
]
```

---

#### 16. Cart Item Details
**Endpoint:** `GET|PUT|DELETE /api/products/cart/{id}/`

**Description:** Update or remove cart item

**Permissions:** Authenticated (own cart items only)

**PUT Request Body:**
```json
{
  "quantity": "integer (required, min 1)"
}
```

---

#### 17. Cart Summary
**Endpoint:** `GET /api/products/cart/summary/`

**Description:** Get cart summary with totals

**Permissions:** Authenticated

**Response (200 OK):**
```json
{
  "total_items": 5,
  "total_price": "45000.00",
  "items_count": 3
}
```

---

#### 18. Clear Cart
**Endpoint:** `DELETE /api/products/cart/clear/`

**Description:** Remove all items from cart

**Permissions:** Authenticated

**Response (200 OK):**
```json
{
  "message": "Cleared 3 items from cart"
}
```

---

### Order Management

#### 19. List/Create Orders
**Endpoint:** `GET|POST /api/orders/`

**Description:** List user's orders or create new order

**Permissions:** Authenticated

**Query Parameters (GET):**
- `status`: Filter by order status

**POST Request Body:**
```json
{
  "shipping_address": "string (required)",
  "shipping_city": "string (required)",
  "shipping_state": "string (required)",
  "shipping_postal_code": "string (required)",
  "shipping_country": "string (optional, default: India)",
  "billing_address": "string (optional)",
  "billing_city": "string (optional)",
  "billing_state": "string (optional)",
  "billing_postal_code": "string (optional)",
  "billing_country": "string (optional)",
  "contact_phone": "string (required)",
  "contact_email": "string (required)",
  "payment_method": "string (required, choices: cod, online, card, wallet)",
  "notes": "string (optional)",
  "use_cart": "boolean (optional, default: false)",
  "items": [
    {
      "product_id": "integer (required if not use_cart)",
      "quantity": "integer (required if not use_cart)"
    }
  ]
}
```

**GET Response (200 OK):**
```json
{
  "count": 10,
  "results": [
    {
      "id": 1,
      "order_number": "ORD12345678",
      "status": "confirmed",
      "total_amount": "30000.00",
      "payment_method": "online",
      "payment_status": "paid",
      "total_items": 3,
      "created_at": "2024-01-20T10:30:00Z",
      "estimated_delivery_date": "2024-01-25"
    }
  ]
}
```

---

#### 20. Order Details
**Endpoint:** `GET /api/orders/{id}/`

**Description:** Get detailed order information

**Permissions:** Authenticated (own orders), Admin (all orders)

**Response (200 OK):**
```json
{
  "id": 1,
  "order_number": "ORD12345678",
  "user": "alice_customer",
  "status": "confirmed",
  "total_amount": "30000.00",
  "payment_method": "online",
  "payment_status": "paid",
  "shipping_address": "123 Main St, Apt 4B",
  "shipping_city": "Mumbai",
  "shipping_state": "Maharashtra",
  "shipping_postal_code": "400001",
  "contact_phone": "+91-9876543210",
  "contact_email": "alice@example.com",
  "notes": "Please handle with care",
  "total_items": 3,
  "items": [
    {
      "id": 1,
      "product": {
        "id": 1,
        "name": "Wedding Buffet Package",
        "vendor": "John's Catering"
      },
      "quantity": 1,
      "unit_price": "15000.00",
      "total_price": "15000.00",
      "status": "confirmed"
    }
  ],
  "status_history": [
    {
      "status": "pending",
      "notes": "Order created",
      "changed_by": "alice_customer",
      "created_at": "2024-01-20T10:30:00Z"
    }
  ],
  "created_at": "2024-01-20T10:30:00Z",
  "confirmed_at": "2024-01-20T11:00:00Z"
}
```

---

#### 21. Update Order Status
**Endpoint:** `PUT /api/orders/{id}/status/`

**Description:** Update order status (Vendor/Admin only)

**Permissions:** Vendor (own orders), Admin (all orders)

**Request Body:**
```json
{
  "status": "string (required, choices: pending, confirmed, processing, shipped, delivered, cancelled, refunded)",
  "notes": "string (optional)"
}
```

**Response (200 OK):**
```json
{
  "message": "Order status updated successfully",
  "order": {
    "id": 1,
    "order_number": "ORD12345678",
    "status": "shipped",
    "shipped_at": "2024-01-22T14:30:00Z"
  }
}
```

---

#### 22. Cancel Order
**Endpoint:** `POST /api/orders/{id}/cancel/`

**Description:** Cancel an order

**Permissions:** Authenticated (own orders), Admin (all orders)

**Request Body:**
```json
{
  "reason": "string (optional)"
}
```

**Response (200 OK):**
```json
{
  "message": "Order cancelled successfully",
  "order": {
    "id": 1,
    "status": "cancelled"
  }
}
```

---

#### 23. Order Statistics
**Endpoint:** `GET /api/orders/stats/`

**Description:** Get order statistics for current user

**Permissions:** Authenticated

**Response (200 OK):**
```json
{
  "total_orders": 15,
  "pending_orders": 2,
  "confirmed_orders": 8,
  "shipped_orders": 3,
  "delivered_orders": 2,
  "cancelled_orders": 0,
  "total_revenue": "125000.00"
}
```

---

### Vendor Management

#### 24. Vendor Orders
**Endpoint:** `GET /api/orders/vendor/orders/`

**Description:** Get orders containing vendor's products

**Permissions:** Vendor only

**Query Parameters:**
- `status`: Filter by order status

**Response (200 OK):**
```json
{
  "count": 20,
  "results": [
    {
      "id": 1,
      "order_number": "ORD12345678",
      "user": "alice_customer",
      "status": "confirmed",
      "total_amount": "30000.00",
      "vendor_items": [
        {
          "id": 1,
          "product": {
            "name": "Wedding Buffet Package"
          },
          "quantity": 1,
          "unit_price": "15000.00",
          "status": "confirmed"
        }
      ],
      "created_at": "2024-01-20T10:30:00Z"
    }
  ]
}
```

---

#### 25. Vendor Order Details
**Endpoint:** `GET /api/orders/vendor/orders/{id}/`

**Description:** Get detailed vendor order information

**Permissions:** Vendor only

---

#### 26. Update Order Item Status
**Endpoint:** `POST /api/orders/vendor/{order_id}/items/{item_id}/status/`

**Description:** Update status of specific order item

**Permissions:** Vendor only (own items)

**Request Body:**
```json
{
  "status": "string (required, choices: pending, confirmed, ready_for_shipping, shipped, delivered, cancelled)"
}
```

---

#### 27. Vendor Notifications
**Endpoint:** `GET /api/orders/vendor/notifications/`

**Description:** Get vendor notifications

**Permissions:** Vendor only

**Query Parameters:**
- `mark_read`: Mark notifications as read (true/false)

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "message": "New order received: ORD12345678",
    "order": {
      "id": 1,
      "order_number": "ORD12345678"
    },
    "is_read": false,
    "created_at": "2024-01-20T10:30:00Z"
  }
]
```

---

#### 28. List Vendors
**Endpoint:** `GET /api/auth/vendors/`

**Description:** List all verified vendors

**Permissions:** Authenticated

**Query Parameters:**
- `category`: Filter by category

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "user": "john_vendor",
    "shop_name": "John's Catering",
    "category": "catering",
    "description": "Premium catering services",
    "rating": 4.5,
    "total_reviews": 25,
    "is_verified": true
  }
]
```

---

#### 29. Vendor Products by ID
**Endpoint:** `GET /api/products/vendor/{vendor_id}/products/`

**Description:** Get products by specific vendor

**Permissions:** Authenticated

**Query Parameters:**
- `category`: Filter by category

---

### Reports & Analytics

#### 30. Sales Report (Admin Only)
**Endpoint:** `GET /api/reports/sales/`

**Description:** Get comprehensive sales report

**Permissions:** Admin only

**Query Parameters:**
- `start_date`: Start date (YYYY-MM-DD)
- `end_date`: End date (YYYY-MM-DD)
- `category`: Filter by product category
- `vendor_id`: Filter by vendor

**Response (200 OK):**
```json
{
  "period": {
    "start_date": "2024-01-01",
    "end_date": "2024-01-31"
  },
  "summary": {
    "total_sales": 500000.00,
    "total_orders": 150,
    "average_order_value": 3333.33
  },
  "sales_by_category": [
    {
      "product__category": "catering",
      "total_sales": 300000.00,
      "total_quantity": 80
    }
  ],
  "sales_by_vendor": [
    {
      "vendor__username": "john_vendor",
      "vendor__vendor_profile__shop_name": "John's Catering",
      "total_sales": 250000.00,
      "total_orders": 75
    }
  ],
  "daily_sales": [
    {
      "date": "2024-01-01",
      "sales": 15000.00
    }
  ]
}
```

---

#### 31. Inventory Report (Admin Only)
**Endpoint:** `GET /api/reports/inventory/`

**Description:** Get inventory and stock report

**Permissions:** Admin only

**Query Parameters:**
- `category`: Filter by category
- `vendor_id`: Filter by vendor
- `status`: Filter by product status

**Response (200 OK):**
```json
{
  "summary": {
    "total_products": 150,
    "total_stock_value": 2500000.00,
    "low_stock_products": 5,
    "out_of_stock_products": 2
  },
  "products_by_category": [
    {
      "category": "catering",
      "count": 50,
      "total_stock": 500,
      "total_value": 1000000.00
    }
  ],
  "low_stock_alert": [
    {
      "name": "Wedding Cake Special",
      "vendor__username": "john_vendor",
      "stock_quantity": 3,
      "category": "catering"
    }
  ]
}
```

---

#### 32. User Activity Report (Admin Only)
**Endpoint:** `GET /api/reports/user-activity/`

**Description:** Get user activity and registration report

**Permissions:** Admin only

**Query Parameters:**
- `start_date`: Start date (YYYY-MM-DD)
- `end_date`: End date (YYYY-MM-DD)

**Response (200 OK):**
```json
{
  "period": {
    "start_date": "2024-01-01",
    "end_date": "2024-01-31"
  },
  "summary": {
    "total_users": 250,
    "active_users": 180,
    "new_users": 25,
    "active_vendors": 15
  },
  "users_by_role": [
    {
      "role": "user",
      "count": 200
    },
    {
      "role": "vendor",
      "count": 45
    }
  ],
  "registration_trend": [
    {
      "date": "2024-01-01",
      "registrations": 3
    }
  ]
}
```

---

#### 33. Vendor Performance Report (Admin Only)
**Endpoint:** `GET /api/reports/vendor-performance/`

**Description:** Get vendor performance analytics

**Permissions:** Admin only

**Query Parameters:**
- `start_date`: Start date (YYYY-MM-DD)
- `end_date`: End date (YYYY-MM-DD)

**Response (200 OK):**
```json
{
  "period": {
    "start_date": "2024-01-01",
    "end_date": "2024-01-31"
  },
  "top_by_sales": [
    {
      "vendor_id": 1,
      "vendor_name": "john_vendor",
      "shop_name": "John's Catering",
      "category": "catering",
      "total_sales": 250000.00,
      "total_orders": 75,
      "average_rating": 4.5
    }
  ]
}
```

---

#### 34. Transaction Report (Admin Only)
**Endpoint:** `GET /api/reports/transactions/`

**Description:** Get transaction and payment report

**Permissions:** Admin only

**Query Parameters:**
- `start_date`: Start date (YYYY-MM-DD)
- `end_date`: End date (YYYY-MM-DD)

**Response (200 OK):**
```json
{
  "period": {
    "start_date": "2024-01-01",
    "end_date": "2024-01-31"
  },
  "summary": {
    "total_transactions": 200,
    "successful_transactions": 185,
    "failed_transactions": 15,
    "success_rate": 92.5,
    "total_amount": 750000.00
  },
  "transactions_by_method": [
    {
      "payment_method": "online",
      "count": 120,
      "total_amount": 500000.00
    }
  ]
}
```

---

#### 35. Export Report CSV (Admin Only)
**Endpoint:** `GET /api/reports/export/csv/`

**Description:** Export report data as CSV file

**Permissions:** Admin only

**Query Parameters:**
- `type`: Report type (sales, inventory) (required)
- `start_date`: Start date (for sales report)
- `end_date`: End date (for sales report)

**Response:** CSV file download

---

#### 36. Admin Order Analytics (Admin Only)
**Endpoint:** `GET /api/reports/admin/analytics/`

**Description:** Get comprehensive order analytics

**Permissions:** Admin only

**Query Parameters:**
- `days`: Number of days to analyze (default: 30)

---

### Utility Endpoints

#### 37. Categories List
**Endpoint:** `GET /api/auth/categories/`

**Description:** Get list of vendor categories

**Permissions:** Public

**Response (200 OK):**
```json
[
  {
    "value": "catering",
    "label": "Catering"
  },
  {
    "value": "florist",
    "label": "Florist"
  },
  {
    "value": "decoration",
    "label": "Decoration"
  },
  {
    "value": "lighting",
    "label": "Lighting"
  }
]
```

---

#### 38. Product Categories
**Endpoint:** `GET /api/products/categories/`

**Description:** Get list of product categories

**Permissions:** Public

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "name": "Catering",
    "description": "Food and beverage services",
    "is_active": true
  }
]
```

---

#### 39. Membership Management (Admin Only)
**Endpoint:** `GET|POST /api/auth/memberships/`

**Description:** List or create user memberships

**Permissions:** Admin only

**POST Request Body:**
```json
{
  "user_id": "integer (required)",
  "duration": "string (required, choices: 6_months, 1_year, 2_years)",
  "start_date": "date (required, format: YYYY-MM-DD)",
  "amount_paid": "decimal (required)"
}
```

---

#### 40. User Memberships
**Endpoint:** `GET /api/auth/my-memberships/`

**Description:** Get current user's memberships

**Permissions:** Authenticated

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "duration": "1_year",
    "start_date": "2024-01-01",
    "end_date": "2024-12-31",
    "is_active": true,
    "is_expired": false,
    "amount_paid": "5000.00"
  }
]
```

---

## Error Handling

### Common Error Responses

#### 400 Bad Request
```json
{
  "field_name": ["Error message for this field"],
  "non_field_errors": ["General error message"]
}
```

#### 401 Unauthorized
```json
{
  "detail": "Authentication credentials were not provided."
}
```

#### 403 Forbidden
```json
{
  "detail": "You do not have permission to perform this action."
}
```

#### 404 Not Found
```json
{
  "detail": "Not found."
}
```

#### 500 Internal Server Error
```json
{
  "detail": "A server error occurred."
}
```

### Validation Errors

**Field-specific errors:**
```json
{
  "username": ["This field is required."],
  "email": ["Enter a valid email address."],
  "password": ["This password is too short. It must contain at least 8 characters."]
}
```

**Authentication errors:**
```json
{
  "detail": "Invalid token.",
  "code": "token_not_valid"
}
```

---

## Status Codes

| Code | Description |
|------|-------------|
| 200 | OK - Request successful |
| 201 | Created - Resource created successfully |
| 204 | No Content - Request successful, no content returned |
| 400 | Bad Request - Invalid request data |
| 401 | Unauthorized - Authentication required |
| 403 | Forbidden - Permission denied |
| 404 | Not Found - Resource not found |
| 405 | Method Not Allowed - HTTP method not supported |
| 429 | Too Many Requests - Rate limit exceeded |
| 500 | Internal Server Error - Server error |

---

## Rate Limiting

The API implements rate limiting to prevent abuse:

- **Authenticated users**: 1000 requests per hour
- **Anonymous users**: 100 requests per hour
- **Admin users**: 10000 requests per hour

Rate limit headers are included in responses:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1640995200
```

---

## Sample Usage

### Complete Order Flow Example

```bash
# 1. Register as customer
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username": "customer1", "email": "customer@example.com", "password": "password123", "password_confirm": "password123", "role": "user"}'

# 2. Login
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "customer1", "password": "password123"}'

# 3. Browse products
curl -X GET http://localhost:8000/api/products/ \
  -H "Authorization: Bearer <access_token>"

# 4. Add to cart
curl -X POST http://localhost:8000/api/products/cart/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"product_id": 1, "quantity": 2}'

# 5. Create order from cart
curl -X POST http://localhost:8000/api/orders/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"use_cart": true, "shipping_address": "123 Main St", "shipping_city": "Mumbai", "shipping_state": "Maharashtra", "shipping_postal_code": "400001", "contact_phone": "+91-9876543210", "contact_email": "customer@example.com", "payment_method": "cod"}'

# 6. Check order status
curl -X GET http://localhost:8000/api/orders/1/ \
  -H "Authorization: Bearer <access_token>"
```

---

## Webhooks (Future Enhancement)

The API is designed to support webhooks for real-time notifications:

- Order status changes
- Payment confirmations
- Stock level alerts
- New vendor registrations

Webhook endpoints would follow the pattern: `POST /api/webhooks/{event_type}/`

---

## API Versioning

Current API version: **v1**

Future versions will be accessible via:
- Header: `Accept: application/vnd.eventmanagement.v2+json`
- URL: `/api/v2/`

---

## Support

For API support and questions:
- Email: kumarpriyanshu.py@gmail.com
- Documentation: [API Docs](http://localhost:8000/api/)
- Status Page: [API Status](http://status.eventmanagement.com)
