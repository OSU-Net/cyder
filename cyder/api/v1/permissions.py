from rest_framework import permissions


class ReadOnlyIfAuthenticated(permissions.IsAuthenticated):
    def has_permission(self, request, view):
        return (request.user and request.user.is_authenticated() and
                request.method in permissions.SAFE_METHODS)


class ReadOnlyIfAuthenticatedWriteIfSpecialCase(permissions.IsAuthenticated):
    def has_permission(self, request, view):
        token = request.auth

        if token.can_write:
            return True

        return (request.user and request.user.is_authenticated() and
                request.method in permissions.SAFE_METHODS)
