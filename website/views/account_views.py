from django.views.generic import View
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from website.models import API_Keys

class LoginRequiredMixin(object):
    @classmethod
    def as_view(cls):
        return login_required(super(LoginRequiredMixin, cls).as_view())

class APIKeyListView(LoginRequiredMixin, ListView):
    model = API_Keys

    def get_queryset(self):
        qs = self.model.objects.all()
        user = self.request.user
        qs = qs.filter(user_id=user.id,enabled=True)
        qs = qs.order_by("key")
        return qs

class APIKeyCreateView(LoginRequiredMixin, View):
    model = API_Keys
    success_url = '/profile/'
    
    def post(self, request, *args, **kwargs):
        user = request.user
        self.model().createNew(user).save()
        return HttpResponseRedirect(self.success_url)

class APIKeyRevokeView(LoginRequiredMixin, UpdateView):
    model = API_Keys
    success_url = '/profile/'

    def post(self, request, *args, **kwargs):
        user = request.user
        self.object = self.get_object()
        if user == self.object.user:
            self.object.revoke().save()
            return HttpResponseRedirect(self.success_url)
        else:
            return HttpResponse('Unauthorized', status=401)

class APIKeyReplaceView(LoginRequiredMixin, View):
    model = API_Keys
    success_url = '/profile/'
    
    def post(self, request, *args, **kwargs):
        user = request.user
        key = self.kwargs.get('pk', None)
        self.object = self.model.objects.get(pk=key)
        if user == self.object.user:
            self.object.revoke().save()
            self.model().createNew(user).save()
            return HttpResponseRedirect(self.success_url)
        else:
            return HttpResponse('Unauthorized', status=401)
