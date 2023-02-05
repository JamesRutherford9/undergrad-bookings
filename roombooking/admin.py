from django.contrib import admin

from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from .models import Account, Building, Company, ExtraBookingMap, Room, Booking, Extra, Internal_Booking, External_Booking, Cost

# Register your models here.

class AccountInline(admin.StackedInline):
    model = Account
    can_delete = False
    verbose_name_plural = 'account'

class UserAdmin(BaseUserAdmin):
    inlines = (AccountInline,)


class AccountAdmin(admin.ModelAdmin):
    list_display = ('user', 'company', 'admin')

    search_fields=['user']
    list_filter=['company']

class RoomAdmin(admin.ModelAdmin):
    list_filter=['building']

class BookingAdmin(admin.ModelAdmin):
    list_display = ('room', 'date', 'startTime', 'verification', )
    list_filter = ['room', 'date', 'verification', 'active',]

class InternalBookingAdmin(BookingAdmin):
    list_display = ('title', 'room', 'date', 'startTime', 'verification', 'account')
    list_filter = ['account', 'active', 'room', 'date']

class ExtraAdmin(admin.ModelAdmin):
    list_display = ('name', 'extra_type')

admin.site.register(Company)

class ExtraMapAdmin(admin.ModelAdmin):
    list_filter = ['booking', 'extra',]

# admin.site.register(Account)
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

admin.site.register(Building)
admin.site.register(Room, RoomAdmin)
admin.site.register(Internal_Booking, InternalBookingAdmin)
admin.site.register(External_Booking)
admin.site.register(Booking, BookingAdmin)
admin.site.register(Extra)
admin.site.register(ExtraBookingMap, ExtraMapAdmin)
admin.site.register(Cost)