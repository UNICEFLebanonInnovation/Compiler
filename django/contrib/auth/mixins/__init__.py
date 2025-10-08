"""Authentication mixins used by a handful of views."""


class LoginRequiredMixin:
    """Placeholder mixin that simply stores the requirement flag."""

    login_url = '/login/'
    redirect_field_name = 'next'
