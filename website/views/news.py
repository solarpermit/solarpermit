from django.views.generic import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy
from website.models import PressRelease, Article, Event

class PressReleaseList(ListView):
    model = PressRelease
class PressReleaseCreate(CreateView):
    model = PressRelease
class PressReleaseUpdate(UpdateView):
    model = PressRelease
class PressReleaseDelete(DeleteView):
    model = PressRelease

class ArticleList(ListView):
    model = Article
class ArticleCreate(CreateView):
    model = Article
class ArticleUpdate(UpdateView):
    model = Article
class ArticleDelete(DeleteView):
    model = Article

class EventList(ListView):
    model = Event
class EventCreate(CreateView):
    model = Event
class EventUpdate(UpdateView):
    model = Event
class EventDelete(DeleteView):
    model = Event
