from django.test import RequestFactory
from django.utils import timezone
from test_plus.test import TestCase

from ..models import User
from student_registration.user_activity import UserActivityMiddleware
from student_registration.backends.models import UserActivity


class TestUserActivityMiddleware(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = self.make_user()
        self.middleware = UserActivityMiddleware(lambda r: None)

    def test_last_activity_updated(self):
        request = self.factory.get('/')
        request.user = self.user
        before = timezone.now()
        self.middleware(request)
        self.user.refresh_from_db()
        self.assertIsNotNone(self.user.last_activity)
        self.assertGreaterEqual(self.user.last_activity, before)

    def test_activity_logged(self):
        request = self.factory.post('/some/', data={'foo': 'bar'})
        request.user = self.user
        self.middleware(request)
        activity = UserActivity.objects.latest('created')
        self.assertEqual(activity.username, self.user)
        self.assertEqual(activity.path, '/some/')
        self.assertEqual(activity.method, 'POST')
