from django.test import TestCase
from django.db import IntegrityError
import datetime

from ..models import *

class BuildingTestCase(TestCase):
    def test_building_roomNumberCantBeZero(self):
        '''
        Building cannot have a total number of rooms less than 1.
        '''
        b = Building(address="", name="Building", totalRooms=0, owner="Example")

        self.assertRaises(ValidationError, b.clean)

    def test_building_requiredInfo(self):
        b = Building()

        b.save()

class BookingTestCase(TestCase):
    '''
    Booking model tests.
    '''
    def setUp(self):
        Building.objects.create(address="Example Address", name="Building", totalRooms=5, owner="Example")
        Room.objects.create(building_id=1, name="Example Room", size=10, price=10.00, maxOccupancy=10)

        Booking.objects.create(title="First", room_id=1, date=datetime.strptime("2022-04-01", "%Y-%m-%d").date(), startTime=0, length=1, attendees=5)
        Booking.objects.create(title="Second", room_id=1, date=datetime.strptime("2022-04-02", "%Y-%m-%d").date(), startTime=2, length=2, attendees=4)

    def test_booking_requiredInfo(self):
        b = Booking()

        self.assertRaises(IntegrityError, b.save)

    # Attendee Tests
    def test_booking_attendeesMoreThanZero(self):
        '''
        Booking attendees must be more than 0.
        '''
        b = Booking(title="Fail", room_id=1, date=datetime.strptime("2023-04-01", "%Y-%m-%d").date(), attendees=0)

        self.assertRaises(ValidationError, b.clean)

    def test_booking_attendeesLessThanRoomOccupancy(self):
        '''
        Booking attendees must be less than room occupancy.
        '''
        b = Booking(title="Fail", room_id=1, date=datetime.strptime("2023-04-01", "%Y-%m-%d").date(), attendees=11)

        self.assertRaises(ValidationError, b.clean)

    # Date Tests
    def test_booking_dateCannotBeInPast(self):
        '''
        Booking cannot be in past.
        '''
        b = Booking(title="Not In Past", room_id=1, date=datetime.strptime("2020-04-01", "%Y-%m-%d").date(), attendees=5)
        self.assertRaises(ValidationError, b.clean)

    # Booking time tests
    def test_booking_cannotBeLaterThanClosing(self):
        '''
        Booking end time cannot be later than closing.
        '''
        b = Booking(title="Fail", room_id=1, date=datetime.strptime("2023-04-01", "%Y-%m-%d").date(), attendees=5, startTime=0, length=22)

        self.assertRaises(ValidationError, b.clean)

    def test_booking_startCannotBeLaterThanClosing(self):
        '''
        Booking start time cannot be later than closing.
        '''
        b = Booking(title="Fail", room_id=1, date=datetime.strptime("2023-04-01", "%Y-%m-%d").date(), attendees=5, startTime=24)

        self.assertRaises(ValidationError, b.clean)

    def test_booking_cannotOverlapAnotherBookingSameStartTime(self):
        '''
        Booking cannot overlap with another bookings start time.
        '''
        b = Booking(title="Overlap", room_id=1, date=datetime.strptime("2022-04-01", "%Y-%m-%d").date(), startTime=0, length=0, attendees=3)
        self.assertRaises(ValidationError, b.clean)


    def test_booking_cannotOverlapAnotherBookingOtherTime(self):
        '''
        Booking length cannot overlap with another bookings start time.
        '''
        b = Booking(title="Overlap", room_id=1, date=datetime.strptime("2022-04-02", "%Y-%m-%d").date(), startTime=1, length=4, attendees=3)
        self.assertRaises(ValidationError, b.clean)

    def test_booking_cannotOverlapAnotherBookingStartTimeWithinLength(self):
        '''
        Booking cannot overlap with another bookings length.
        '''
        b = Booking(title="Overlap", room_id=1, date=datetime.strptime("2022-04-02", "%Y-%m-%d").date(), startTime=3, length=4, attendees=3)
        self.assertRaises(ValidationError, b.clean)

    # Functional Tests
    # Cost Gen Functions
    def test_booking_canGenerateCost(self):
        '''
        Booking has function to generate costs.
        '''
        b = Booking.objects.get(title="First")
        b.generateCosts()

        cost = Cost.objects.get(booking=b)

        self.assertEqual(True, Cost.objects.filter(booking=b).exists())

    def test_booking_onlyOneCostPerBooking(self):
        '''
        Only one cost associated with booking.
        '''
        b = Booking.objects.get(title="First")
        b.generateCosts()
        b.generateCosts()
        b.generateCosts()

        self.assertEqual(1, Cost.objects.filter(booking=b).count())

    def test_booking_canGetEnd(self):
        '''
        Booking can get the end time of booking as string.
        '''
        b = Booking.objects.get(title="First")
        
        self.assertEqual("8:30", b.get_end_time())

    def test_booking_canIdentifyUpcoming(self):
        '''
        Booking has function to identify status of booking.
        '''
        b = Booking.objects.get(title="First")

        self.assertEqual("Future Date", b.get_status())

    # Gradient Deletion Function
    def test_booking_gradientDelete(self):
        '''
        Booking has a gradient delete option.
        '''

        currentDate = datetime.now()

        plusWeek = currentDate + timedelta(days=3)

        plus2Week = currentDate + timedelta(days=9)

        moreThan2Weeks = currentDate + timedelta(days=20)
        
        lessThanWeek = Booking(title="LessThanWeek", room_id=1, date=plusWeek.date())
        lessThan2Week = Booking(title="Less than 2 weeks", room_id=1, date=plus2Week.date())
        further = Booking(title="Far Future", room_id=1, date=moreThan2Weeks.date())

        lessThanWeek.save()
        lessThan2Week.save()
        further.save()

        lessThanWeek.generateCosts()
        lessThan2Week.generateCosts()
        further.generateCosts()

        lessThanWeekFullCost = Cost.objects.get(booking=lessThanWeek).get_total_cost()
        lessThan2WeekHalfCost = Cost.objects.get(booking=lessThan2Week).roomPrice/2
        furtherFullCost = Cost.objects.get(booking=further)

        # Apply Delete Function
        lessThanWeek.gradient_delete()
        lessThan2Week.gradient_delete()
        further.gradient_delete()

        self.assertEqual(lessThanWeekFullCost, Cost.objects.get(booking=lessThanWeek).get_total_cost())
        self.assertEqual(False, lessThanWeek.active)

        self.assertEqual(lessThan2WeekHalfCost, Cost.objects.get(booking=lessThan2Week).roomPrice)
        self.assertEqual(False, lessThan2Week.active)

        self.assertEqual(False, Cost.objects.filter(booking=further).exists())
        self.assertEqual(False, further.active)

    def test_booking_requiredInfo(self):
        b = Booking()

        self.assertRaises(IntegrityError, b.save)

class RoomTestCase(TestCase):
    '''
    Tests for the Room model.
    '''
    def setUp(self):
        Building.objects.create(address="Example Address", name="Building", totalRooms=1, owner="Example")

    def test_room_Occupancy(self):
        r = Room(building_id=1, name="Room", size=1, price=10.00, maxOccupancy=0)

        self.assertRaises(ValidationError, r.clean)

        r2 = Room(building_id=1, name="Room", size=1, price=10.00, maxOccupancy=1001)

        self.assertRaises(ValidationError, r2.clean)

    def test_room_size(self):
        r = Room(building_id=1, name="Room", size=-10, price=10.00, maxOccupancy=10)

        self.assertRaises(ValidationError, r.clean)

    def test_room_price(self):
        r = Room(building_id=1, name="Room", size=10, price=-1, maxOccupancy=10)

        self.assertRaises(ValidationError, r.clean)

    def test_room_cannotExceedBuildingRooms(self):
        r = Room(building_id=1, name="Room", size=10, price=10.00, maxOccupancy=10)
        r.save()

        r2 = Room(building_id=1, name="Room", size=10, price=10.00, maxOccupancy=10)

        self.assertRaises(ValidationError, r2.clean)

    def test_room_requiredInfo(self):
        r = Room()
        self.assertRaises(IntegrityError, r.save)

class ExtraModelTestCase(TestCase):
    '''
    Tests for Extra & ExtraBookingMap Models
    '''
    def setUp(self):
        Building.objects.create(address="Example Address", name="Building", totalRooms=5, owner="Example")
        Room.objects.create(building_id=1, name="Example Room", size=10, price=10.00, maxOccupancy=10)

        Booking.objects.create(title="First", room_id=1, date=datetime.strptime("2022-04-01", "%Y-%m-%d").date(), startTime=0, length=1, attendees=5)

        Extra.objects.create(name="Example", price=10.00, supplier="Example")

    def test_extra_price(self):
        e = Extra(name="Example", price=-10, supplier="Example")

        self.assertRaises(ValidationError, e.clean)

    def test_extraBookingMap(self):
        b = Booking.objects.get(title="First")
        e = Extra.objects.get(name="Example")

        ebm = ExtraBookingMap(extra=e, booking=b, quantity=-1, timing='8:00')

        self.assertRaises(ValidationError, ebm.clean)

    def test_ebm_requiredInfo(self):
        ebm = ExtraBookingMap()

        self.assertRaises(IntegrityError, ebm.save)

    
class AccountTestCase(TestCase):
    def test_account_requiredInfo(self):
        a = Account()
        self.assertRaises(IntegrityError, a.save)
    
    def test_account_requiredUser(self):
        a = Account(user=None, company=None)

        self.assertRaises(IntegrityError, a.save)

class ExtraTestCase(TestCase):
    def test_extra_requiredInfo(self):
        e = Extra()
        
        self.assertRaises(IntegrityError, e.save)

    def test_extra_price(self):
        e = Extra(price = -10.00)

        self.assertRaises(ValidationError, e.clean)

class CostTestCase(TestCase):
    def setUp(self):
        Building.objects.create(address="Example Address", name="Building", totalRooms=5, owner="Example")
        Room.objects.create(building_id=1, name="Example Room", size=10, price=10.00, maxOccupancy=10)

        Booking.objects.create(title="First", room_id=1, date=datetime.strptime("2022-04-01", "%Y-%m-%d").date(), startTime=0, length=1, attendees=5)



    def test_cost_requiredInfo(self):
        c = Cost()

        self.assertRaises(IntegrityError, c.save)

    def test_cost_getTotalPrice(self):
        b = Booking.objects.get(title="First")

        b.generateCosts()
        c = Cost.objects.get(booking=b)
        x = c.get_total_cost()

        self.assertEqual(5.00, x)

