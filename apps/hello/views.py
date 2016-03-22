# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.core import serializers

from .models import Contact, RequestsStore
from .decorator import not_record_request


def home_page(request):
    context = {}
    person = Contact.objects.first()
    context['person'] = person
    return render(request, 'home.html', context)


def request_view(request):
    if request.user.is_authenticated():
        RequestsStore.objects.filter(new_request=1).update(new_request=0)
    return render(request, 'requests.html')


@not_record_request
def request_ajax(request):
    if request.is_ajax():
        new_request = RequestsStore.objects.filter(new_request=1).count()
        request_list = RequestsStore.objects.all()[:10]
        list = serializers.serialize("json", request_list)
        data = json.dumps((new_request, list))
        return HttpResponse(data, content_type="application/json")

    return HttpResponseBadRequest('Error request')
