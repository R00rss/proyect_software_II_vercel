from typing import List, Optional
from pydantic import BaseModel, UUID4
import datetime


class AirplaneSeatBase(BaseModel):
    plane_id: str
    seat_number: str
    seat_type: str
    seat_status: str


class AirplaneSeatCreate(AirplaneSeatBase):
    pass


class AirplaneSeat(AirplaneSeatBase):
    id: UUID4

    class Config:
        from_attributes = True


class PlaneBase(BaseModel):
    model: str
    capacity: int
    serial_number: str
    code: str


class PlaneCreate(PlaneBase):
    pass


class Plane(PlaneBase):
    id: UUID4
    airplaneSeats: List[AirplaneSeat] = []

    class Config:
        from_attributes = True


class PilotBase(BaseModel):
    name: str
    lastname: str
    ci: str
    license: str


class PilotCreate(PilotBase):
    pass


class Pilot(PilotBase):
    id: UUID4

    class Config:
        from_attributes = True


class AirportBase(BaseModel):
    name: str
    city: str
    country: str
    code: str


class AirportCreate(AirportBase):
    pass


class Airport(AirportBase):
    id: UUID4

    class Config:
        from_attributes = True


class PassengerBase(BaseModel):
    name: str
    lastname: str
    ci: str
    phone: str
    email: str


class PassengerCreate(PassengerBase):
    pass


class Passenger(PassengerBase):
    id: UUID4

    class Config:
        from_attributes = True


class UserBase(BaseModel):
    name: str
    lastname: str
    ci: str
    phone: str
    email: str
    role: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: UUID4

    class Config:
        from_attributes = True


class LuggageBase(BaseModel):
    weight: float
    price: float


class LuggageCreate(LuggageBase):
    pass


class Luggage(LuggageBase):
    id: UUID4

    class Config:
        from_attributes = True


class FlightBase(BaseModel):
    plane_id: UUID4
    pilot_id: UUID4
    airport_origin_id: UUID4
    airport_destination_id: UUID4
    cost: float
    costa: float
    costb: float
    origin: str
    destination: str
    departure: datetime.datetime
    arrival: datetime.datetime
    direct: bool


class FlightCreate(FlightBase):
    pass


class Flight(FlightBase):
    id: UUID4
    pilot: Pilot
    plane: Plane
    airport_origin: Airport
    airport_destination: Airport
    reservations: List

    class Config:
        from_attributes = True


class InvoiceBase(BaseModel):
    invoice_status: str
    invoice_date: Optional[datetime.datetime]
    payment_type: str
    payment_status: str
    user_id: str
    total: float


class InvoiceCreate(InvoiceBase):
    pass


class Invoice(InvoiceBase):
    id: UUID4

    class Config:
        from_attributes = True


class ReservationBase(BaseModel):
    flight_id: str
    seat_id: str
    passenger_id: str
    luggage_id: str
    invoice_id: str
    reservation_code: str
    reservation_status: str
    reservation_date: datetime.datetime


class ReservationCreate(ReservationBase):
    pass


class Reservation(ReservationBase):
    id: UUID4

    class Config:
        from_attributes = True


class PayPalBase(BaseModel):
    invoice_id: str
    paypal_email: str
    paypal_password: str


class PayPalCreate(PayPalBase):
    pass


class PayPal(PayPalBase):
    id: UUID4

    class Config:
        from_attributes = True


class CreditCardBase(BaseModel):
    invoice_id: str
    creditcard_number: str
    creditcard_name: str
    creditcard_expiration: str
    creditcard_cvv: str
    creditcard_type: str


class CreditCardCreate(CreditCardBase):
    pass


class CreditCard(CreditCardBase):
    id: UUID4

    class Config:
        from_attributes = True
