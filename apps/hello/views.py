# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render


def home_page(request):
    person = {
        'name': 'Aleks',
        'surname': 'Woronow',
        'date_of_birth': 'Feb. 25, 2016',
        'bio': 'I was born ...',
        'email': 'aleks.woronow@yandex.ru',
        'jabber': 'aleks@42cc.co',
        'skype_id': 'aleks_woronow'}

    return render(request, 'home.html', person)
