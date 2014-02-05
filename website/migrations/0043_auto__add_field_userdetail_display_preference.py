# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'UserDetail.display_preference'
        db.add_column('website_userdetail', 'display_preference',
                      self.gf('django.db.models.fields.CharField')(max_length=16, null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'UserDetail.display_preference'
        db.delete_column('website_userdetail', 'display_preference')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'website.action': {
            'Meta': {'object_name': 'Action'},
            'action_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['website.ActionCategory']", 'null': 'True', 'blank': 'True'}),
            'data': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'entity_id': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'entity_name': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'jurisdiction': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['website.Jurisdiction']", 'null': 'True', 'blank': 'True'}),
            'level': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['website.RatingLevel']", 'null': 'True', 'blank': 'True'}),
            'question_category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['website.QuestionCategory']", 'null': 'True', 'blank': 'True'}),
            'scale': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        'website.actioncategory': {
            'Meta': {'object_name': 'ActionCategory'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'points': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'rating_category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['website.RatingCategory']", 'null': 'True', 'blank': 'True'})
        },
        'website.actiontutorial': {
            'Meta': {'object_name': 'ActionTutorial'},
            'action_identifier': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'tutorial': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['website.Tutorial']", 'null': 'True', 'blank': 'True'})
        },
        'website.address': {
            'Meta': {'object_name': 'Address'},
            'address1': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'address2': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latitude': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '7', 'blank': 'True'}),
            'longitude': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '7', 'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '8', 'null': 'True', 'blank': 'True'}),
            'zip_code': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'})
        },
        'website.answerchoice': {
            'Meta': {'object_name': 'AnswerChoice'},
            'answer_choice_group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['website.AnswerChoiceGroup']"}),
            'display_order': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        'website.answerchoicegroup': {
            'Meta': {'object_name': 'AnswerChoiceGroup'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '128', 'null': 'True', 'blank': 'True'})
        },
        'website.answerreference': {
            'Meta': {'object_name': 'AnswerReference'},
            'approval_status': ('django.db.models.fields.CharField', [], {'default': "'P'", 'max_length': '8', 'db_index': 'True', 'blank': 'True'}),
            'create_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'file_upload': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_callout': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_current': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True'}),
            'jurisdiction': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['website.Jurisdiction']", 'null': 'True', 'blank': 'True'}),
            'migrated_answer_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'modify_datetime': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['website.Question']"}),
            'rating': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'rating_status': ('django.db.models.fields.CharField', [], {'default': "'U'", 'max_length': '8', 'db_index': 'True', 'blank': 'True'}),
            'value': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        'website.applicability': {
            'Meta': {'object_name': 'Applicability'},
            'accepted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'create_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modify_datetime': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'reviewed': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'website.application': {
            'Meta': {'object_name': 'Application'},
            'address': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['website.Address']", 'null': 'True', 'blank': 'True'}),
            'applicant': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'current_status': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '8', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'jurisdiction': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['website.Jurisdiction']", 'null': 'True', 'blank': 'True'}),
            'status_datetime': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'template': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['website.Template']", 'null': 'True', 'blank': 'True'})
        },
        'website.applicationanswer': {
            'Meta': {'object_name': 'ApplicationAnswer'},
            'application': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['website.Application']"}),
            'create_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'file_upload': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modify_datetime': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['website.Question']"}),
            'template': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['website.Template']"}),
            'value': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        'website.applicationhistory': {
            'Meta': {'object_name': 'ApplicationHistory'},
            'application': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['website.Application']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '8', 'null': 'True', 'blank': 'True'}),
            'status_by': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'status_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'})
        },
        'website.comment': {
            'Meta': {'object_name': 'Comment'},
            'approval_status': ('django.db.models.fields.CharField', [], {'default': "'P'", 'max_length': '8', 'db_index': 'True', 'blank': 'True'}),
            'comment': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'comment_type': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '8', 'db_index': 'True', 'blank': 'True'}),
            'create_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'entity_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'entity_name': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'rating': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'rating_status': ('django.db.models.fields.CharField', [], {'default': "'U'", 'max_length': '8', 'db_index': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        'website.document': {
            'Meta': {'object_name': 'Document'},
            'accepted': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'create_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'file_name': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'file_path': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'jurisdiction': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['website.Jurisdiction']", 'null': 'True', 'blank': 'True'}),
            'modify_datetime': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'region': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['website.Region']", 'null': 'True', 'blank': 'True'}),
            'reviewed': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '128', 'null': 'True', 'blank': 'True'})
        },
        'website.documentcategory': {
            'Meta': {'object_name': 'DocumentCategory'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'})
        },
        'website.entityview': {
            'Meta': {'object_name': 'EntityView'},
            'entity_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'entity_name': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latest_datetime': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'session_key': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '40', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        'website.entityviewcount': {
            'Meta': {'object_name': 'EntityViewCount'},
            'count_30_days': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'entity_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'entity_name': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'total_count': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'})
        },
        'website.jurisdiction': {
            'Meta': {'object_name': 'Jurisdiction'},
            'city': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'county': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'create_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'jurisdiction_type': ('django.db.models.fields.CharField', [], {'max_length': '8', 'null': 'True', 'blank': 'True'}),
            'last_contributed': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'last_contributed_by': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'latitude': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '7', 'blank': 'True'}),
            'longitude': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '7', 'blank': 'True'}),
            'modify_datetime': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'organization': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['website.Organization']", 'null': 'True', 'blank': 'True'}),
            'region': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['website.Region']", 'null': 'True', 'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '8', 'null': 'True', 'blank': 'True'})
        },
        'website.jurisdictioncontributor': {
            'Meta': {'object_name': 'JurisdictionContributor'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'jurisdiction': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['website.Jurisdiction']", 'null': 'True', 'blank': 'True'}),
            'organization': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['website.Organization']", 'null': 'True', 'blank': 'True'}),
            'points': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'question_category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['website.QuestionCategory']", 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        'website.organization': {
            'Meta': {'object_name': 'Organization'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['website.OrganizationCategory']", 'null': 'True', 'blank': 'True'}),
            'create_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'fax': ('django.contrib.localflavor.us.models.PhoneNumberField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'logo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'logo_scaled': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'parent_org': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['website.Organization']", 'null': 'True', 'blank': 'True'}),
            'phone': ('django.contrib.localflavor.us.models.PhoneNumberField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'A'", 'max_length': '8', 'null': 'True', 'db_index': 'True', 'blank': 'True'}),
            'status_datetime': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'website': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        'website.organizationaddress': {
            'Meta': {'object_name': 'OrganizationAddress'},
            'address': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['website.Address']", 'null': 'True', 'blank': 'True'}),
            'address_type': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '8', 'null': 'True', 'blank': 'True'}),
            'display_order': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'organization': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['website.Organization']", 'null': 'True', 'blank': 'True'})
        },
        'website.organizationcategory': {
            'Meta': {'object_name': 'OrganizationCategory'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'})
        },
        'website.organizationmember': {
            'Meta': {'object_name': 'OrganizationMember'},
            'display_order': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invitation_key': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'invitor': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'_member_invitor'", 'null': 'True', 'to': "orm['auth.User']"}),
            'join_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'organization': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['website.Organization']", 'null': 'True', 'blank': 'True'}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['website.Person']", 'null': 'True', 'blank': 'True'}),
            'requested_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'role': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['website.RoleType']", 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'P'", 'max_length': '8', 'null': 'True', 'db_index': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'_member_user'", 'null': 'True', 'to': "orm['auth.User']"})
        },
        'website.organizationrating': {
            'Meta': {'object_name': 'OrganizationRating'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['website.RatingCategory']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['website.RatingLevel']", 'null': 'True', 'blank': 'True'}),
            'organization': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['website.Organization']", 'null': 'True', 'blank': 'True'}),
            'scale': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'updated_datetime': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'})
        },
        'website.person': {
            'Meta': {'object_name': 'Person'},
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'phone_mobile': ('django.contrib.localflavor.us.models.PhoneNumberField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'phone_primary': ('django.contrib.localflavor.us.models.PhoneNumberField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'phone_secondary': ('django.contrib.localflavor.us.models.PhoneNumberField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        'website.personaddress': {
            'Meta': {'object_name': 'PersonAddress'},
            'address': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['website.Address']", 'null': 'True', 'blank': 'True'}),
            'address_type': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '8', 'null': 'True', 'blank': 'True'}),
            'display_order': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['website.Person']", 'null': 'True', 'blank': 'True'})
        },
        'website.question': {
            'Meta': {'object_name': 'Question'},
            'accepted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'answer_choice_group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['website.AnswerChoiceGroup']", 'null': 'True', 'blank': 'True'}),
            'applicability': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['website.Applicability']", 'null': 'True', 'blank': 'True'}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['website.QuestionCategory']", 'null': 'True', 'blank': 'True'}),
            'create_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'default_value': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'display_order': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'form_type': ('django.db.models.fields.CharField', [], {'max_length': '8', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'instruction': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'label': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'modify_datetime': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'question': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'reviewed': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'website.questioncategory': {
            'Meta': {'object_name': 'QuestionCategory'},
            'accepted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'create_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'display_order': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modify_datetime': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'reviewed': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'website.questiondependency': {
            'Meta': {'object_name': 'QuestionDependency'},
            'answer_text': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'create_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modify_datetime': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'question1': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'_questionDependency_question1'", 'to': "orm['website.Question']"}),
            'question2': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'_questionDependency_question2'", 'to': "orm['website.Question']"}),
            'required': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'strength': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        'website.ratingcategory': {
            'Meta': {'object_name': 'RatingCategory'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'rating_type': ('django.db.models.fields.CharField', [], {'max_length': '8', 'null': 'True', 'blank': 'True'})
        },
        'website.ratinglevel': {
            'Meta': {'object_name': 'RatingLevel'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['website.RatingCategory']", 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'rank': ('django.db.models.fields.PositiveSmallIntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'})
        },
        'website.reaction': {
            'Meta': {'object_name': 'Reaction'},
            'action': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['website.Action']", 'null': 'True', 'blank': 'True'}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['website.ReactionCategory']", 'null': 'True', 'blank': 'True'}),
            'data': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'jurisdiction': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['website.Jurisdiction']", 'null': 'True', 'blank': 'True'}),
            'level': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['website.RatingLevel']", 'null': 'True', 'blank': 'True'}),
            'question_category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['website.QuestionCategory']", 'null': 'True', 'blank': 'True'}),
            'reaction_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'scale': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        'website.reactioncategory': {
            'Meta': {'object_name': 'ReactionCategory'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'points': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'rating_category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['website.RatingCategory']", 'null': 'True', 'blank': 'True'})
        },
        'website.region': {
            'Meta': {'object_name': 'Region'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latitude': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '7', 'blank': 'True'}),
            'longitude': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '7', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '8', 'null': 'True', 'blank': 'True'})
        },
        'website.rewardcategory': {
            'Meta': {'object_name': 'RewardCategory'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '64', 'null': 'True', 'blank': 'True'})
        },
        'website.roletype': {
            'Meta': {'object_name': 'RoleType'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'})
        },
        'website.template': {
            'Meta': {'object_name': 'Template'},
            'accepted': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'create_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'jurisdiction': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['website.Jurisdiction']", 'null': 'True', 'blank': 'True'}),
            'modify_datetime': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'reviewed': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'template_type': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '8', 'db_index': 'True', 'blank': 'True'})
        },
        'website.templatequestion': {
            'Meta': {'object_name': 'TemplateQuestion'},
            'create_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['website.Question']"}),
            'template': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['website.Template']"})
        },
        'website.tutorial': {
            'Meta': {'object_name': 'Tutorial'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'end_datetime': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'identifier': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'start_datetime': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'})
        },
        'website.tutorialpage': {
            'Meta': {'object_name': 'TutorialPage'},
            'display_order': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'selector': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'tip': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'tutorial': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['website.Tutorial']", 'null': 'True', 'blank': 'True'})
        },
        'website.userdetail': {
            'Meta': {'object_name': 'UserDetail'},
            'display_preference': ('django.db.models.fields.CharField', [], {'max_length': '16', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latitude': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '7', 'blank': 'True'}),
            'longitude': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '7', 'blank': 'True'}),
            'notification_preference': ('django.db.models.fields.CharField', [], {'max_length': '2', 'null': 'True', 'blank': 'True'}),
            'old_password': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'reset_password_key': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        'website.userfavorite': {
            'Meta': {'object_name': 'UserFavorite'},
            'display_order': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'entity_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'entity_name': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        'website.userrating': {
            'Meta': {'object_name': 'UserRating'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['website.RatingCategory']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['website.RatingLevel']", 'null': 'True', 'blank': 'True'}),
            'scale': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'updated_datetime': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        'website.userreward': {
            'Meta': {'object_name': 'UserReward'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reward': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['website.RewardCategory']", 'null': 'True', 'blank': 'True'}),
            'reward_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        'website.usersearch': {
            'Meta': {'object_name': 'UserSearch'},
            'entity_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'entity_name': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'search_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        'website.usertutorialhistory': {
            'Meta': {'object_name': 'UserTutorialHistory'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'tutorial': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['website.Tutorial']", 'null': 'True', 'blank': 'True'}),
            'user_email': ('django.db.models.fields.EmailField', [], {'db_index': 'True', 'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'view_datetime': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'})
        },
        'website.usertutorialpagehistory': {
            'Meta': {'object_name': 'UserTutorialPageHistory'},
            'checked': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'page': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['website.TutorialPage']", 'null': 'True', 'blank': 'True'}),
            'tutorial': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['website.Tutorial']", 'null': 'True', 'blank': 'True'}),
            'user_email': ('django.db.models.fields.EmailField', [], {'db_index': 'True', 'max_length': '75', 'null': 'True', 'blank': 'True'})
        },
        'website.zipcode': {
            'Meta': {'object_name': 'Zipcode'},
            'city': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'county': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latitude': ('django.db.models.fields.DecimalField', [], {'db_index': 'True', 'null': 'True', 'max_digits': '10', 'decimal_places': '7', 'blank': 'True'}),
            'longitude': ('django.db.models.fields.DecimalField', [], {'db_index': 'True', 'null': 'True', 'max_digits': '10', 'decimal_places': '7', 'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '2', 'null': 'True', 'blank': 'True'}),
            'zip_code': ('django.db.models.fields.CharField', [], {'max_length': '10', 'db_index': 'True'})
        }
    }

    complete_apps = ['website']