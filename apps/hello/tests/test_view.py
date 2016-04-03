# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import date
import StringIO

from django.test import TestCase, RequestFactory
from django.core.urlresolvers import reverse
from django.http import HttpRequest
from django.core.files.uploadedfile import InMemoryUploadedFile

from ..views import home_page
from ..models import Contact, RequestsStore
from .test_models import get_temporary_image


# create text file for test
def get_temporary_text_file(name):
    io = StringIO.StringIO()
    io.write('test')
    text_file = InMemoryUploadedFile(
        io, None, name, 'text', io.len, None)
    text_file.seek(0)
    return text_file


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


class RequestViewTest(TestCase):
    def test_request_view(self):
        """Test request_view"""

        # send request to home page
        self.client.get(reverse('hello:home'))

        # take home request from db
        all_requests = RequestsStore.objects.all()
        self.assertEquals(len(all_requests), 1)
        home_request = all_requests[0]

        # check that new_request = 1
        self.assertEquals(home_request.path, '/')
        self.assertEquals(home_request.new_request, 1)

        # send request to requests page
        response = self.client.get(reverse('hello:requests'))
        self.client.get(
            reverse('hello:requests_ajax'),
            {'viewed': 'yes'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        # check that new_request = 0
        all_requests = RequestsStore.objects.all()
        self.assertEquals(len(all_requests), 2)
        home_request = all_requests[0]

        self.assertEquals(home_request.path, '/requests/')
        self.assertEquals(home_request.new_request, 0)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'requests.html')
        self.assertIn('Requests', response.content)
        self.assertIn('Path', response.content)
        self.assertIn('Method', response.content)
        self.assertIn('Date', response.content)


class RequestAjaxTest(TestCase):
    def test_request_ajax_view(self):
        """Test request ajax view"""
        self.client.get(reverse('hello:home'))
        response = self.client.get(reverse('hello:requests_ajax'),
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        self.assertIn('method', response.content)
        self.assertIn('GET', response.content)
        self.assertIn('path', response.content)
        self.assertIn('/', response.content)

    def test_request_ajax_content_empty_db(self):
        """
        Test check that request_ajax view returns
        empty response when transition to request_view page.
        """

        response = self.client.get(reverse('hello:requests_ajax'),
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        # check that db is empty
        request_store_count = RequestsStore.objects.count()
        self.assertGreaterEqual(request_store_count, 0)
        # check response is empty too
        self.assertIn('0', response.content)
        self.assertIn('[]', response.content)

    def test_request_ajax_content_record_db_more_10(self):
        """
        Test check that request_ajax view returns 10 objects
        when in db more than 10 records.
        """

        # create 15 records to db
        for i in range(1, 15):
            path = '/test%s' % i
            method = 'GET'
            RequestsStore.objects.create(path=path, method=method, priority=i)

        self.client.get(reverse('hello:home'))
        request_store_count = RequestsStore.objects.count()
        self.assertGreaterEqual(request_store_count, 1)

        # check number of objects in db
        req_list = RequestsStore.objects.count()
        self.assertEqual(req_list, i+1)

        # check that 10 objects in response
        response = self.client.get(reverse('hello:requests_ajax'),
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(10, response.content.count('pk'))
        self.assertEqual(10, response.content.count('GET'))
        self.assertNotIn('/test3', response.content)
        self.assertNotIn('/test4', response.content)
        self.assertIn('/test6', response.content)
        self.assertIn('/', response.content)

    def test_requests_ajax_change_priority(self):
        """
        Test requests_ajax view, changing priority for same requests.
        """
        self.client.get(reverse('hello:home'))

        # check request: path - '/', priority - 0
        all_req = RequestsStore.objects.all()
        self.assertEquals(len(all_req), 1)
        only_req = all_req[0]
        self.assertEqual(only_req.path, '/')
        self.assertEqual(only_req.method, 'GET')
        self.assertEqual(only_req.priority, 0)

        data = {'path': '/', 'priority': 1}
        # send new priority
        self.client.post(
            reverse('hello:requests_ajax'),
            data,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        all_req = RequestsStore.objects.all()
        self.assertEquals(len(all_req), 1)
        only_req = all_req[0]
        self.assertEquals(only_req.path, '/')
        self.assertEquals(only_req.method, 'GET')
        self.assertEquals(only_req.priority, 1)

    def test_requests_ajax_view_sort_requests_list(self):
        """
        Test requests_ajax view sort requests list by path.
        """
        self.client.get(reverse('hello:home'))
        self.client.get(reverse('hello:form'))
        self.client.get(reverse('hello:home'))

        # now in RequestsStore
        all_req = RequestsStore.objects.all()
        self.assertEquals(all_req[0].path, '/')
        self.assertEquals(all_req[1].path, '/form/')
        self.assertEquals(all_req[2].path, '/')

        # check that response is sorted by path
        response = self.client.get(reverse('hello:requests_ajax'),
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual('"path\\": \\"/\\"', (response.content[-453:-439]))
        self.assertEqual('"path\\": \\"/\\"', (response.content[-259:-245]))
        self.assertEqual('"path\\": \\"/form/\\"', (response.content[-65:-46]))


class FormPageTest(TestCase):
    fixtures = ['data.json']

    def setUp(self):
        self.person = Contact.objects.first()
        self.data = dict(name='Ivan', surname='Ivanov',
                         date_of_birth='2016-02-02',
                         bio='', email='ivanov@yandex.ru',
                         jabber='iv@jabb.com',
                         image=get_temporary_image())

    def test_form_page_view(self):
        """
        Test check access to form page only authenticate
        users and it used template request.html.
        """

        # if user is not authenticate
        response = self.client.get(reverse('hello:form'))
        self.assertEqual(response.status_code, 302)

        # after authentication
        self.client.login(username='admin', password='admin')
        response = self.client.get(reverse('hello:form'))
        self.assertTemplateUsed(response, 'edit_form.html')

    def test_form_page_edit_data(self):
        """Test check edit data at form page."""

        # login on the site
        self.client.login(username='admin', password='admin')

        # send new data to server
        response = self.client.post(reverse('hello:form'), self.data,
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        response = self.client.get(reverse('hello:form'))
        self.assertEqual(response.status_code, 200)

        # data are shown at form page according to changed data
        self.assertNotIn(self.person.name, response.content)
        self.assertNotIn(self.person.surname, response.content)
        self.assertNotIn(self.person.date_of_birth.strftime('%Y-%m-%d'),
                         response.content)
        self.assertNotIn(self.person.email, response.content)
        self.assertNotIn(self.person.jabber, response.content)

        self.assertIn('Ivan', response.content)
        self.assertIn('Ivanov', response.content)
        self.assertIn('2016-02-02', response.content)
        self.assertIn('ivanov@yandex.ru', response.content)
        self.assertIn('iv@jabb.com', response.content)
        self.assertIn('test.jpg', response.content)

    def test_form_page_on_text_file(self):
        """
        Test check form_page return error if upload text file.
        """

        # add to data text file text.txt
        self.data.update({'image': get_temporary_text_file('text.txt')})

        self.client.login(username='admin', password='admin')
        response = self.client.post(reverse('hello:form'), self.data,
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(400, response.status_code)
        self.assertIn('Upload a valid image. The file you uploaded',
                      response.content)

        # add to data text file text.jpg
        self.data.update({'image': get_temporary_text_file('text.jpg')})

        self.client.login(username='admin', password='admin')
        response = self.client.post(reverse('hello:form'), self.data,
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(400, response.status_code)
        self.assertIn('Upload a valid image. The file you uploaded',
                      response.content)

    def test_form_page_edit_data_to_wrong(self):
        """Test check edit data at form page to wrong data."""

        # check enter empty name and invalid data_of_birth, email
        # login on the site
        self.client.login(username='admin', password='admin')

        # edit data with empty name and invalid data_of_birth, email
        self.data.update({'name': '',
                          'date_of_birth': 'date',
                          'email': 'ivanovyandex.ru'})

        # send new data to server
        response = self.client.post(reverse('hello:form'), self.data,
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 400)

        # response errors
        self.assertIn('This field is required.', response.content)
        self.assertIn('Enter a valid date.', response.content)
        self.assertIn('Enter a valid email address.', response.content)

        # data in db did not change
        edit_person = Contact.objects.first()
        self.assertEqual(self.person.name, edit_person.name)

    def test_form_page_delete_image(self):
        """
        Test check delete image at form page
        """
        # login on the site
        self.client.login(username='admin', password='admin')

        # check that test.jpg isn't at form page
        response = self.client.get(reverse('hello:form'))
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('test.jpg', response.content)

        # send new contact data to server
        self.client.post(reverse('hello:form'), self.data,
                         HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        response1 = self.client.get(reverse('hello:form'))
        self.assertEqual(response1.status_code, 200)
        self.assertIn('test.jpg', response1.content)

        self.data.update({'image-clear': 'on', 'image': ''})

        # send new data to server
        self.client.post(reverse('hello:form'), self.data,
                         HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        response2 = self.client.get(reverse('hello:form'))
        self.assertEqual(response2.status_code, 200)
        self.assertNotIn('test.jpg', response2.content)
