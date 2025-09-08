from .settings import *  # reuse your base settings

# Use local SQLite in CI so no RDS/Secrets are needed
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "ci.sqlite3",
    }
}

# Fast/isolated CI defaults
DEBUG = False
ALLOWED_HOSTS = ["*"]
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "ci-cache",
    }
}

# Speed up auth hashing if you ever run tests in CI
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
