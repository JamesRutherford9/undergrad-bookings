# Page holding the forms for the bookings.
from logging import PlaceHolder
from django.db.models import fields
from django.forms import ModelForm, Form, DateField, DateInput, widgets, CharField, BooleanField, PasswordInput, IntegerField
from datetime import datetime
from django.forms.fields import ImageField
from django.forms.models import ModelChoiceField

from django.contrib.auth.models import User
from roombooking.models import *

class BookingForm(ModelForm):
    class Meta:
        model = Booking
        fields = ('title', 'room', 'date', 'startTime', 'length',  'attendees', 'note')
        labels = {'title': "Meeting Title", 'startTime':"Start Time", 'length':"Booking Length",}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['date'].widget.attrs.update({'placeholder':'YYYY:MM:DD', 'id':'datepicker'})

        self.fields['room'].empty_label=None

        self.fields['note'].label = ''
        self.fields['note'].widget.attrs.update({'placeholder':'Add an optional note...'})

    
class InternalBookingForm(BookingForm):
    class Meta(BookingForm.Meta):
        model = Internal_Booking

class BookingCreateForm(ModelForm):
    class Meta:
        model = Booking
        fields = ('title', 'length', 'attendees', 'room', 'date', 'startTime', 'note')
        labels = {'title': "Meeting Title", 'length':"Booking Length",}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['room'].widget = widgets.HiddenInput()
        self.fields['date'].widget = widgets.HiddenInput()
        self.fields['startTime'].widget = widgets.HiddenInput()

        self.fields['note'].label = ''
        self.fields['note'].widget.attrs.update({'placeholder':'Add an optional note...'})


class InternalBookingCreateForm(BookingCreateForm):
    class Meta(BookingCreateForm.Meta):
        model = Internal_Booking

class ExtraMapForm(ModelForm):
    class Meta:
        model = ExtraBookingMap
        fields = ('extra', 'quantity', 'timing', 'note')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['timing'].widget.attrs.update({'placeholder':'HH:MM', 'class':'timepicker'})

        self.fields['note'].label = ''
        self.fields['note'].widget.attrs.update({'placeholder':'Add an optional note...'})


class viewDateForm(Form):
    date = DateField(widget=DateInput(attrs={'placeholder':'YYYY-MM-DD', 'id':'datepicker', "onChange":'submit()'}))
    building = ModelChoiceField(queryset=Building.objects.all(), empty_label=None, widget=widgets.Select(attrs={'onChange':'submit()',}))
    
    
class chatForm(Form):
    user_input = fields.TextField()

class imageForm(Form):
    image_file = ImageField()

class imageClassForm(ModelForm):
    class Meta:
        model = Image
        fields = ('title', 'image')

class invoiceDatesForm(Form):
    date1 = DateField(widget=DateInput(attrs={'placeholder':'YYY:MM:DD', 'class':'datepicker'}))
    date2 = DateField(widget=DateInput(attrs={'placeholder':'YYY:MM:DD', 'class':'datepicker'}))

class bookingFilterForm(Form):
    title = fields.CharField()
    date_after = DateField(widget=DateInput(attrs={'placeholder':'YYY:MM:DD', 'class':'datepicker'}))
    date_before = DateField(widget=DateInput(attrs={'placeholder':'YYY:MM:DD', 'class':'datepicker'}))
    attendees = IntegerField()
    
class buildingSelectForm(Form):
    building = ModelChoiceField(queryset=Building.objects.all(), empty_label=None, widget=widgets.Select(attrs={'onChange':'submit()',}))

class filterForm(Form):
    title = CharField(max_length=100, required=False, widget=DateInput(attrs={'placeholder':'Meeting Title'}))
    start_date = DateField(required=False, widget=DateInput(attrs={'placeholder':'YYY:MM:DD', 'class':'datepicker'}))
    end_date = DateField(required=False, widget=DateInput(attrs={'placeholder':'YYY:MM:DD', 'class':'datepicker'}))
    room = ModelChoiceField(queryset=Room.objects.all(), required=False)
    include_deleted = BooleanField(required=False)

class adminFilterForm(Form):
    title = CharField(max_length=100, required=False, widget=DateInput(attrs={'placeholder':'Meeting Title'}))
    start_date = DateField(required=False, widget=DateInput(attrs={'placeholder':'YYY:MM:DD', 'class':'datepicker',}))
    end_date = DateField(required=False, widget=DateInput(attrs={'placeholder':'YYY:MM:DD', 'class':'datepicker'}))
    room = ModelChoiceField(queryset=Room.objects.all(), required=False)
    building = ModelChoiceField(queryset=Building.objects.all(), required=False)
    user = ModelChoiceField(queryset=User.objects.all(), required=False)
    include_deleted = BooleanField(required=False)

class loginForm(Form):
    username = CharField(max_length=100)
    password = CharField(max_length=100, widget=PasswordInput())