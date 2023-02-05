from logging import exception, raiseExceptions
from booking.settings import MEDIA_ROOT
from datetime import datetime, timedelta, time
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.deletion import CASCADE, SET_NULL

from django.contrib.auth.models import User

from django.core.files import File
from django.conf import settings

import os

from decimal import Decimal

import decimal

# Create your models here.

time_choices = [
        (0, '8:00'),
        (1, '8:30'),
        (2, '9:00'),
        (3, '9:30'),
        (4, '10:00'),
        (5, '10:30'),
        (6, '11:00'),
        (7, '11:30'),
        (8, '12:00'),
        (9, '12:30'),
        (10, '13:00'),
        (11, '13:30'),
        (12, '14:00'),
        (13, '14:30'),
        (14, '15:00'),
        (15, '15:30'),
        (16, '16:00'),
        (17, '16:30'),
        (18, '17:00'),
        (19, '17:30'),
        (20, '18:00'),
    ]

length_choices = [
        (1, '0:30'),
        (2, '1:00'),
        (3, '1:30'),
        (4, '2:00'),
        (5, '2:30'),
        (6, '3:00'),
        (7, '3:30'),
        (8, '4:00'),
        (9, '4:30'),
        (10, '5:00'),
        (11, '5:30'),
        (12, '6:00'),
        (13, '6:30'),
        (14, '7:00'),
        (15, '7:30'),
        (16, '8:00'),
        (17, '8:30'),
        (18, '9:00'),
        (19, '9:30'),
        (20, '10:00'),
]

class Building(models.Model):
    '''
    Representation of a building in the system.
    '''
    address = models.CharField(max_length=200)
    name = models.CharField(max_length=100)
    totalRooms = models.IntegerField(default=0)
    owner = models.CharField(max_length=200)

    def __str__(self):
        return self.name

    def clean(self):
        cleaned_date = super().clean()

        if self.totalRooms < 1:
            raise ValidationError("Room number cannot be less than 0.")
        
class Room(models.Model):
    building = models.ForeignKey(Building, on_delete=CASCADE)
    name = models.CharField(max_length=100)
    size = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=100, decimal_places=2, default=0.00)
    maxOccupancy = models.IntegerField(default=0)

    def __str__(self):
        return self.name

    def clean(self):
        cleaned_data = super().clean()
        # Occupancy Checks
        if self.maxOccupancy < 1: # Check against minimum occupancy.
            raise ValidationError("Can't have a maximum occupancy less than 1.")
        if self.maxOccupancy > 500: # Check against maximum occupancy.
            raise ValidationError("Can't have an occupancy more than 100.")

        # Size Checks
        if self.size <= 0: # Checks minimal value
            raise ValidationError("Can't have a negative or zero size room.")
        
        # Price Check
        if self.price < 0:
            raise ValidationError("Can't have a negative price.")

        # Number of Rooms Check
        existing = self.building.totalRooms
        num = Room.objects.filter(building=self.building)
        if len(num) + 1 > existing:
            raise ValidationError("Can't have more rooms than total rooms in building.")

        return cleaned_data

class Company(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=SET_NULL, null=True)
    admin = models.BooleanField(default=False)

    def __str__(self):
        return self.user.get_username()

class Extra(models.Model):
    type_choice = [
        (0, 'Catering'),
        (1, 'Refreshments'),
        (2, 'Equipment'),
    ]

    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=100, decimal_places=2)
    supplier = models.CharField(max_length=200)
    extra_type = models.IntegerField(default=0, choices=type_choice)

    def __str__(self):
        return self.name

    def clean(self):
        cleaned_data = super().clean()
        if self.price < 0:
            raise ValidationError("Can't have a negative price.")

        return cleaned_data

class Booking(models.Model):
    verification_choices = [
        (0, 'Unverified'),
        (1, 'Verified'),
        (2, 'Requires Further Attention'),
        (3, 'Auto-Verified'),
    ]

    title = models.CharField(max_length=100)
    room = models.ForeignKey(Room, on_delete=CASCADE)
    date = models.DateField()
    startTime = models.IntegerField(default=0, choices=time_choices)
    length = models.IntegerField(default=0, choices=length_choices)
    verification = models.IntegerField(default=0, choices=verification_choices)
    attendees = models.IntegerField(default=1)
    extras = models.ManyToManyField(Extra, through='ExtraBookingMap')
    active = models.BooleanField(default=True)
    note = models.TextField(blank=True)

    def __str__(self):
        return (self.title + ", " + self.room.name + ", " + self.date.strftime("%d:%m:%Y") + ", " + self.get_startTime_display())

    def clean(self):

        cleaned_data = super().clean()

        # Attendee Checks
        if self.attendees < 1: # Checks attendees must be larger than 1.
            raise ValidationError('Attendees must be larger than 1.')

        # Occupancy Checks
        if self.room.maxOccupancy < self.attendees: # Checks that attendees can't be larger than the rooms occupancy.
            raise ValidationError("Can't have more attendees than the max occupancy of the room.")
            
        # Cannot have the meeting time go beyond the closing time.
        if (self.startTime + self.length) > 21:
            raise ValidationError("Cannot extend meeting past closing time.")

        #Date Checks
        current_date = datetime.now().date()
        if self.date < current_date:
            raise ValidationError("Cannot create booking in the past.")

        # Perform Checks Against other Bookings
        other_bookings = Booking.objects.filter(date=self.date, room=self.room, active=True).exclude(pk=self.id)
        for book in other_bookings:
                
            if book.startTime == self.startTime: # Check start time.
                raise ValidationError("Start time is already taken.")
                
            if self.startTime > book.startTime:
                if self.startTime <= book.startTime + book.length - 1: # Start time overlap other booking
                    raise ValidationError("Cannot overlap with existing bookings.")

            else:
                if self.startTime + self.length > book.startTime:
                    raise ValidationError("Cannot overlap with existing bookings.")

        return cleaned_data

    def generateCosts(self):
        extras = ExtraBookingMap.objects.filter(booking=self)

        print("Extras Num: ", len(extras))

        totalCost = 0
        roomCost = self.room.price

        #print("Multiplying: ", type(roomCost), " and ", type(self.length/2))

        half_len = decimal.Decimal(self.length/2)

        #print("Multiplying: ", type(roomCost), " and ", type(half_len))

        total_room_cost = roomCost * half_len

        extras_cost = 0

        for x in extras:
            extras_cost = extras_cost + (x.extra.price * x.quantity)


        print("Extras Cost: ", extras_cost)
        print("Room Cost: ", total_room_cost)

        try:
            costs = Cost.objects.get(booking=self)
        except:
            costs = Cost()
            costs.booking = self

        costs.roomPrice = total_room_cost
        costs.extraPrice = extras_cost
        
        totalCost += total_room_cost
        totalCost += extras_cost

        costs.save()

        print("Costs Generated")

        return totalCost

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs) 
        self.generateCosts()

    def get_end_time(self):
        end_time = self.startTime + self.length
        end_time = time_choices[end_time][1]
        return end_time

    def get_status(self):
        currentDT = datetime.now()
        current_date = currentDT.date()
        current_time = currentDT.time()

        start_time = self.get_startTime_display()
        start_time = datetime.strptime(start_time, "%H:%M").time()
        end_time = datetime.strptime(self.get_end_time(), "%H:%M").time()

        if current_date > self.date:
            # This shouldn't occur in main operation
            return ("Past Date")

        elif current_date < self.date:
            # This shouldn't occur in main operation
            return ("Future Date")

        elif current_date == self.date:
            if current_time < start_time:
                return("Upcoming")
            if current_time > end_time:
                return("Finished")
            else:
                return("Ongoing")

        else:
            return ("Unkown")

    def gradient_delete(self,  *args, **kwargs):
        # if less than 2 weeks 50% room cost, full catering
        # if less than 1 week full cost.
        current_date = datetime.now().date()
        date_diff = self.date - current_date

        cost = Cost.objects.get(booking=self)
        print(date_diff.days)

        if date_diff.days <= 7:
            print("full cost")

        elif date_diff.days <= 14:
            print("slight cost")
            cost.roomPrice = cost.roomPrice / 2
            cost.save()

        else:
            print("no cost")
            print("delete cost")
            self.delete()
            
        self.active = False
        
        super().save(*args, **kwargs)


class Cost(models.Model):
    booking = models.OneToOneField(Booking, on_delete=CASCADE)
    roomPrice = models.DecimalField(max_digits=100, decimal_places=2)
    extraPrice = models.DecimalField(max_digits=100, decimal_places=2)

    def __str__(self):
        return self.booking.title

    def get_total_cost(self):
        return self.roomPrice + self.extraPrice

    def invoice_string(self):
        extras = ExtraBookingMap.objects.filter(booking=self.booking)
        book = Internal_Booking.objects.get(pk=self.booking.id)

        d = Decimal(0.2)
        #print(d)

        user_id = str(book.account.id)
        date = self.booking.date
        date = date.strftime("%Y-%m-%d")

        desc = "Room " + str(self.booking.room)
        quantity = "1"
        unit = "Hour"
        value = self.roomPrice
        value_per_unit = self.booking.room.price
        vat = (d * value).quantize(Decimal('.00'))

        total_cost = value + vat

        room_string = user_id + "," + date + "," + desc + "," + quantity + "," + unit + "," + str(value) + "," + str(value_per_unit) + "," + str(vat) + "," + str(total_cost) + "\n"

        extras_string = ""

        for x in extras:
            e_desc = str(x.extra)
            e_quantity = x.quantity
            e_unit = "Unit"

            e_value = x.extra.price * x.quantity
            e_value_per_unit = x.extra.price
            e_vat = (e_value * d).quantize(Decimal('.00'))
            
            e_total_cost = e_value + e_vat

            extras_string = extras_string + user_id + "," + date + "," + e_desc + "," + str(e_quantity) + "," + e_unit + "," + str(e_value) + "," + str(e_value_per_unit) + "," + str(e_vat) + "," + str(e_total_cost) + "\n"

        return room_string + extras_string

    def generate_invoice_file(self):
        extras = ExtraBookingMap.objects.filter(booking=self.booking)
        book = Internal_Booking.objects.get(pk=self.booking.id)

        d = Decimal(0.2)
        print(d)

        user_id = str(book.account.id)
        date = self.booking.date
        date = date.strftime("%Y-%m-%d")

        desc = "Room " + str(self.booking.room)
        quantity = "1"
        unit = "Hour"
        value = self.roomPrice
        value_per_unit = self.booking.room.price
        vat = (d * value).quantize(Decimal('.00'))

        total_cost = self.get_total_cost() + vat

        path = "invoice\\" + str(self) +  "-" + str(self.booking.id) + "-" + date + ".csv"
        print("path: ", path)

        joined_path = os.path.join (MEDIA_ROOT , path )

        print("joined: ", joined_path)

        f = open(joined_path, "w")
        file = File(f)

        room_string = user_id + "," + date + "," + desc + "," + quantity + "," + unit + "," + str(value) + "," + str(value_per_unit) + "," + str(vat) + "," + str(total_cost)

        print("TYPE: ", type(room_string))

        #f = File.open(path, 'w')

        file.write(room_string)

        file.close()


class Internal_Booking(Booking):
    account = models.ForeignKey(User, on_delete=CASCADE)


class External_Booking(Booking):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    company = models.CharField(max_length=200)


class ExtraBookingMap(models.Model):
    extra = models.ForeignKey(Extra, on_delete=CASCADE)
    booking = models.ForeignKey(Booking, on_delete=CASCADE)
    quantity = models.IntegerField(default=0)
    timing = models.TimeField(default='00:00')
    note = models.TextField(blank=True)

    def clean(self):
        cleaned_data = super().clean()

        if self.quantity < 1:
            raise ValidationError("Cannot have a negative quantity of an extra.")

        return cleaned_data


class Image(models.Model):
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to="images")

    def __str__(self):
        return self.title