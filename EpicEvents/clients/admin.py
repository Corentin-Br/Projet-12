import logging

from django import forms
from django.contrib import admin
from django.contrib.admin.options import ModelAdmin
from django.core.exceptions import PermissionDenied


from api.urls import client_create, client_change, client_list, client_delete
from api.urls import contract_create, contract_change, contract_list, contract_delete

from .models import Contract, Client
from accounts.admin import create_view, modification_view

logger = logging.getLogger(__name__)
file_handler = logging.FileHandler('debug2.log')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


class ClientCreationForm(forms.ModelForm):
    """A form for creating new events."""

    class Meta:
        model = Client
        fields = ('first_name', 'last_name', 'email', 'phone_number', 'mobile_number', 'company_name', 'sales_contact')


class ClientChangeForm(forms.ModelForm):
    """A form for updating events."""

    class Meta:
        model = Client
        fields = ('first_name', 'last_name', 'email', 'phone_number', 'mobile_number', 'company_name', 'sales_contact')


class ContractCreationForm(forms.ModelForm):
    """A form for creating new events."""

    class Meta:
        model = Contract
        fields = ('sales_contact', 'client', 'status', 'amount', 'payment_due')


class ContractChangeForm(forms.ModelForm):
    """A form for updating events."""

    class Meta:
        model = Contract
        fields = ('sales_contact', 'client', 'status', 'amount', 'payment_due')


@admin.register(Client)
class ClientAdmin(ModelAdmin):
    form = ClientChangeForm
    add_form = ClientCreationForm
    list_display = ('first_name', 'last_name', 'email', 'phone_number', 'mobile_number', 'company_name', 'date_created', 'date_updated', 'sales_contact')
    search_fields = ('company_name', 'email')
    ordering = ('date_created',)
    filter_horizontal = ()

    def add_view(self, request, form_url='', extra_context=None):
        return create_view(self, request, api_view=client_create, allowed_roles=["gestion", "sales"], logs=["email", "first_name", "last_name", "sales_contact"], form_url=form_url, extra_context=extra_context)


    def change_view(self, request, object_id, form_url='', extra_context=None):
        return modification_view(self, request, object_id, logs=["email", "first_name", "last_name", "sales_contact"],
                                 api_view=client_change, form_url='', extra_context=None)
        # if request.method == 'POST':
        #     response = client_change(request, pk=object_id)
        #     if response.status_code == 200:
        #         return self.response_change(request, self.get_object(request, object_id))
        #     else:
        #         if response.status_code != 403:
        #             logger.warning(f"Failed to edit client {object_id} with \n"
        #                            f"email: {request.POST['email']} \n"
        #                            f"first_name: {request.POST['first_name']}\n"
        #                            f"last_name: {request.POST['last_name']}\n"
        #                            f"sale_contact: {request.POST['sales_contact']}")
        #         else:
        #             logger.warning(f"Unauthorized user {request.user} failed to edit a client")
        #         context, add, obj = get_context(self, request, object_id, extra_context, status_code=response.status_code)
        #         return self.render_change_form(request, context, add=add, change=not add, obj=obj, form_url=form_url)
        # else:
        #     return super().change_view(request, object_id, form_url, extra_context)

    def get_queryset(self, request):
        response = client_list(request)
        if response.status_code in (200, 204):
            qs = self.model._default_manager.get_queryset()
            qs = qs.filter(id__in=[client["id"] for client in response.data])
            ordering = self.get_ordering(request)
            if ordering:
                qs = qs.order_by(*ordering)
        elif response.status_code == 403:
            logger.warning(f"Unauthorized user {request.user} failed to obtain the list of clients.")
            raise PermissionDenied
        else:
            logger.warning(f"An empty list of clients was sent to {request.user}.\n"
                           f"The API sent : {response.data}")
            qs = self.model.objects.none()
        return qs

    def delete_model(self, request, obj):
        response = client_delete(request, pk=obj.pk)
        if response.status_code == 403:
            logger.warning(f"Unauthorized user {request.user} failed to delete {obj}")
            raise PermissionDenied
        elif response.status_code != 204:
            logger.warning(f"{request.user} failed to delete {obj}.\n"
                           f"The API sent: {response.data}")

    def delete_queryset(self, request, queryset):
        for user in queryset:
            response = client_delete(request, pk=user.pk)
            if response.status_code == 403:
                logger.warning(f"Unauthorized user {request.user} failed to delete {user}")
                raise PermissionDenied
            elif response.status_code != 204:
                logger.warning(f"{request.user} failed to delete {user}.\n"
                               f"The API sent: {response.data}")


@admin.register(Contract)
class ContractAdmin(ModelAdmin):
    form = ContractChangeForm
    add_form = ContractCreationForm
    list_display = ('sales_contact', 'client', 'date_created', 'date_updated', 'status', 'amount', 'payment_due')
    search_fields = ('date_created',)
    ordering = ('date_created',)
    filter_horizontal = ()

    def add_view(self, request, form_url='', extra_context=None):
        return create_view(self, request, api_view=contract_create, allowed_roles=["gestion", "sales"], logs=["client", "sales_contact"], form_url=form_url, extra_context=extra_context)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        return modification_view(self, request, object_id, logs=["client", "sales_contact"],
                                 api_view=contract_change, form_url='', extra_context=None)
        # if request.method == 'POST':
        #     response = contract_change(request, pk=object_id)
        #     if response.status_code == 200:
        #         return self.response_change(request, self.get_object(request, object_id))
        #     else:
        #         if response.status_code != 403:
        #             logger.warning(f"Failed to edit contract {object_id} with \n"
        #                            f"client: {request.POST['client']} \n"
        #                            f"sales contact: {request.POST['sales_contact']}")
        #         else:
        #             logger.warning(f"Unauthorized user {request.user} failed to edit a contract")
        #         context, add, obj = get_context(self, request, object_id, extra_context, status_code=response.status_code)
        #         return self.render_change_form(request, context, add=add, change=not add, obj=obj, form_url=form_url)
        # else:
        #     return super().change_view(request, object_id, form_url, extra_context)

    def get_queryset(self, request):
        response = contract_list(request)
        if response.status_code in (200, 204):
            qs = self.model._default_manager.get_queryset()
            qs = qs.filter(id__in=[contract["id"] for contract in response.data])
            ordering = self.get_ordering(request)
            if ordering:
                qs = qs.order_by(*ordering)
        elif response.status_code == 403:
            logger.warning(f"Unauthorized user {request.user} failed to obtain the list of contracts.")
            raise PermissionDenied
        else:
            logger.warning(f"An empty list of contracts was sent to {request.user}.\n"
                           f"The API sent : {response.data}")
            qs = self.model.objects.none()
        return qs

    def delete_model(self, request, obj):
        response = contract_delete(request, pk=obj.pk)
        if response.status_code == 403:
            logger.warning(f"Unauthorized user {request.user} failed to delete {obj}")
            raise PermissionDenied
        elif response.status_code != 204:
            logger.warning(f"{request.user} failed to delete {obj}.\n"
                           f"The API sent: {response.data}")

    def delete_queryset(self, request, queryset):
        for user in queryset:
            response = contract_delete(request, pk=user.pk)
            if response.status_code == 403:
                logger.warning(f"Unauthorized user {request.user} failed to delete {user}")
                raise PermissionDenied
            elif response.status_code != 204:
                logger.warning(f"{request.user} failed to delete {user}.\n"
                               f"The API sent: {response.data}")



