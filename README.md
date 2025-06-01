# IQ Test Platform

A comprehensive online platform for conducting IQ tests, managing users, processing payments, and generating certificates.

## Features

-   **Professional IQ Testing**
    -   Multiple question types (text and image-based)
    -   Time-limited test sessions
    -   Randomized question selection from a large pool
    -   Category-based question distribution
    -   Real-time scoring and IQ calculation
    -   Question hints
-   **User Management**
    -   Secure user registration and authentication (including email-based login)
    -   Social authentication (Google, Facebook, Twitter)
    -   Personalized user dashboard
    -   Test history tracking
    -   Review submission system for completed tests
-   **Payment Integration**
    -   Stripe for card payments
    -   Paynow for mobile money payments (Ecocash)
    -   Secure payment verification and status tracking
-   **Certificate System**
    -   Professional PDF certificate generation upon test completion and payment
    -   Customizable certificate names
    -   Secure and shareable certificates
-   **Administrative Features**
    -   Admin interface for managing users, questions, and reviews.
    -   Management command for loading quiz questions from JSON files.

## Technology Stack

-   **Backend:**
    -   Python 3.x
    -   Django 5.1+
    -   Django REST Framework (for potential future API needs)
    -   `python-dotenv` for environment variable management
-   **Database:**
    -   SQLite (default for development)
    -   MySQL (planned for PythonAnywhere deployment)
-   **Payment Processing:**
    -   `stripe` Python library
    -   `paynow` Python SDK (custom or third-party, assuming via `Paynow` class)
-   **Authentication:**
    -   Django Authentication system
    -   `social-auth-app-django` for social logins
-   **PDF Generation:**
    -   ReportLab
-   **Image Handling:**
    -   Pillow
-   **Frontend:**
    -   Django Templates
    -   HTML, CSS, JavaScript
-   **Development Tools:**
    -   `django-debug-toolbar`
    -   `django-extensions`

## Prerequisites

-   Python 3.10+
-   Pip (Python package installer)
-   Git
-   Virtualenv (recommended for isolating project dependencies)
-   Access to a terminal or command prompt.

## Installation and Setup

1.  **Clone the Repository:**

    ```bash
    git clone https://github.com/meloShaya/iqtest.git
    cd iqtest
    ```

2.  **Create and Activate a Virtual Environment:**

    ```bash
    python -m venv venv
    # On Windows
    # venv\Scripts\activate
    # On macOS/Linux
    source venv/bin/activate
    ```

3.  **Install Dependencies:**
    
    ```bash
    pip install -r requirements.txt
    # or if Pipfile is used and preferred:
    # pip install pipenv
    # pipenv install
    # pipenv shell
    ```

4.  **Set Up Environment Variables:**

    -   Create a `.env` file in the project root directory (alongside `manage.py`).
    -   Copy the contents of `.env.example` into your new `.env` file.
    -   Fill in the required API keys and settings:
        -   `SECRET_KEY`: A strong, unique secret key. You can generate one using Django's `get_random_secret_key()` or an online generator.
        -   `DEBUG`: Set to `True` for development, `False` for production.
        -   `ALLOWED_HOSTS`: For development, `localhost,127.0.0.1` is usually fine. For production, add your domain(s).
        -   `DATABASE_URL` (Optional, if you switch from SQLite, e.g., for PythonAnywhere MySQL later): `mysql://USER:PASSWORD@HOST:PORT/NAME`
        -   Stripe Keys: `STRIPE_PUBLISHABLE_KEY`, `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`.
        -   Paynow Keys: `PAYNOW_INTEGRATION_ID`, `PAYNOW_INTEGRATION_KEY`, `PAYNOW_RETURN_URL`, `PAYNOW_RESULT_URL`.
        -   `HOST_URL`: The base URL of your site (e.g., `http://127.0.0.1:8000` for local dev, `https://yourdomain.com` for production).
        -   Email Settings (e.g., for password resets): `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `EMAIL_USE_TLS`.
        -   Social Auth Keys (Google, Facebook, Twitter): `SOCIAL_AUTH_GOOGLE_OAUTH2_KEY`, `SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET`, etc.

5.  **Apply Database Migrations:**

    ```bash
    python iqtest/manage.py migrate
    ```

6.  **Create a Superuser (Admin Account):**

    ```bash
    python iqtest/manage.py createsuperuser
    ```

    Follow the prompts to set up your admin username, email, and password.

7.  **Load Quiz Questions:**
    The project includes a script to load questions from JSON data files. The main question loading logic is in `iqtest/quiz/load_questions.py`.
    To load all datasets, you'll need to run a custom management command or adapt the `load_questions.py` script.

    _Example of how it might be structured if `load_questions.py` was a management command (this needs to be implemented or adapted):_

    ```bash
    # python iqtest/manage.py load_quiz_data
    ```

    _Currently, you might need to run the script directly or call its functions from the Django shell, ensuring the Django environment is set up. For example, by adding a main execution block to `load_questions.py` that can be called, or by integrating it into a custom management command._

    **Manual Loading via Django Shell (Example for one dataset):**

    ```bash
    python iqtest/manage.py shell
    ```

    Then in the shell:

    ```python
    from quiz.load_questions import load_questions
    import os
    from django.conf import settings

    # Define the base directory for data if not already clear
    DATA_DIR = os.path.join(settings.BASE_DIR, 'data') # Assuming 'data' is at the project root

    # Example for one dataset (repeat for others)
    # Ensure the paths correctly point to your data files and media folders
    json_file_path = os.path.join(DATA_DIR, 'T1-105-public.json')
    answer_file_path = os.path.join(DATA_DIR, 'T1-105-public.answer.json')
    image_base_dir_path = os.path.join(DATA_DIR, 'T1-105-public', 'media') # Or wherever media is relative to json

    if os.path.exists(json_file_path) and os.path.exists(answer_file_path):
        print(f"Loading questions from {json_file_path}...")
        load_questions(json_file_path, answer_file_path, image_base_dir_path)
        print("Done.")
    else:
        print(f"Error: One or more files not found for T1-105-public dataset.")
        print(f"Checked JSON: {json_file_path}")
        print(f"Checked Answer: {answer_file_path}")

    # Repeat for other datasets:
    # logic-diagram-public, seq-public, verbal-E-public, verbal1-public, etc.
    # Ensure the 'image_base_dir' path is correct for each. Some might be 'data/dataset_name/media', others 'data/media/dataset_name'.
    # The script `load_questions.py` uses `os.path.join(image_base_dir, image_name)`.
    # The `image_base_dir` argument should be the path to the directory containing the actual image files (e.g., 1.png, 1A.png).
    ```

    **Important for Image Paths in `load_questions.py`**:
    The `load_questions` script extracts image paths like `![](path/to/image.png)` from `stem` and `options`.
    The `image_base_dir` argument passed to `load_questions` should be the directory _containing these actual image files_.
    For example, if an option contains `![](1A.png)` and the `image_base_dir` is `iqtest/data/T1-105-public/media/`, the script will look for `iqtest/data/T1-105-public/media/1A.png`.

## Running the Application

1.  **Start the Development Server:**
    ```bash
    python iqtest/manage.py runserver
    ```
2.  Open your web browser and navigate to `http://127.0.0.1:8000/`.
3.  Access the admin panel at `http://127.0.0.1:8000/admin/`.

## Payment Integration Notes

-   **Stripe:**
    -   Ensure your Stripe API keys and webhook secret are correctly set in the `.env` file.
    -   The Stripe webhook endpoint is `/payment/webhook/`. You'll need to configure this in your Stripe dashboard, especially for production.
-   **Paynow:**
    -   Ensure your Paynow Integration ID, Key, and callback URLs are correctly set in the `.env` file.
    -   Test Paynow integration thoroughly, especially the callback mechanisms.

## Deployment to PythonAnywhere (Preparation)

This project can be deployed to PythonAnywhere. Here's a general outline of steps to prepare for and perform the deployment:

1.  **Sign up/Log in to PythonAnywhere.**
2.  **Database Setup (MySQL):**
    -   On PythonAnywhere, create a MySQL database (available on free and paid tiers). Note down the database name, username, password, and host address.
    -   Update your `.env` file (or PythonAnywhere's environment variables configuration) with these MySQL credentials using the `DATABASE_URL` format or individual `DATABASES` settings.
    -   Install `mysqlclient` or a similar MySQL database adapter in your PythonAnywhere virtual environment: `pip install mysqlclient`. Add this to `requirements.txt`.
3.  **Code Upload:**
    -   You can clone your GitHub repository directly into your PythonAnywhere file system.
    -   Set up a "Web app" on PythonAnywhere, choosing "Manual configuration" and the appropriate Python/Django version.
4.  **Virtual Environment:**
    -   Create a virtual environment on PythonAnywhere and install project dependencies from `requirements.txt`.
    -   `mkvirtualenv --python=/usr/bin/python3.x myenvname` (replace x and myenvname)
    -   `workon myenvname`
    -   `pip install -r requirements.txt`
5.  **WSGI Configuration:**
    -   Edit the WSGI configuration file provided by PythonAnywhere to point to your project's `wsgi.py` file.
    -   Ensure the paths to your project and virtual environment are correct.
6.  **Static and Media Files:**
    -   Configure PythonAnywhere to serve your static files (CSS, JS, images).
    -   Run `python manage.py collectstatic` on PythonAnywhere.
    -   Set up mappings for `STATIC_URL` and `STATIC_ROOT`, and `MEDIA_URL` and `MEDIA_ROOT` in the PythonAnywhere web app settings.
7.  **Environment Variables:**
    -   Set up all necessary environment variables (from your `.env` file) in the PythonAnywhere "Web" tab, under the "Code" section -> "Environment variables". **Do not upload your `.env` file directly if it contains secrets.**
8.  **Migrations:**
    -   Run database migrations on PythonAnywhere using a "Bash console":
        ```bash
        python manage.py migrate
        ```
9.  **Load Initial Data:**
    -   If needed, load your quiz questions using the Django shell or a management command as you did locally.
10. **Security:**
    -   Ensure `DEBUG = False` in your production settings.
    -   Set `ALLOWED_HOSTS` to your PythonAnywhere domain (e.g., `yourusername.pythonanywhere.com`).
11. **Reload Web App:**
    -   After making changes, reload your web app from the PythonAnywhere dashboard.

_(More detailed PythonAnywhere deployment steps will be covered as we proceed.)_

## File Structure Overview

```
iqtest/
├── .env.example        # Example environment variables
├── .gitignore          # Specifies intentionally untracked files that Git should ignore
├── Pipfile             # For Pipenv, if used
├── iqtest/             # Django project root
│   ├── README.md       # This file (consider moving to project root)
│   ├── data/           # Quiz data files (JSON, media)
│   ├── iqtest/         # Django app configuration directory
│   │   ├── __init__.py
│   │   ├── asgi.py
│   │   ├── settings.py # Project settings
│   │   ├── urls.py     # Main URL configurations
│   │   └── wsgi.py
│   ├── manage.py       # Django's command-line utility
│   ├── media/          # User-uploaded media files (e.g., question images)
│   ├── payment/        # Django app for payment processing
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── migrations/
│   │   ├── models.py
│   │   ├── templates/payment/
│   │   ├── test_utils.py # Payment testing utilities
│   │   ├── urls.py
│   │   ├── views.py
│   │   └── webhooks.py # Stripe webhook handler
│   ├── quiz/           # Django app for quiz logic and user management
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── authentication.py # Custom email auth backend
│   │   ├── forms.py
│   │   ├── load_questions.py # Script to load quiz data
│   │   ├── migrations/
│   │   ├── models.py
│   │   ├── templates/      # HTML templates for quiz and user pages
│   │   ├── templatetags/
│   │   ├── urls.py
│   │   └── views.py
│   ├
│   ├── static/           # Static files (CSS, JS, site images)
│   └── ... (other files like cert.crt, cert.key, Pipfile.lock if used)
├── requirements.txt      # Main requirements file (recommended location)
└── ... (other root level files like stripe CLI if it's a binary)
```


## Contributing

Contributions are welcome! Please follow these steps:

1.  Fork the repository.
2.  Create a new branch (`git checkout -b feature/your-feature-name`).
3.  Make your changes.
4.  Commit your changes (`git commit -m 'Add some feature'`).
5.  Push to the branch (`git push origin feature/your-feature-name`).
6.  Create a new Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
