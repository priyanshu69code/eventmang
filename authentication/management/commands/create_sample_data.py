from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from authentication.models import VendorProfile, Membership
from products.models import Product, Category
from orders.models import Order, OrderItem
from decimal import Decimal
from datetime import date, timedelta
import random

User = get_user_model()


class Command(BaseCommand):
    help = 'Create sample data for testing the Event Management System'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before creating new data',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing data...')
            Order.objects.all().delete()
            Product.objects.all().delete()
            VendorProfile.objects.all().delete()
            User.objects.filter(is_superuser=False).delete()
            Category.objects.all().delete()

        self.stdout.write('Creating sample data...')

        # Create admin user
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@eventmanagement.com',
                'first_name': 'System',
                'last_name': 'Administrator',
                'role': 'admin',
                'is_staff': True,
                'is_superuser': True,
                'is_verified': True,
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write(f'Created admin user: {admin_user.username}')

        # Create categories
        categories = [
            {'name': 'Catering', 'description': 'Food and beverage services'},
            {'name': 'Florist', 'description': 'Flower arrangements and decorations'},
            {'name': 'Decoration', 'description': 'Event decoration services'},
            {'name': 'Lighting', 'description': 'Professional lighting solutions'},
        ]

        for cat_data in categories:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults=cat_data
            )
            if created:
                self.stdout.write(f'Created category: {category.name}')

        # Create vendor users and profiles
        vendors_data = [
            {
                'username': 'delicious_catering',
                'email': 'contact@deliciouscatering.com',
                'first_name': 'John',
                'last_name': 'Smith',
                'role': 'vendor',
                'shop_name': 'Delicious Catering Services',
                'category': 'catering',
                'description': 'Premium catering services for all events',
            },
            {
                'username': 'blooming_flowers',
                'email': 'info@bloomingflowers.com',
                'first_name': 'Sarah',
                'last_name': 'Johnson',
                'role': 'vendor',
                'shop_name': 'Blooming Flowers Studio',
                'category': 'florist',
                'description': 'Beautiful flower arrangements for special occasions',
            },
            {
                'username': 'elegant_decor',
                'email': 'hello@elegantdecor.com',
                'first_name': 'Michael',
                'last_name': 'Brown',
                'role': 'vendor',
                'shop_name': 'Elegant Event Decorations',
                'category': 'decoration',
                'description': 'Stunning decorations to make your event memorable',
            },
            {
                'username': 'bright_lights',
                'email': 'support@brightlights.com',
                'first_name': 'Emily',
                'last_name': 'Davis',
                'role': 'vendor',
                'shop_name': 'Bright Lights Solutions',
                'category': 'lighting',
                'description': 'Professional lighting for events of all sizes',
            },
        ]

        vendors = []
        for vendor_data in vendors_data:
            profile_data = {
                'shop_name': vendor_data.pop('shop_name'),
                'category': vendor_data.pop('category'),
                'description': vendor_data.pop('description'),
                'is_verified': True,
            }

            user, created = User.objects.get_or_create(
                username=vendor_data['username'],
                defaults={**vendor_data, 'is_verified': True}
            )
            if created:
                user.set_password('vendor123')
                user.save()
                vendors.append(user)

                # Create vendor profile
                VendorProfile.objects.create(user=user, **profile_data)

                # Create membership
                Membership.objects.create(
                    user=user,
                    duration='1_year',
                    start_date=date.today(),
                    amount_paid=Decimal('5000.00')
                )

                self.stdout.write(f'Created vendor: {user.username}')

        # Create regular users
        users_data = [
            {
                'username': 'alice_customer',
                'email': 'alice@example.com',
                'first_name': 'Alice',
                'last_name': 'Wilson',
                'role': 'user',
            },
            {
                'username': 'bob_customer',
                'email': 'bob@example.com',
                'first_name': 'Bob',
                'last_name': 'Taylor',
                'role': 'user',
            },
        ]

        customers = []
        for user_data in users_data:
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults={**user_data, 'is_verified': True}
            )
            if created:
                user.set_password('user123')
                user.save()
                customers.append(user)
                self.stdout.write(f'Created customer: {user.username}')

        # Create products for each vendor
        products_data = {
            'catering': [
                {'name': 'Wedding Buffet Package', 'price': '15000.00', 'stock': 20},
                {'name': 'Corporate Lunch Catering', 'price': '8000.00', 'stock': 50},
                {'name': 'Birthday Party Snacks', 'price': '3500.00', 'stock': 30},
                {'name': 'Anniversary Dinner Set', 'price': '12000.00', 'stock': 15},
            ],
            'florist': [
                {'name': 'Bridal Bouquet - Roses', 'price': '2500.00', 'stock': 25},
                {'name': 'Table Centerpieces (Set of 10)', 'price': '4000.00', 'stock': 20},
                {'name': 'Flower Arch Decoration', 'price': '8500.00', 'stock': 10},
                {'name': 'Corsage and Boutonniere Set', 'price': '1200.00', 'stock': 40},
            ],
            'decoration': [
                {'name': 'Balloon Decoration Package', 'price': '3000.00', 'stock': 30},
                {'name': 'Stage Backdrop Setup', 'price': '12000.00', 'stock': 8},
                {'name': 'Table Linens and Chair Covers', 'price': '5500.00', 'stock': 25},
                {'name': 'Photo Booth Props Set', 'price': '2000.00', 'stock': 15},
            ],
            'lighting': [
                {'name': 'LED Dance Floor Lighting', 'price': '8000.00', 'stock': 12},
                {'name': 'Ambient String Lights', 'price': '3500.00', 'stock': 35},
                {'name': 'Spotlight Package', 'price': '6500.00', 'stock': 18},
                {'name': 'Disco Ball and Effects', 'price': '4500.00', 'stock': 22},
            ],
        }

        # Get vendor users for each category
        catering_vendor = User.objects.get(username='delicious_catering')
        florist_vendor = User.objects.get(username='blooming_flowers')
        decoration_vendor = User.objects.get(username='elegant_decor')
        lighting_vendor = User.objects.get(username='bright_lights')

        vendor_mapping = {
            'catering': catering_vendor,
            'florist': florist_vendor,
            'decoration': decoration_vendor,
            'lighting': lighting_vendor,
        }

        for category, products in products_data.items():
            vendor = vendor_mapping[category]
            for product_data in products:
                product, created = Product.objects.get_or_create(
                    vendor=vendor,
                    name=product_data['name'],
                    defaults={
                        'description': f'High-quality {product_data["name"].lower()} for your special events',
                        'price': Decimal(product_data['price']),
                        'category': category,
                        'stock_quantity': product_data['stock'],
                        'status': 'active',
                        'sku': f'{category.upper()[:3]}{random.randint(1000, 9999)}',
                    }
                )
                if created:
                    self.stdout.write(f'Created product: {product.name}')

        # Create some sample orders
        if customers:
            customer = customers[0]  # Alice

            # Create a sample order
            order = Order.objects.create(
                user=customer,
                status='confirmed',
                total_amount=Decimal('18500.00'),
                payment_method='online',
                payment_status='paid',
                shipping_address='123 Main St, Apartment 4B',
                shipping_city='Mumbai',
                shipping_state='Maharashtra',
                shipping_postal_code='400001',
                contact_phone='+91-9876543210',
                contact_email=customer.email,
                notes='Please handle with care. Event date: Next Saturday'
            )

            # Add order items
            wedding_buffet = Product.objects.get(name='Wedding Buffet Package')
            bridal_bouquet = Product.objects.get(name='Bridal Bouquet - Roses')
            string_lights = Product.objects.get(name='Ambient String Lights')

            OrderItem.objects.create(
                order=order,
                product=wedding_buffet,
                vendor=wedding_buffet.vendor,
                quantity=1,
                unit_price=wedding_buffet.price,
                total_price=wedding_buffet.price,
                status='confirmed'
            )

            OrderItem.objects.create(
                order=order,
                product=bridal_bouquet,
                vendor=bridal_bouquet.vendor,
                quantity=1,
                unit_price=bridal_bouquet.price,
                total_price=bridal_bouquet.price,
                status='confirmed'
            )

            self.stdout.write(f'Created sample order: {order.order_number}')

        self.stdout.write(
            self.style.SUCCESS('Successfully created sample data!')
        )
        self.stdout.write('')
        self.stdout.write('Sample login credentials:')
        self.stdout.write('Admin: admin / admin123')
        self.stdout.write('Vendors: delicious_catering, blooming_flowers, elegant_decor, bright_lights / vendor123')
        self.stdout.write('Customers: alice_customer, bob_customer / user123')
