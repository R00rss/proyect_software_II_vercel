from sqlalchemy import (
    Column,
    String,
    Integer,
    Float,
    DateTime,
    ForeignKey,
    Boolean,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .database import Base
import uuid


class Plane(Base):
    __tablename__ = "plane"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    model = Column(String, nullable=False)
    capacity = Column(Integer, nullable=False)
    serial_number = Column(String, nullable=False)
    code = Column(String, nullable=False)

    airplane_seats = relationship("AirplaneSeat", back_populates="plane")
    flights = relationship("Flight", back_populates="plane")


class Pilot(Base):
    __tablename__ = "pilot"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    lastname = Column(String, nullable=False)
    ci = Column(String, nullable=False, unique=True)
    license = Column(String, nullable=False)

    flights = relationship("Flight", back_populates="pilot")


class Passenger(Base):
    __tablename__ = "passenger"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    lastname = Column(String, nullable=False)
    ci = Column(String, nullable=False, unique=True)
    phone = Column(String, nullable=False)
    email = Column(String, nullable=False)

    reservations = relationship("Reservation", back_populates="passenger")


class User(Base):
    __tablename__ = "user"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    lastname = Column(String, nullable=False)
    ci = Column(String, nullable=False, unique=True)
    phone = Column(String, nullable=False)
    email = Column(String, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String, nullable=False)

    invoices = relationship("Invoice", back_populates="user")


class Luggage(Base):
    __tablename__ = "luggage"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    weight = Column(Float, nullable=False)
    price = Column(Float, nullable=False)

    reservations = relationship("Reservation", back_populates="luggage")


class AirplaneSeat(Base):
    __tablename__ = "airplane_seat"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    plane_id = Column(UUID(as_uuid=True), ForeignKey("plane.id"), nullable=False)
    seat_number = Column(String, nullable=False)
    seat_type = Column(String, nullable=False)
    seat_status = Column(String, nullable=False)

    plane = relationship("Plane", back_populates="airplane_seats")
    reservations = relationship("Reservation", back_populates="seat")


class Flight(Base):
    __tablename__ = "flight"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    plane_id = Column(UUID(as_uuid=True), ForeignKey("plane.id"), nullable=False)
    pilot_id = Column(UUID(as_uuid=True), ForeignKey("pilot.id"), nullable=False)
    airport_origin_id = Column(
        UUID(as_uuid=True), ForeignKey("airport.id"), nullable=False
    )
    airport_destination_id = Column(
        UUID(as_uuid=True), ForeignKey("airport.id"), nullable=False
    )
    origin = Column(String, nullable=False)
    destination = Column(String, nullable=False)
    departure = Column(DateTime, nullable=False)
    arrival = Column(DateTime, nullable=False)
    cost = Column(Float, nullable=False)
    costa = Column(Float, nullable=False)
    costb = Column(Float, nullable=False)
    direct = Column(Boolean, nullable=False)
    plane = relationship("Plane", back_populates="flights")
    pilot = relationship("Pilot", back_populates="flights")
    reservations = relationship("Reservation", back_populates="flight")
    airport_origin = relationship(
        "Airport",
        foreign_keys=[airport_origin_id],
        back_populates="flights_origin",
        primaryjoin="Flight.airport_origin_id == Airport.id",  # Agregar esto
    )

    airport_destination = relationship(
        "Airport",
        foreign_keys=[airport_destination_id],
        back_populates="flights_destination",
        primaryjoin="Flight.airport_destination_id == Airport.id",  # Agregar esto
    )


class Airport(Base):
    __tablename__ = "airport"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    city = Column(String, nullable=False)
    country = Column(String, nullable=False)
    code = Column(String, nullable=False, unique=True)

    flights_origin = relationship(
        "Flight",
        foreign_keys=[
            Flight.airport_origin_id
        ],  # Especifica las columnas de clave foránea
        back_populates="airport_origin",
    )

    flights_destination = relationship(
        "Flight",
        foreign_keys=[
            Flight.airport_destination_id
        ],  # Especifica las columnas de clave foránea
        back_populates="airport_destination",
    )


class Invoice(Base):
    __tablename__ = "invoice"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    invoice_status = Column(String, nullable=False)
    invoice_date = Column(DateTime)
    payment_type = Column(String, nullable=False)
    payment_status = Column(String, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)
    total = Column(Float, nullable=False)

    user = relationship("User", back_populates="invoices")
    reservations = relationship("Reservation", back_populates="invoice")
    paypal = relationship("PayPal", back_populates="invoice")
    creditcard = relationship("CreditCard", back_populates="invoice")


class Reservation(Base):
    __tablename__ = "reservation"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    flight_id = Column(UUID(as_uuid=True), ForeignKey("flight.id"), nullable=False)
    seat_id = Column(UUID(as_uuid=True), ForeignKey("airplane_seat.id"), nullable=False)
    passenger_id = Column(
        UUID(as_uuid=True), ForeignKey("passenger.id"), nullable=False
    )
    luggage_id = Column(UUID(as_uuid=True), ForeignKey("luggage.id"), nullable=False)
    invoice_id = Column(UUID(as_uuid=True), ForeignKey("invoice.id"), nullable=False)
    reservation_code = Column(String, nullable=False)
    reservation_status = Column(String, nullable=False)
    reservation_date = Column(DateTime, nullable=False)

    flight = relationship("Flight", back_populates="reservations")
    seat = relationship("AirplaneSeat", back_populates="reservations")
    passenger = relationship("Passenger", back_populates="reservations")
    luggage = relationship("Luggage", back_populates="reservations")
    invoice = relationship("Invoice", back_populates="reservations")


class PayPal(Base):
    __tablename__ = "paypal"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    invoice_id = Column(UUID(as_uuid=True), ForeignKey("invoice.id"), nullable=False)
    paypal_email = Column(String, nullable=False)
    paypal_password = Column(String, nullable=False)

    invoice = relationship("Invoice", back_populates="paypal")


class CreditCard(Base):
    __tablename__ = "creditcard"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    invoice_id = Column(UUID(as_uuid=True), ForeignKey("invoice.id"), nullable=False)
    creditcard_number = Column(String, nullable=False)
    creditcard_name = Column(String, nullable=False)
    creditcard_expiration = Column(String, nullable=False)
    creditcard_cvv = Column(String, nullable=False)
    creditcard_type = Column(String, nullable=False)

    invoice = relationship("Invoice", back_populates="creditcard")
