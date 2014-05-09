from django.views.generic import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.decorators import permission_required, user_passes_test
from django.utils.decorators import method_decorator
from website.models import PressRelease, Article, Event

def user_is_staff(user):
    return user.is_staff

class PressReleaseList(ListView):
    model = PressRelease
    @method_decorator(user_passes_test(user_is_staff))
    def dispatch(self, *args, **kwargs):
        return super(PressReleaseCreate, self).dispatch(*args, **kwargs)
class PressReleaseCreate(CreateView):
    model = PressRelease
    fields = ("published", "url", "title")
    success_url = reverse_lazy('pressrelease_list')
    @method_decorator(permission_required('website.add_pressrelease'))
    def dispatch(self, *args, **kwargs):
        return super(PressReleaseCreate, self).dispatch(*args, **kwargs)
class PressReleaseUpdate(UpdateView):
    model = PressRelease
    fields = ("published", "url", "title")
    success_url = reverse_lazy('pressrelease_list')
    @method_decorator(permission_required('website.change_pressrelease'))
    def dispatch(self, *args, **kwargs):
        return super(PressReleaseUpdate, self).dispatch(*args, **kwargs)
class PressReleaseDelete(DeleteView):
    model = PressRelease
    success_url = reverse_lazy('pressrelease_list')
    @method_decorator(permission_required('website.delete_pressrelease'))
    def dispatch(self, *args, **kwargs):
        return super(PressReleaseDelete, self).dispatch(*args, **kwargs)

class ArticleList(ListView):
    model = Article
class ArticleCreate(CreateView):
    model = Article
    fields = ("published", "url", "title", "publisher")
    success_url = reverse_lazy('article_list')
    @method_decorator(permission_required('website.add_article'))
    def dispatch(self, *args, **kwargs):
        return super(ArticleCreate, self).dispatch(*args, **kwargs)
class ArticleUpdate(UpdateView):
    model = Article
    fields = ("published", "url", "title", "publisher")
    success_url = reverse_lazy('article_list')
    @method_decorator(permission_required('website.add_article'))
    def dispatch(self, *args, **kwargs):
        return super(ArticleUpdate, self).dispatch(*args, **kwargs)
class ArticleDelete(DeleteView):
    model = Article
    success_url = reverse_lazy('article_list')
    @method_decorator(permission_required('website.add_article'))
    def dispatch(self, *args, **kwargs):
        return super(ArticleDelete, self).dispatch(*args, **kwargs)

class EventList(ListView):
    model = Event
class EventCreate(CreateView):
    model = Event
    fields = ("published", "url", "title", "start", "end", "expiration", "location")
    success_url = reverse_lazy('event_list')
    @method_decorator(permission_required('website.add_event'))
    def dispatch(self, *args, **kwargs):
        return super(EventCreate, self).dispatch(*args, **kwargs)
class EventUpdate(UpdateView):
    model = Event
    fields = ("published", "url", "title", "start", "end", "expiration", "location")
    success_url = reverse_lazy('event_list')
    @method_decorator(permission_required('website.add_event'))
    def dispatch(self, *args, **kwargs):
        return super(EventUpdate, self).dispatch(*args, **kwargs)
class EventDelete(DeleteView):
    model = Event
    success_url = reverse_lazy('event_list')
    @method_decorator(permission_required('website.add_event'))
    def dispatch(self, *args, **kwargs):
        return super(EventDelete, self).dispatch(*args, **kwargs)

