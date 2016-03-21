# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import date

from django.test import TestCase
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator

from ..models import Person


class PersonModelTests(TestCase):
    def setUp(self):
        self.person = Person.objects.create(
            name='Aleks',
            surname='Woronow',
            email='aleks.woronow@yandex.ru',
            jabber='aleksw@42cc.co',
            skype_id='aleks_woronow',
            date_of_birth=date(2016, 2, 25),
            bio='I was born ...')

    def test_person_model_blank_fields_validation(self):
        """
        Test check validation blank fields person model
        """
        person = Person()

        # test model blank and null fields validation
        with self.assertRaises(ValidationError) as err:
            person.full_clean()
        err_dict = err.exception.message_dict
        self.assertEquals(
            err_dict['name'][0],
            Person._meta.get_field('name').error_messages['blank'])
        self.assertEquals(
            err_dict['surname'][0],
            Person._meta.get_field('surname').error_messages['blank'])
        self.assertEquals(
            err_dict['email'][0],
            Person._meta.get_field('email').error_messages['blank'])
        self.assertEquals(
            err_dict['date_of_birth'][0],
            Person._meta.get_field('date_of_birth').
            error_messages['null'])

    def test_person_model_email_date_field_validation(self):
        """
        Test check validation email and date fields person model
        """
        person = Person()
        # test model email and date field validation
        person.email = 'aleks@'
        person.jabber = '42cc'
        person.date_of_birth = 'sd'
        with self.assertRaises(ValidationError) as err:
            person.full_clean()
        err_dict = err.exception.message_dict
        self.assertEquals(err_dict['email'][0],
                          EmailValidator.message)
        self.assertEquals(err_dict['jabber'][0],
                          EmailValidator.message)
        self.assertIn(Person._meta.get_field('date_of_birth').
                      error_messages['invalid'].format()[12:],
                      err_dict['date_of_birth'][0])

    def test_person_model_initial_data(self):
        """
        Test check that initial_data is in the database
        """
        # now check we can find initial_data in the database
        all_persons = Person.objects.all()
        self.assertEquals(len(all_persons), 1)
        only_person = all_persons[0]

        # and check that it's saved its attributes
        self.assertEquals(only_person.name, 'Aleks')
        self.assertEquals(only_person.surname, 'Woronow')
        self.assertEquals(only_person.email, 'aleks.woronow@yandex.ru')
        self.assertEquals(only_person.jabber, 'aleksw@42cc.co')
        self.assertEquals(only_person.skype_id, 'aleks_woronow')
        self.assertEquals(only_person.date_of_birth, date(2016, 2, 25))
        self.assertEquals(only_person.bio, 'I was born ...')
        self.assertEquals(str(only_person), 'Woronow Aleks')
