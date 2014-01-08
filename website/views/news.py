from django.views.generic import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy
from website.models import PressRelease, Article, Event

class PressReleaseList(ListView):
    model = PressRelease
class PressReleaseCreate(CreateView):
    model = PressRelease
    fields = ("published", "url", "title")
    success_url = reverse_lazy('pressrelease_list')
class PressReleaseUpdate(UpdateView):
    model = PressRelease
    fields = ("published", "url", "title")
    success_url = reverse_lazy('pressrelease_list')
class PressReleaseDelete(DeleteView):
    model = PressRelease
    success_url = reverse_lazy('pressrelease_list')

class ArticleList(ListView):
    model = Article
class ArticleCreate(CreateView):
    model = Article
    fields = ("published", "url", "title", "publisher")
    success_url = reverse_lazy('article_list')
class ArticleUpdate(UpdateView):
    model = Article
    fields = ("published", "url", "title", "publisher")
    success_url = reverse_lazy('article_list')
class ArticleDelete(DeleteView):
    model = Article
    success_url = reverse_lazy('article_list')

class EventList(ListView):
    model = Event
class EventCreate(CreateView):
    model = Event
    fields = ("published", "url", "title", "start", "end", "expiration", "location")
    success_url = reverse_lazy('event_list')
class EventUpdate(UpdateView):
    model = Event
    fields = ("published", "url", "title", "start", "end", "expiration", "location")
    success_url = reverse_lazy('event_list')
class EventDelete(DeleteView):
    model = Event
    success_url = reverse_lazy('event_list')

