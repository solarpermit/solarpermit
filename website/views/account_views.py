from django.views.generic import View
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView
from django.utils import timezone
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from website.models import API_Keys

class APIKeyListView(ListView):
    model = API_Keys

    def get_context_data(self, **kwargs):
        context = super(APIKeyListView, self).get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context

    def get_queryset(self):
        qs = self.model.objects.all()
        user = self.request.user
        if user.is_authenticated():
            if user.id:
                qs = qs.filter(user_id=user.id,enabled=True)
            qs = qs.order_by("key")
            return qs

class APIKeyCreateView(View):
    model = API_Keys
    success_url = '/profile/'
    
    def post(self, request, *args, **kwargs):
        user = request.user
        if user.is_authenticated() and user.id:
            self.model().createNew(user).save()
            return HttpResponseRedirect(self.success_url)
        else:
            return HttpResponse('Unauthorized', status=401)

class APIKeyRevokeView(UpdateView):
    model = API_Keys
    success_url = '/profile/'

    def post(self, request, *args, **kwargs):
        user = request.user
        self.object = self.get_object()
        if user.is_authenticated() and user.id and user.id == self.object.user_id:
            self.object.revoke().save()
            return HttpResponseRedirect(self.success_url)
        else:
            return HttpResponse('Unauthorized', status=401)

class APIKeyReplaceView(View):
    model = API_Keys
    success_url = '/profile/'
    
    def post(self, request, *args, **kwargs):
        user = request.user
        if user.is_authenticated() and user.id:
            key = self.kwargs.get('pk', None)
            self.object = self.model.objects.get(pk=key,user_id=user.id)
            self.object.revoke().save()
            self.model().createNew(user).save()
            return HttpResponseRedirect(self.success_url)
        else:
            return HttpResponse('Unauthorized', status=401)
