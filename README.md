# Django Email-Based Two-Factor Authentication (2FA)

This project is a Django web application with **email-based two-factor authentication**.\
After a successful username/password login, users receive a one-time code via email to complete the login process.

---

## Features

- Django user authentication
- Email-based one-time password (OTP)
- Configurable OTP expiration time
- Environment-based configuration (`local_settings.py` or `.env`)
- Secure session handling
- Ready for local and production deployment

---

## Requirements

- Python 3.9+
- Django 4.2+
- An SMTP server (Gmail, Outlook, or custom)
- Virtual environment recommended

---

## Setup

### 1. Clone the Repository

```
git clone https://github.com/harrykein75/django_2fa.git
cd django_2fa
```

### 2. Create & Activate Virtual Environment

```
python -m venv venv
source venv/bin/activate       # Linux/Mac
venv\Scripts\activate          # Windows
```

### 3. Install Dependencies

```
pip install -r requirements.txt
```

### 4. Configure Email Settings

Create a `local_settings.py` file in the same folder as `settings.py`:

```
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'your_email@example.com'
EMAIL_HOST_PASSWORD = 'your_app_password'
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = 'Your App Support <support@example.com>'

# Session settings
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
```

**Tip:** Add `local_settings.py` to `.gitignore` so credentials are not stored in Git.

---

### 5. Apply Migrations

```
python manage.py migrate
```

### 6. Create a Superuser

```
python manage.py createsuperuser
```

### 7. Run Development Server

```
python manage.py runserver
```

Visit [http://localhost:8000](http://localhost:8000) to access the app.

---

## How It Works

1. User logs in with username & password.
2. If credentials are correct, Django generates an OTP and sends it to the user's email.
3. User enters the OTP on the verification page.
4. If OTP is valid and not expired, login is completed.

---

## Running in Production

- Use `.env` files or environment variables instead of `local_settings.py`.
- Set `DEBUG = False` in settings.
- Use a proper SMTP server with an app-specific password.
- Serve static files via `collectstatic` and a web server (Nginx/Apache).

---

## Development Notes

- **Debug Email Backend**: For local testing without sending real emails:

```
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

This will print email content to the terminal instead of sending.

---

## License

This project is released under the MIT License.
Copyright (c) 2025 harrykein75