from events.models import Event
from braces.views import LoginRequiredMixin
from django.core.urlresolvers import reverse
from django.views import generic
from events.forms import CreateEventForm
from rushtracker.models import Rush

class EventCreateView(LoginRequiredMixin, generic.CreateView):
    template_name = 'events/create_event.html'
    form_class = CreateEventForm
    model = Event

    def get_form_kwargs(self):
		kwargs = super(EventCreateView, self).get_form_kwargs()
		kwargs['request'] = self.request
		return kwargs
    def get_success_url(self):
        return reverse('rushtracker:index')

class EventIndexView(LoginRequiredMixin, generic.ListView):
	template_name = 'events/take_attendance.html'
	context_object_name = 'events'
	def get_queryset(self):
		return Event.tenant_objects.all().order_by('date')

class EventAttendanceView(LoginRequiredMixin, generic.ListView):
	template_name = 'events/take_attendance.html'
	context_object_name = 'rushes'
	def get_queryset(self):
		return Rush.tenant_objects.all()