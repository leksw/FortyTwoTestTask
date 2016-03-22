# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

from .models import Contact


def home_page(request):
    context = {}
    person = Contact.objects.first()
    context['person'] = person
    return render(request, 'home.html', context)


def request_view(request):
    return render(request, 'requests.html')
