# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'ActionTutorial'
        db.delete_table('website_actiontutorial')

        # Deleting model 'Person'
        db.delete_table('website_person')

        # Deleting model 'UserReward'
        db.delete_table('website_userreward')

        # Deleting model 'ApplicationHistory'
        db.delete_table('website_applicationhistory')

        # Deleting model 'Document'
        db.delete_table('website_document')

        # Deleting model 'UserTutorialHistory'
        db.delete_table('website_usertutorialhistory')

        # Deleting model 'Tutorial'
        db.delete_table('website_tutorial')

        # Deleting model 'DocumentCategory'
        db.delete_table('website_documentcategory')

        # Deleting model 'QuestionDependency'
        db.delete_table('website_questiondependency')

        # Deleting model 'ApplicationAnswer'
        db.delete_table('website_applicationanswer')

        # Deleting model 'PersonAddress'
        db.delete_table('website_personaddress')

        # Deleting model 'Application'
        db.delete_table('website_application')

        # Deleting model 'Region'
        db.delete_table('website_region')

        # Deleting model 'UserTutorialPageHistory'
        db.delete_table('website_usertutorialpagehistory')

        # Deleting model 'TutorialPage'
        db.delete_table('website_tutorialpage')

        # Deleting field 'Jurisdiction.region'
        db.delete_column('website_jurisdiction', 'region_id')

        # Deleting field 'OrganizationAddress.address_type'
        db.delete_column('website_organizationaddress', 'address_type')

        # Deleting field 'OrganizationMember.person'
        db.delete_column('website_organizationmember', 'person_id')


    def backwards(self, orm):
        # Adding model 'ActionTutorial'
        db.create_table('website_actiontutorial', (
            ('create_datetime', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
            ('modify_datetime', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True)),
            ('action_identifier', self.gf('django.db.models.fields.CharField')(blank=True, max_length=64, null=True, db_index=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('tutorial', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['website.Tutorial'], null=True, blank=True)),
        ))
        db.send_create_signal('website', ['ActionTutorial'])

        # Adding model 'Person'
        db.create_table('website_person', (
            ('phone_primary', self.gf('django.contrib.localflavor.us.models.PhoneNumberField')(max_length=20, null=True, blank=True)),
            ('last_name', self.gf('django.db.models.fields.CharField')(blank=True, max_length=64, null=True, db_index=True)),
            ('create_datetime', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
            ('modify_datetime', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('first_name', self.gf('django.db.models.fields.CharField')(blank=True, max_length=64, null=True, db_index=True)),
            ('phone_secondary', self.gf('django.contrib.localflavor.us.models.PhoneNumberField')(max_length=20, null=True, blank=True)),
            ('phone_mobile', self.gf('django.contrib.localflavor.us.models.PhoneNumberField')(max_length=20, null=True, blank=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75, null=True, blank=True)),
        ))
        db.send_create_signal('website', ['Person'])

        # Adding model 'UserReward'
        db.create_table('website_userreward', (
            ('reward_datetime', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
            ('create_datetime', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
            ('modify_datetime', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('reward', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['website.RewardCategory'], null=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('website', ['UserReward'])

        # Adding model 'ApplicationHistory'
        db.create_table('website_applicationhistory', (
            ('status', self.gf('django.db.models.fields.CharField')(blank=True, max_length=8, null=True, db_index=True)),
            ('application', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['website.Application'])),
            ('status_datetime', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
            ('status_by', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('create_datetime', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('modify_datetime', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True)),
        ))
        db.send_create_signal('website', ['ApplicationHistory'])

        # Adding model 'Document'
        db.create_table('website_document', (
            ('create_datetime', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('file_name', self.gf('django.db.models.fields.CharField')(blank=True, max_length=64, null=True, db_index=True)),
            ('jurisdiction', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['website.Jurisdiction'], null=True, blank=True)),
            ('modify_datetime', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True)),
            ('reviewed', self.gf('django.db.models.fields.BooleanField')(default=False, db_index=True)),
            ('accepted', self.gf('django.db.models.fields.BooleanField')(default=False, db_index=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(blank=True, max_length=128, null=True, db_index=True)),
            ('region', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['website.Region'], null=True, blank=True)),
            ('file_path', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
        ))
        db.send_create_signal('website', ['Document'])

        # Adding model 'UserTutorialHistory'
        db.create_table('website_usertutorialhistory', (
            ('view_datetime', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('create_datetime', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
            ('modify_datetime', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True)),
            ('user_email', self.gf('django.db.models.fields.EmailField')(blank=True, max_length=75, null=True, db_index=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('tutorial', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['website.Tutorial'], null=True, blank=True)),
        ))
        db.send_create_signal('website', ['UserTutorialHistory'])

        # Adding model 'Tutorial'
        db.create_table('website_tutorial', (
            ('start_datetime', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('modify_datetime', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('identifier', self.gf('django.db.models.fields.CharField')(blank=True, max_length=64, null=True, db_index=True)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('name', self.gf('django.db.models.fields.CharField')(blank=True, max_length=128, null=True, db_index=True)),
            ('create_datetime', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('end_datetime', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal('website', ['Tutorial'])

        # Adding model 'DocumentCategory'
        db.create_table('website_documentcategory', (
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=64, null=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('website', ['DocumentCategory'])

        # Adding model 'QuestionDependency'
        db.create_table('website_questiondependency', (
            ('required', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('answer_text', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('question2', self.gf('django.db.models.fields.related.ForeignKey')(related_name='_questionDependency_question2', to=orm['website.Question'])),
            ('question1', self.gf('django.db.models.fields.related.ForeignKey')(related_name='_questionDependency_question1', to=orm['website.Question'])),
            ('strength', self.gf('django.db.models.fields.PositiveSmallIntegerField')(null=True, blank=True)),
            ('create_datetime', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('modify_datetime', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True)),
        ))
        db.send_create_signal('website', ['QuestionDependency'])

        # Adding model 'ApplicationAnswer'
        db.create_table('website_applicationanswer', (
            ('application', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['website.Application'])),
            ('template', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['website.Template'])),
            ('file_upload', self.gf('django.db.models.fields.files.FileField')(max_length=100, null=True, blank=True)),
            ('create_datetime', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
            ('question', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['website.Question'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('value', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('modify_datetime', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True)),
        ))
        db.send_create_signal('website', ['ApplicationAnswer'])

        # Adding model 'PersonAddress'
        db.create_table('website_personaddress', (
            ('person', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['website.Person'], null=True, blank=True)),
            ('address', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['website.Address'], null=True, blank=True)),
            ('display_order', self.gf('django.db.models.fields.PositiveSmallIntegerField')(null=True, blank=True)),
            ('address_type', self.gf('django.db.models.fields.CharField')(blank=True, max_length=8, null=True, db_index=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('create_datetime', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
            ('modify_datetime', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True)),
        ))
        db.send_create_signal('website', ['PersonAddress'])

        # Adding model 'Application'
        db.create_table('website_application', (
            ('jurisdiction', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['website.Jurisdiction'], null=True, blank=True)),
            ('template', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['website.Template'], null=True, blank=True)),
            ('address', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['website.Address'], null=True, blank=True)),
            ('applicant', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('current_status', self.gf('django.db.models.fields.CharField')(blank=True, max_length=8, null=True, db_index=True)),
            ('modify_datetime', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True)),
        ))
        db.send_create_signal('website', ['Application'])

        # Adding model 'Region'
        db.create_table('website_region', (
            ('state', self.gf('django.db.models.fields.CharField')(blank=True, max_length=8, null=True, db_index=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(blank=True, max_length=64, null=True, db_index=True)),
            ('latitude', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=10, decimal_places=7, blank=True)),
            ('create_datetime', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('longitude', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=10, decimal_places=7, blank=True)),
            ('modify_datetime', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True)),
        ))
        db.send_create_signal('website', ['Region'])

        # Adding model 'UserTutorialPageHistory'
        db.create_table('website_usertutorialpagehistory', (
            ('checked', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('tutorial', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['website.Tutorial'], null=True, blank=True)),
            ('user_email', self.gf('django.db.models.fields.EmailField')(blank=True, max_length=75, null=True, db_index=True)),
            ('create_datetime', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('page', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['website.TutorialPage'], null=True, blank=True)),
            ('modify_datetime', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True)),
        ))
        db.send_create_signal('website', ['UserTutorialPageHistory'])

        # Adding model 'TutorialPage'
        db.create_table('website_tutorialpage', (
            ('selector', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('display_order', self.gf('django.db.models.fields.SmallIntegerField')(default=0)),
            ('create_datetime', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
            ('tip', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('tutorial', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['website.Tutorial'], null=True, blank=True)),
            ('modify_datetime', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True)),
        ))
        db.send_create_signal('website', ['TutorialPage'])

        # Adding field 'Jurisdiction.region'
        db.add_column('website_jurisdiction', 'region',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['website.Region'], null=True, blank=True),
                      keep_default=False)

        # Adding field 'OrganizationAddress.address_type'
        db.add_column('website_organizationaddress', 'address_type',
                      self.gf('django.db.models.fields.CharField')(blank=True, max_length=8, null=True, db_index=True),
                      keep_default=False)

        # Adding field 'OrganizationMember.person'
        db.add_column('website_organizationmember', 'person',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['website.Person'], null=True, blank=True),
                      keep_default=False)


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
            'create_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'data': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'entity_id': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'entity_name': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'jurisdiction': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['website.Jurisdiction']", 'null': 'True', 'blank': 'True'}),
            'level': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['website.RatingLevel']", 'null': 'True', 'blank': 'True'}),
            'modify_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'organization': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['website.Organization']", 'null': 'True', 'blank': 'True'}),
            'question_category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['website.QuestionCategory']", 'null': 'True', 'blank': 'True'}),
            'scale': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        'website.actioncategory': {
            'Meta': {'object_name': 'ActionCategory'},
            'create_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modify_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'points': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'rating_category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['website.RatingCategory']", 'null': 'True', 'blank': 'True'})
        },
        'website.address': {
            'Meta': {'object_name': 'Address'},
            'address1': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'address2': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'create_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latitude': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '7', 'blank': 'True'}),
            'longitude': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '7', 'blank': 'True'}),
            'modify_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '8', 'null': 'True', 'blank': 'True'}),
            'zip_code': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'})
        },
        'website.answerchoice': {
            'Meta': {'object_name': 'AnswerChoice'},
            'answer_choice_group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['website.AnswerChoiceGroup']"}),
            'create_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'display_order': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'modify_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        'website.answerchoicegroup': {
            'Meta': {'object_name': 'AnswerChoiceGroup'},
            'create_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modify_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
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
            'modify_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'organization': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['website.Organization']", 'null': 'True', 'blank': 'True'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['website.Question']"}),
            'rating': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'rating_status': ('django.db.models.fields.CharField', [], {'default': "'U'", 'max_length': '8', 'db_index': 'True', 'blank': 'True'}),
            'status_datetime': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'value': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        'website.applicability': {
            'Meta': {'object_name': 'Applicability'},
            'accepted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'create_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modify_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'reviewed': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
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
            'jurisdiction': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['website.Jurisdiction']", 'null': 'True', 'blank': 'True'}),
            'modify_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'parent_comment': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'parent_reference'", 'null': 'True', 'to': "orm['website.Comment']"}),
            'rating': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'rating_status': ('django.db.models.fields.CharField', [], {'default': "'U'", 'max_length': '8', 'db_index': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        'website.entityview': {
            'Meta': {'object_name': 'EntityView'},
            'create_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'entity_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'entity_name': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latest_datetime': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'modify_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'session_key': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '40', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        'website.entityviewcount': {
            'Meta': {'object_name': 'EntityViewCount'},
            'count_30_days': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'create_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'entity_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'entity_name': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modify_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
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
            'last_contributed_by_org': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'_org_contributor'", 'null': 'True', 'to': "orm['website.Organization']"}),
            'latitude': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '7', 'blank': 'True'}),
            'longitude': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '7', 'blank': 'True'}),
            'modify_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'db_index': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'organization': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'_org_jurisdiction'", 'null': 'True', 'to': "orm['website.Organization']"}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'parent_jurisdiction'", 'null': 'True', 'to': "orm['website.Jurisdiction']"}),
            'state': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '8', 'null': 'True', 'blank': 'True'})
        },
        'website.jurisdictioncontributor': {
            'Meta': {'object_name': 'JurisdictionContributor'},
            'create_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'jurisdiction': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['website.Jurisdiction']", 'null': 'True', 'blank': 'True'}),
            'modify_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'organization': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['website.Organization']", 'null': 'True', 'blank': 'True'}),
            'points': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'question_category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['website.QuestionCategory']", 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        'website.migrationhistory': {
            'Meta': {'object_name': 'MigrationHistory'},
            'create_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'jurisdiction_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'modify_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'notes2': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'source_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'source_table': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'target_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'target_table': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '64', 'null': 'True', 'blank': 'True'})
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
            'modify_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
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
            'create_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'display_order': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modify_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
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
            'create_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'display_order': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invitation_key': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'invitor': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'_member_invitor'", 'null': 'True', 'to': "orm['auth.User']"}),
            'join_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'modify_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'organization': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['website.Organization']", 'null': 'True', 'blank': 'True'}),
            'requested_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'role': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['website.RoleType']", 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'P'", 'max_length': '8', 'null': 'True', 'db_index': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'_member_user'", 'null': 'True', 'to': "orm['auth.User']"})
        },
        'website.organizationrating': {
            'Meta': {'object_name': 'OrganizationRating'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['website.RatingCategory']", 'null': 'True', 'blank': 'True'}),
            'create_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['website.RatingLevel']", 'null': 'True', 'blank': 'True'}),
            'modify_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'organization': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['website.Organization']", 'null': 'True', 'blank': 'True'}),
            'scale': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'updated_datetime': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'})
        },
        'website.question': {
            'Meta': {'object_name': 'Question'},
            'accepted': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'answer_choice_group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['website.AnswerChoiceGroup']", 'null': 'True', 'blank': 'True'}),
            'applicability': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['website.Applicability']", 'null': 'True', 'blank': 'True'}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['website.QuestionCategory']", 'null': 'True', 'blank': 'True'}),
            'create_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'default_value': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'display_order': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'display_template': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'field_attributes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'field_suffix': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'form_type': ('django.db.models.fields.CharField', [], {'max_length': '8', 'null': 'True', 'blank': 'True'}),
            'has_multivalues': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'instruction': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'js': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'label': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'migration_type': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'modify_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'qtemplate': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['website.Template']", 'null': 'True'}),
            'question': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'reviewed': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'state_exclusive': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'template': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'terminology': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'validation_class': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        'website.questioncategory': {
            'Meta': {'object_name': 'QuestionCategory'},
            'accepted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'create_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'display_order': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modify_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'reviewed': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'website.ratingcategory': {
            'Meta': {'object_name': 'RatingCategory'},
            'create_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modify_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'rating_type': ('django.db.models.fields.CharField', [], {'max_length': '8', 'null': 'True', 'blank': 'True'})
        },
        'website.ratinglevel': {
            'Meta': {'object_name': 'RatingLevel'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['website.RatingCategory']", 'null': 'True', 'blank': 'True'}),
            'create_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modify_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'rank': ('django.db.models.fields.PositiveSmallIntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'})
        },
        'website.reaction': {
            'Meta': {'object_name': 'Reaction'},
            'action': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['website.Action']", 'null': 'True', 'blank': 'True'}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['website.ReactionCategory']", 'null': 'True', 'blank': 'True'}),
            'create_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'data': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'jurisdiction': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['website.Jurisdiction']", 'null': 'True', 'blank': 'True'}),
            'level': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['website.RatingLevel']", 'null': 'True', 'blank': 'True'}),
            'modify_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'question_category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['website.QuestionCategory']", 'null': 'True', 'blank': 'True'}),
            'reaction_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'scale': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        'website.reactioncategory': {
            'Meta': {'object_name': 'ReactionCategory'},
            'create_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modify_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'points': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'rating_category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['website.RatingCategory']", 'null': 'True', 'blank': 'True'})
        },
        'website.rewardcategory': {
            'Meta': {'object_name': 'RewardCategory'},
            'create_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modify_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '64', 'null': 'True', 'blank': 'True'})
        },
        'website.roletype': {
            'Meta': {'object_name': 'RoleType'},
            'create_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modify_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'})
        },
        'website.servervariable': {
            'Meta': {'object_name': 'ServerVariable'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'value': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        'website.template': {
            'Meta': {'object_name': 'Template'},
            'accepted': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'create_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'jurisdiction': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['website.Jurisdiction']", 'null': 'True', 'blank': 'True'}),
            'modify_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'reviewed': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'template_type': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '8', 'db_index': 'True', 'blank': 'True'})
        },
        'website.templatequestion': {
            'Meta': {'object_name': 'TemplateQuestion'},
            'create_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modify_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['website.Question']"}),
            'template': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['website.Template']"})
        },
        'website.usercommentview': {
            'Meta': {'object_name': 'UserCommentView'},
            'comments_count': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'create_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'entity_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'entity_name': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'jurisdiction': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['website.Jurisdiction']", 'null': 'True', 'blank': 'True'}),
            'last_comment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['website.Comment']", 'null': 'True', 'blank': 'True'}),
            'modify_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'view_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'})
        },
        'website.userdetail': {
            'Meta': {'object_name': 'UserDetail'},
            'create_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'display_preference': ('django.db.models.fields.CharField', [], {'max_length': '16', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latitude': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '7', 'blank': 'True'}),
            'longitude': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '7', 'blank': 'True'}),
            'migrated_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'modify_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'notification_preference': ('django.db.models.fields.CharField', [], {'max_length': '2', 'null': 'True', 'blank': 'True'}),
            'old_password': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'reset_password_key': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '124', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        'website.userfavorite': {
            'Meta': {'object_name': 'UserFavorite'},
            'create_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'display_order': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'entity_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'entity_name': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modify_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        'website.userpageview': {
            'Meta': {'object_name': 'UserPageView'},
            'create_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_page_view_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'modify_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        'website.userrating': {
            'Meta': {'object_name': 'UserRating'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['website.RatingCategory']", 'null': 'True', 'blank': 'True'}),
            'create_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['website.RatingLevel']", 'null': 'True', 'blank': 'True'}),
            'modify_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'scale': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'updated_datetime': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        'website.usersearch': {
            'Meta': {'object_name': 'UserSearch'},
            'create_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'entity_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'entity_name': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'modify_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'search_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        'website.view': {
            'Meta': {'object_name': 'View'},
            'accepted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'create_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'jurisdiction': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['website.Jurisdiction']", 'null': 'True', 'blank': 'True'}),
            'modify_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'reviewed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'view_type': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '8', 'db_index': 'True', 'blank': 'True'})
        },
        'website.vieworgs': {
            'Meta': {'object_name': 'ViewOrgs'},
            'create_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modify_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'organization': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['website.Organization']"}),
            'view': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['website.View']"})
        },
        'website.viewquestions': {
            'Meta': {'object_name': 'ViewQuestions'},
            'create_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'display_order': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modify_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['website.Question']"}),
            'view': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['website.View']"})
        },
        'website.zipcode': {
            'Meta': {'object_name': 'Zipcode'},
            'city': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'county': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'create_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latitude': ('django.db.models.fields.DecimalField', [], {'db_index': 'True', 'null': 'True', 'max_digits': '10', 'decimal_places': '7', 'blank': 'True'}),
            'longitude': ('django.db.models.fields.DecimalField', [], {'db_index': 'True', 'null': 'True', 'max_digits': '10', 'decimal_places': '7', 'blank': 'True'}),
            'modify_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '2', 'null': 'True', 'blank': 'True'}),
            'zip_code': ('django.db.models.fields.CharField', [], {'max_length': '10', 'db_index': 'True'})
        }
    }

    complete_apps = ['website']