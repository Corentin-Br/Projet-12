import logging

from django import forms
from django.contrib import admin
from django.contrib.admin import helpers
from django.contrib.admin.exceptions import DisallowedModelAdminToField
from django.contrib.admin.options import TO_FIELD_VAR, IS_POPUP_VAR
from django.contrib.admin.utils import unquote, flatten_fieldsets
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.core.exceptions import ValidationError
from django.core.exceptions import PermissionDenied


from .models import MyUser
from api.urls import user_change, user_create, user_list, user_delete

logger = logging.getLogger(__name__)
file_handler = logging.FileHandler('debug2.log')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


class UserCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = MyUser
        fields = ('email', 'first_name', 'last_name', 'role', 'password', 'password2')

    def clean_password2(self):
        password1 = self.cleaned_data.get("password")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        data = self.cleaned_data.copy()
        del(data["password2"])
        super().save(commit=False)
        user = MyUser.objects.create_user(**data)
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    disabled password hash display field.
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = MyUser
        fields = ('email', 'password', 'first_name', 'last_name', 'role', 'is_active')


class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    list_display = ('email', 'first_name', 'last_name', 'role', 'is_admin')
    fieldsets = ((None, {'fields': form.Meta.fields}),)
    add_fieldsets = ((None, {'fields': add_form.Meta.fields}),)
    list_filter = ('is_admin',)
    search_fields = ('email', 'role')
    ordering = ('email',)
    filter_horizontal = ()

    def add_view(self, request, form_url='', extra_context=None):
        return create_view(self, request, api_view=user_create, allowed_roles=["gestion"],
                           logs=["email", "first_name", "last_name", "role"], form_url=form_url,
                           extra_context=extra_context)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        return modification_view(self, request, object_id, logs=["email", "first_name", "last_name", "role"], api_view=user_change, form_url='', extra_context=None)

    def get_queryset(self, request):
        return list_view(self, request, user_list)

    def delete_model(self, request, obj):
        delete_view(request, obj, user_delete)

    def delete_queryset(self, request, queryset):
        for model in queryset:
            self.delete_model(request, model)


admin.site.register(MyUser, UserAdmin)


def get_context(admin_model, request, object_id, extra_context, status_code):
    """Create the context required to render the admin template.

    It is needed because django's default change_view will perform change on the database, while we want the API to be
    the only one to do so."""
    to_field = request.POST.get(TO_FIELD_VAR, request.GET.get(TO_FIELD_VAR))
    if to_field and not admin_model.to_field_allowed(request, to_field):
        raise DisallowedModelAdminToField("The field %s cannot be referenced." % to_field)
    model = admin_model.model
    opts = model._meta
    if '_saveasnew' in request.POST:
        object_id = None

    add = object_id is None

    if add:
        if status_code == 403:
            raise PermissionDenied
        obj = None
    else:
        obj = admin_model.get_object(request, unquote(object_id), to_field)
        if status_code == 403:
            raise PermissionDenied
        if obj is None:
            return admin_model._get_obj_does_not_exist_redirect(request, opts, object_id)
    fieldsets = admin_model.get_fieldsets(request, obj)
    ModelForm = admin_model.get_form(
        request, obj, change=not add, fields=flatten_fieldsets(fieldsets)
    )

    form = ModelForm(request.POST, request.FILES, instance=obj)
    formsets, inline_instances = admin_model._create_formsets(request, form.instance, change=not add)

    if not add and not admin_model.has_change_permission(request, obj):
        readonly_fields = flatten_fieldsets(fieldsets)
    else:
        readonly_fields = admin_model.get_readonly_fields(request, obj)
    adminForm = helpers.AdminForm(
        form,
        list(fieldsets),
        # Clear prepopulated fields on a view-only form to avoid a crash.
        admin_model.get_prepopulated_fields(request, obj) if add or admin_model.has_change_permission(request,
                                                                                                      obj) else {},
        readonly_fields,
        model_admin=admin_model)
    media = admin_model.media + adminForm.media

    inline_formsets = admin_model.get_inline_formsets(request, formsets, inline_instances, obj)
    for inline_formset in inline_formsets:
        media = media + inline_formset.media

    if add:
        title = 'Add %s'
    elif admin_model.has_change_permission(request, obj):
        title = 'Change %s'
    else:
        title = 'View %s'
    context = {
        **admin_model.admin_site.each_context(request),
        'title': title % opts.verbose_name,
        'subtitle': str(obj) if obj else None,
        'adminform': adminForm,
        'object_id': object_id,
        'original': obj,
        'is_popup': IS_POPUP_VAR in request.POST or IS_POPUP_VAR in request.GET,
        'to_field': to_field,
        'media': media,
        'inline_admin_formsets': inline_formsets,
        'errors': helpers.AdminErrorList(form, formsets),
        'preserved_filters': admin_model.get_preserved_filters(request),
    }

    # Hide the "Save" and "Save and continue" buttons if "Save as New" was
    # previously chosen to prevent the interface from getting confusing.
    if "_saveasnew" in request.POST:
        context['show_save'] = False
        context['show_save_and_continue'] = False
        # Use the change template instead of the add template.
        add = False

    context.update(extra_context or {})
    return context, add, obj


def create_view(admin_model, request, logs, api_view, allowed_roles, form_url='', extra_context=None):
    model_name = admin_model.model.__name__.lower()
    if request.method == 'POST':
        if "password" in request.POST and "password2" in request.POST:
            if request.POST["password"] != request.POST["password2"]:
                logger.warning(f"Password mismatch: failed to create user")
                context, add, obj = get_context(admin_model, request, None, extra_context, status_code=200)
                return admin_model.render_change_form(request, context, add=add, change=not add, obj=obj,
                                                      form_url=form_url)
        response = api_view(request)
        if response.status_code == 201:
            return admin_model.response_add(request, admin_model.model.objects.last())
        else:
            if response.status_code != 403:
                data = "\n".join(
                    [f"{information.replace('_', ' ')}:{request.POST[information]}"
                     for information in logs])
                logger.warning(f"Failed to create {model_name} with \n"
                               f"{data} \n"
                               f"The API sent {response.data}")
            else:
                logger.warning(f"Unauthorized user {request.user} failed to create a {model_name}")
            context, add, obj = get_context(admin_model, request, None, extra_context,
                                            status_code=response.status_code)
            return admin_model.render_change_form(request, context, add=add, change=not add, obj=obj,
                                                  form_url=form_url)
    else:
        if request.user.role in allowed_roles:
            return super(type(admin_model), admin_model).add_view(request, form_url, extra_context)
        else:
            logger.warning(f"Unauthorized user {request.user} tried to acces {model_name} creation.")
            raise PermissionDenied


def modification_view(admin_model, request, object_id, logs, api_view, form_url='', extra_context=None):
    model_name = admin_model.model.__name__.lower()
    if request.method == 'POST':
        response = api_view(request, pk=object_id)
        if response.status_code == 200:
            return admin_model.response_change(request, admin_model.get_object(request, object_id))
        else:
            if response.status_code != 403:
                data = "\n".join(
                    [f"{information.replace('_', ' ')}:{request.POST[information]}"
                     for information in logs])
                logger.warning(f"Failed to edit {model_name} {object_id} with \n"
                               f"{data}\n"
                               f"The API sent {response.data}")
            else:
                logger.warning(f"Unauthorized user {request.user} failed to edit a {model_name}")
            context, add, obj = get_context(admin_model, request, object_id, extra_context,
                                            status_code=response.status_code)
            return admin_model.render_change_form(request, context, add=add, change=not add, obj=obj,
                                                  form_url=form_url)
    else:
        return super(type(admin_model), admin_model).change_view(request, object_id, form_url, extra_context)


def list_view(admin_model, request, api_view):
    model_name = admin_model.model.__name__.lower()
    response = api_view(request)
    if response.status_code in (200, 204):
        qs = admin_model.model._default_manager.get_queryset()
        qs = qs.filter(id__in=[item["id"] for item in response.data])
        ordering = admin_model.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)
    elif response.status_code == 403:
        logger.warning(f"Unauthorized user {request.user} failed to obtain the list of {model_name}s.")
        raise PermissionDenied
    else:
        logger.warning(f"An empty list of {model_name}s was sent to {request.user}.\n"
                       f"The API sent : {response.data}")
        qs = admin_model.model.objects.none()
    return qs


def delete_view(request, obj, api_view):
    response = api_view(request, pk=obj.pk)
    if response.status_code == 403:
        logger.warning(f"Unauthorized user {request.user} failed to delete {obj}")
        raise PermissionDenied
    elif response.status_code != 204:
        logger.warning(f"{request.user} failed to delete {obj}.\n"
                       f"The API sent: {response.data}")


