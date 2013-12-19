import datetime
from django.db import models
from django.conf import settings

#server variables that needed to be stored in db
class ServerVariable(models.Model):
    name = models.CharField(max_length=64, blank=True, null=True)
    value = models.TextField(blank=True, null=True)
    
    class Meta:
            app_label = 'website'
    
    @staticmethod
    def get(name):
        try:
            server_variable = ServerVariable.objects.get(name=name)
        except:
            return None
        return server_variable.value

    @staticmethod
    def set(name, value):
        try:
            server_variable = ServerVariable.objects.get(name=name)
        except:
            server_variable = ServerVariable(name=name)
        server_variable.value = value
        server_variable.save()
        return server_variable
    
class MigrationHistory(models.Model):
    jurisdiction_id = models.IntegerField(blank=True, null=True, db_index=True)
    source_table = models.CharField(max_length=64, blank=True, null=True, db_index=True)
    source_id = models.IntegerField(blank=True, null=True, db_index=True)
    target_table = models.CharField(max_length=64, blank=True, null=True, db_index=True)
    target_id = models.IntegerField(blank=True, null=True, db_index=True)
    notes = models.TextField(blank=True, null=True)
    notes2 = models.TextField(blank=True, null=True)
    create_datetime = models.DateTimeField(auto_now_add=True)
    modify_datetime = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'website'
            
    @staticmethod
    def save_history(jurisdiction, source_table, source_id, target_table, target_id, notes='', notes2=''):
        history, created = MigrationHistory.objects.get_or_create(source_table=source_table, source_id=source_id, target_table=target_table, target_id=target_id)
        if jurisdiction != None:
            history.jurisdiction_id = jurisdiction.id
        history.notes = notes
        history.notes2 = notes2
        history.save()
        return history
    
    @staticmethod
    def get_target_id(source_table, source_id, target_table):
        try:
            history = MigrationHistory.objects.get(source_table=source_table, source_id=source_id, target_table=target_table)
            return history.target_id
        except:
            return None
