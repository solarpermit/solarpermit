from django.contrib import admin
from website.models import *

class JurisdictionAdmin(admin.ModelAdmin):
    fields = ['name', 'jurisdiction_type', 'city', 'county', 'state', 'latitude', 'longitude']
    list_display = ['name', 'city', 'county', 'state']
    list_filter = ['jurisdiction_type']
    search_fields = ['name', 'city', 'county', 'state']
    ordering = ['name', 'city', 'county', 'state']

admin.site.register(Jurisdiction, JurisdictionAdmin)

class ZipcodeAdmin(admin.ModelAdmin):
    fields = ['zip_code', 'city', 'county', 'state', 'latitude', 'longitude']
    list_display = ['zip_code', 'city', 'county', 'state']
    list_filter = []
    search_fields = ['zip_code', 'city', 'county', 'state']
    ordering = ['zip_code']

admin.site.register(Zipcode, ZipcodeAdmin)

class UserDetailAdmin(admin.ModelAdmin):
    fields = ['user', 'notification_preference', 'display_preference', 'title']
    list_display = ['user', 'notification_preference', 'display_preference', 'title']
    list_filter = []
    search_fields = ['user']
    ordering = ['user']

admin.site.register(UserDetail, UserDetailAdmin)

class NewsAdmin(admin.ModelAdmin):
    list_display = ['published', 'title']
    date_heirarchy = 'published'

admin.site.register(PressRelease, NewsAdmin)
admin.site.register(Article, NewsAdmin)
admin.site.register(Event, NewsAdmin)
