from rest_framework import permissions


class IsContactOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user.role in ("sales", "support", "gestion")
        return request.user.role in ("sales", "gestion")  # Only users in sales/gestion can edit those objects.

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return request.user.role in ("sales", "support", "gestion")
        return view.queryset.filter(pk=obj.id, sales_contact=request.user).exists() or \
            (view.queryset.filter(pk=obj.id, sales_contact__isnull=True).exists() and request.user.role == "sales") or \
            request.user.role == "gestion"  # Either the user is the sales_contact OR there is no sales_contact OR the user is a gestion user.


class IsContactOrSupportOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        if view.action == "create":
            return request.user.role in ("sales", "gestion")  # Only sales and gestion can create those objects.
        return request.user.role in ("sales", "gestion", "support")

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return request.user.role in ("sales", "support", "gestion")
        return view.queryset.filter(pk=obj.id, support=request.user).exists() or request.user.role == "gestion"
        # Only the corresponding support or a gestion user can edit those objects.


class IsManager(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role == "gestion"
