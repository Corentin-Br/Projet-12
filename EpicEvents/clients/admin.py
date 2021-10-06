import logging

from django import forms
from django.contrib import admin
from django.contrib.admin.options import ModelAdmin


from api.urls import client_create, client_change, client_list, client_delete
from api.urls import contract_create, contract_change, contract_list, contract_delete

from .models import Contract, Client
from accounts.admin import create_view, modification_view, obtain_queryset, delete_view

module_logger = logging.getLogger(__name__)
file_handler = logging.FileHandler('debug2.log')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
module_logger.addHandler(file_handler)


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
    api_views = {"create": client_create,
                 "change": client_change,
                 "list": client_list,
                 "delete": client_delete}
    data_to_log = ["email", "first_name", "last_name", "sales_contact"]
    logger = module_logger

    def add_view(self, request, form_url='', extra_context=None):
        """A view used to create a Client."""
        return create_view(self, request, allowed_roles=["gestion", "sales"], form_url=form_url, extra_context=extra_context)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        """A view used to edit a Client."""
        return modification_view(self, request, object_id, form_url='', extra_context=None)

    def get_queryset(self, request):
        """Return the queryset asked by the request."""
        return obtain_queryset(self, request)

    def delete_model(self, request, obj):
        """Delete a Client."""
        delete_view(self, request, obj)

    def delete_queryset(self, request, queryset):
        """Delete a queryset of Clients."""
        for model in queryset:
            self.delete_model(request, model)

    def has_add_permission(self, request):
        if request.user.role in ('gestion', 'sales'):
            return True
        return False

    def has_view_permission(self, request, obj=None):
        if request.user.role in ('gestion', 'sales', 'support'):
            return True
        return False

    def has_change_permission(self, request, obj=None):
        if request.user.role == 'gestion' or request.user.role == "sales" and (obj is None or
                                                                               obj.sales_contact == request.user or
                                                                               obj.sales_contact is not None):
            return True
        return False

    def has_delete_permission(self, request, obj=None):
        if request.user.role == 'gestion' or request.user.role == "sales" and (obj is None or
                                                                               obj.sales_contact == request.user or
                                                                               obj.sales_contact is not None):
            return True
        return False



@admin.register(Contract)
class ContractAdmin(ModelAdmin):
    form = ContractChangeForm
    add_form = ContractCreationForm
    list_display = ('sales_contact', 'client', 'date_created', 'date_updated', 'status', 'amount', 'payment_due')
    search_fields = ('date_created',)
    ordering = ('date_created',)
    filter_horizontal = ()
    api_views = {"create": contract_create,
                 "change": contract_change,
                 "list": contract_list,
                 "delete": contract_delete}
    data_to_log = ["client", "sales_contact"]
    logger = module_logger

    def add_view(self, request, form_url='', extra_context=None):
        """A view used to create a Contract."""
        return create_view(self, request, allowed_roles=["gestion", "sales"], form_url=form_url, extra_context=extra_context)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        """A view used to edit a Contract."""
        return modification_view(self, request, object_id, form_url='', extra_context=None)

    def get_queryset(self, request):
        """Return the queryset asked by the request."""
        return obtain_queryset(self, request)

    def delete_model(self, request, obj):
        """Delete a Contract."""
        delete_view(self, request, obj)

    def delete_queryset(self, request, queryset):
        """Delete a queryset of Contracts."""
        for model in queryset:
            self.delete_model(request, model)

    def has_add_permission(self, request):
        if request.user.role in ('gestion', 'sales'):
            return True
        return False

    def has_view_permission(self, request, obj=None):
        if request.user.role in ('gestion', 'sales', 'support'):
            return True
        return False

    def has_change_permission(self, request, obj=None):
        if request.user.role == 'gestion' or request.user.role == "sales" and (obj is None or
                                                                               obj.sales_contact == request.user or
                                                                               obj.sales_contact is not None):
            return True
        return False

    def has_delete_permission(self, request, obj=None):
        if request.user.role == 'gestion' or request.user.role == "sales" and (obj is None or
                                                                               obj.sales_contact == request.user or
                                                                               obj.sales_contact is not None):
            return True
        return False



