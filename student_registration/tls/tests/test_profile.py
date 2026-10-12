import inspect
import re
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from urllib.parse import unquote

from django.template import Context, Engine
from django.template.loader import get_template
from django.test import SimpleTestCase
from django.urls import resolve, reverse

from student_registration.mscc.models import Registration
from student_registration.tls import education_view, services_view, urls, views
from student_registration.tls.education_form import EducationServiceForm
from student_registration.tls.forms import MainForm, ReferralForm
from student_registration.tls.profile_views import ProfileRegistrationMixin


class TLSProfileTests(SimpleTestCase):
    def test_only_requested_tab_is_active(self):
        profile = Path(views.__file__).parents[1] / 'templates/tls/profile.html'
        text = profile.read_text()
        text = re.sub(r'{% (?:extends|load|bootstrap_css).*?%}', '', text)
        engine = Engine(loaders=[('django.template.loaders.locmem.Loader', {
            'tls/child_info_tab.html': 'CHILD INFO CONTENT',
            'tls/child_services_tab.html': 'SERVICES CONTENT',
        })])
        template = engine.from_string(text)
        for tab, panel in [('info', 'tab-eg9-0'), ('services', 'tab-eg9-1')]:
            with self.subTest(tab=tab):
                html = template.render(Context({'current_tab': tab}))
                active = re.findall(r'<div class="tab-pane show active" id="([^"]+)"', html)
                self.assertEqual(active, [panel])
                self.assertEqual(len(re.findall(r'class="nav-link[^\"]* active"', html)), 1)

    def test_unknown_tab_falls_back_to_info(self):
        view = views.TLSProfileView()
        view.kwargs = {'pk': 216007}
        view.request = SimpleNamespace(GET={'current_tab': 'invalid'})
        registration = SimpleNamespace(child=SimpleNamespace(id=1, age=10), center=None)
        with patch.object(views.Registration, 'objects') as registrations, \
                patch.object(views.EducationService, 'objects') as education, \
                patch.object(views.Round, 'objects'), \
                patch.object(views.ProvidedServices, 'objects') as services, \
                patch.object(views, 'generate_services'):
            registrations.get.return_value = registration
            education.filter.return_value.values_list.return_value = []
            services.filter.return_value = []
            self.assertEqual(view.get_context_data()['current_tab'], 'info')

    def test_forms_use_mscc_models(self):
        self.assertIs(MainForm.Meta.model, Registration)
        self.assertEqual(ReferralForm.Meta.model._meta.app_label, 'mscc')
        self.assertEqual(EducationServiceForm.Meta.model._meta.app_label, 'mscc')

    def test_profile_picture_queryset_is_tls_only(self):
        view = ProfileRegistrationMixin()
        view.request = SimpleNamespace(user=SimpleNamespace(partner=None, partner_id=None, center_id=None))
        with patch('student_registration.tls.profile_views.Registration.objects') as manager, \
                patch('student_registration.tls.profile_views.has_group', return_value=False):
            view.get_queryset()
            manager.filter.assert_called_once_with(deleted=False, type='TLS')

    def test_every_tls_route_resolves_locally(self):
        for route in urls.urlpatterns:
            kwargs = {name: ('RS Grade 1' if name == 'programme_type' else 'pre' if name == 'pre_post' else 'file.zip' if name == 'file_name' else '1')
                      for name in route.pattern.regex.groupindex}
            with self.subTest(route=route.name):
                url = reverse('tls:' + route.name, kwargs=kwargs)
                self.assertTrue(url.startswith('/tls/'), url)
                match = resolve(unquote(url))
                callback = getattr(match.func, 'view_class', match.func)
                self.assertTrue(callback.__module__.startswith('student_registration.tls'), callback)

    def test_service_saves_return_to_tls_services_tab(self):
        classes = [views.TLSEducationServiceFormView]
        for module in (education_view, services_view):
            classes += [cls for _, cls in inspect.getmembers(module, inspect.isclass)
                        if cls.__module__ == module.__name__ and 'get_success_url' in cls.__dict__]
        for cls in classes:
            with self.subTest(view=cls.__name__):
                view = cls()
                view.kwargs = {'registry': 216007}
                self.assertEqual(view.get_success_url(), '/tls/child-profile/216007/?current_tab=services')

    def test_tls_links_do_not_reference_mscc_routes(self):
        app = Path(views.__file__).parents[1]
        for directory in (app / 'tls', app / 'templates/tls', app / 'static/js/tls', app / 'templates/django_tables2/tls'):
            for file in directory.rglob('*'):
                if file.suffix in ('.py', '.html', '.js') and 'tests' not in file.parts:
                    with self.subTest(file=str(file)):
                        self.assertNotIn('mscc:', file.read_text())
                        self.assertNotIn('/mscc/', file.read_text())


    def test_all_tls_templates_compile(self):
        app = Path(views.__file__).parents[1]
        for file in (app / 'templates/tls').rglob('*.html'):
            with self.subTest(template=str(file)):
                get_template('tls/' + str(file.relative_to(app / 'templates/tls')))

    def test_template_url_arguments_match_tls_routes(self):
        app = Path(views.__file__).parents[1]
        directories = [app / 'templates/tls', app / 'templates/django_tables2/tls']
        for directory in directories:
            for file in directory.rglob('*.html'):
                for name, arguments in re.findall(r"{% url ['\"]tls:([^'\"]+)['\"]([^%]*)%}", file.read_text()):
                    arguments = re.findall(r"(?:['\"][^'\"]*['\"]|[^\s]+)", arguments.strip())
                    if 'as' in arguments:
                        arguments = arguments[:arguments.index('as')]
                    route = next(route for route in urls.urlpatterns if route.name == name)
                    with self.subTest(file=str(file), route=name):
                        self.assertEqual(len(arguments), len(route.pattern.regex.groupindex))
