from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse

from django.http import HttpResponse
from django.contrib import messages

from ..models import *
from ..forms import *

from ..auxiliary_functions import admin_filter_bookings

def generate_invoice_file_in_range(date1, date2):
    bookings = Booking.objects.filter(date__range=(date1, date2))
    costs = Cost.objects.filter(booking__in = bookings)

    end_string = ""

    for c in costs:
        end_string = end_string + c.invoice_string()

        print("Current End String: ", end_string)

    # path = "invoice\\" + date1.strftime("%Y-%m-%d") +  "-" + date2.strftime("%Y-%m-%d") + ".csv"

    path = "invoice\\" + date1 +  "_" + date2 + ".csv"


    joined_path = os.path.join (MEDIA_ROOT , path)

    print("Joined: ", joined_path)

    f = open(joined_path, "w")
    file = File(f)

    file.write(end_string)

    file.close()

    f.close()

    return joined_path

@login_required
def invoice_gen_view(request):

    if  request.user.is_staff:
        # print("Admin Comfirmation")

        if request.method == 'POST':
            if 'dates_selected' in request.POST:
                dates_form = invoiceDatesForm(request.POST)

                if dates_form.is_valid():
                    date1 = dates_form.cleaned_data['date1'].strftime("%Y-%m-%d")
                    date2 = dates_form.cleaned_data['date2'].strftime("%Y-%m-%d")

                    file_name = date1 + "_" + date2 + ".csv"

                    file_path = os.path.join(MEDIA_ROOT, "include\\")

                    filepath = generate_invoice_file_in_range(date1, date2)

                    f = open(filepath, 'rb')

                    response = HttpResponse(f, content_type="application/force-download")
                    response['Content-Disposition']='attachment; filename=%s' % file_name

                    return response
 
        else:
            dates_form =invoiceDatesForm()

        context = {
            'dates_form':dates_form,
        }

        return render(request, 'roombooking/roomadmin/invoice_gen.html', context)

    return redirect(reverse('roombooking:index'))

@login_required
def view_bookings_admin(request):
    

    # print("USER IS STAFF: ", request.user.is_staff)

    if request.user.is_staff:
        
        if request.method == "POST":
            if "form_filter_submit" in request.POST:
                filter_form = adminFilterForm(request.POST)

                if filter_form.is_valid():
                    print("Filter is valid")

                    bookings = admin_filter_bookings(filter_form.cleaned_data)
            if 'remove_filters' in request.POST:
                filter_form = adminFilterForm()
                bookings = Internal_Booking.objects.filter(account=request.user, active=True)



        else:
            filter_form = adminFilterForm()
            bookings = Internal_Booking.objects.filter(active=True)
            

        context = {
            'booking_list':bookings,
            'filter_form':filter_form,
        }

        return render(request, 'roombooking/roomadmin/viewall.html', context)


    else:
        return redirect(reverse('roombooking:index'))

extra_list=[]
login_required
def admin_edit(request, booking_id):
    extra_set = True
    booking = get_object_or_404(Internal_Booking, pk=booking_id)

    booking_form = InternalBookingForm(instance=booking)
    extra_form = ExtraMapForm()

    if request.user.is_staff:
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

                if booking_form.is_valid():
                    booking = booking_form.save(commit=False)

                    booking.id = booking_id
                    booking.account = request.user
                    booking.verification = 3

                    booking.save()

                    messages.success(request, "Edit Booking Succeeded")

                    return redirect(reverse('roombooking:viewbooking', args=(booking_id,)))

            if 'extra_submit' in request.POST:
                extra_form = ExtraMapForm(request.POST)
                if extra_form.is_valid():
                    extra = extra_form.save(commit=False)
                    extra.booking = booking
                    extra.save()
                    print("Should of Saved")

            if "delete_btn" in request.POST:
                booking.gradient_delete()

                return redirect(reverse('roombooking:viewbookingsadmin'))

            if 'true_delete' in request.POST:
                booking.delete()
                return redirect(reverse('roombooking:viewbookingsadmin'))

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

        return render(request, 'roombooking/roomadmin/admin_edit.html', context)

    return redirect(reverse('roombooking:index'))

@login_required
def daily_timeline(request):

    if request.user.is_staff:

        if request.method == 'POST' and 'building_select' in request.POST:
            building_form = buildingSelectForm(request.POST)

            if building_form.is_valid():
                building = building_form.cleaned_data.get('building')
                #building = Building.objects.get(pk=building_id)
        else:

            building = Building.objects.first()
            building_form = buildingSelectForm()

        current_date = datetime.now().date()

        rooms = Room.objects.filter(building=building)

        daily_bookings = Internal_Booking.objects.filter(date=current_date, room__in=rooms)

        events = []


        for booking in daily_bookings:
            events.append({'event':"Meeting starts in room " + str(booking.room) + "." , 'time':datetime.strptime(booking.get_startTime_display(), "%H:%M").time()})

            events.append({'event':"Meeting ends in room " + str(booking.room) + "." , 'time':datetime.strptime(booking.get_end_time(), "%H:%M").time()})


            e = ExtraBookingMap.objects.filter(booking=booking)

            for extra in e:
                events.append({'event':str(extra.quantity) + " " + str(extra.extra) + " to room " + str(booking.room) + "." , 'time':extra.timing})

        events_sorted = sorted(events, key=lambda k: k['time'])

        print(events)
        print(events_sorted)

        context = {
            'events':events_sorted,
            'building_form':building_form,
        }
        
        return render(request, 'roombooking/roomadmin/daily_timeline.html', context)


