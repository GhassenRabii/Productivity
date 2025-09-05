"""
Custom OIDC backend for AWS Cognito.

- Authenticates users via OIDC (mozilla-django-oidc).
- Creates/updates Django users from token claims.
- Mirrors Cognito groups (cognito:groups) to Django groups.
- Optionally elevates Admins to staff/superuser (configurable below).

Requirements:
    pip install mozilla-django-oidc

settings.py:
    AUTHENTICATION_BACKENDS = [
        "django.contrib.auth.backends.ModelBackend",
        "tasks.auth.MyOIDCBackend",
    ]
"""

import logging
from typing import List

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from mozilla_django_oidc.auth import OIDCAuthenticationBackend

logger = logging.getLogger(__name__)
User = get_user_model()


# --- Optional role mapping knobs ---
ELEVATE_ADMINS_TO_STAFF = True       # Admin group -> user.is_staff = True
ELEVATE_ADMINS_TO_SUPERUSER = False  # Admin group -> user.is_superuser = True (set True only if you want this)
ADMIN_GROUP_NAME = "Admin"           # Name of the admin group in Cognito


class MyOIDCBackend(OIDCAuthenticationBackend):
    """
    OIDC backend that:
    - Picks a stable username.
    - Matches existing users by email (to avoid dupes).
    - Syncs groups from `cognito:groups`.
    - Copies common profile fields (email, name).
    """

    # ---- Username selection -------------------------------------------------
    def get_username(self, claims):
        """
        Return a stable username for Django.

        Order of preference:
        1) `sub` (the Cognito user unique identifier) – safest and globally unique.
        2) email (lowercased).
        3) `cognito:username` if present.
        4) Fallback to whatever the parent class would do.
        """
        sub = claims.get("sub")
        if sub:
            return sub

        email = (claims.get("email") or "").strip().lower()
        if email:
            return email

        cognito_username = claims.get("cognito:username")
        if cognito_username:
            return cognito_username

        # Defer to default implementation as a last resort
        return super().get_username(claims)

    # ---- User matching to prevent duplicates --------------------------------
    def filter_users_by_claims(self, claims):
        """
        Try to find an existing user by email before creating a new one.
        This helps when you switch to OIDC in an app that already had users.
        """
        email = (claims.get("email") or "").strip().lower()
        if not email:
            return self.UserModel.objects.none()

        try:
            return [User.objects.get(email__iexact=email)]
        except User.DoesNotExist:
            return self.UserModel.objects.none()

    # ---- Create & update hooks ----------------------------------------------
    def create_user(self, claims):
        """
        Create a new Django user from OIDC claims, then sync fields and groups.
        """
        user = super().create_user(claims)
        user = self._apply_claims(user, claims)
        user = self._sync_groups(user, claims)
        user.save()
        logger.info("Created user via OIDC: %s", user.username)
        return user

    def update_user(self, user, claims):
        """
        Update an existing user from OIDC claims and keep groups in sync.
        """
        user = super().update_user(user, claims)
        user = self._apply_claims(user, claims)
        user = self._sync_groups(user, claims)
        user.save()
        logger.info("Updated user via OIDC: %s", user.username)
        return user

    # ---- Helpers -------------------------------------------------------------
    def _apply_claims(self, user, claims):
        """
        Copy common profile fields from claims to the Django user.
        Safe to call on create or update.
        """
        # Email
        email = (claims.get("email") or "").strip()
        if email and user.email != email:
            user.email = email

        # Name fields (best-effort)
        given_name = (claims.get("given_name") or "").strip()
        family_name = (claims.get("family_name") or "").strip()
        name = (claims.get("name") or "").strip()

        # Prefer explicit given/family name; fall back to 'name'
        if given_name or family_name:
            user.first_name = given_name[:150]
            user.last_name = family_name[:150]
        elif name:
            # Split naive "First Last"
            parts = name.split()
            user.first_name = (parts[0] if parts else "")[:150]
            user.last_name = (" ".join(parts[1:]) if len(parts) > 1 else "")[:150]

        return user

    def _sync_groups(self, user, claims):
        """
        Mirror Cognito groups to Django groups.
        - Creates any missing groups locally.
        - Replaces the user's group set with the incoming set (authoritative).
          If you prefer additive, switch to .add() and don't call .set().
        - Optionally elevates admins to staff/superuser.
        """
        group_names: List[str] = claims.get("cognito:groups", []) or []
        # Normalize
        group_names = [str(g).strip() for g in group_names if str(g).strip()]

        # Ensure groups exist and collect them
        groups = [Group.objects.get_or_create(name=name)[0] for name in group_names]

        # Authoritative sync: replace the set to match Cognito
        user.groups.set(groups)

        # Optional: elevate Admins
        if ADMIN_GROUP_NAME in group_names:
            if ELEVATE_ADMINS_TO_STAFF:
                user.is_staff = True
            if ELEVATE_ADMINS_TO_SUPERUSER:
                user.is_superuser = True
        else:
            # If you want to *revoke* staff/superuser when not Admin, uncomment:
            # user.is_staff = False
            # user.is_superuser = False
            pass

        return user
