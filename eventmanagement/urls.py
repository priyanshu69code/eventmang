"""
URL configuration for eventmanagement project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request):
    """
    Event Management System API

    Welcome to the Event Management System API. This system provides endpoints for:
    - User authentication and management
    - Product catalog management
    - Shopping cart functionality
    - Order processing and tracking
    - Vendor management
    - Reports and analytics
    """
    return Response({
        'message': 'Welcome to Event Management System API',
        'version': '1.0.0',
        'endpoints': {
            'authentication': '/api/auth/',
            'products': '/api/products/',
            'orders': '/api/orders/',
            'reports': '/api/reports/',
            'admin': '/admin/',
        },
        'documentation': 'Please refer to the README.md for detailed API documentation'
    })


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', api_root, name='api_root'),
    path('api/auth/', include('authentication.urls')),
    path('api/products/', include('products.urls')),
    path('api/orders/', include('orders.urls')),
    path('api/reports/', include('reports.urls')),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
