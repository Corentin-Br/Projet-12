import logging

from django import forms
from django.contrib import admin
from django.contrib.admin.options import ModelAdmin
from django.core.exceptions import PermissionDenied, ValidationError

from api.urls import event_create, event_change, event_list, event_delete

from .models import Event
from accounts.admin import get_context

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
        if request.method == 'POST':
            response = event_create(request)
            if response.status_code == 201:
                return self.response_add(request, self.model.objects.last())
            else:
                if response.status_code != 403:
                    logger.warning(f"Failed to create event with \n"
                                   f"client: {request.POST['client']} \n"
                                   f"contract: {request.POST['contract']}.")

                else:
                    logger.warning(f"Unauthorized user {request.user} failed to create an event")
                context, add, obj = get_context(self, request, None, extra_context, status_code=response.status_code)
                return self.render_change_form(request, context, add=add, change=not add, obj=obj, form_url=form_url)
        else:
            if request.user.role in ("gestion", "sales"):
                return super().add_view(request, form_url, extra_context)
            else:
                logger.warning(f"Unauthorized user {request.user} tried to acces event creation.")
                raise PermissionDenied

    def change_view(self, request, object_id, form_url='', extra_context=None):
        if request.method == 'POST':
            response = event_change(request, pk=object_id)
            if response.status_code == 200:
                return self.response_change(request, self.get_object(request, object_id))
            else:
                if response.status_code != 403:
                    logger.warning(f"Failed to edit event {object_id} with \n"
                                   f"client: {request.POST['client']} \n"
                                   f"contract: {request.POST['contract']}")
                else:
                    logger.warning(f"Unauthorized user {request.user} failed to edit an event")
                context, add, obj = get_context(self, request, object_id, extra_context, status_code=response.status_code)
                return self.render_change_form(request, context, add=add, change=not add, obj=obj, form_url=form_url)
        else:
            return super().change_view(request, object_id, form_url, extra_context)

    def get_queryset(self, request):
        response = event_list(request)
        if response.status_code in (200, 204):
            qs = self.model._default_manager.get_queryset()
            qs = qs.filter(id__in=[event["id"] for event in response.data])
            ordering = self.get_ordering(request)
            if ordering:
                qs = qs.order_by(*ordering)
        elif response.status_code == 403:
            logger.warning(f"Unauthorized user {request.user} failed to obtain the list of events.")
            raise PermissionDenied
        else:
            logger.warning(f"An empty list of events was sent to {request.user}.\n"
                           f"The API sent : {response.data}")
            qs = self.model.objects.none()
        return qs

    def delete_model(self, request, obj):
        response = event_delete(request, pk=obj.pk)
        if response.status_code == 403:
            logger.warning(f"Unauthorized user {request.user} failed to delete {obj}")
            raise PermissionDenied
        elif response.status_code != 204:
            logger.warning(f"{request.user} failed to delete {obj}.\n"
                           f"The API sent: {response.data}")

    def delete_queryset(self, request, queryset):
        for user in queryset:
            response = event_delete(request, pk=user.pk)
            if response.status_code == 403:
                logger.warning(f"Unauthorized user {request.user} failed to delete {user}")
                raise PermissionDenied
            elif response.status_code != 204:
                logger.warning(f"{request.user} failed to delete {user}.\n"
                               f"The API sent: {response.data}")

