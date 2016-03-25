# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import StringIO
import os

from django.db import models
from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile

from PIL import Image as Img

from hello.storage import HelloStorage


class Contact(models.Model):
    name = models.CharField('name', max_length=250)
    surname = models.CharField('surname', max_length=250)
    date_of_birth = models.DateField('date of birth')
    bio = models.TextField('bio', blank=True)
    email = models.EmailField('email')
    jabber = models.EmailField('jabber', blank=True)
    skype_id = models.CharField('skype id',
                                blank=True,
                                max_length=250)
    other = models.TextField('other contact', blank=True)
    image = models.ImageField('photo',
                              blank=True,
                              null=True,
                              upload_to='photo/',
                              storage=HelloStorage(),
                              height_field='height',
                              width_field='width')
    height = models.PositiveIntegerField(default=1, null=True, blank=True)
    width = models.PositiveIntegerField(default=1,  null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.image:
            try:
                image = Img.open(StringIO.StringIO(self.image.read()))
            except ValueError:
                return super(Contact, self).save(*args, **kwargs)
            image.thumbnail((200, 200), Img.ANTIALIAS)
            output = StringIO.StringIO()
            image.save(output, format='JPEG', quality=75)
            output.seek(0)

            self.image = InMemoryUploadedFile(output,
                                              'ImageField',
                                              "%s" % self.image.name,
                                              'image/jpeg',
                                              output.len,
                                              None)

        super(Contact, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.image:
            if os.path.isfile(self.image.path):
                os.remove(self.image.path)

        super(Contact, self).delete(*args, **kwargs)

    def __unicode__(self):
        return '%s %s' % (self.surname, self.name)


class RequestsStore(models.Model):
    path = models.CharField(max_length=250)
    method = models.CharField(max_length=10)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             blank=True,
                             null=True)
    date = models.DateTimeField(auto_now_add=True)
    new_request = models.PositiveIntegerField(default=1)

    def __unicode__(self):
        return "%s - %s" % (self.path, self.method)

    class Meta:
        ordering = ["-date"]


class NoteModel(models.Model):
    ACTION_TYPE = (
        (0, 'created'),
        (1, 'changed'),
        (2, 'deleted')
    )
    model = models.CharField('model', max_length=50)
    inst = models.CharField('instance', max_length=250)
    action_type = models.PositiveIntegerField(
        'action type', max_length=1, choices=ACTION_TYPE)

    def __unicode__(self):
        return "%s  %s: %s " % (
            self.model, self.get_action_type_display(), self.inst)
