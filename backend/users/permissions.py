from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed for any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the object.
        return obj == request.user


class IsLearner(permissions.BasePermission):
    """
    Permission class to allow access only to learners.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'learner'


class IsMentor(permissions.BasePermission):
    """
    Permission class to allow access only to mentors.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'mentor'


class IsApprovedMentor(permissions.BasePermission):
    """
    Permission class to allow access only to approved mentors.
    """

    def has_permission(self, request, view):
        return (request.user and 
                request.user.is_authenticated and 
                request.user.role == 'mentor' and 
                request.user.is_mentor_approved)


class IsAdmin(permissions.BasePermission):
    """
    Permission class to allow access only to admin users.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'admin'


class IsLearnerOrMentor(permissions.BasePermission):
    """
    Permission class to allow access to both learners and mentors.
    """

    def has_permission(self, request, view):
        return (request.user and 
                request.user.is_authenticated and 
                request.user.role in ['learner', 'mentor'])


class IsEmailVerified(permissions.BasePermission):
    """
    Permission class to ensure user has verified their email.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_email_verified


class CanCreateSession(permissions.BasePermission):
    """
    Permission to check if user can create/book sessions.
    Learners need verified email, mentors need approval.
    """

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        
        if request.user.role == 'learner':
            return request.user.is_email_verified
        elif request.user.role == 'mentor':
            return request.user.is_mentor_approved and request.user.is_email_verified
        
        return request.user.role == 'admin'


class IsMentorOrAdmin(permissions.BasePermission):
    """
    Permission class to allow access to mentors and admins.
    """

    def has_permission(self, request, view):
        return (request.user and 
                request.user.is_authenticated and 
                request.user.role in ['mentor', 'admin'])


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permission to allow owners or admins to access/modify objects.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Admin can access everything
        if request.user.role == 'admin':
            return True
        
        # Check if user is the owner
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        return obj == request.user


class ReadOnlyOrIsAuthenticated(permissions.BasePermission):
    """
    Permission to allow read-only access to anonymous users,
    but require authentication for write operations.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        return request.user and request.user.is_authenticated
