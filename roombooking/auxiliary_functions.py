from django.core.mail import send_mail

from . import forms
from roombooking.models import *

def filter_bookings(filter_form_data):
    name = filter_form_data['title']
    sDate = filter_form_data['start_date']
    eDate = filter_form_data['end_date']
    room = filter_form_data['room']
    active = filter_form_data['include_deleted']

    filter_string = ""

    bookings = Internal_Booking.objects.all()

    if name != "":
        filter_string = filter_string + "name__contains"
        bookings = bookings.filter(title__contains=name)

    if sDate != None:
        bookings = bookings.filter(date__gte=sDate)

    if eDate != None:
        bookings = bookings.filter(date__lte=eDate)

    if room != None:
        bookings = bookings.filter(room=room)

    if active != True:
        bookings = bookings.filter(active=True)

    return bookings

def admin_filter_bookings(filter_form_data):
    name = filter_form_data['title']
    sDate = filter_form_data['start_date']
    eDate = filter_form_data['end_date']
    room = filter_form_data['room']
    user = filter_form_data['user']
    building = filter_form_data['building']
    active = filter_form_data['include_deleted']

    print(name, " ", sDate, " ", eDate, " ", room, " ", user)

    filter_string = ""

    bookings = Internal_Booking.objects.all()

    if name != "":
        filter_string = filter_string + "name__contains"
        bookings = bookings.filter(title__contains=name)

    if sDate != None:
        bookings = bookings.filter(date__gte=sDate)

    if eDate != None:
        bookings = bookings.filter(date__lte=eDate)

    if room != None:
        bookings = bookings.filter(room=room)

    if user != None:
        bookings = bookings.filter(account=user)

    if active != True:
        bookings = bookings.filter(active=True)
    

    if building != None:
        # bookings = bookings.filter(room.building==building)
        rooms = Room.objects.filter(building=building)
        print(str(building))
        print(len(rooms))
        bookings = bookings.filter(room__in=rooms)

    return bookings


def convert_timedelta(duration):
    seconds = duration.total_seconds()

    seconds_passed = duration.total_seconds()

    hours_passed = seconds_passed // 3600
    minutes_passed = (seconds_passed % 3600) // 60

    # h_p = "{:02d}".format(int(hours_passed))
    m_p = "{:02d}".format(int(minutes_passed))

    ret = str(int(hours_passed)) + ":" + m_p

    return ret

    # return "{}:{}".format(int(hours_passed), int(minutes_passed))
    
