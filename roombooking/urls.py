from roombooking.views.main_views import booking_login, booking_logout
from roombooking.views.booking_views import image_upload
from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

app_name = 'roombooking'
urlpatterns = [
    path('', views.index, name='index'),
    path('viewbookings/', views.view_bookings, name='viewbookings'),
    
    # path('accounts/login/', auth_views.LoginView.as_view(), name='login'),
    # path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),

    path('accounts/login/', views.booking_login, name='login'),
    path('accounts/logout/', views.booking_logout, name='logout'),

    path('accounts/profile/', views.profile_view, name='profile'),

    # Create Bookings URLs
    path('viewdates/', views.view_dates, name='viewdates'),
    path('viewdates/<int:selected_building>/<str:selected_date>', views.view_dates, name='viewdatesargs'),

    path('createbooking/', views.create_booking, name='createbooking'),
    path('createbooking/<int:roomID>/<int:timeslot>/<str:date>/', views.create_booking, name='createbookingargs'),

    path('uploadform/', views.image_upload, name='uploadform'),

    # Booking View and Edit
    path('confirmbooking/<int:booking_id>', views.confirm_booking, name='confirmbooking'),
    path('editbooking/<int:booking_id>/', views.edit_booking, name='editbooking'),
    path('viewbooking/<int:booking_id>/', views.view_booking, name='viewbooking'),

    # Chatbot Urls
    path('chatbot/', views.chatbot, name="chatbot"),

    # Current Booking Interactions
    path('todaysbookings/', views.view_todays_bookings, name="todaysbookings"),
    path('todaysbookings/<int:booking_id>/', views.todays_booking_specific, name="specificbookingtoday"),

    # Room Admin Pages
    path('invoices/', views.invoice_gen_view, name='invoices'),
    path('viewbookingsadmin/', views.view_bookings_admin, name='viewbookingsadmin'),
    path('adminedit/<int:booking_id>/', views.admin_edit, name='adminedit'),
    path('dailytimeline/', views.daily_timeline, name='dailytimeline'),

]