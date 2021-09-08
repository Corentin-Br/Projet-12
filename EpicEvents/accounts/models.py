from django.db import models
from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser


class MyUserManager(BaseUserManager):
    def create_user(self, first_name, last_name, role, email, password=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not email:
            raise ValueError('Users must have an email')

        user = self.model(
            email=self.normalize_email(email),
            first_name=first_name.capitalize(),
            last_name=last_name.upper(),
            role=role,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name, last_name, password=None):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            first_name=first_name,
            email=email,
            password=password,
            last_name=last_name,
            role="gestion",
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class MyUser(AbstractBaseUser):
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )
    first_name = models.CharField(
        verbose_name='first name',
        max_length=50)
    last_name = models.CharField(
        verbose_name='last_name',
        max_length=50
    )
    roles = [
        ('gestion', 'Gestion'),
        ('sales', 'Vente'),
        ('support', 'Support')
    ]
    role = models.CharField(choices=roles, max_length=10)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = MyUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'password']

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True
    def has_module_perms(self, app_label):
        """Does the user have permissions to view the app `app_label`?"""
        if app_label in ("api", "accounts"):
            return self.role == "gestion"
        elif app_label == "clients":
            return self.role in ("gestion", "sales")
        elif app_label == "events":
            return self.role in ("gestion", "support")

    @property
    def is_staff(self):
        """Is the user a member of staff?"""
        return self.role == "gestion"
