from logging import log
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from datetime import date, datetime

from ..models import *
from ..forms import *

from ..auxiliary_functions import convert_timedelta

@login_required
def view_todays_bookings(request):
    currentDT = datetime.now()
    current_time = currentDT.time()
    current_date = currentDT.date()

    bookings = Internal_Booking.objects.filter(date=current_date, account=request.user, active=True)

    ongoing = []
    upcoming = []
    finished = []
    
    for x in bookings:
        start_time = x.get_startTime_display()
        print(start_time)

        status = x.get_status()

        print(status)

        if status == "Upcoming":
            upcoming.append(x)
        elif status == "Finished":
            finished.append(x)
        elif status == "Ongoing":
            ongoing.append(x)

    context = {
        'bookings':bookings,
        'upcoming':upcoming,
        'ongoing':ongoing,
        'finished':finished,
    }

    return render(request, 'roombooking/todays_bookings/view_todays_bookings.html', context)

@login_required
def todays_booking_specific(request, booking_id):
    booking = get_object_or_404(Internal_Booking, pk=booking_id)

    if request.user == booking.account:
        extras = ExtraBookingMap.objects.filter(booking=booking)


        start = datetime.strptime(booking.get_startTime_display(), "%H:%M").time()
        end = datetime.strptime(booking.get_end_time(), "%H:%M").time()

        length = datetime.strptime(booking.get_length_display(), "%H:%M").time()

        now = datetime.now()
        today = datetime.now().date()

        start = datetime.combine(today, start)
        # end = datetime.combine(today, end)

        length = timedelta(hours=length.hour, minutes=length.minute, seconds=length.second)

        time_passed = now - start

        percent = int((time_passed / length) * 100)

        time_left = length - time_passed

        print(time_passed)
        print(time_left)

        print(convert_timedelta(time_passed))
        print(convert_timedelta(time_left))

        time_passed = convert_timedelta(time_passed)
        time_left = convert_timedelta(time_left)

        print("PERCENT: " , percent)

        events = []

        events.append({'event':'Meeting Start', 'content':"Meeting starts in room " + str(booking.room) + ".", 'time':datetime.strptime(booking.get_startTime_display(), "%H:%M").time()})
        events.append({'event':"Meeting End", 'content':"Meeting ends.", 'time':datetime.strptime(booking.get_end_time(), "%H:%M").time()})


        e = ExtraBookingMap.objects.filter(booking=booking)

        for extra in e:
            extra_string = "Type: " + extra.extra.get_extra_type_display() + "\nQuantity: " + str(extra.quantity)
            events.append({'event':str(extra.extra), 'content':extra_string, 'time':extra.timing})

        events_sorted = sorted(events, key=lambda k: k['time'])

        context = {
            'booking':booking,
            'extras':extras,
            'completion_percent':percent,
            'time_passed':time_passed,
            'time_left':time_left,
            'events_list':events_sorted,
        }

        return render(request, 'roombooking/todays_bookings/view_specific_booking.html', context)

    else:
        return redirect(reverse('roombooking:index'))

