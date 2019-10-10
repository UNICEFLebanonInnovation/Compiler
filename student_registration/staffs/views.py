from django.views.generic import CreateView, UpdateView, ListView
from django.shortcuts import render_to_response, render, get_object_or_404, redirect
from student_registration.staffs.forms import StaffForm
from django.utils.translation import ugettext as _
from student_registration.staffs.models import Staffs
from django.http import Http404, HttpResponseRedirect
from django.template.context_processors import csrf
from django.views.generic import ListView, FormView, TemplateView, UpdateView
from django.core.urlresolvers import reverse
from student_registration.users.utils import force_default_language


class CreateStaffView(CreateView):
    template_name = 'staffs/staff_form.html'
    form_class = StaffForm()
    queryset = Staffs.objects.all()

    def get(self, request, *args, **kwargs):
        the_form = StaffForm()
        context = {
            'title': _('STAFF FORM'),
            'form': the_form,
        }
        return render(request, 'staffs/staff_form.html', context)

    def post(self, request, *args, **kwargs):
        form = StaffForm(request.POST, request.FILES)
        if request.POST:
            if form.is_valid():
                staff = form.save()
                staff.owner = request.user
                staff.save()
                return HttpResponseRedirect('/staffs/add/')
            else:
                return render(request, 'staffs/staff_form.html', {'form': form})
        else:
            form = StaffForm()

            args = {}
            args.update(csrf(request))

            args['form'] = form
            return render_to_response('staffs/staff_form.html', args)


class EditStaffView(UpdateView, FormView):
    model = Staffs
    form_class = StaffForm()

    template_name = 'staffs/staff_form.html'
    success_url = '/staffs/stafflist/'
    context_object_name = 'staff'

    def get_context_data(self, **kwargs):
        force_default_language(self.request)
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        return super(EditStaffView, self).get_context_data(**kwargs)

    def get_form(self, form_class=None):
        instance = Staffs.objects.get(id=self.kwargs['pk'])
        if self.request.method == "POST":
            return StaffForm(self.request.POST, instance=instance)
        else:
            return StaffForm(instance=instance)

    def form_valid(self, form):
        instance = Staffs.objects.get(id=self.kwargs['pk'])
        if self.request.FILES and self.request.FILES['image']:
            form.instance.image = self.request.FILES['image']
            form.instance.save()
        form.save()
        return super(EditStaffView, self).form_valid(form)

'''class EditStaffView(UpdateView):
    model = Staffs
    fields = (
        'first_name',
        'father_name',
        'last_name',
        'image',
        'MinisterApproval',
        'id_number',
    )
    template_name = 'staffs/staff_update_form.html'
    success_url = '/staffs/stafflist/'
    context_object_name = 'staff'
'''


class ListStaffView(ListView):
    model = Staffs
    template_name = 'staffs/stafflist.html'
    context_object_name = 'staff_list'

    def get_queryset(self):
        return Staffs.objects.all()
