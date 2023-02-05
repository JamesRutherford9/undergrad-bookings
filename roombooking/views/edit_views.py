from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.core import serializers
from datetime import datetime, time
from django.contrib import messages

from django.core.mail import send_mail
from booking.settings import EMAIL_HOST_USER

from django.contrib.auth.decorators import login_required

from ..models import *
from ..forms import *

# Booking Edit and View

extra_list = []
@login_required
def edit_booking(request, booking_id): # Edit a booking
    extra_set = True
    booking = get_object_or_404(Internal_Booking, pk=booking_id)

    booking_form = InternalBookingForm(instance=booking)
    extra_form = ExtraMapForm()

    if request.user == booking.account:
        if request.method == 'POST':
            if 'remove_extra' in request.POST:

                extra_id = request.POST.get('extra_id')
                extra_quantity = request.POST.get('extra_quantity')
                extra_timing = request.POST.get('extra_timing')

                extraID = request.POST.get('extraID')

                print("Extra ID: ", extraID)

                for x in extra_list:
                    extraID = int(extraID)

                    extra_id = int(extra_id)
                    extra_quantity = int(extra_quantity)
                    x_timing = x.timing.strftime("%H:%M:%S")

                ExtraBookingMap.objects.get(pk=extraID).delete()
                extras = ExtraBookingMap.objects.filter(booking=booking)

                print("New num: ", len(extras))

            if 'booking_submit' in request.POST:
                booking_form = InternalBookingForm(request.POST, instance=booking)
                extra_form=ExtraMapForm()

                print("Editing the booking.")
                print(request.POST)

                if booking_form.is_valid():
                    booking = booking_form.save(commit=False)

                    booking.id = booking_id
                    booking.account = request.user
                    booking.verification = 3

                    booking.save()

                    messages.success(request, "Edit Booking Succeeded")

                    # Send confirmation email.
                    subject = "Booking Edited"
                    content = "A booking has been edited.\nThe new values are:\nMeeting Title: " + booking.title + "\nRoom: " + str(booking.room) + "\nTime: " + booking.get_startTime_display() + "\nLength: " + booking.get_length_display() + "\nAttendees: " + str(booking.attendees) 

                    send_mail(subject, content, EMAIL_HOST_USER, [booking.account.email])

                    return redirect(reverse('roombooking:viewbooking', args=(booking_id,)))

            if 'extra_submit' in request.POST:
                extra_form = ExtraMapForm(request.POST)
                if extra_form.is_valid():
                    extra = extra_form.save(commit=False)

                    # VERIFY EXTRA FITS IN TIME RANGE

                    start_time = booking.get_startTime_display()
                    start_time = datetime.strptime(start_time, "%H:%M").time()

                    end_time = booking.get_end_time()
                    end_time = datetime.strptime(end_time, "%H:%M").time()

                    err_message = ""

                    if extra.timing < start_time:
                        err_message = "Too early"
                        print(err_message)
                        messages.error(request, err_message)
                        

                    elif extra.timing > end_time:
                        err_message = "Too late"
                        print(err_message)
                        messages.error(request, err_message)
                    
                    else:
                        extra.booking = booking
                        extra.save()
                        print("Should of Saved")

            if 'delete_btn' in request.POST:
                booking.gradient_delete()

                # Send deletion email.
                subject = "Booking Deleted"
                content = "The booking has been deleted:\nMeeting Title: " + booking.title + "\nRoom: " + str(booking.room) + "\nTime: " + booking.get_startTime_display() + "\nLength: " + booking.get_length_display() + "\nAttendees: " + str(booking.attendees) 

                send_mail(subject, content, EMAIL_HOST_USER, [booking.account.email])

                return redirect(reverse('roombooking:viewbookings'))



        extras = ExtraBookingMap.objects.filter(booking=booking)

        print("Extras: " , len(extras))
        if len(extras) < 1:
            extra_set = False

        context = {
            'booking':booking,
            'booking_form':booking_form,
            'extra_form':extra_form,
            'extra_list':extras,
            'extra_set':extra_set,
        }

        subject = "Booking Created"
        content = "A booking has been created:\nMeeting Title: " + booking.title + "\nRoom: " + str(booking.room) + "\nTime: " + booking.get_startTime_display() + "\nLength: " + booking.get_length_display() + "\nAttendees: " + str(booking.attendees) 

        send_mail(subject, content, EMAIL_HOST_USER, [booking.account.email])


        return render(request, 'roombooking/editbooking.html', context)

    return redirect(reverse('roombooking:index'))

@login_required
def confirm_booking(request, booking_id): # Confirm a booking once it's created, link to edit.
    if 'continue_booking' in request.GET:
        return redirect(reverse('roombooking:index'))

    elif 'edit_booking' in request.GET:
        return redirect(reverse('roombooking:editbooking', args=(booking_id,)))

    booking = get_object_or_404(Internal_Booking, pk=booking_id)
    extras = ExtraBookingMap.objects.filter(booking=booking)
    cost = Cost.objects.get(booking=booking)

    context = {'booking':booking, 'extras':extras, 'costs':cost,}
    return render(request, 'roombooking/confirmbooking.html', context)