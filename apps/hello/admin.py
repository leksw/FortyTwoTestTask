# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from .models import Contact, RequestsStore


admin.site.register(Contact)
admin.site.register(RequestsStore)
