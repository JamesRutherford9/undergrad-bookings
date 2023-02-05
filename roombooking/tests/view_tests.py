from django.test import TestCase, Client
from django.contrib.auth.models import User
import datetime

from ..models import *
from ..views import *

class ViewBookingsTestCase(TestCase):
    def setUp(self):
        Building.objects.create(address="Example Address", name="Building", totalRooms=5, owner="Example")
        Room.objects.create(building_id=1, name="Example Room", size=10, price=10.00, maxOccupancy=10)

        staffUser = User.objects.create_user(username='staff', email='staff@email.com', password='password', is_staff=True)
        basicUser = User.objects.create_user('example', 'example@email.com', 'password')

        Internal_Booking.objects.create(account=basicUser, title="First", room_id=1, date=datetime.strptime("2022-04-01", "%Y-%m-%d").date(), startTime=0, length=1, attendees=5)
        Internal_Booking.objects.create(account=basicUser, title="Second", room_id=1, date=datetime.strptime("2022-04-02", "%Y-%m-%d").date(), startTime=2, length=2, attendees=4)

        Internal_Booking.objects.create(account=staffUser, title="Third", room_id=1, date=datetime.strptime("2023-04-02", "%Y-%m-%d").date(), startTime=2, length=2, attendees=4)

        Internal_Booking.objects.create(account=staffUser, title="Fourth", room_id=1, date=datetime.now().date(), startTime=2, length=2, attendees=4)


    def test_viewbookings(self):
        client = Client()
        client.login(username="example", password="password")
        response = client.get('/roombooking/viewbookings/')

        bookings = response.context['booking_list']

        self.assertEqual(2, len(bookings))

    def test_viewbookings_filter(self):
        client = Client()
        client.login(username="example", password="password")

        response = client.post('/roombooking/viewbookings/', data={'title': [''], 'start_date': [''], 'end_date': [''], 'room': ['1'], 'form_filter_submit': ['Apply Filters']})

        bookings = response.context['booking_list']

        self.assertEqual(2, len(bookings))

        response_two = client.post('/roombooking/viewbookings/', data={'title': ['First'], 'start_date': [''], 'end_date': [''], 'room': ['1'], 'form_filter_submit': ['Apply Filters']})

        bookings_two = response_two.context['booking_list']
        self.assertEqual(1, len(bookings_two))

    def test_viewbooking(self):
        client = Client()
        client.login(username="example", password="password")

        c2 = Client()
        c2.login(username="staff", password="password")

        response = client.get('/roombooking/viewbooking/1/')

        booking = response.context['booking']

        self.assertEqual("First", booking.title)
        
        failed_response = client.get('/roombooking/viewbooking/100/')

        self.assertEqual(404, failed_response.status_code)

        no_access = c2.get('/roombooking/viewbooking/1/')
        self.assertEqual(404, no_access.status_code)


    def test_editbooking(self):
        client = Client()
        client.login(username="example", password="password")

        response = client.get('/roombooking/editbooking/1/')

        booking = response.context['booking']

        self.assertEqual("First", booking.title)
        
        failed_response = client.get('/roombooking/editbooking/100/')

        self.assertEqual(404, failed_response.status_code)

        response_edit_attempt = client.post('/roombooking/editbooking/1/', data={'title': ['First'], 'room': ['1'], 'date': ['2022-04-01'], 'startTime': ['0'], 'length': ['2'], 'attendees': ['4'], 'note': [''], 'booking_submit': ['Submit']})

        b = Booking.objects.get(pk=1)

        self.assertEqual(4, b.attendees)

    # def test_createBooking(self):
    #     client = Client()
    #     client.login(username="example", password="password")

    #     c2 = Client()
        
    #     failed = c2.get('/roombooking/createbooking/')

    #     self.assertRedirects(failed, '/roombooking/account/login/')


class ProfileTestCase(TestCase):
    def setUp(self):
        basicUser = User.objects.create_user('example', 'example@email.com', 'password')

    def test_login(self):
        client = Client()
        c2 = Client()

        c3 = Client()
        c3.login(username="example", password="password")

        response = client.post('/roombooking/accounts/login/', data={'username':['example'], 'password':['password']})
        self.assertRedirects(response, '/roombooking/')
        failed_response = c2.post('/roombooking/accounts/login/', data={'username':['example'], 'password':['wrong']})
        self.assertRedirects(failed_response, '/roombooking/accounts/login/')

        redirect_response = c3.get('/roombooking/accounts/login/')
        self.assertRedirects(redirect_response, '/roombooking/')


    def test_logout(self):
        client = Client()
        client.login(username="example", password="password")

        response = client.post('/roombooking/accounts/logout/')

        self.assertRedirects(response, '/roombooking/')

    def test_indexAlwaysView(self):
        client = Client()
    
        response = client.get('/roombooking/')

        self.assertTemplateUsed(response, 'roombooking/index.html')


class TodaysViewsTestCase(TestCase):
    def setUp(self):
        Building.objects.create(address="Example Address", name="Building", totalRooms=5, owner="Example")
        Room.objects.create(building_id=1, name="Example Room", size=10, price=10.00, maxOccupancy=10)

        basicUser = User.objects.create_user(username='example', email='example@email.com', password='password')
        staffUser = User.objects.create_user(username='staff', email='staff@email.com', password='password', is_staff=True)

        Internal_Booking.objects.create(account=basicUser, title="First", room_id=1, date=datetime.strptime("2022-04-01", "%Y-%m-%d").date(), startTime=0, length=1, attendees=5)
        Internal_Booking.objects.create(account=basicUser, title="Second", room_id=1, date=datetime.strptime("2022-04-02", "%Y-%m-%d").date(), startTime=2, length=2, attendees=4)

        Internal_Booking.objects.create(account=staffUser, title="Third", room_id=1, date=datetime.strptime("2023-04-02", "%Y-%m-%d").date(), startTime=2, length=2, attendees=4)

        Internal_Booking.objects.create(account=staffUser, title="Fourth", room_id=1, date=datetime.now().date(), startTime=2, length=2, attendees=4)

    def test_todaysBookings(self):
        c2 = Client()
        c2.login(username="staff", password="password")

        response = c2.get('/roombooking/todaysbookings/')

        self.assertEqual(1, len(response.context['bookings']))


    def test_todaySpecific(self):
        c2 = Client()
        c2.login(username="staff", password="password")

        response = c2.get('/roombooking/todaysbookings/4/')

        b = Booking.objects.get(pk=4)

        self.assertEqual(b.id, response.context['booking'].id)

        self.assertEqual(2, len(response.context['events_list']))

        failed_response = c2.get('/roombooking/todaysbookings/400/')

        self.assertEqual(404, failed_response.status_code)


class AdminViewsTestCase(TestCase):
    def setUp(self):
        Building.objects.create(address="Example Address", name="Building", totalRooms=5, owner="Example")
        Room.objects.create(building_id=1, name="Example Room", size=10, price=10.00, maxOccupancy=10)

        basicUser = User.objects.create_user(username='example', email='example@email.com', password='password')
        staffUser = User.objects.create_user(username='staff', email='staff@email.com', password='password', is_staff=True)

        Internal_Booking.objects.create(account=basicUser, title="First", room_id=1, date=datetime.strptime("2022-04-01", "%Y-%m-%d").date(), startTime=0, length=1, attendees=5)
        Internal_Booking.objects.create(account=basicUser, title="Second", room_id=1, date=datetime.strptime("2022-04-02", "%Y-%m-%d").date(), startTime=2, length=2, attendees=4)

        Internal_Booking.objects.create(account=staffUser, title="Third", room_id=1, date=datetime.strptime("2023-04-02", "%Y-%m-%d").date(), startTime=2, length=2, attendees=4)

        Internal_Booking.objects.create(account=staffUser, title="Fourth", room_id=1, date=datetime.now().date(), startTime=2, length=2, attendees=4)

    def test_viewBookingsAdmin(self):
        client = Client()
        client.login(username="example", password="password")

        c2 = Client()
        c2.login(username="staff", password="password")

        response_fail = client.get('/roombooking/viewbookingsadmin/')

        response_success = c2.get('/roombooking/viewbookingsadmin/')

        self.assertRedirects(response_fail, '/roombooking/')

        b = response_success.context['booking_list']

        self.assertEqual(len(b), 4)

    def test_adminEditBooking(self):
        c2 = Client()
        c2.login(username="staff", password="password")

        response_edit_attempt = c2.post('/roombooking/adminedit/1/', data={'title': ['First'], 'room': ['1'], 'date': ['2022-04-01'], 'startTime': ['0'], 'length': ['2'], 'attendees': ['3'], 'note': [''], 'booking_submit': ['Submit']})

        b = Booking.objects.get(pk=1)

        self.assertEqual(3, b.attendees)

    def test_daily_timeline(self):
        c2 = Client()
        c2.login(username="staff", password="password")

        response = c2.get('/roombooking/dailytimeline/')

        events = response.context['events']

        self.assertEqual(2, len(events))

