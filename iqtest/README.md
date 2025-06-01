# IQ Test Website

A professional and comprehensive IQ testing platform built with Django, featuring secure payment processing, certificate generation, and detailed analytics.

## Features

-   **Professional IQ Testing**

    -   Multiple question types (text and image-based)
    -   Time-limited test sessions
    -   Randomized question selection
    -   Category-based question distribution
    -   Real-time scoring and IQ calculation

-   **User Management**

    -   Secure user authentication
    -   User registration system
    -   Personal dashboard
    -   Test history tracking
    -   Performance analytics

-   **Payment Integration**

    -   Stripe payment processing
    -   Paynow integration
    -   Secure payment verification
    -   Multiple payment status tracking

-   **Certificate System**

    -   Professional PDF certificate generation
    -   Customizable certificate names
    -   Secure certificate access
    -   Shareable certificates

-   **Analytics & Reporting**
    -   Detailed test results
    -   Visual data representation
    -   Performance tracking
    -   Historical data analysis

## Technology Stack

-   **Backend**

    -   Django 5.1.6
    -   Django REST Framework
    -   SQLite Database
    -   ReportLab (PDF generation)
    -   Pillow (Image processing)

-   **Payment Processing**

    -   Stripe
    -   Paynow

-   **Authentication**
    -   Django Authentication
    -   Social Auth

## Installation

1. Clone the repository:

```bash
git clone [repository-url]
cd iqtest
```

2. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Set up environment variables:

```bash
# Copy the example environment file
cp .env.example .env

# Edit the .env file with your actual credentials
nano .env  # or use your preferred text editor
```

The `.env` file should contain the following variables (already in the example file):

```
# Django Secret Key
SECRET_KEY=your-secret-key-here

# Stripe Configuration
STRIPE_PUBLISHABLE_KEY=your-stripe-publishable-key
STRIPE_SECRET_KEY=your-stripe-secret-key
STRIPE_API_VERSION=2022-08-01
STRIPE_WEBHOOK_SECRET=your-stripe-webhook-secret

# Paynow Configuration
PAYNOW_INTEGRATION_ID=your-paynow-integration-id
PAYNOW_INTEGRATION_KEY=your-paynow-integration-key
PAYNOW_RETURN_URL=http://yourdomain.com/payment/return
PAYNOW_RESULT_URL=http://yourdomain.com/payment/result
HOST_URL=http://yourdomain.com

# Social Auth - Facebook
SOCIAL_AUTH_FACEBOOK_KEY=your-facebook-app-id
SOCIAL_AUTH_FACEBOOK_SECRET=your-facebook-app-secret

# Social Auth - Twitter
SOCIAL_AUTH_TWITTER_KEY=your-twitter-api-key
SOCIAL_AUTH_TWITTER_SECRET=your-twitter-api-secret

# Social Auth - Google
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY=your-google-client-id
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET=your-google-client-secret

# Debug Mode (set to False in production)
DEBUG=False
```

Replace all placeholder values with your actual credentials.

5. Run migrations:

```bash
python manage.py migrate
```

6. Create a superuser:

```bash
python manage.py createsuperuser
```

7. Run the development server:

```bash
python manage.py runserver
```

## Project Structure

```
iqtest/
├── iqtest/              # Main project configuration
├── quiz/                # Core IQ test application
├── payment/             # Payment processing
├── static/              # Static files
├── media/               # User-uploaded media
├── data/                # Data files
└── manage.py            # Django management script
```

## Usage

1. **Taking the Test**

    - Register or log in to your account
    - Start a new test session
    - Complete the time-limited test
    - View your results and IQ score

2. **Certificate Generation**

    - Complete a test session
    - Process payment
    - Generate and download your certificate
    - Share your results

3. **Dashboard**
    - View test history
    - Track performance
    - Access certificates
    - View analytics

## Security

-   Secure user authentication
-   Payment data encryption
-   Session management
-   Protected certificate access
-   Secure file handling

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

