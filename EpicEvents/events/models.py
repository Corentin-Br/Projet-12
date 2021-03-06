from django.db import models


class Event(models.Model):
    client = models.ForeignKey('clients.Client', on_delete=models.CASCADE, related_name="events")
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    support = models.ForeignKey('accounts.MyUser', on_delete=models.CASCADE, limit_choices_to={'role': 'support'}, related_name="events")
    contract = models.OneToOneField('clients.Contract', on_delete=models.CASCADE, related_name="event")
    attendees = models.PositiveIntegerField()
    date = models.DateTimeField()
    notes = models.TextField(blank=True, null=True)

    @property
    def status(self):
        return self.contract.status

    def __str__(self):
        return f"{self.client} {self.date.date()}"
