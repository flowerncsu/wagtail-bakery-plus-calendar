from django.views.generic import TemplateView


class ScheduleView(TemplateView):
    template_name = "events/schedule.html"

    # def dispatch(self, request, *args, **kwargs):
    #     import ipdb; ipdb.set_trace()
    #     return super().dispatch(request, *args, **kwargs)
