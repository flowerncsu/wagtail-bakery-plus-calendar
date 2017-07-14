import datetime

from django.db import models
from django.contrib.auth.models import User

from schedule.models.events import Event

from wagtail.wagtailcore.signals import page_published, page_unpublished
from wagtail.wagtailcore.models import Page
from wagtail.wagtailcore.fields import StreamField
from wagtail.wagtailadmin.edit_handlers import (
    FieldPanel, StreamFieldPanel
)
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel
from wagtail.wagtailsearch import index

from bakerydemo.base.blocks import BaseStreamBlock


class EventIndexPage(Page):
    introduction = models.TextField(
        help_text='Text to describe the page',
        blank=True)
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text='Landscape mode only; horizontal width between 1000px and 3000px.'
    )

    def get_events(self):
        """
        Return most recent live EventDetailPages that are direct descendants of EventIndexPage.
        """
        return EventDetailPage.objects.live().descendant_of(
            self).order_by('-first_published_at')

    def get_context(self, request):
        context = super(EventIndexPage, self).get_context(request)
        context['events'] = self.get_events()
        return context


class EventDetailPage(Page):
    introduction = models.TextField(
        help_text='Text to describe the event',
        blank=True
    )
    body = StreamField(
        BaseStreamBlock(), verbose_name="Event body", blank=True
    )
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text='Landscape mode only; horizontal width between 1000px and 3000px.'
    )
    event_time = models.DateTimeField()

    duration = models.DurationField(
        default=datetime.timedelta(hours=1)
    )

    creator = models.ForeignKey(
        User,
        null=True,
        blank=True,
    )

    content_panels = Page.content_panels + [
        FieldPanel('event_time', classname="full"),
        FieldPanel('introduction', classname="full"),
        ImageChooserPanel('image'),
        StreamFieldPanel('body'),
    ]
    search_fields = Page.search_fields + [
        index.SearchField('title'),
        index.SearchField('body'),
    ]
    parent_page_types = ['EventIndexPage']
    event_object = models.ForeignKey(
        'schedule.Event',
        null=True,
        blank=True,
    )


###########
# Signals #
###########

def create_or_update_event(sender, **kwargs):
    instance = kwargs['instance']

    if not instance.event_object:
        instance.event_object = Event()
        new_event = True
    else:
        new_event = False

    if not instance.creator:
        instance.event_object.creator = User.objects.get(username='admin')
    else:
        instance.event_object.creator = instance.creator

    instance.event_object.description = instance.introduction
    instance.event_object.start = instance.event_time
    instance.event_object.end = instance.event_time + instance.duration
    instance.event_object.title = instance.title
    instance.event_object.creator = instance.creator

    instance.event_object.save()
    if new_event:
        # Save the reference to the Event object; must happen after Event object is saved
        instance.save()


def delete_unused_event(sender, **kwargs):
    """
    When an event is unpublished, we can delete its event_object, since event_objects do not store any information
    besides that which is contained in the EventDetailPage object.
    """
    instance = kwargs['instance']
    if instance.event_object:
        instance.event_object.delete()

print('running signal code')
page_published.connect(create_or_update_event, sender=EventDetailPage)
page_unpublished.connect(delete_unused_event, sender=EventDetailPage)
