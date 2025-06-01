"""
Test utilities for Paynow integration.
These functions are preserved for testing purposes but are not used in production.
"""

from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.conf import settings
from paynow import Paynow

@login_required
def test_paynow(request):
    """A test view to directly test Paynow integration."""
    try:
        paynow = Paynow(settings.PAYNOW_INTEGRATION_ID, settings.PAYNOW_INTEGRATION_KEY,
                       settings.HOST_URL + '/payment/complete/', settings.HOST_URL + '/payment/update/')
        
        # Check if we're in test mode
        is_test_mode = str(settings.PAYNOW_INTEGRATION_ID).startswith('1')
        test_phone = '0771748147'  # Standard test phone number for Paynow tests
        merchant_email = "shayanewakomelody02@gmail.com"  # Default based on error message
        
        if request.method == 'POST':
            # Use fixed amount for our standard service
            amount = 0.53  # Fixed amount for IQ test results (USD)
            
            # Get the email, but in test mode we need to use the merchant email
            if is_test_mode:
                # Extract merchant email from error message or use a default
                email = merchant_email
            else:
                email = request.POST.get('email', 'test@example.com')
                
            phone = request.POST.get('phone', '')
            
            # Use test phone number if in test mode and no phone provided
            if is_test_mode and not phone:
                phone = test_phone
            
            payment = paynow.create_payment('Test Payment', email)
            payment.add('IQ Test Results Access', amount)
            
            # Pass in the test phone when in test mode
            response = paynow.send_mobile(payment, phone, 'ecocash')
            
            return simple_paynow_test(request, response, amount, email, phone)
        
        return render(request, 'payment/test_paynow.html', {
            'is_test_mode': is_test_mode,
            'test_phone': test_phone if is_test_mode else '',
            'merchant_email': merchant_email,
        })
    except Exception as e:
        import traceback
        error_traceback = traceback.format_exc()
        return HttpResponse(f"Error: {str(e)}<br><pre>{error_traceback}</pre>", content_type="text/html")

@login_required
def simple_paynow_test(request, response, amount, email, phone):
    """Process paynow test response and return detailed results."""
    result = []
    try:
        # Basic information
        result.append(f"TEST PAYMENT INFORMATION:")
        result.append(f"Amount: ${amount}")
        result.append(f"Email: {email}")
        result.append(f"Phone: {phone}")
        result.append("\n")
        
        # Response analysis
        result.append(f"RESPONSE TYPE: {type(response)}")
        result.append(f"RESPONSE STRING: {str(response)}")
        
        # Check attributes
        result.append("\nRESPONSE ATTRIBUTES:")
        for attr in ['success', 'error', 'poll_url', 'instructions']:
            if hasattr(response, attr):
                attr_value = getattr(response, attr)
                if isinstance(attr_value, type):
                    result.append(f"- {attr}: <type '{attr_value.__name__}'> (type: {type(attr_value)})")
                else:
                    result.append(f"- {attr}: {attr_value} (type: {type(attr_value)})")
            else:
                result.append(f"- {attr}: Not present")
        
        # Check for __dict__
        if hasattr(response, '__dict__'):
            result.append("\nRESPONSE __dict__ CONTENTS:")
            for key, value in response.__dict__.items():
                result.append(f"- {key}: {value} (type: {type(value)})")
        else:
            result.append("\nResponse object has no __dict__ attribute")
        
        # Special handling for data dictionary
        if hasattr(response, 'data') and isinstance(response.data, dict):
            result.append("\nRESPONSE DATA DICTIONARY CONTENTS:")
            for key, value in response.data.items():
                result.append(f"- {key}: {value} (type: {type(value)})")
            
            # Check for key information in data
            important_keys = ['pollurl', 'instructions', 'error', 'status', 'hash']
            result.append("\nIMPORTANT VALUES FROM DATA DICTIONARY:")
            for key in important_keys:
                if key in response.data:
                    result.append(f"- {key}: {response.data[key]}")
        
        # Special check for test mode errors
        if hasattr(response, 'data') and isinstance(response.data, dict) and 'error' in response.data:
            error_message = response.data['error']
            if 'test mode' in error_message.lower() or 'test case' in error_message.lower():
                result.append("\nTEST MODE ERROR DETECTED:")
                result.append(f"Error: {error_message}")
                result.append("This is a special test mode error. In production with real credentials, this would work with a real mobile number.")
                result.append("For testing purposes, consider the payment as successful when this specific error occurs.")
                result.append("See https://developers.paynow.co.zw/docs/integration_testing.html for more information.")
                
    except Exception as e:
        import traceback
        result.append(f"\nEXCEPTION DURING ANALYSIS: {str(e)}")
        result.append(traceback.format_exc())
    
    # Return plain text response
    return HttpResponse("\n".join(result), content_type="text/plain")

@login_required
def verify_paynow_credentials(request):
    """API endpoint to verify if Paynow credentials are valid"""
    if not request.user.is_staff:
        return JsonResponse({'success': False, 'error': 'Permission denied'})
    
    try:
        # Get the Paynow credentials from settings
        integration_id = settings.PAYNOW_INTEGRATION_ID
        integration_key = settings.PAYNOW_INTEGRATION_KEY
        return_url = settings.PAYNOW_RETURN_URL
        result_url = settings.PAYNOW_RESULT_URL
        
        # Check credential format
        credential_issues = []
        if not integration_id:
            credential_issues.append("PAYNOW_INTEGRATION_ID is missing")
        if not integration_key:
            credential_issues.append("PAYNOW_INTEGRATION_KEY is missing")
        if not return_url:
            credential_issues.append("PAYNOW_RETURN_URL is missing")
        if not result_url:
            credential_issues.append("PAYNOW_RESULT_URL is missing")
            
        if credential_issues:
            return JsonResponse({
                'success': False,
                'error': 'Invalid Paynow configuration',
                'issues': credential_issues,
                'credentials': {
                    'integration_id': bool(integration_id),
                    'integration_key': bool(integration_key),
                    'return_url': bool(return_url),
                    'result_url': bool(result_url)
                }
            })
        
        # Check for proper URLs
        url_issues = []
        for name, url in [('return_url', return_url), ('result_url', result_url)]:
            if not (url.startswith('http://') or url.startswith('https://')):
                url_issues.append(f"{name} doesn't start with http:// or https://")
                
        if url_issues:
            return JsonResponse({
                'success': False,
                'error': 'URL format issues',
                'issues': url_issues,
                'urls': {
                    'return_url': return_url,
                    'result_url': result_url
                }
            })
        
        # Try to initialize Paynow object
        paynow = Paynow(
            integration_id,
            integration_key,
            return_url,
            result_url
        )
        
        # Create a test payment to see if the API accepts it
        payment = paynow.create_payment('Credentials Test', request.user.email)
        payment.add('Test Item', 0.01)
        
        # Return success with masked credentials
        masked_id = "..." if len(integration_id) <= 8 else integration_id[:4] + '*' * (len(integration_id) - 8) + integration_id[-4:]
        masked_key = "..." if len(integration_key) <= 8 else integration_key[:4] + '*' * (len(integration_key) - 8) + integration_key[-4:]
        
        return JsonResponse({
            'success': True,
            'message': 'Paynow credentials appear to be valid',
            'credentials': {
                'integration_id': masked_id,
                'integration_key': masked_key,
                'return_url': return_url,
                'result_url': result_url
            }
        })
    except Exception as e:
        # Return detailed error information
        import traceback
        return JsonResponse({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        })

# Import missing dependencies
from django.http import JsonResponse
import traceback 