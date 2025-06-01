from django.urls import path
from . import views
from . import webhooks
from . import test_utils  # Import testing utilities

app_name = 'payment'

urlpatterns = [
    path('process/<int:session_id>/', views.payment_process, name='process'),
    path('initiate-paynow/<int:session_id>/', views.initiate_paynow_payment, name='initiate_paynow'),
    path('check-status/<int:session_id>/', views.check_paynow_status, name='check_paynow_status'),
    path('completed/<int:session_id>/', views.payment_completed, name='completed'),
    path('canceled/<int:session_id>/', views.payment_canceled, name='canceled'),
    path('webhook/', webhooks.stripe_webhook, name='webhook'),
]

# Test-only URLs - can be removed in production
test_urlpatterns = [
    path('test-paynow/', test_utils.test_paynow, name='test_paynow'),
    path('verify-paynow-credentials/', test_utils.verify_paynow_credentials, name='verify_paynow_credentials'),
]

# Add test URLs to main URL patterns
urlpatterns += test_urlpatterns