from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()

class IDOrUsernameBackend(ModelBackend):
    """
    Custom authentication backend that allows users to log in using either
    their username or their university ID number.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get(User.USERNAME_FIELD)
        
        try:
            # Check both username and id_number
            user = User.objects.filter(Q(username=username) | Q(id_number=username)).distinct()
            if user.count() > 1:
                # If multiple users found with same ID, we don't know which one it is
                return None
            user = user.first()
            if not user:
                raise User.DoesNotExist
        except User.DoesNotExist:
            # Run the default password hasher once to reduce the vulnerability to timing attacks
            User().set_password(password)
        else:
            if user and user.check_password(password) and self.user_can_authenticate(user):
                return user
        return None
