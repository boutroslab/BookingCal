from django.db import models
from django.contrib.auth.models import User
from django.contrib import admin
from _ast import Eq
from django.forms.models import ModelForm
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseRedirect
from datetime import datetime
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse

class Guest(models.Model):
    firstname = models.CharField(max_length=40, blank=False)
    surname = models.CharField(max_length=40, blank=False)
    email = models.CharField(max_length=40, blank=False)

class Equipment(models.Model):
    name = models.CharField(max_length=40, blank=False)
    enabled = models.BooleanField(default=True)
    room = models.CharField(max_length=10, blank=False)
    person = models.CharField(max_length=40, blank=False)
    desc =  models.CharField(max_length=200)

class Entry(models.Model):
    equipment = models.ForeignKey(Equipment , blank=False, null=False )
    title = models.CharField(max_length=40)
    body = models.TextField(max_length=10000, blank=True, verbose_name="Extra Information")
    created = models.DateTimeField(auto_now_add=True)
    date = models.DateTimeField(blank=False,default=datetime.now)
    enddate = models.DateTimeField(blank=False)
    creator = models.ForeignKey(User,blank=True)
    remind = models.BooleanField(default=False)
    guest = models.ForeignKey(Guest , blank= False, null=False)

    def equipment_name(self):
        return self.equipment.name
    equipment_name.admin_order_field = 'equipment__name'



#    def save(self, **kwargs):
##        if self.creator:
##          return self.creator
##        else :
##           return self.creator == request.user
#
#        checknumber =0
#        for e in Entry.objects.raw('SELECT * FROM ecalendar_entry'):
#            if self.equipment.id == e.equipment_id:
#                if self.enddate >= e.date and self.enddate <=e.enddate:
#                        checknumber +=1
#                elif self.date >=e.date and self.date <=e.enddate:
#                         checknumber +=1
#                elif self.date<=e.date and self.enddate>=e.enddate:
#                     checknumber +=1
#        for equipm in Equipment.objects.raw('SELECT * FROM ecalendar_equipment'):
#            if equipm.id == self.equipment.id:
#                if equipm.enabled==False:
#                    checknumber +=1
#
#
#        if checknumber>0:
#            error_messages='Not available'
#            return error_messages
#        else:
#            super(Entry, self).save(**kwargs)
#
#                # Call the "real" save() method.
#
#
#
#    class Meta:
#        verbose_name_plural="entries"


  ##Admin
class EntryAdmin(admin.ModelAdmin):



    raw_id_fields = ("equipment",)
    fieldsets = [
            ('Equipment',               {'fields': ['equipment']}),
            ('Date information',        {'fields': ['date','enddate']}),
            ('Informations',            {'fields':['title','body']}),

        ]
    list_display = ["title","body", "creator", "date", "enddate", "equipment_name"]

    list_filter =["equipment"]

    ordering = ['date']
    list_per_page = 20


    def save_model(self, request, obj, form, change):
        instance = form.save(commit=False)
        if not hasattr(instance,'creator'):
            instance.creator = request.user

        instance.save()
        form.save_m2m()
        return instance

    def save_formset(self, request, form, formset, change):

        def set_creator(instance):
            if not instance.creator:
                instance.creator = request.user
            instance.edited_by = request.user
            instance.save()

        if formset.model == Entry:
            instances = formset.save(commit=False)
            map(set_creator, instances)
            formset.save_m2m()
            return instances
        else:
            return formset.save()


admin.site.register(Entry, EntryAdmin)

class EquipmentAdmin(admin.ModelAdmin):

        list_display = ["name", "enabled", "room", "person", "desc"]
        list_filter =["enabled"]
        list_per_page = 20

admin.site.register(Equipment, EquipmentAdmin)
