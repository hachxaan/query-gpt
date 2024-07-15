# login_app/models.py

from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from rolepermissions.roles import AbstractUserRole

# Definición de los roles
class AdminMultikrd(AbstractUserRole):
    available_permissions = {
        "administer_users": True,
        "administer_queries": True,
    }


class AdminMarketing(AbstractUserRole):
    available_permissions = {
        "manage_queries": True,
    }


class UserMarketing(AbstractUserRole):
    available_permissions = {
        "execute_queries": True,
    }


# Definición del modelo de usuario
class User(AbstractUser):
    ROLES = (
        ("AdminMultikrd", "AdminMultikrd"),
        ("AdminMarketing", "AdminMarketing"),
        ("UserMarketing", "UserMarketing"),
    )

    role = models.CharField(
        "role", max_length=15, choices=ROLES, default="UserMarketing"
    )

    groups = models.ManyToManyField(
        Group, blank=True, related_name="custom_user_groups"
    )
    user_permissions = models.ManyToManyField(
        Permission, blank=True, related_name="custom_user_permissions"
    )

