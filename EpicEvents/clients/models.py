from django.db import models
from django.db.models import Q
from phonenumber_field.modelfields import PhoneNumberField


class Client(models.Model):
    first_name = models.CharField(
        verbose_name='prénom',
        max_length=50)
    last_name = models.CharField(
        verbose_name='nom',
        max_length=50
    )
    email = models.EmailField(
        verbose_name='email',
        max_length=255,
        unique=True,
    )
    phone_number = PhoneNumberField()
    mobile_number = PhoneNumberField(null=True)
    company_name = models.CharField(
        verbose_name="nom d'entreprise",
        max_length=250)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    sales_contact = models.ForeignKey('accounts.MyUser', on_delete=models.CASCADE, limit_choices_to={'role': 'sales'}, blank=True,
                                      null=True, related_name="clients")

    def __str__(self):
        return self.company_name


class Contract(models.Model):
    sales_contact = models.ForeignKey('accounts.MyUser', on_delete=models.CASCADE, limit_choices_to={'role': 'sales'}, related_name="contracts")
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="contracts", limit_choices_to=Q(sales_contact__isnull=False))
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    status = models.BooleanField()
    amount = models.FloatField()
    payment_due = models.DateTimeField()

    def __str__(self):
        return f"{self.client} with {self.sales_contact} {self.date_created.date()}"
