'''
Build a complete Travel Booking Management System using Python OOP.

It must support:

Customer
Agent
Hotel
Room
Flight
Airline
HotelBooking
FlightBooking
Payment
Invoice
Cancellation
Discount
Notification

Required operations:

Customer registration
Hotel booking
Flight booking
Room availability
Payment
Cancellation
Refund
Invoice generation
Discount calculation
Booking history
Revenue calculation
'''

"""
Travel Booking Management System
=================================
A complete OOP-based system for managing hotel and flight bookings,
payments, invoices, cancellations, refunds, discounts, and notifications.
"""

from __future__ import annotations
from datetime import datetime, date
from enum import Enum
from typing import List, Optional, Dict
from uuid import uuid4
import itertools


# ----------------------------------------------------------------------
# ENUMS
# ----------------------------------------------------------------------

class BookingStatus(Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"


class PaymentStatus(Enum):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"


class PaymentMethod(Enum):
    CREDIT_CARD = "CREDIT_CARD"
    DEBIT_CARD = "DEBIT_CARD"
    UPI = "UPI"
    NET_BANKING = "NET_BANKING"
    WALLET = "WALLET"


class RoomType(Enum):
    SINGLE = "SINGLE"
    DOUBLE = "DOUBLE"
    DELUXE = "DELUXE"
    SUITE = "SUITE"


class SeatClass(Enum):
    ECONOMY = "ECONOMY"
    BUSINESS = "BUSINESS"
    FIRST = "FIRST"


def gen_id(prefix: str) -> str:
    return f"{prefix}-{uuid4().hex[:8].upper()}"


# ----------------------------------------------------------------------
# NOTIFICATION
# ----------------------------------------------------------------------

class Notification:
    """Handles sending notifications (simulated via console output)."""

    def __init__(self):
        self._log: List[Dict] = []

    def send(self, recipient: "Customer", subject: str, message: str) -> None:
        record = {
            "id": gen_id("NOTIF"),
            "to": recipient.email,
            "subject": subject,
            "message": message,
            "timestamp": datetime.now(),
        }
        self._log.append(record)
        print(f"[NOTIFICATION -> {recipient.name} <{recipient.email}>] "
              f"{subject}: {message}")

    def history(self) -> List[Dict]:
        return self._log


# ----------------------------------------------------------------------
# PEOPLE: CUSTOMER & AGENT
# ----------------------------------------------------------------------

class Customer:
    def __init__(self, name: str, email: str, phone: str):
        self.customer_id = gen_id("CUST")
        self.name = name
        self.email = email
        self.phone = phone
        self.registered_on = datetime.now()
        self.hotel_bookings: List["HotelBooking"] = []
        self.flight_bookings: List["FlightBooking"] = []

    def booking_history(self) -> List[Dict]:
        history = []
        for hb in self.hotel_bookings:
            history.append({
                "type": "HOTEL",
                "booking_id": hb.booking_id,
                "status": hb.status.value,
                "amount": hb.total_amount,
                "date": hb.booking_date,
            })
        for fb in self.flight_bookings:
            history.append({
                "type": "FLIGHT",
                "booking_id": fb.booking_id,
                "status": fb.status.value,
                "amount": fb.total_amount,
                "date": fb.booking_date,
            })
        history.sort(key=lambda x: x["date"])
        return history

    def __repr__(self):
        return f"Customer({self.customer_id}, {self.name})"


class Agent:
    """Represents a booking agent who can create bookings on behalf of customers."""

    def __init__(self, name: str, email: str, agency: str = "Independent"):
        self.agent_id = gen_id("AGT")
        self.name = name
        self.email = email
        self.agency = agency
        self.commission_rate = 0.05  # 5% commission on bookings handled
        self.handled_bookings: List[str] = []

    def record_booking(self, booking_id: str) -> None:
        self.handled_bookings.append(booking_id)

    def calculate_commission(self, amount: float) -> float:
        return round(amount * self.commission_rate, 2)

    def __repr__(self):
        return f"Agent({self.agent_id}, {self.name}, {self.agency})"


# ----------------------------------------------------------------------
# HOTEL & ROOM
# ----------------------------------------------------------------------

class Room:
    def __init__(self, room_number: str, room_type: RoomType, price_per_night: float):
        self.room_number = room_number
        self.room_type = room_type
        self.price_per_night = price_per_night
        self.is_available = True

    def __repr__(self):
        status = "Available" if self.is_available else "Booked"
        return f"Room({self.room_number}, {self.room_type.value}, ${self.price_per_night}/night, {status})"


class Hotel:
    def __init__(self, name: str, city: str, star_rating: int = 3):
        self.hotel_id = gen_id("HTL")
        self.name = name
        self.city = city
        self.star_rating = star_rating
        self.rooms: List[Room] = []

    def add_room(self, room: Room) -> None:
        self.rooms.append(room)

    def available_rooms(self, room_type: Optional[RoomType] = None) -> List[Room]:
        rooms = [r for r in self.rooms if r.is_available]
        if room_type:
            rooms = [r for r in rooms if r.room_type == room_type]
        return rooms

    def find_room(self, room_number: str) -> Optional[Room]:
        for r in self.rooms:
            if r.room_number == room_number:
                return r
        return None

    def __repr__(self):
        return f"Hotel({self.hotel_id}, {self.name}, {self.city}, {self.star_rating}*)"


# ----------------------------------------------------------------------
# FLIGHT & AIRLINE
# ----------------------------------------------------------------------

class Airline:
    def __init__(self, name: str, code: str):
        self.airline_id = gen_id("AIRL")
        self.name = name
        self.code = code
        self.flights: List["Flight"] = []

    def add_flight(self, flight: "Flight") -> None:
        self.flights.append(flight)

    def __repr__(self):
        return f"Airline({self.code}, {self.name})"


class Flight:
    def __init__(self, flight_number: str, airline: Airline, origin: str,
                 destination: str, departure: datetime, arrival: datetime,
                 total_seats: int, base_fare: float):
        self.flight_id = gen_id("FLT")
        self.flight_number = flight_number
        self.airline = airline
        self.origin = origin
        self.destination = destination
        self.departure = departure
        self.arrival = arrival
        self.total_seats = total_seats
        self.seats_booked = 0
        self.base_fare = base_fare
        airline.add_flight(self)

    def seats_available(self) -> int:
        return self.total_seats - self.seats_booked

    def fare_for_class(self, seat_class: SeatClass) -> float:
        multiplier = {
            SeatClass.ECONOMY: 1.0,
            SeatClass.BUSINESS: 2.5,
            SeatClass.FIRST: 4.0,
        }
        return round(self.base_fare * multiplier[seat_class], 2)

    def book_seats(self, count: int) -> bool:
        if self.seats_available() >= count:
            self.seats_booked += count
            return True
        return False

    def release_seats(self, count: int) -> None:
        self.seats_booked = max(0, self.seats_booked - count)

    def __repr__(self):
        return (f"Flight({self.flight_number}, {self.origin}->{self.destination}, "
                f"{self.departure.strftime('%Y-%m-%d %H:%M')}, seats left={self.seats_available()})")


# ----------------------------------------------------------------------
# DISCOUNT
# ----------------------------------------------------------------------

class Discount:
    """Represents a discount/promo code applied to a booking amount."""

    def __init__(self, code: str, percentage: float = 0.0, flat_amount: float = 0.0,
                 max_discount: Optional[float] = None, active: bool = True):
        self.code = code.upper()
        self.percentage = percentage
        self.flat_amount = flat_amount
        self.max_discount = max_discount
        self.active = active

    def calculate(self, amount: float) -> float:
        if not self.active:
            return 0.0
        discount = amount * (self.percentage / 100.0)
        if self.max_discount is not None:
            discount = min(discount, self.max_discount)
        discount += self.flat_amount
        return round(min(discount, amount), 2)

    def __repr__(self):
        return f"Discount({self.code}, {self.percentage}% + ${self.flat_amount}, active={self.active})"


class DiscountRegistry:
    def __init__(self):
        self._codes: Dict[str, Discount] = {}

    def add(self, discount: Discount) -> None:
        self._codes[discount.code] = discount

    def get(self, code: str) -> Optional[Discount]:
        return self._codes.get(code.upper())

    def apply(self, code: str, amount: float) -> float:
        d = self.get(code)
        return d.calculate(amount) if d else 0.0


# ----------------------------------------------------------------------
# PAYMENT
# ----------------------------------------------------------------------

class Payment:
    def __init__(self, amount: float, method: PaymentMethod):
        self.payment_id = gen_id("PAY")
        self.amount = amount
        self.method = method
        self.status = PaymentStatus.PENDING
        self.timestamp = datetime.now()

    def process(self) -> bool:
        """Simulates payment processing. In real life this would call a gateway."""
        self.status = PaymentStatus.SUCCESS
        self.timestamp = datetime.now()
        return True

    def refund(self) -> bool:
        if self.status == PaymentStatus.SUCCESS:
            self.status = PaymentStatus.REFUNDED
            return True
        return False

    def __repr__(self):
        return f"Payment({self.payment_id}, ${self.amount}, {self.method.value}, {self.status.value})"


# ----------------------------------------------------------------------
# INVOICE
# ----------------------------------------------------------------------

class Invoice:
    def __init__(self, booking: "BaseBooking", payment: Payment):
        self.invoice_id = gen_id("INV")
        self.booking = booking
        self.payment = payment
        self.issued_on = datetime.now()

    def generate(self) -> str:
        b = self.booking
        lines = [
            "=" * 50,
            f"INVOICE: {self.invoice_id}",
            "=" * 50,
            f"Issued On     : {self.issued_on.strftime('%Y-%m-%d %H:%M:%S')}",
            f"Booking ID    : {b.booking_id}",
            f"Booking Type  : {b.__class__.__name__}",
            f"Customer      : {b.customer.name} ({b.customer.email})",
            f"Subtotal      : ${b.subtotal:.2f}",
            f"Discount      : -${b.discount_amount:.2f}",
            f"Total Amount  : ${b.total_amount:.2f}",
            f"Payment ID    : {self.payment.payment_id}",
            f"Payment Method: {self.payment.method.value}",
            f"Payment Status: {self.payment.status.value}",
            "=" * 50,
        ]
        return "\n".join(lines)

    def __repr__(self):
        return f"Invoice({self.invoice_id}, booking={self.booking.booking_id})"


# ----------------------------------------------------------------------
# CANCELLATION
# ----------------------------------------------------------------------

class Cancellation:
    """Handles cancellation logic and refund calculation for a booking."""

    # Refund policy: % of amount refunded based on days before service date
    REFUND_POLICY = [
        (7, 0.90),   # 7+ days before: 90% refund
        (3, 0.50),   # 3-6 days before: 50% refund
        (1, 0.20),   # 1-2 days before: 20% refund
        (0, 0.0),    # less than 1 day / same day: no refund
    ]

    def __init__(self, booking: "BaseBooking", reason: str = ""):
        self.cancellation_id = gen_id("CNL")
        self.booking = booking
        self.reason = reason
        self.cancelled_on = datetime.now()
        self.refund_amount: float = 0.0
        self.refund_processed = False

    def _refund_percentage(self, days_before: int) -> float:
        for threshold, pct in self.REFUND_POLICY:
            if days_before >= threshold:
                return pct
        return 0.0

    def process(self, service_date: date) -> float:
        days_before = (service_date - date.today()).days
        pct = self._refund_percentage(max(days_before, 0))
        self.refund_amount = round(self.booking.total_amount * pct, 2)

        self.booking.status = BookingStatus.CANCELLED
        if self.booking.payment and self.booking.payment.status == PaymentStatus.SUCCESS:
            self.booking.payment.refund()
            self.refund_processed = True

        return self.refund_amount

    def __repr__(self):
        return f"Cancellation({self.cancellation_id}, refund=${self.refund_amount})"


# ----------------------------------------------------------------------
# BOOKINGS (BASE + HOTEL + FLIGHT)
# ----------------------------------------------------------------------

class BaseBooking:
    """Common base for all booking types."""

    def __init__(self, customer: Customer, agent: Optional[Agent] = None):
        self.booking_id = gen_id("BKG")
        self.customer = customer
        self.agent = agent
        self.booking_date = datetime.now()
        self.status = BookingStatus.PENDING
        self.subtotal: float = 0.0
        self.discount_amount: float = 0.0
        self.total_amount: float = 0.0
        self.payment: Optional[Payment] = None
        self.invoice: Optional[Invoice] = None

    def apply_discount(self, discount_registry: DiscountRegistry, code: Optional[str]) -> None:
        self.discount_amount = discount_registry.apply(code, self.subtotal) if code else 0.0
        self.total_amount = round(self.subtotal - self.discount_amount, 2)

    def pay(self, method: PaymentMethod) -> Payment:
        payment = Payment(self.total_amount, method)
        payment.process()
        self.payment = payment
        if payment.status == PaymentStatus.SUCCESS:
            self.status = BookingStatus.CONFIRMED
        if self.agent:
            self.agent.record_booking(self.booking_id)
        return payment

    def generate_invoice(self) -> Invoice:
        if not self.payment:
            raise ValueError("Cannot generate invoice before payment is made.")
        self.invoice = Invoice(self, self.payment)
        return self.invoice


class HotelBooking(BaseBooking):
    def __init__(self, customer: Customer, hotel: Hotel, room: Room,
                 check_in: date, check_out: date, agent: Optional[Agent] = None):
        super().__init__(customer, agent)
        if not room.is_available:
            raise ValueError(f"Room {room.room_number} is not available.")
        if check_out <= check_in:
            raise ValueError("Check-out date must be after check-in date.")

        self.hotel = hotel
        self.room = room
        self.check_in = check_in
        self.check_out = check_out
        self.nights = (check_out - check_in).days

        room.is_available = False
        self.subtotal = round(room.price_per_night * self.nights, 2)
        self.total_amount = self.subtotal

        customer.hotel_bookings.append(self)

    def cancel(self) -> Cancellation:
        cancellation = Cancellation(self, reason="Customer requested")
        cancellation.process(self.check_in)
        self.room.is_available = True
        return cancellation

    def __repr__(self):
        return (f"HotelBooking({self.booking_id}, {self.hotel.name}, "
                f"room={self.room.room_number}, {self.nights} nights, "
                f"total=${self.total_amount}, status={self.status.value})")


class FlightBooking(BaseBooking):
    def __init__(self, customer: Customer, flight: Flight, seat_class: SeatClass,
                 num_passengers: int = 1, agent: Optional[Agent] = None):
        super().__init__(customer, agent)
        if flight.seats_available() < num_passengers:
            raise ValueError(f"Not enough seats available on flight {flight.flight_number}.")

        self.flight = flight
        self.seat_class = seat_class
        self.num_passengers = num_passengers

        flight.book_seats(num_passengers)
        fare = flight.fare_for_class(seat_class)
        self.subtotal = round(fare * num_passengers, 2)
        self.total_amount = self.subtotal

        customer.flight_bookings.append(self)

    def cancel(self) -> Cancellation:
        cancellation = Cancellation(self, reason="Customer requested")
        cancellation.process(self.flight.departure.date())
        self.flight.release_seats(self.num_passengers)
        return cancellation

    def __repr__(self):
        return (f"FlightBooking({self.booking_id}, {self.flight.flight_number}, "
                f"{self.seat_class.value}, pax={self.num_passengers}, "
                f"total=${self.total_amount}, status={self.status.value})")


# ----------------------------------------------------------------------
# TRAVEL BOOKING SYSTEM (FACADE / ORCHESTRATOR)
# ----------------------------------------------------------------------

class TravelBookingSystem:
    """Top-level system tying together all entities and operations."""

    def __init__(self):
        self.customers: Dict[str, Customer] = {}
        self.agents: Dict[str, Agent] = {}
        self.hotels: Dict[str, Hotel] = {}
        self.airlines: Dict[str, Airline] = {}
        self.hotel_bookings: List[HotelBooking] = []
        self.flight_bookings: List[FlightBooking] = []
        self.discount_registry = DiscountRegistry()
        self.notifier = Notification()

    # ---------------- Registration ----------------

    def register_customer(self, name: str, email: str, phone: str) -> Customer:
        customer = Customer(name, email, phone)
        self.customers[customer.customer_id] = customer
        self.notifier.send(customer, "Welcome!", f"Hi {name}, your account has been created.")
        return customer

    def register_agent(self, name: str, email: str, agency: str = "Independent") -> Agent:
        agent = Agent(name, email, agency)
        self.agents[agent.agent_id] = agent
        return agent

    def add_hotel(self, hotel: Hotel) -> None:
        self.hotels[hotel.hotel_id] = hotel

    def add_airline(self, airline: Airline) -> None:
        self.airlines[airline.airline_id] = airline

    def add_discount(self, discount: Discount) -> None:
        self.discount_registry.add(discount)

    # ---------------- Availability ----------------

    def check_room_availability(self, hotel: Hotel, room_type: Optional[RoomType] = None) -> List[Room]:
        return hotel.available_rooms(room_type)

    def check_flight_seats(self, flight: Flight) -> int:
        return flight.seats_available()

    # ---------------- Booking Operations ----------------

    def book_hotel(self, customer: Customer, hotel: Hotel, room: Room,
                   check_in: date, check_out: date, payment_method: PaymentMethod,
                   discount_code: Optional[str] = None,
                   agent: Optional[Agent] = None) -> HotelBooking:
        booking = HotelBooking(customer, hotel, room, check_in, check_out, agent)
        booking.apply_discount(self.discount_registry, discount_code)
        booking.pay(payment_method)
        booking.generate_invoice()
        self.hotel_bookings.append(booking)
        self.notifier.send(
            customer, "Hotel Booking Confirmed",
            f"Your booking at {hotel.name} ({room.room_number}) is confirmed. "
            f"Total: ${booking.total_amount}"
        )
        return booking

    def book_flight(self, customer: Customer, flight: Flight, seat_class: SeatClass,
                     payment_method: PaymentMethod, num_passengers: int = 1,
                     discount_code: Optional[str] = None,
                     agent: Optional[Agent] = None) -> FlightBooking:
        booking = FlightBooking(customer, flight, seat_class, num_passengers, agent)
        booking.apply_discount(self.discount_registry, discount_code)
        booking.pay(payment_method)
        booking.generate_invoice()
        self.flight_bookings.append(booking)
        self.notifier.send(
            customer, "Flight Booking Confirmed",
            f"Your flight {flight.flight_number} ({flight.origin}->{flight.destination}) "
            f"is confirmed. Total: ${booking.total_amount}"
        )
        return booking

    # ---------------- Cancellation / Refund ----------------

    def cancel_hotel_booking(self, booking: HotelBooking) -> Cancellation:
        cancellation = booking.cancel()
        self.notifier.send(
            booking.customer, "Hotel Booking Cancelled",
            f"Booking {booking.booking_id} cancelled. Refund: ${cancellation.refund_amount}"
        )
        return cancellation

    def cancel_flight_booking(self, booking: FlightBooking) -> Cancellation:
        cancellation = booking.cancel()
        self.notifier.send(
            booking.customer, "Flight Booking Cancelled",
            f"Booking {booking.booking_id} cancelled. Refund: ${cancellation.refund_amount}"
        )
        return cancellation

    # ---------------- Reporting ----------------

    def booking_history(self, customer: Customer) -> List[Dict]:
        return customer.booking_history()

    def total_revenue(self) -> float:
        """Total amount currently collected (successful, non-refunded payments)."""
        total = 0.0
        for b in itertools.chain(self.hotel_bookings, self.flight_bookings):
            if b.payment and b.payment.status == PaymentStatus.SUCCESS:
                total += b.total_amount
        return round(total, 2)

    def net_revenue(self) -> float:
        """Gross revenue collected minus refunds issued."""
        gross = 0.0
        refunded = 0.0
        for b in itertools.chain(self.hotel_bookings, self.flight_bookings):
            if b.payment and b.payment.status in (PaymentStatus.SUCCESS, PaymentStatus.REFUNDED):
                gross += b.total_amount
            if b.payment and b.payment.status == PaymentStatus.REFUNDED:
                refunded += b.total_amount
        return round(gross - refunded, 2)

    def revenue_by_type(self) -> Dict[str, float]:
        hotel_rev = sum(
            b.total_amount for b in self.hotel_bookings
            if b.payment and b.payment.status == PaymentStatus.SUCCESS
        )
        flight_rev = sum(
            b.total_amount for b in self.flight_bookings
            if b.payment and b.payment.status == PaymentStatus.SUCCESS
        )
        return {"hotel": round(hotel_rev, 2), "flight": round(flight_rev, 2)}


# ----------------------------------------------------------------------
# DEMO / SAMPLE USAGE
# ----------------------------------------------------------------------

def run_demo():
    print("\n" + "#" * 60)
    print("TRAVEL BOOKING MANAGEMENT SYSTEM - DEMO")
    print("#" * 60 + "\n")

    system = TravelBookingSystem()

    system.add_discount(Discount("WELCOME10", percentage=10, max_discount=50))
    system.add_discount(Discount("FLAT20", flat_amount=20))

    hotel = Hotel("Grand Palace", "Kolkata", star_rating=5)
    hotel.add_room(Room("101", RoomType.SINGLE, 60))
    hotel.add_room(Room("102", RoomType.DOUBLE, 100))
    hotel.add_room(Room("201", RoomType.DELUXE, 150))
    system.add_hotel(hotel)

    airline = Airline("IndiGo", "6E")
    flight = Flight(
        flight_number="6E-202",
        airline=airline,
        origin="Kolkata",
        destination="Delhi",
        departure=datetime(2026, 10, 5, 8, 30),
        arrival=datetime(2026, 10, 5, 10, 45),
        total_seats=150,
        base_fare=80,
    )
    system.add_airline(airline)

    customer = system.register_customer("Tanmoy Roy", "tanmoy@example.com", "9876543210")
    agent = system.register_agent("Priya Sharma", "priya@travelagency.com", "TravelEase")

    print("\n--- Checking Availability ---")
    print("Available rooms:", system.check_room_availability(hotel))
    print("Available seats on flight:", system.check_flight_seats(flight))

    print("\n--- Booking a Hotel Room ---")
    room = hotel.find_room("201")
    hotel_booking = system.book_hotel(
        customer=customer,
        hotel=hotel,
        room=room,
        check_in=date(2026, 10, 4),
        check_out=date(2026, 10, 7),
        payment_method=PaymentMethod.CREDIT_CARD,
        discount_code="WELCOME10",
        agent=agent,
    )
    print(hotel_booking)
    print(hotel_booking.invoice.generate())

    print("\n--- Booking a Flight ---")
    flight_booking = system.book_flight(
        customer=customer,
        flight=flight,
        seat_class=SeatClass.BUSINESS,
        payment_method=PaymentMethod.UPI,
        num_passengers=2,
        discount_code="FLAT20",
        agent=agent,
    )
    print(flight_booking)
    print(flight_booking.invoice.generate())

    print("\n--- Booking History ---")
    for entry in system.booking_history(customer):
        print(entry)

    print("\n--- Cancelling Hotel Booking ---")
    cancellation = system.cancel_hotel_booking(hotel_booking)
    print(cancellation)
    print("Room now available again:", room.is_available)

    print("\n--- Revenue Reports ---")
    print("Total revenue (active only):", system.total_revenue())
    print("Net revenue (after refunds):", system.net_revenue())
    print("Revenue by type:", system.revenue_by_type())

    print("\n--- Agent Commission ---")
    print(f"{agent.name} handled {len(agent.handled_bookings)} bookings, "
          f"commission on flight booking: ${agent.calculate_commission(flight_booking.total_amount)}")


if __name__ == "__main__":
    run_demo()