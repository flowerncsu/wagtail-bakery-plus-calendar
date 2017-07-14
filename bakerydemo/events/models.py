from django.db import models

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
    datetime = models.DateTimeField()

    content_panels = Page.content_panels + [
        FieldPanel('datetime', classname="full"),
        FieldPanel('introduction', classname="full"),
        ImageChooserPanel('image'),
        StreamFieldPanel('body'),
    ]
    search_fields = Page.search_fields + [
        index.SearchField('title'),
        index.SearchField('body'),
    ]
    parent_page_types = ['EventIndexPage']
