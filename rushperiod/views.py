from django.shortcuts import render
from django.views import generic
from rushperiod.models import RushPeriod
from rushperiod.forms import CreateRushPeriodForm
from django.core.urlresolvers import reverse
from braces.views import LoginRequiredMixin, PermissionRequiredMixin, UserFormKwargsMixin

class IndexView(LoginRequiredMixin, PermissionRequiredMixin, generic.ListView):
	template_name = 'rushperiod/index.html'
	permission_required = "authentication.chapter_admin"
	context_object_name = 'rush_periods'

	def get_queryset(self):
		return RushPeriod.tenant_objects.all().order_by('start_date')

class CreateRushPeriodView(LoginRequiredMixin, UserFormKwargsMixin, generic.CreateView):
	template_name = 'rushperiod/create_rushperiod.html'
	model = RushPeriod
	form_class = CreateRushPeriodForm
	def get_success_url(self):
		return reverse('rushperiod:index')