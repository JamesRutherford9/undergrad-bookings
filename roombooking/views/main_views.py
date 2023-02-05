from django.contrib.auth import authenticate, logout, login
from django.http.response import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required

from django.urls import reverse

from django.core.mail import send_mail
from booking.settings import EMAIL_HOST_USER

from ..models import *
from ..forms import *

from ..auxiliary_functions import filter_bookings

# Main View
def index(request):
    
    return render(request, 'roombooking/index.html')

# Login and Profile Views
@login_required
def profile_view(request):
    account = request.user

    company = Account.objects.get(user=account).company

    bookings = Internal_Booking.objects.filter(account=account)

    ongoing = []
    upcoming = []
    finished = []

    for x in bookings:
        
        status = x.get_status()

        print("STATUS ", status)
        
        if status == "Finished" or status == "Past Date":
            finished.append(x)
        elif status == "Ongoing":
            ongoing.append(x)
        else:
            upcoming.append(x)

    # print("COMPANY", str(company))

    context = {
        'account':account,
        'number_of_bookings':bookings.count(),
        'company':str(company),
        'ongoing':len(ongoing),
        'finished':len(finished),
        'upcoming':len(upcoming),
    }

    return render(request, 'roombooking/profile.html', context)


def booking_login(request):
    if request.user.is_authenticated:
        return redirect(reverse('roombooking:index'))

    if request.method == 'POST':
        print("POST REQUEST FOUND")
        login_form = loginForm(request.POST)
        if login_form.is_valid():
            username = login_form.cleaned_data['username']
            password = login_form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect(reverse('roombooking:index'))
            else:
                return redirect(reverse('roombooking:login'))

    else:
        print("GET REQUEST")

        login_form = loginForm()

    context = {
        'login_form':login_form,
    }

    return render(request, 'roombooking/login.html', context)

@login_required
def booking_logout(request):
    logout(request)

    return redirect(reverse('roombooking:index'))

# View Bookings
@login_required
def view_bookings(request): # See user's bookings
    if request.method == "POST":
        if 'form_filter_submit' in request.POST:
            filter_form = filterForm(request.POST)

            # print(request.POST)

            if filter_form.is_valid():
                # print("Filter is valid")

                filtered = filter_bookings(filter_form.cleaned_data)

                bookings = filtered.filter(account=request.user)

        if 'remove_filters' in request.POST:
            filter_form = filterForm()
            bookings = Internal_Booking.objects.filter(account=request.user, active=True)


    else:
        filter_form = filterForm()
        bookings = Internal_Booking.objects.filter(account=request.user, active=True)

    context = {
        'booking_list': bookings,
        'filter_form':filter_form,
    }

    return render(request, 'roombooking/viewbookings.html', context)

@login_required
def view_booking(request, booking_id): # View single booking
    booking = get_object_or_404(Internal_Booking, pk=booking_id)

    if request.user == booking.account:

        if request.method == 'POST':
            if 'edit_btn' in request.POST:
                return redirect(reverse('roombooking:editbooking', args=(booking_id,)))

            if 'del_btn' in request.POST:
                # booking.delete()
                booking.gradient_delete()

                # Send deletion email.
                subject = "Booking Deleted"
                content = "The booking has been deleted:\nMeeting Title: " + booking.title + "\nRoom: " + str(booking.room) + "\nTime: " + booking.get_startTime_display() + "\nLength: " + booking.get_length_display() + "\nAttendees: " + str(booking.attendees) 

                send_mail(subject, content, EMAIL_HOST_USER, [booking.account.email])


                return redirect(reverse('roombooking:viewbookings'))

        extras = ExtraBookingMap.objects.filter(booking=booking)
        cost = Cost.objects.filter(booking=booking).first()

        context = {
            'booking':booking,
            'extra_list':extras,
            'costs':cost,
        }

        return render(request, 'roombooking/viewbooking.html', context)

    else:
        raise Http404("No Access")