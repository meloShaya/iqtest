from django.shortcuts import render, redirect, reverse, get_object_or_404
import stripe
import uuid
import time
from django.urls import reverse
import json

from django.conf import settings
from quiz.models import TestSession  # Adjust the import based on your app structure
from paynow import Paynow
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib import messages

stripe.api_key = settings.STRIPE_SECRET_KEY
stripe.api_version = settings.STRIPE_API_VERSION

def payment_process(request, session_id):
    """Handle the payment initiation for a specific test session."""
    # Ensure the session exists, belongs to the user, and isn't already paid
    test_session = get_object_or_404(
        TestSession,
        id=session_id,
        user=request.user,
        payment_status='pending'
    )

    if request.method == 'POST':
        # Check which payment method was selected
        payment_method = request.POST.get('payment_method')
        
        if payment_method == 'stripe':
            # Process Stripe payment
            return process_stripe_payment(request, test_session)
        elif payment_method == 'paynow':
            # Process Paynow payment
            return redirect('payment:initiate_paynow', session_id=session_id)
        else:
            messages.error(request, "Please select a payment method.")

    # Render the payment page with options
    context = {
        'test_session': test_session,
        'amount': 0.53,  # Display as dollars
    }
    return render(request, 'payment/process.html', context)

def process_stripe_payment(request, test_session):
    """Process payment using Stripe."""
    success_url = request.build_absolute_uri(
        reverse('payment:completed', kwargs={'session_id': test_session.id})
    )
    cancel_url = request.build_absolute_uri(
        reverse('payment:canceled', kwargs={'session_id': test_session.id})
    )

    # Define the Stripe checkout session data
    session_data = {
        'mode': 'payment',
        'client_reference_id': str(request.user.id),
        'success_url': success_url,
        'cancel_url': cancel_url,
        'metadata': {'test_session_id': str(test_session.id)},
        'line_items': [{
            'price_data': {
                'unit_amount': 53,  # 53 cents in USD
                'currency': 'usd',
                'product_data': {
                    'name': 'Test Results Access',
                },
            },
            'quantity': 1,
        }],
    }

    # Create the Stripe checkout session
    session = stripe.checkout.Session.create(**session_data)
    
    # Save the Stripe session ID to the test session
    test_session.stripe_session_id = session.id
    test_session.save()

    # Redirect to Stripe's payment form
    return redirect(session.url, code=303)

def payment_completed(request, session_id):
    """Handle successful payment and redirect to dashboard."""
    test_session = get_object_or_404(TestSession, id=session_id, user=request.user)
    
    if test_session.stripe_session_id:
        # Retrieve the Stripe session to verify payment
        stripe_session = stripe.checkout.Session.retrieve(test_session.stripe_session_id)
        if stripe_session.payment_status == 'paid':
            test_session.payment_status = 'paid'
            test_session.save()
            # Redirect to the dashboard (adjust the URL name as needed)
            return render(request, 'payment/completed.html')  # Or pass session_id if dashboard needs it
        else:
            # Payment not completed, treat as canceled
            return redirect('payment:canceled', session_id=session_id)
    else:
        # No Stripe session found, check if Paynow payment was successful
        if test_session.payment_status == 'paid':
            return render(request, 'payment/completed.html')
        # If not paid through any method, treat as canceled
        return redirect('payment:canceled', session_id=session_id)

def payment_canceled(request, session_id):
    """Handle canceled payment."""
    test_session = get_object_or_404(TestSession, id=session_id, user=request.user)
    context = {'test_session': test_session}
    return render(request, 'payment/canceled.html', context)


@login_required
def initiate_paynow_payment(request, session_id):
    """Initiate a Paynow mobile payment for a test session."""
    # Get the session or return 404 if not found
    test_session = get_object_or_404(TestSession, id=session_id, user=request.user, payment_status='pending')
    
    if request.method == 'POST':
        # Get phone number from the form
        phone_number = request.POST.get('phone_number', '').strip()
        
        if not phone_number:
            messages.error(request, "Please provide a valid phone number.")
            return render(request, 'payment/initiate-paynow.html', {'test_session': test_session})
        
        # Format phone number (ensure it starts with 07)
        if phone_number.startswith('+263'):
            # Convert +263 format to 07 format
            phone_number = '0' + phone_number[4:]
        elif phone_number.startswith('263'):
            # Convert 263 format to 07 format
            phone_number = '0' + phone_number[3:]
        
        # Ensure it's in the correct format
        if not (phone_number.startswith('07') and len(phone_number) >= 10):
            messages.error(request, "Please provide a valid Ecocash mobile number (e.g., 07XXXXXXXX).")
            return render(request, 'payment/initiate-paynow.html', {'test_session': test_session})
        
        # Initialize Paynow
        paynow = Paynow(
            settings.PAYNOW_INTEGRATION_ID,
            settings.PAYNOW_INTEGRATION_KEY,
            settings.PAYNOW_RETURN_URL,
            settings.PAYNOW_RESULT_URL
        )

        # Create payment for the test session
        payment = paynow.create_payment(f'IQ Test #{test_session.id}', request.user.email)
        
        # Use USD (original currency)
        try:
            # Create a payment with a single item
            payment.add('IQ Test Access', 0.53)  # 0.53 USD
        except Exception as e:
            print("Error adding item to payment:", str(e))
            # Try alternative format
            payment.add('IQ Test Access', '0.53')
        
        try:
            # Send mobile payment request with improved error handling
            print(f"Initiating payment to {phone_number} for USD 0.53")
            
            # Debug the payment object
            print("Payment details:", {
                "reference": payment.reference,
                "auth_email": payment.auth_email,
                "items": payment.items
            })
            
            # Send the mobile payment request
            response = paynow.send_mobile(payment, phone_number, 'ecocash')
            
            # Debug output
            print("Paynow Response object type:", type(response))
            print("Paynow Response string:", str(response))
            
            # Generic success detection
            is_success = False
            instructions = None
            poll_url = None
            error_message = None
            
            # Extract attributes regardless of how they're stored
            if hasattr(response, 'success'):
                is_success = bool(response.success)
            
            # Check for data dictionary first (more reliable)
            if hasattr(response, 'data') and isinstance(response.data, dict):
                # Extract error if present
                if 'error' in response.data:
                    error_message = response.data['error']
                
                # Extract poll_url if present
                if 'pollurl' in response.data:
                    poll_url = response.data['pollurl']
                
                # Extract instructions if present
                if 'instructions' in response.data:
                    instructions = response.data['instructions']
            
            # Fall back to direct attributes if needed
            if instructions is None and hasattr(response, 'instructions'):
                # Make sure instructions is a string, not a type
                if isinstance(response.instructions, type):
                    instructions = "Please check your phone for payment instructions."
                else:
                    instructions = str(response.instructions)
            
            if poll_url is None and hasattr(response, 'poll_url'):
                if isinstance(response.poll_url, type):
                    poll_url = None
                else:
                    poll_url = str(response.poll_url)
            
            if error_message is None and hasattr(response, 'error'):
                error = response.error
                if isinstance(error, type):
                    error_message = f"Unknown error occurred"
                else:
                    error_message = str(error)
            
            # Success case: we need both poll_url and either success=True or instructions
            if poll_url and (is_success or instructions):
                # Save the poll URL to check status later
                test_session.poll_url = poll_url
                test_session.save()
                
                # Use extracted instructions or default message
                if instructions is None or isinstance(instructions, type):
                    instructions_text = "Please check your phone for a payment request and follow the instructions."
                else:
                    instructions_text = str(instructions)
                
                # Show the user instructions
                return render(request, 'payment/payment_instructions.html', {
                    'instructions': instructions_text,
                    'test_session': test_session
                })
            else:
                # Payment failed - use extracted error or default
                error_text = error_message or "Unknown error occurred with the payment service"
                print("Error message:", error_text)
                return render(request, 'payment/payment_error.html', {
                    'error': f'Payment failed: {error_text}',
                    'test_session': test_session
                })
        except Exception as e:
            # Handle exceptions
            import traceback
            print("Exception:", str(e))
            print(traceback.format_exc())
            return render(request, 'payment/payment_error.html', {
                'error': f'Payment system error: {str(e)}',
                'test_session': test_session
            })
    
    # Show form to enter phone number
    return render(request, 'payment/initiate-paynow.html', {
        'test_session': test_session
    })

@login_required
def check_paynow_status(request, session_id):
    """Check the status of a Paynow payment."""
    test_session = get_object_or_404(TestSession, id=session_id, user=request.user)
    
    # Get poll URL from model
    if not test_session.poll_url:
        messages.error(request, "No payment has been initiated for this session.")
        return redirect('payment:process', session_id=session_id)

    # Initialize Paynow
    paynow = Paynow(
        settings.PAYNOW_INTEGRATION_ID,
        settings.PAYNOW_INTEGRATION_KEY,
        settings.PAYNOW_RETURN_URL,
        settings.PAYNOW_RESULT_URL
    )

    try:
        # Check the transaction status
        status = paynow.check_transaction_status(test_session.poll_url)
        
        # Debug information
        print("Status object:", status)
        if hasattr(status, '__dict__'):
            print("Status dict:", status.__dict__)
        
        # Check if payment is paid
        is_paid = False
        if hasattr(status, 'paid'):
            is_paid = status.paid
        elif hasattr(status, 'status') and status.status == 'paid':
            is_paid = True
        
        if is_paid:
            # Payment confirmed, update the session
            test_session.payment_status = 'paid'
            test_session.save()
            messages.success(request, "Payment successful! You can now access your test results.")
            return redirect('payment:completed', session_id=session_id)
        else:
            # Payment not yet paid, wait and inform user
            return render(request, 'payment/payment_pending.html', {
                'message': 'Payment is still pending. Please complete it on your phone.',
                'test_session': test_session
            })
    except Exception as e:
        # Handle any errors when checking status
        print("Error checking payment status:", str(e))
        messages.error(request, f"Error checking payment status: {str(e)}")
        return render(request, 'payment/payment_error.html', {
            'error': f'Error checking payment status: {str(e)}',
            'test_session': test_session
        })