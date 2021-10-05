import logging

from django import forms
from django.contrib import admin
from django.contrib.admin.options import ModelAdmin
from django.core.exceptions import ValidationError

from api.urls import event_create, event_change, event_list, event_delete

from .models import Event
from accounts.admin import create_view, modification_view, list_view, delete_view

logger = logging.getLogger(__name__)
file_handler = logging.FileHandler('debug2.log')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


class EventCreationForm(forms.ModelForm):
    """A form for creating new events."""

    class Meta:
        model = Event
        fields = ('client', 'support', 'contract', 'attendees', 'date', 'notes')

    def clean(self):
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

    def add_view(self, request, form_url='', extra_context=None):
        return create_view(self, request, api_view=event_create, allowed_roles=["gestion", "sales"],
                           logs=["client", "contract"], form_url=form_url,
                           extra_context=extra_context)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        return modification_view(self, request, object_id, logs=["client", "contract"],
                                 api_view=event_change, form_url='', extra_context=None)

    def get_queryset(self, request):
        return list_view(self, request, event_list)

    def delete_model(self, request, obj):
        delete_view(request, obj, event_delete)

    def delete_queryset(self, request, queryset):
        for model in queryset:
            self.delete_model(request, model)

