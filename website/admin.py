from django.contrib import admin
from website import models
from django.db.models import get_models, get_app

class AddressAdmin(admin.ModelAdmin):
    fields = ['address1', 'address2', 'city', 'state', 'zip_code']
    list_display = ['address1', 'address2', 'city', 'state', 'zip_code']
    list_filter = ['city', 'state', 'zip_code']
    search_fields = ['address1', 'address2', 'city', 'state', 'zip_code']
admin.site.register(models.Address, AddressAdmin)

class OrganizationCategoryAdmin(admin.ModelAdmin):
    fields = ['name', 'description']
    list_display = ['name', 'description']
admin.site.register(models.OrganizationCategory, OrganizationCategoryAdmin)

class OrganizationAdmin(admin.ModelAdmin):
    fields = ['name', 'description', 'category', 'parent_org', 'email', 'website', 'phone', 'fax', 'logo', 'logo_scaled']
    list_display = ['name', 'description', 'category', 'parent_org', 'email', 'website', 'phone']
    search_fields = ['name', 'description', 'email', 'website', 'phone']
admin.site.register(models.Organization, OrganizationAdmin)

class TemplateAdmin(admin.ModelAdmin):
    fields = ['name', 'description', 'template_type', 'jurisdiction', 'reviewed', 'accepted']
    list_display = ['name', 'description', 'template_type', 'jurisdiction', 'reviewed', 'accepted']
    list_filter = ['template_type', 'jurisdiction', 'reviewed', 'accepted']
    search_fields = ['name', 'description']
admin.site.register(models.Template, TemplateAdmin)

class AnswerChoiceInline(admin.TabularInline):
    model = models.AnswerChoice
    fields = ['display_order', 'label', 'value']
    list_display_links = ['label']
    ordering = ['display_order']

class AnswerChoiceInline(admin.TabularInline):
    model = models.AnswerChoice
    fields = ['display_order', 'label', 'value']
    list_display_links = ['label']
    ordering = ['display_order']

class AnswerChoiceGroupAdmin(admin.ModelAdmin):
    fields = ['name', 'description']
    list_display = ['name', 'description']
    search_fields =  ['name', 'description']
    inlines = [AnswerChoiceInline]
admin.site.register(models.AnswerChoiceGroup, AnswerChoiceGroupAdmin)

class AnswerChoiceAdmin(admin.ModelAdmin):
    fields = ['label', 'value', 'display_order']
    list_display = ['label', 'value', 'display_order']
    list_display_links = ['label']
    search_fields = ['label', 'value']
    ordering = ['label', 'display_order']
admin.site.register(models.AnswerChoice, AnswerChoiceAdmin)

class QuestionCategoryAdmin(admin.ModelAdmin):
    fields = ['display_order', 'name', 'description', 'reviewed', 'accepted']
    list_display = ['display_order', 'name', 'description', 'accepted']
    list_display_links = ['name']
    ordering = ['display_order']
admin.site.register(models.QuestionCategory, QuestionCategoryAdmin)

class QuestionAdmin(admin.ModelAdmin):
    list_display = ['category', 'display_order', 'label', 'form_type', 'template', 'display_template', 'accepted']
    list_display_links = ['label']
    list_filter = ['category', 'form_type', 'template', 'display_template', 'accepted']
    search_fields = ['label', 'question', 'instruction', 'terminology']
    ordering = ['category', 'display_order', 'label']
admin.site.register(models.Question, QuestionAdmin)

class AnswerReferenceAdmin(admin.ModelAdmin):
    list_display = ['jurisdiction', 'question', 'approval_status', 'creator', 'organization', 'value']
    list_display_links = ['value']
    list_filter = ['question', 'approval_status', 'creator', 'organization']
    search_fields = ['value', 'question', 'creator', 'organization']
    ordering = ['jurisdiction', 'question']
    date_heirarchy = ['create_datetime']
admin.site.register(models.AnswerReference, AnswerReferenceAdmin)

#class AnswerAttachmentAdmin(admin.ModelAdmin):
#    42
#admin.site.register(models.AnswerAttachment, AnswerAttachmentAdmin)

class CommentAdmin(admin.ModelAdmin):
    list_display = ['jurisdiction', 'user', 'comment_type', 'comment', 'rating', 'approval_status']
    list_display_links = ['comment']
    list_filter = ['user', 'comment_type', 'rating', 'rating_status', 'approval_status']
    search_fields = ['jurisdiction', 'user', 'comment']
admin.site.register(models.Comment, CommentAdmin)

class ActionCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'rating_category', 'points']
    list_filter = ['rating_category']
    search_fields = ['name', 'description']
admin.site.register(models.ActionCategory, ActionCategoryAdmin)

class ActionAdmin(admin.ModelAdmin):
    list_display = ['organization', 'user', 'category', 'jurisdiction', 'question_category', 'data']
    list_display_links = ['data']
    list_filter = ['question_category', 'category', 'organization', 'user']
    search_fields = ['organization', 'user', 'category', 'jurisdiction', 'question_category', 'data']
admin.site.register(models.Action, ActionAdmin)

class ReactionCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'rating_category', 'points']
    list_filter = ['rating_category']
    search_fields = ['name', 'description']
admin.site.register(models.ReactionCategory, ReactionCategoryAdmin)

class ReactionAdmin(admin.ModelAdmin):
    list_display = ['user', 'category', 'jurisdiction', 'question_category', 'data']
    list_display_links = ['data']
    list_filter = ['question_category', 'category', 'user']
    search_fields = ['organization', 'user', 'category', 'jurisdiction', 'question_category', 'data']
admin.site.register(models.Reaction, ReactionAdmin)

class UserRatingAdmin(admin.ModelAdmin):
    list_display = ['user', 'category', 'scale', 'level']
    list_filter = ['category', 'level', 'user']
    search_fields = ['user']
admin.site.register(models.UserRating, UserRatingAdmin)

class OrganizationRatingAdmin(admin.ModelAdmin):
    list_display = ['organization', 'category', 'scale', 'level']
    list_filter = ['category', 'level', 'organization']
    search_fields = ['user']
admin.site.register(models.OrganizationRating, OrganizationRatingAdmin)

class JurisdictionRatingAdmin(admin.ModelAdmin):
    list_display = ['jurisdiction', 'rating_type', 'rank', 'value']
    search_fields = ['jurisdiction']
admin.site.register(models.JurisdictionRating, JurisdictionRatingAdmin)

class ServerVariableAdmin(admin.ModelAdmin):
    list_display = ['name', 'value']
    search_fields = ['name', 'value']
admin.site.register(models.ServerVariable, ServerVariableAdmin)

class API_KeysAdmin(admin.ModelAdmin):
    list_display = ['user', 'key']
    search_fields = ['user']
admin.site.register(models.API_Keys, API_KeysAdmin)

class JurisdictionAdmin(admin.ModelAdmin):
    list_display = ['name', 'city', 'county', 'state']
    list_filter = ['jurisdiction_type', 'state']
    search_fields = ['name', 'city', 'county', 'state']
    ordering = ['name', 'city', 'county', 'state']
admin.site.register(models.Jurisdiction, JurisdictionAdmin)

class ZipcodeAdmin(admin.ModelAdmin):
    list_display = ['zip_code', 'city', 'county', 'state']
    list_filter = ['state']
    search_fields = ['zip_code', 'city', 'county', 'state']
    ordering = ['zip_code']
admin.site.register(models.Zipcode, ZipcodeAdmin)

class UserDetailAdmin(admin.ModelAdmin):
    list_display = ['user', 'notification_preference', 'display_preference', 'title']
    list_filter = ['notification_preference', 'display_preference', 'title']
    search_fields = ['user']
    ordering = ['user']
admin.site.register(models.UserDetail, UserDetailAdmin)

class NewsAdmin(admin.ModelAdmin):
    list_display = ['published', 'title']
    date_heirarchy = 'published'
admin.site.register(models.Article, NewsAdmin)
admin.site.register(models.Event, NewsAdmin)
admin.site.register(models.PressRelease, NewsAdmin)
