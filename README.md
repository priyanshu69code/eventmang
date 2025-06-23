# Event Management System Backend

A Django REST API backend for an Event Management System with JWT authentication and role-based access control.

## Features

- JWT Authentication with role-based access (Admin, Vendor, User)
- User Management with memberships
- Vendor Product Management
- Shopping Cart functionality
- Order Management with status tracking
- Category-based vendor browsing
- Admin reports and transaction logs

## Tech Stack

- Django 5.0.7
- Django REST Framework 3.15.2
- JWT Authentication (djangorestframework-simplejwt)
- SQLite Database
- Python 3.8+

## Setup

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

4. Create superuser:
```bash
python manage.py createsuperuser
```

5. Run development server:
```bash
python manage.py runserver
```

## API Endpoints

### Authentication
- `POST /api/auth/register/` - User/Vendor registration
- `POST /api/auth/login/` - Login (returns JWT tokens)
- `POST /api/auth/logout/` - Logout
- `POST /api/auth/token/refresh/` - Refresh token

### Users & Vendors
- `GET/POST /api/users/` - List/Create users (Admin only)
- `GET/PUT/DELETE /api/users/{id}/` - User details (Admin only)
- `GET/POST /api/vendors/` - List/Create vendors (Admin only)
- `GET/PUT /api/profile/` - User profile

### Products
- `GET/POST /api/products/` - Product list/create
- `GET/PUT/DELETE /api/products/{id}/` - Product details
- `GET /api/vendor/products/` - Vendor's products

### Categories & Browsing
- `GET /api/categories/` - List categories
- `GET /api/vendors/?category={name}` - Vendors by category
- `GET /api/vendor/{id}/products/` - Vendor's products

### Cart & Orders
- `GET/POST /api/cart/` - Cart items
- `PUT/DELETE /api/cart/{id}/` - Update/Delete cart item
- `POST /api/orders/` - Place order
- `GET /api/orders/{id}/status/` - Order status
- `GET /api/vendor/orders/` - Vendor orders
- `PUT /api/orders/{id}/status/` - Update order status (Vendor)

### Memberships & Reports
- `GET/POST /api/memberships/` - Memberships (Admin)
- `GET /api/reports/transactions/` - Transaction reports (Admin)
- `GET /api/reports/activity/` - Activity reports (Admin)

## User Roles

- **Admin**: Full system access
- **Vendor**: Manage products and orders
- **User**: Browse, cart, and order functionality
