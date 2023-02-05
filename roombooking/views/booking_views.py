from logging import exception
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db.models.query import QuerySet
from django.shortcuts import redirect, render
from django.urls import reverse
from django.core import serializers

from azure.ai.formrecognizer import FormRecognizerClient
from azure.core.credentials import AzureKeyCredential

import datetime

from django.core.mail import send_mail
from booking.settings import EMAIL_HOST_USER

from ..models import *
from ..forms import *

# Create Booking Views
@login_required
def view_dates(request, selected_building=None, selected_date=None):
    if request.method == 'POST':
        #print("POST REQUEST RECEIVED")
        #print(request.POST)
        if 'date_select_submit' in request.POST:
                
            date_select_form = viewDateForm(request.POST)
            if date_select_form.is_valid():
                    
                building_id = date_select_form.cleaned_data['building'].id
                date = date_select_form.cleaned_data['date']
                date = date.strftime("%Y-%m-%d")

                print("ID: ", building_id, " ", "date: ", date)

                return redirect(reverse('roombooking:viewdatesargs', args=(building_id, date,)))

        if 'empty_cell_submit' in request.POST:
            post_building_id = request.POST.get('building')
            post_date = request.POST.get('date')
            post_room = request.POST.get('roomID')
            post_time = request.POST.get('time')

            #Check date
            check_date = datetime.strptime(post_date, ("%Y-%m-%d")).date()

            print("Check date type: ", type(check_date))

            today = datetime.now().date()
            if check_date < today:
                print("HISTORY")
                err_msg = "Can't book in the past."

                messages.error(request, "Cannot create booking in the past.")

                return redirect(reverse('roombooking:viewdatesargs', args=(post_building_id, post_date,)))
            else:

                print("POST INFO\nRoom: ", post_room, "\nDate: ", post_date, "\nBuilding", post_building_id, "\nTime: ", post_time)

                return redirect(reverse('roombooking:createbookingargs', args=(post_room, post_time, post_date,)))
            
    else:
        #print("POST NOT REQUEST RECEIVED")
        date_select_form = viewDateForm()

    # Handle display of rooms
    if selected_building is not None and selected_date is not None:
        current_date = datetime.strptime(selected_date, "%Y-%m-%d")
        print(current_date, " ", current_date.date())

        date_bookings = Booking.objects.filter(date=selected_date, active=True)
        #date_bookings = Booking.objects.all()
        user_bookings = Internal_Booking.objects.filter(account=request.user, date=current_date, active=True)

        building = Building.objects.get(pk=selected_building)
        rooms = Room.objects.filter(building=building)

        print("Num bookings: ", len(date_bookings), "\nNum user bookings: ", len(user_bookings))
        #date_bookings_no_user = [x for x in date_bookings if x not in user_bookings]
        #print("Num after: ", len(date_bookings_no_user))

        date_bookings_no_user = []

        for x in date_bookings:
            print(x.id)
        print("\n")
        for x in user_bookings:
            print(x.id)

        date_bookings_no_user = date_bookings.exclude(id__in=user_bookings)            
        date_bookings_only_user = []

        for x in date_bookings:
            if x not in date_bookings_no_user:
                date_bookings_only_user.append(x)

        #user_objs = [*date_bookings_only_user, *user_bookings]

        print("No user bookings len: ", len(date_bookings_no_user))
        print("Only user bookings len: ", len(date_bookings_only_user))

        date_select_form = viewDateForm(initial={'date':selected_date, 'building':building})

        rooms_json = serializers.serialize("json", rooms)
        date_bookings_no_user_json = serializers.serialize("json", date_bookings_no_user)
        user_bookings_json = serializers.serialize("json", date_bookings_only_user)

        print(rooms_json)

        context = {
            'user_bookings':user_bookings,
            'date_bookings_no_user':date_bookings_no_user,
            'rooms':rooms,
            'date_select_form':date_select_form,
            'set':True,
            # Json Context Variables
            'rooms_json':rooms_json,
            'date_bookings_no_user_json':date_bookings_no_user_json,
            'user_bookings_json':user_bookings_json,

        }

        return render(request, 'roombooking/viewdates.html', context)

    else:
        current_date = datetime.now().date()
        current_date = datetime.strftime(current_date, "%Y-%m-%d")

        building = Building.objects.all().first()
            

        if building is not None:
            primary = building.id

            return redirect(reverse('roombooking:viewdatesargs', args=(primary, current_date,)))

    context = {
        'date_select_form':date_select_form,
        'set':False,
    }

    return render(request, 'roombooking/viewdates.html', context)


# Create Booking Second Ver
extras_list = []
@login_required
def create_booking(request, roomID=None, timeslot=None, date=None):
    room = Room.objects.get(pk=roomID)
    #print("Room: ", room)

    conv_date = datetime.strptime(date, "%Y-%m-%d").date()
    

    if request.method == 'POST':
        print("REQUEST POST")
        print(request.POST)
        if 'booking_submit' in request.POST:
            booking_form = InternalBookingCreateForm(request.POST)
            extra_form=ExtraMapForm()

            if booking_form.is_valid():
                print("save 1 ")
                booking = booking_form.save(commit=False)
                

                booking.account = request.user
                booking.verification = 3

                # Set Data from Grid
                
                conv_date = datetime.strptime(date, "%Y-%m-%d").date()

                #booking.room = room
                #booking.startTime = timeslot
                #booking.date = conv_date

                # print("\nLENGTH: ", booking.length, "\nLENGTH TYPE: ", type(booking.length))
                # print("START: ", booking.startTime, "\nSTART TYPE: ", type(booking.startTime))
                # print("ROOM: ", booking.room, "\nROOM TYPE: ", type(booking.room))
                # print("DATE: ", booking.date, "\nDATE TYPE: ", type(booking.date))
                # print("VERIFICATION: ", booking.verification, "\nVERIF TYPE: ", type(booking.verification))
                # print("ATTENDEES: ", booking.attendees, "\nATTENDEES TYPE: ", type(booking.attendees))

                # print("save 2")


                #booking.full_clean()
                booking.save()

                for extra in extras_list:

                    # VERIFY EXTRA FITS IN TIME RANGE

                    start_time = booking.get_startTime_display()
                    start_time = datetime.strptime(start_time, "%H:%M").time()

                    end_time = booking.get_end_time()
                    end_time = datetime.strptime(end_time, "%H:%M").time()

                    err_message = ""

                    if extra.timing < start_time:
                        err_message = "Too early"
                        print(err_message)
                        extras_list.remove(extra)
                        continue

                    if extra.timing > end_time:
                        err_message = "Too late"
                        print(err_message)
                        extras_list.remove(extra)
                        continue

                    extra.booking = booking

                    print("PRINTING EXTRA: ", type(extra))

                    print("\nBOOKING ID: ", extra.booking)
                    print("EXTRA: ", extra.extra)
                    print("QUANTITY: ", extra.quantity)
                    print("TIMING: ", extra.timing, "\n")

                    extra.save()
                
                print("Num extras saved: ", len(extras_list))

                extras_list.clear()
                print("EXTRAS: ", booking.extras.all())

                booking.generateCosts()

                # Send confirmation email.
                subject = "Booking Created"
                content = "A booking has been created:\nMeeting Title: " + booking.title + "\nRoom: " + str(booking.room) + "\nTime: " + booking.get_startTime_display() + "\nLength: " + booking.get_length_display() + "\nAttendees: " + str(booking.attendees) 

                send_mail(subject, content, EMAIL_HOST_USER, [booking.account.email])

                return redirect(reverse('roombooking:confirmbooking', args=(booking.id,)))

        elif 'extra_submit' in request.POST:
            booking_form = BookingCreateForm(initial={'room':room, 'date':conv_date, 'startTime':timeslot})
            extra_form = ExtraMapForm(request.POST)
            if extra_form.is_valid():
                extra = extra_form.save(commit=False)
                extras_list.append(extra)

                print("Items in list: ", len(extras_list))

        elif 'remove_extra' in request.POST:
            booking_form = BookingCreateForm(initial={'room':room, 'date':conv_date, 'startTime':timeslot})
            extra_form = ExtraMapForm()

            extra_id = request.POST.get('extra_id')
            extra_quantity = request.POST.get('extra_quantity')
            extra_timing = request.POST.get('extra_timing')

            for x in extras_list:

                extra_id = int(extra_id)
                extra_quantity = int(extra_quantity)
                x_timing = x.timing.strftime("%H:%M:%S")


                if extra_id == x.extra.id and extra_quantity == x.quantity and extra_timing == x_timing:
                    print("X found.")
                    extras_list.remove(x)
                else:
                    print("X not found.")

    else:
        booking_form = BookingCreateForm(initial={'room':room, 'date':conv_date, 'startTime':timeslot})
        
        extra_form = ExtraMapForm()

    time_str = time_choices[timeslot][1]

    print(time_str)

    context = {
        'booking_form':booking_form,
        'extra_form':extra_form,
        'extra_list':extras_list,
        'room':room,
        'timeslot':time_str,
        'date':date,
        }

    return render(request, 'roombooking/createbooking.html', context)

@login_required
def image_upload(request):

    if request.user.is_staff == False:
        return redirect(reverse('roombooking:index'))
    
    if request.method == 'POST':
        img_form = imageClassForm(request.POST, request.FILES)
        
        if img_form.is_valid():
           # FOR NON MODEL VER // image = img_form.cleaned_data['image_file']

            i = img_form.save()

            img_obj = img_form.instance

            #print("Absolute URL: ", img_obj.image.url)

            values = form_reading(img_obj)

            x = booking_from_values(values, i.title)

            print(x)

            if x == "Succeeded":
                latest = Booking.objects.latest("id")
                return redirect(reverse('roombooking:adminedit', args=(latest.id,)))

            context = {
                'img_form':img_form,
                'img_obj':img_obj.image.url,
            }

            return render(request, 'roombooking/create_booking/image_upload.html', context)

            
    else:
        img_form = imageClassForm()

    context = {
        'img_form':img_form,
        
    }

    return render(request, 'roombooking/create_booking/image_upload.html', context)


def form_reading(image_object):
    form_key = "d0f56eb9c438476b9e12d8b01cde2597"
    form_endpoint = "https://bookingrecognizer.cognitiveservices.azure.com/"
    print('Ready to use cognitive services at {} using key {}'.format(form_endpoint, form_key))

    form_recogniser_client = FormRecognizerClient(endpoint=form_endpoint, credential=AzureKeyCredential(form_key))

    try:
        print("Analysing Doc...")

        #with open(image_object.image.path) as img:
        #   analyze_form = form_recogniser_client.begin_recognize_content(img)

        img = open(image_object.image.path, 'rb')

        analyze_form = form_recogniser_client.begin_recognize_content(img)

        form_data = analyze_form.result()

        form = form_data[0]

        # print("Form Data: ", form_data)

        # print("FORM: ", form, "\nTYPE: ", type(form))

        # print("TABLES:" , form.tables)

        # print("TYPE: ", type(form.tables))

        values = []

        s = False
        p = False

        for x in form.tables:
            # print(x)
            # print(x.cells[0].text)
            for y in x.cells:
                print(y.text)
                if s == True:
                    values.append(y.text)
                    s = False

                if p == True:
                    p = False
                    s = True

                if y.text == "E-mail Address:":
                    s = True

                elif y.text == "Date of Meeting:":
                    s = True

                elif y.text == "Room Requested:":
                    s = True

                elif y.text == "Start Time:":
                    p = True
                
                elif y.text == "Length of meeting: (To the half hour)":
                    s = True

                elif y.text == "Number of Attendees:":
                    s=True

        print("VALS=" , values)

        return values




        #print("Form Types: ", form)

    except Exception as exc:
        print("Error: ", exc)



def booking_from_values(values, title):
    email = values[0]
    date = values[1]
    room = values[2]
    start = values[3]
    length = values[4]
    attendees = values[5]

    date = datetime.strptime(date, "%d/%m/%Y").date()

    if User.objects.filter(email=email).exists():
        account = User.objects.get(email=email)

        room = Room.objects.get(name=room)

        for x, y in time_choices:
            if y == start:
                start = x
                break

        for x, y in length_choices:
            if y == length:
                length = x
                break

        attendees = int(attendees)

        b = Internal_Booking(account=account, title=title, room=room, date=date, startTime=start, length=length, attendees=attendees)

        try:
            b.clean()
        except:
            return("Failed")

        b.save()
        return("Succeeded")

    else:
        return("No account with matching email.")
