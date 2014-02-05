# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'UserDetail'
        db.create_table('website_userdetail', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('latitude', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=10, decimal_places=7, blank=True)),
            ('longitude', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=10, decimal_places=7, blank=True)),
        ))
        db.send_create_signal('website', ['UserDetail'])

        # Adding model 'Address'
        db.create_table('website_address', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('address1', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('address2', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('state', self.gf('django.db.models.fields.CharField')(max_length=8, null=True, blank=True)),
            ('zip_code', self.gf('django.db.models.fields.CharField')(max_length=32, null=True, blank=True)),
            ('latitude', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=10, decimal_places=7, blank=True)),
            ('longitude', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=10, decimal_places=7, blank=True)),
        ))
        db.send_create_signal('website', ['Address'])

        # Adding model 'Person'
        db.create_table('website_person', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('first_name', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=64, null=True, blank=True)),
            ('last_name', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=64, null=True, blank=True)),
            ('phone_primary', self.gf('django.contrib.localflavor.us.models.PhoneNumberField')(max_length=20, null=True, blank=True)),
            ('phone_secondary', self.gf('django.contrib.localflavor.us.models.PhoneNumberField')(max_length=20, null=True, blank=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75, null=True, blank=True)),
        ))
        db.send_create_signal('website', ['Person'])

        # Adding model 'PersonAddress'
        db.create_table('website_personaddress', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('person', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['website.Person'], null=True, blank=True)),
            ('address', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['website.Address'], null=True, blank=True)),
            ('address_type', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=8, null=True, blank=True)),
            ('display_order', self.gf('django.db.models.fields.PositiveSmallIntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal('website', ['PersonAddress'])

        # Adding model 'OrganizationCategory'
        db.create_table('website_organizationcategory', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=64, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('website', ['OrganizationCategory'])

        # Adding model 'Organization'
        db.create_table('website_organization', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=64, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['website.OrganizationCategory'], null=True, blank=True)),
            ('parent_org', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['website.Organization'], null=True, blank=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75, null=True, blank=True)),
            ('website', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
        ))
        db.send_create_signal('website', ['Organization'])

        # Adding model 'OrganizationAddress'
        db.create_table('website_organizationaddress', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('organization', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['website.Organization'], null=True, blank=True)),
            ('address', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['website.Address'], null=True, blank=True)),
            ('address_type', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=8, null=True, blank=True)),
            ('display_order', self.gf('django.db.models.fields.PositiveSmallIntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal('website', ['OrganizationAddress'])

        # Adding model 'RoleType'
        db.create_table('website_roletype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=64, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('website', ['RoleType'])

        # Adding model 'OrganizationMember'
        db.create_table('website_organizationmember', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('organization', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['website.Organization'], null=True, blank=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('person', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['website.Person'], null=True, blank=True)),
            ('role', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['website.RoleType'], null=True, blank=True)),
            ('display_order', self.gf('django.db.models.fields.PositiveSmallIntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal('website', ['OrganizationMember'])

        # Adding model 'Region'
        db.create_table('website_region', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=64, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('state', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=8, null=True, blank=True)),
        ))
        db.send_create_signal('website', ['Region'])

        # Adding model 'Jurisdiction'
        db.create_table('website_jurisdiction', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=64, null=True, blank=True)),
            ('organization', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['website.Organization'], null=True, blank=True)),
            ('city', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=64, null=True, blank=True)),
            ('region', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['website.Region'], null=True, blank=True)),
            ('county', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=64, null=True, blank=True)),
            ('state', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=8, null=True, blank=True)),
            ('latitude', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=10, decimal_places=7, blank=True)),
            ('longitude', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=10, decimal_places=7, blank=True)),
            ('create_datetime', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
            ('modify_datetime', self.gf('django.db.models.fields.DateTimeField')(db_index=True, null=True, blank=True)),
        ))
        db.send_create_signal('website', ['Jurisdiction'])

        # Adding model 'Application'
        db.create_table('website_application', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('jurisdiction', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['website.Jurisdiction'], null=True, blank=True)),
            ('applicant', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('address', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['website.Address'], null=True, blank=True)),
            ('current_status', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=8, null=True, blank=True)),
            ('status_datetime', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal('website', ['Application'])

        # Adding model 'ApplicationHistory'
        db.create_table('website_applicationhistory', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('application', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['website.Application'])),
            ('status', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=8, null=True, blank=True)),
            ('status_by', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('status_datetime', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
        ))
        db.send_create_signal('website', ['ApplicationHistory'])

        # Adding model 'DocumentCategory'
        db.create_table('website_documentcategory', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=64, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('website', ['DocumentCategory'])

        # Adding model 'Document'
        db.create_table('website_document', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=128, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('file_name', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=64, null=True, blank=True)),
            ('file_path', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
            ('region', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['website.Region'], null=True, blank=True)),
            ('jurisdiction', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['website.Jurisdiction'], null=True, blank=True)),
            ('reviewed', self.gf('django.db.models.fields.BooleanField')(default=False, db_index=True)),
            ('accepted', self.gf('django.db.models.fields.BooleanField')(default=False, db_index=True)),
            ('create_datetime', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
            ('modify_datetime', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal('website', ['Document'])

        # Adding model 'RequirementCategory'
        db.create_table('website_requirementcategory', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=128, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('reviewed', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('accepted', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('create_datetime', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
            ('modify_datetime', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal('website', ['RequirementCategory'])

        # Adding model 'Template'
        db.create_table('website_template', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=128, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['website.RequirementCategory'], null=True, blank=True)),
            ('template_type', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=8, null=True, blank=True)),
            ('region', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['website.Region'], null=True, blank=True)),
            ('jurisdiction', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['website.Jurisdiction'], null=True, blank=True)),
            ('reviewed', self.gf('django.db.models.fields.BooleanField')(default=False, db_index=True)),
            ('accepted', self.gf('django.db.models.fields.BooleanField')(default=False, db_index=True)),
            ('create_datetime', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
            ('modify_datetime', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal('website', ['Template'])

        # Adding model 'AnswerChoiceGroup'
        db.create_table('website_answerchoicegroup', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=128, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('website', ['AnswerChoiceGroup'])

        # Adding model 'AnswerChoice'
        db.create_table('website_answerchoice', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('answer_choice_group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['website.AnswerChoiceGroup'])),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=64, null=True, blank=True)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('display_order', self.gf('django.db.models.fields.PositiveSmallIntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal('website', ['AnswerChoice'])

        # Adding model 'Question'
        db.create_table('website_question', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('template', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['website.Template'])),
            ('title', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=128, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('form_type', self.gf('django.db.models.fields.CharField')(max_length=8, null=True, blank=True)),
            ('answer_choice_group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['website.AnswerChoiceGroup'], null=True, blank=True)),
            ('display_order', self.gf('django.db.models.fields.PositiveSmallIntegerField')(null=True, blank=True)),
            ('default_value', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('reviewed', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('accepted', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('create_datetime', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
            ('modify_datetime', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal('website', ['Question'])

        # Adding model 'AnswerReference'
        db.create_table('website_answerreference', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('template', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['website.Template'])),
            ('question', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['website.Question'])),
            ('value', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('file_upload', self.gf('django.db.models.fields.files.FileField')(max_length=100, null=True, blank=True)),
            ('reviewed', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('accepted', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('create_datetime', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
            ('modify_datetime', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal('website', ['AnswerReference'])

        # Adding model 'AnswerData'
        db.create_table('website_answerdata', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('application', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['website.Application'])),
            ('template', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['website.Template'])),
            ('question', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['website.Question'])),
            ('value', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('file_upload', self.gf('django.db.models.fields.files.FileField')(max_length=100, null=True, blank=True)),
            ('create_datetime', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
            ('modify_datetime', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal('website', ['AnswerData'])

        # Adding model 'RatingCategory'
        db.create_table('website_ratingcategory', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=64, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('rating_type', self.gf('django.db.models.fields.CharField')(max_length=8, null=True, blank=True)),
        ))
        db.send_create_signal('website', ['RatingCategory'])

        # Adding model 'RatingLevel'
        db.create_table('website_ratinglevel', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['website.RatingCategory'], null=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=64, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('rank', self.gf('django.db.models.fields.PositiveSmallIntegerField')(db_index=True, null=True, blank=True)),
        ))
        db.send_create_signal('website', ['RatingLevel'])

        # Adding model 'RewardCategory'
        db.create_table('website_rewardcategory', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=64, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('website', ['RewardCategory'])

        # Adding model 'ActionCategory'
        db.create_table('website_actioncategory', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=64, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('rating_category', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['website.RatingCategory'], null=True, blank=True)),
        ))
        db.send_create_signal('website', ['ActionCategory'])

        # Adding model 'Action'
        db.create_table('website_action', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['website.ActionCategory'], null=True, blank=True)),
            ('entity_id', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
            ('data', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('scale', self.gf('django.db.models.fields.IntegerField')(db_index=True, null=True, blank=True)),
            ('level', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['website.RatingLevel'], null=True, blank=True)),
            ('action_datetime', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
        ))
        db.send_create_signal('website', ['Action'])

        # Adding model 'ReactionCategory'
        db.create_table('website_reactioncategory', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=64, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('rating_category', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['website.RatingCategory'], null=True, blank=True)),
        ))
        db.send_create_signal('website', ['ReactionCategory'])

        # Adding model 'Reaction'
        db.create_table('website_reaction', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('action', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['website.Action'], null=True, blank=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['website.ReactionCategory'], null=True, blank=True)),
            ('data', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('scale', self.gf('django.db.models.fields.IntegerField')(db_index=True, null=True, blank=True)),
            ('level', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['website.RatingLevel'], null=True, blank=True)),
            ('reaction_datetime', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
        ))
        db.send_create_signal('website', ['Reaction'])

        # Adding model 'UserRating'
        db.create_table('website_userrating', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('scale', self.gf('django.db.models.fields.IntegerField')(db_index=True, null=True, blank=True)),
            ('level', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['website.RatingLevel'], null=True, blank=True)),
            ('updated_datetime', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal('website', ['UserRating'])

        # Adding model 'OrganizationRating'
        db.create_table('website_organizationrating', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('organization', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['website.Organization'], null=True, blank=True)),
            ('scale', self.gf('django.db.models.fields.IntegerField')(db_index=True, null=True, blank=True)),
            ('level', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['website.RatingLevel'], null=True, blank=True)),
            ('updated_datetime', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal('website', ['OrganizationRating'])

        # Adding model 'UserReward'
        db.create_table('website_userreward', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('reward', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['website.RewardCategory'], null=True, blank=True)),
            ('reward_datetime', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
        ))
        db.send_create_signal('website', ['UserReward'])


    def backwards(self, orm):
        
        # Deleting model 'UserDetail'
        db.delete_table('website_userdetail')

        # Deleting model 'Address'
        db.delete_table('website_address')

        # Deleting model 'Person'
        db.delete_table('website_person')

        # Deleting model 'PersonAddress'
        db.delete_table('website_personaddress')

        # Deleting model 'OrganizationCategory'
        db.delete_table('website_organizationcategory')

        # Deleting model 'Organization'
        db.delete_table('website_organization')

        # Deleting model 'OrganizationAddress'
        db.delete_table('website_organizationaddress')

        # Deleting model 'RoleType'
        db.delete_table('website_roletype')

        # Deleting model 'OrganizationMember'
        db.delete_table('website_organizationmember')

        # Deleting model 'Region'
        db.delete_table('website_region')

        # Deleting model 'Jurisdiction'
        db.delete_table('website_jurisdiction')

        # Deleting model 'Application'
        db.delete_table('website_application')

        # Deleting model 'ApplicationHistory'
        db.delete_table('website_applicationhistory')

        # Deleting model 'DocumentCategory'
        db.delete_table('website_documentcategory')

        # Deleting model 'Document'
        db.delete_table('website_document')

        # Deleting model 'RequirementCategory'
        db.delete_table('website_requirementcategory')

        # Deleting model 'Template'
        db.delete_table('website_template')

        # Deleting model 'AnswerChoiceGroup'
        db.delete_table('website_answerchoicegroup')

        # Deleting model 'AnswerChoice'
        db.delete_table('website_answerchoice')

        # Deleting model 'Question'
        db.delete_table('website_question')

        # Deleting model 'AnswerReference'
        db.delete_table('website_answerreference')

        # Deleting model 'AnswerData'
        db.delete_table('website_answerdata')

        # Deleting model 'RatingCategory'
        db.delete_table('website_ratingcategory')

        # Deleting model 'RatingLevel'
        db.delete_table('website_ratinglevel')

        # Deleting model 'RewardCategory'
        db.delete_table('website_rewardcategory')

        # Deleting model 'ActionCategory'
        db.delete_table('website_actioncategory')

        # Deleting model 'Action'
        db.delete_table('website_action')

        # Deleting model 'ReactionCategory'
        db.delete_table('website_reactioncategory')

        # Deleting model 'Reaction'
        db.delete_table('website_reaction')

        # Deleting model 'UserRating'
        db.delete_table('website_userrating')

        # Deleting model 'OrganizationRating'
        db.delete_table('website_organizationrating')

        # Deleting model 'UserReward'
        db.delete_table('website_userreward')


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
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['website.RatingLevel']", 'null': 'True', 'blank': 'True'}),
            'scale': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        'website.actioncategory': {
            'Meta': {'object_name': 'ActionCategory'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'rating_category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['website.RatingCategory']", 'null': 'True', 'blank': 'True'})
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
            'label': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        'website.answerchoicegroup': {
            'Meta': {'object_name': 'AnswerChoiceGroup'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '128', 'null': 'True', 'blank': 'True'})
        },
        'website.answerdata': {
            'Meta': {'object_name': 'AnswerData'},
            'application': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['website.Application']"}),
            'create_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'file_upload': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modify_datetime': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['website.Question']"}),
            'template': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['website.Template']"}),
            'value': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        'website.answerreference': {
            'Meta': {'object_name': 'AnswerReference'},
            'accepted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'create_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'file_upload': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modify_datetime': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['website.Question']"}),
            'reviewed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'template': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['website.Template']"}),
            'value': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        'website.application': {
            'Meta': {'object_name': 'Application'},
            'address': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['website.Address']", 'null': 'True', 'blank': 'True'}),
            'applicant': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'current_status': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '8', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'jurisdiction': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['website.Jurisdiction']", 'null': 'True', 'blank': 'True'}),
            'status_datetime': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'})
        },
        'website.applicationhistory': {
            'Meta': {'object_name': 'ApplicationHistory'},
            'application': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['website.Application']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '8', 'null': 'True', 'blank': 'True'}),
            'status_by': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'status_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'})
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
        'website.jurisdiction': {
            'Meta': {'object_name': 'Jurisdiction'},
            'city': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'county': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'create_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latitude': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '7', 'blank': 'True'}),
            'longitude': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '7', 'blank': 'True'}),
            'modify_datetime': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'organization': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['website.Organization']", 'null': 'True', 'blank': 'True'}),
            'region': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['website.Region']", 'null': 'True', 'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '8', 'null': 'True', 'blank': 'True'})
        },
        'website.organization': {
            'Meta': {'object_name': 'Organization'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['website.OrganizationCategory']", 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'parent_org': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['website.Organization']", 'null': 'True', 'blank': 'True'}),
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
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'organization': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['website.Organization']", 'null': 'True', 'blank': 'True'}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['website.Person']", 'null': 'True', 'blank': 'True'}),
            'role': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['website.RoleType']", 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        'website.organizationrating': {
            'Meta': {'object_name': 'OrganizationRating'},
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
            'create_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'default_value': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'display_order': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'form_type': ('django.db.models.fields.CharField', [], {'max_length': '8', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modify_datetime': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'reviewed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'template': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['website.Template']"}),
            'title': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '128', 'null': 'True', 'blank': 'True'})
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
            'level': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['website.RatingLevel']", 'null': 'True', 'blank': 'True'}),
            'reaction_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'scale': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        'website.reactioncategory': {
            'Meta': {'object_name': 'ReactionCategory'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'rating_category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['website.RatingCategory']", 'null': 'True', 'blank': 'True'})
        },
        'website.region': {
            'Meta': {'object_name': 'Region'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '8', 'null': 'True', 'blank': 'True'})
        },
        'website.requirementcategory': {
            'Meta': {'object_name': 'RequirementCategory'},
            'accepted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'create_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modify_datetime': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'reviewed': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
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
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['website.RequirementCategory']", 'null': 'True', 'blank': 'True'}),
            'create_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'jurisdiction': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['website.Jurisdiction']", 'null': 'True', 'blank': 'True'}),
            'modify_datetime': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'region': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['website.Region']", 'null': 'True', 'blank': 'True'}),
            'reviewed': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'template_type': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '8', 'null': 'True', 'blank': 'True'})
        },
        'website.userdetail': {
            'Meta': {'object_name': 'UserDetail'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latitude': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '7', 'blank': 'True'}),
            'longitude': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '7', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        'website.userrating': {
            'Meta': {'object_name': 'UserRating'},
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
        }
    }

    complete_apps = ['website']
