from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.core.validators import EmailValidator
from django.utils.translation import gettext_lazy as _
# Create your models here.


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        ''' Create and return a regular user with an email and password. '''
        if not email:
            raise ValueError('User must have an email address.')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        ''' Create and return a superuser with an email and password. '''
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(
        _('Email'),
        max_length=255,
        unique=True,
        db_index=True,
        validators=[EmailValidator(message=_("Enter a valid email address."))]
    )
    fullname = models.CharField(_('Fullname'), max_length=255)
    is_active = models.BooleanField(default=True, db_index=True)
    is_staff = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['fullname']  # Removed phone_number

    class Meta:
        indexes = [
            models.Index(fields=['email'], name='email'),
            models.Index(fields=['is_active'], name='active'),
            models.Index(fields=['is_staff'], name='staff')
        ]

    def __str__(self):
        return f'{self.email}: {self.fullname}'
