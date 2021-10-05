import logging

from django import forms
from django.contrib import admin
from django.contrib.admin.options import ModelAdmin
from django.core.exceptions import ValidationError

from api.urls import event_create, event_change, event_list, event_delete

from .models import Event
from accounts.admin import create_view, modification_view, obtain_queryset, delete_view

module_logger = logging.getLogger(__name__)
file_handler = logging.FileHandler('debug2.log')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
module_logger.addHandler(file_handler)


class EventCreationForm(forms.ModelForm):
    """A form for creating new events."""

    class Meta:
        model = Event
        fields = ('client', 'support', 'contract', 'attendees', 'date', 'notes')

    def clean(self):
        """Clean the data of the form and ensure that the client and the client in the contract are the same."""
        cleaned_data = super().clean()
        client = cleaned_data.get('client')
        contract_client = getattr(cleaned_data.get("contract"), "client")

        if client and contract_client:
            if client != contract_client:
                raise ValidationError("The client for the event and the client on the contract must be the same.")


class EventChangeForm(forms.ModelForm):
    """A form for updating events."""

    class Meta:
        model = Event
        fields = ('client', 'support', 'contract', 'attendees', 'date', 'notes')

    def clean(self):
        """Clean the data of the form and ensure that the client and the client in the contract are the same."""
        cleaned_data = super().clean()
        client = cleaned_data.get('client')
        contract_client = getattr(cleaned_data.get("contract"), "client")

        if client and contract_client:
            if client != contract_client:
                raise ValidationError("The client for the event and the client on the contract must be the same.")


@admin.register(Event)
class EventAdmin(ModelAdmin):
    form = EventChangeForm
    add_form = EventCreationForm
    list_display = ('client', 'date_created', 'date_updated', 'support', 'contract', 'attendees', 'date', 'notes', 'status')
    search_fields = ('date_created',)
    ordering = ('date_created',)
    filter_horizontal = ()
    api_views = {"create": event_create,
                 "change": event_change,
                 "list": event_list,
                 "delete": event_delete}
    data_to_log = ["client", "contract"]
    logger = module_logger

    def add_view(self, request, form_url='', extra_context=None):
        """A view used to create an Event."""
        return create_view(self, request, allowed_roles=["gestion", "sales"], form_url=form_url, extra_context=extra_context)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        """A view used to create an Event."""
        return modification_view(self, request, object_id, form_url='', extra_context=None)

    def get_queryset(self, request):
        """Return the queryset asked by the request."""
        return obtain_queryset(self, request)

    def delete_model(self, request, obj):
        """Delete an Event."""
        delete_view(self, request, obj)

    def delete_queryset(self, request, queryset):
        """Delete a queryset of Events."""
        for model in queryset:
            self.delete_model(request, model)

