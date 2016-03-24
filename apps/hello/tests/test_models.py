# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import date
from PIL import Image as Img
import StringIO

from django.test import TestCase
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.core.files.uploadedfile import InMemoryUploadedFile

from ..models import Contact, RequestsStore


# create image file for test
def get_temporary_image():
        output = StringIO.StringIO()
        size = (1200, 700)
        color = (255, 0, 0, 0)
        image = Img.new("RGBA", size, color)
        image.save(output, format='JPEG')
        image_file = InMemoryUploadedFile(
            output, None, 'test.jpg', 'jpeg', output.len, None)
        image_file.seek(0)
        return image_file


class ContactModelTests(TestCase):
    fixtures = ['data.json']

    def setUp(self):
        self.person = Contact.objects.create(
            name='Leks',
            surname='Woronow',
            email='aleks.woronow@yandex.ru',
            jabber='aleksw@42cc.co',
            skype_id='aleks_woronow',
            date_of_birth=date(2016, 2, 25),
            bio='I was born ...')

    def test_contact_model_blank_fields_validation(self):
        """
        Test check validation blank fields contact model
        """
        person = Contact()

        # test model blank and null fields validation
        with self.assertRaises(ValidationError) as err:
            person.full_clean()
        err_dict = err.exception.message_dict
        self.assertEquals(
            err_dict['name'][0],
            Contact._meta.get_field('name').error_messages['blank'])
        self.assertEquals(
            err_dict['surname'][0],
            Contact._meta.get_field('surname').error_messages['blank'])
        self.assertEquals(
            err_dict['email'][0],
            Contact._meta.get_field('email').error_messages['blank'])
        self.assertEquals(
            err_dict['date_of_birth'][0],
            Contact._meta.get_field('date_of_birth').
            error_messages['null'])

    def test_contact_model_email_date_field_validation(self):
        """
        Test check validation email and date fields contact model
        """
        person = Contact()
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
        self.assertIn(Contact._meta.get_field('date_of_birth').
                      error_messages['invalid'].format()[12:],
                      err_dict['date_of_birth'][0])

    def test_contact_model_fixture_data(self):
        """
        Test check that fixture_data is first in the database
        """
        # now check we can find initial_data in the database
        all_persons = Contact.objects.all()
        self.assertEquals(len(all_persons), 2)
        only_person = all_persons[0]
        second_person = all_persons[1]

        # and check that it's saved its attributes and fixture data is first
        self.assertEquals(only_person.name, 'Aleks')
        self.assertEquals(second_person.name, 'Leks')
        self.assertEquals(only_person.surname, 'Woronow')
        self.assertEquals(only_person.email, 'aleks.woronow@yandex.ru')
        self.assertEquals(only_person.jabber, 'aleksw@42cc.co')
        self.assertEquals(only_person.skype_id, 'aleks_woronow')
        self.assertEquals(only_person.date_of_birth, date(2016, 2, 25))
        self.assertEquals(only_person.bio, 'I was born ...')
        self.assertEquals(str(only_person), 'Woronow Aleks')

    def test_person_model_image(self):
        """
        Test check that overwritten save method maintaining aspect ratio
        and reduce image to <= 200*200.
        """

        # save image file
        person = Contact.objects.get(id=1)
        person.image = get_temporary_image()
        person.save()

        # check that height and width <= 200
        self.assertTrue(person.height <= 200)
        self.assertTrue(person.width <= 200)


class RequestsStoreTest(TestCase):
    fixtures = ['data.json']

    def test_request_store(self):
        """Test creating a new request and saving it to the database"""

        request_store = RequestsStore()
        user = get_user_model().objects.get(id=1)

        # test model blank and null fields validation
        with self.assertRaises(ValidationError) as err:
            request_store.full_clean()
        err_dict = err.exception.message_dict
        self.assertEquals(err_dict['path'][0],
                          RequestsStore._meta.get_field('path').
                          error_messages['blank'])
        self.assertEquals(err_dict['method'][0],
                          RequestsStore._meta.get_field('method').
                          error_messages['blank'])

        # test cretae and save object
        request_store.path = '/'
        request_store.method = 'GET'
        request_store.user = user

        # check we can save it to the database
        request_store.save()

        # now check we can find it in the database again
        all_requests = RequestsStore.objects.all()
        self.assertEquals(len(all_requests), 1)
        only_request = all_requests[0]
        self.assertEquals(str(only_request), str(request_store))

        # and check that it's saved its two attributes: path and method
        self.assertEquals(only_request.path, '/')
        self.assertEquals(only_request.method, 'GET')
        self.assertEquals(only_request.new_request, 1)
        self.assertEquals(only_request.user, user)
