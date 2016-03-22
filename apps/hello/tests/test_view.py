# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import date

from django.test import TestCase, RequestFactory
from django.core.urlresolvers import reverse
from django.http import HttpRequest

from ..views import home_page
from ..models import Contact


class HomePageViewTest(TestCase):
    def setUp(self):
        # Every test needs access to the request factory.
        self.factory = RequestFactory()

    def test_home_page_view(self):
        """Test view home_page"""
        # Create an instance of a GET request.
        request = self.factory.get('/')

        # Test home_page() as if it were deployed at /
        response = home_page(request)
        self.assertEqual(response.status_code, 200)

        # Test home.html was used in rendering response
        self.assertTemplateUsed(response, 'home.html')


class HomePageTest(TestCase):
    def setUp(self):
        self.person = Contact.objects.create(
            name='Aleks',
            surname='Woronow',
            email='aleks.woronow@yandex.ru',
            jabber='aleksw@42cc.co',
            skype_id='aleks_woronow',
            date_of_birth=date(2016, 2, 25),
            bio='I was born ...')

    def test_home_page(self):
        """Test home page"""

        response = self.client.get(reverse('hello:home'))

        self.assertTemplateUsed(response, 'home.html')
        self.assertContains(response,
                            '<h1>42 Coffee Cups Test Assignment</h1>',
                            html=True)
        self.assertContains(response, 'Aleks')
        self.assertContains(response, 'Woronow')
        self.assertContains(response, 'Feb. 25, 2016')
        self.assertContains(response, 'aleks.woronow@yandex.ru')
        self.assertContains(response, 'aleksw@42cc.co')
        self.assertContains(response, 'aleks_woronow')
        self.assertContains(response, 'I was born ...')

    def test_home_page_if_person_more_then_one(self):
        """
        Test check that home page displays only the first record
        that db has more than 1 instance
        """
        # Create second person
        Contact.objects.create(
            name='Ivan',
            surname='Ivanov',
            email='ivan@yandex.ru',
            jabber='ivan@42cc.co',
            skype_id='ivan_ivanov',
            date_of_birth=date(2016, 1, 25),
            bio='I was born ...')

        # Check that two person in db
        all_persons = Contact.objects.all()
        self.assertEquals(len(all_persons), 2)
        first_person = all_persons[0]

        # home page displays only the first record: Aleks
        response = self.client.get(reverse('hello:home'))
        self.assertEquals(response.context['person'], first_person)
        self.assertContains(response, 'Woronow')
        self.assertNotContains(response, 'Ivan')

    def test_home_page_if_no_person(self):
        """
        Test check that home page displays "Contact data no yet"
        if db has not person instance
        """
        # Delete all the Person instance
        Contact.objects.all().delete()

        # home page displays "Contact data no yet"
        response = self.client.get(reverse('hello:home'))
        self.assertEquals(response.context['person'], None)
        self.assertContains(response, 'Contact data no yet')

    def test_home_page_returns_correct_html(self):
        """Test home page returns correct html"""
        request = HttpRequest()
        response = home_page(request)
        self.assertTrue(response.content.strip().
                        startswith(b'<!DOCTYPE html>'))
        self.assertIn(b'<title>My card</title>', response.content)
        self.assertTrue(response.content.strip().endswith(b'</html>'))
