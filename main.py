from fastapi import FastAPI, HTTPException, Depends, Body, Query

from os import path
import uvicorn
from database.database import SessionLocal, engine
from fastapi.middleware.cors import CORSMiddleware
from database import models, schemas
from sqlalchemy.orm import Session, aliased
from sqlalchemy import func, case
from typing import List
from datetime import datetime
import schemas as schemasResponse
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import ssl
from PIL import Image
import io

origins = [
    # all origins
    "*"
]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

models.Base.metadata.create_all(bind=engine)

pathname = path.dirname(path.realpath(__file__))

API_KEY = "mysecretkeyemail"


async def validate_token_query(api_key: str = Query()):
    if api_key == "":
        raise HTTPException(status_code=401, detail="No API key provided")

    if api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
async def root():
    return {"message": "Hello World"}


# Rutas CRUD para la tabla Plane
@app.get("/planes/", response_model=List[schemas.Plane])
def read_plane(db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
    db_planes = db.query(models.Plane).offset(skip).limit(limit).all()
    if db_planes is None:
        raise HTTPException(status_code=404, detail="Plane not found")
    return db_planes


@app.post("/planes/", response_model=schemas.Plane)
def create_plane(plane: schemas.PlaneCreate, db: Session = Depends(get_db)):
    db_plane = models.Plane(**plane.dict())
    db.add(db_plane)
    db.commit()
    db.refresh(db_plane)
    return db_plane


@app.get("/planes/{plane_id}", response_model=schemas.Plane)
def read_plane(plane_id: str, db: Session = Depends(get_db)):
    db_plane = db.query(models.Plane).filter(models.Plane.id == plane_id).first()
    if db_plane is None:
        raise HTTPException(status_code=404, detail="Plane not found")
    return db_plane


@app.put("/planes/{plane_id}", response_model=schemas.Plane)
def update_plane(
    plane_id: str, plane: schemas.PlaneCreate, db: Session = Depends(get_db)
):
    db_plane = db.query(models.Plane).filter(models.Plane.id == plane_id).first()
    if db_plane is None:
        raise HTTPException(status_code=404, detail="Plane not found")
    for key, value in plane.dict().items():
        setattr(db_plane, key, value)
    db.commit()
    db.refresh(db_plane)
    return db_plane


@app.delete("/planes/{plane_id}", response_model=schemas.Plane)
def delete_plane(plane_id: str, db: Session = Depends(get_db)):
    db_plane = db.query(models.Plane).filter(models.Plane.id == plane_id).first()
    if db_plane is None:
        raise HTTPException(status_code=404, detail="Plane not found")
    db.delete(db_plane)
    db.commit()
    return db_plane


# Rutas CRUD para la tabla Flight
@app.get("/flights/", response_model=List[schemas.Flight])
def read_flights(db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
    db_flights = db.query(models.Flight).offset(skip).limit(limit).all()
    return db_flights


@app.get("/flights/search", response_model=schemasResponse.DataAndCount[schemas.Flight])
def search_flights(
    db: Session = Depends(get_db),
    dateFrom: datetime = Query(None),
    dateTo: datetime = Query(None),
    origin: str = Query(None),
    destination: str = Query(None),
    adults: int = 0,
    children: int = 0,
    infants: int = 0,
    old: int = 0,
    skip: int = 0,
    limit: int = 100,
):
    query = db.query(models.Flight)

    if dateFrom:
        query = query.filter(models.Flight.departure >= dateFrom)
    if dateTo:
        query = query.filter(models.Flight.departure <= dateTo)
    if origin:
        query = query.filter(models.Flight.origin == origin)
    if destination:
        query = query.filter(models.Flight.destination == destination)

    total_seats = adults + children + infants + old
    if total_seats > 0:
        Subquery = (
            db.query(models.Flight.id)
            .join(models.Flight.plane)
            .join(models.AirplaneSeat)
            .filter(models.AirplaneSeat.seat_status == "Available")
            .group_by(models.Flight.id)
            .having(func.count(models.AirplaneSeat.id) > total_seats)
            .subquery()
        )
        query = query.filter(models.Flight.id.in_(Subquery))

    total_count = query.count()

    db_flights = query.offset(skip).limit(limit).all()

    # if not db_flights:
    #     raise HTTPException(status_code=404, detail="No flights found")

    return schemasResponse.DataAndCount[schemas.Flight](
        data=db_flights, count=total_count
    )


@app.get("/plane_seat/{plane_id}")
def read_flight(plane_id: str, db: Session = Depends(get_db)):
    db_flight = (
        db.query(models.AirplaneSeat)
        .filter(models.AirplaneSeat.plane_id == plane_id)
        .all()
    )
    if db_flight is None:
        raise HTTPException(status_code=404, detail="Flight not found")
    return db_flight


@app.get("/plane_seat")
def get_planes(db: Session = Depends(get_db)):
    db_flight = db.query(models.AirplaneSeat).all()
    if db_flight is None:
        raise HTTPException(status_code=404, detail="Flight not found")
    return db_flight


@app.put("/plane_seat/list")
def get_planes(db: Session = Depends(get_db), list: List[schemas.AirplaneSeat] = []):
    for item in list:
        db_flight = (
            db.query(models.AirplaneSeat)
            .filter(models.AirplaneSeat.id == item.id)
            .first()
        )
        if db_flight is None:
            raise HTTPException(status_code=404, detail="Flight not found")
        db_flight.seat_status = item.seat_status
        db.commit()
        db.refresh(db_flight)
    return db_flight


@app.post("/plane_seat/", response_model=schemas.AirplaneSeat)
def create_plane_seat(
    plane_seat: schemas.AirplaneSeatCreate, db: Session = Depends(get_db)
):
    db_plane_seat = models.AirplaneSeat(**plane_seat.dict())
    db.add(db_plane_seat)
    db.commit()
    db.refresh(db_plane_seat)
    return db_plane_seat


#


@app.post("/flights/", response_model=schemas.Flight)
def create_flight(flight: schemas.FlightCreate, db: Session = Depends(get_db)):
    db_flight = models.Flight(**flight.dict())
    db.add(db_flight)
    db.commit()
    db.refresh(db_flight)
    return db_flight


@app.post("/invoice/", response_model=schemas.InvoiceCreate)
def create_flight(invoice: schemas.InvoiceCreate, db: Session = Depends(get_db)):
    print(invoice)
    invoice.invoice_date = datetime.now()
    db_invoice = models.Invoice(**invoice.dict())
    db.add(db_invoice)
    db.commit()
    db.refresh(db_invoice)
    return db_invoice


@app.post("/reservation/", response_model=schemas.ReservationCreate)
def create_flight(
    reservation: schemas.ReservationCreate, db: Session = Depends(get_db)
):
    db_reservation = models.Reservation(**reservation.dict())
    db.add(db_reservation)
    db.commit()
    db.refresh(db_reservation)
    return db_reservation


@app.get("/flights/{flight_id}", response_model=schemas.Flight)
def read_flight(flight_id: str, db: Session = Depends(get_db)):
    db_flight = db.query(models.Flight).filter(models.Flight.id == flight_id).first()
    if db_flight is None:
        raise HTTPException(status_code=404, detail="Flight not found")
    return db_flight


@app.put("/flights/{flight_id}", response_model=schemas.Flight)
def update_flight(
    flight_id: str, flight: schemas.FlightCreate, db: Session = Depends(get_db)
):
    db_flight = db.query(models.Flight).filter(models.Flight.id == flight_id).first()
    if db_flight is None:
        raise HTTPException(status_code=404, detail="Flight not found")
    for key, value in flight.dict().items():
        setattr(db_flight, key, value)
    db.commit()
    db.refresh(db_flight)
    return db_flight


@app.delete("/flights/{flight_id}", response_model=schemas.Flight)
def delete_flight(flight_id: str, db: Session = Depends(get_db)):
    db_flight = db.query(models.Flight).filter(models.Flight.id == flight_id).first()
    if db_flight is None:
        raise HTTPException(status_code=404, detail="Flight not found")
    db.delete(db_flight)
    db.commit()
    return db_flight


# Rutas CRUD para la tabla Airports
@app.get("/airports/", response_model=List[schemas.Airport])
def read_airports(db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
    db_airports = db.query(models.Airport).offset(skip).limit(limit).all()
    return db_airports


@app.get("/airports/search", response_model=List[schemas.Airport])
def search_airports(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
):
    query = db.query(models.Airport)
    db_airport = query.offset(skip).limit(limit).all()
    if not db_airport:
        raise HTTPException(status_code=404, detail="No airports found")
    return db_airport


@app.post("/airports/", response_model=schemas.Airport)
def create_airports(airport: schemas.AirportCreate, db: Session = Depends(get_db)):
    db_airport = models.Airport(**airport.dict())
    db.add(db_airport)
    db.commit()
    db.refresh(db_airport)
    return db_airport


@app.get("/airports/{airport_id}", response_model=schemas.Airport)
def read_airport(airport_id: str, db: Session = Depends(get_db)):
    db_airport = (
        db.query(models.Airport).filter(models.Airport.id == airport_id).first()
    )
    if db_airport is None:
        raise HTTPException(status_code=404, detail="Airport not found")
    return db_airport


@app.put("/airports/{airport_id}", response_model=schemas.Airport)
def update_airport(
    airport_id: str, airport: schemas.AirportCreate, db: Session = Depends(get_db)
):
    db_airport = (
        db.query(models.Airport).filter(models.Airport.id == airport_id).first()
    )
    if db_airport is None:
        raise HTTPException(status_code=404, detail="Airport not found")
    for key, value in airport.dict().items():
        setattr(db_airport, key, value)
    db.commit()
    db.refresh(db_airport)
    return db_airport


@app.delete("/airports/{airport_id}", response_model=schemas.Airport)
def delete_airport(airport_id: str, db: Session = Depends(get_db)):
    db_airport = db.query(models.Flight).filter(models.Airport.id == airport_id).first()
    if db_airport is None:
        raise HTTPException(status_code=404, detail="Flight not found")
    db.delete(db_airport)
    db.commit()
    return db_airport


@app.get("/airports/", response_model=List[schemas.Airport])
def read_airports(db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
    db_airports = db.query(models.Airport).offset(skip).limit(limit).all()
    return db_airports


@app.get("/destinations/", response_model=List[schemasResponse.destination])
def get_destinations(db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
    db_airports = db.query(models.Airport).offset(skip).limit(limit).all()
    return db_airports


# CRUD FOR PILOTS
@app.get("/pilots/", response_model=List[schemas.Pilot])
def read_pilots(db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
    db_pilots = db.query(models.Pilot).offset(skip).limit(limit).all()
    return db_pilots


@app.post("/pilots/", response_model=schemas.Pilot)
def create_pilot(pilot: schemas.PilotCreate, db: Session = Depends(get_db)):
    db_pilot = models.Pilot(**pilot.dict())
    db.add(db_pilot)
    db.commit()
    db.refresh(db_pilot)
    return db_pilot


@app.get("/pilots/{pilot_id}", response_model=schemas.Pilot)
def read_pilot(pilot_id: str, db: Session = Depends(get_db)):
    db_pilot = db.query(models.Pilot).filter(models.Pilot.id == pilot_id).first()
    if db_pilot is None:
        raise HTTPException(status_code=404, detail="Pilot not found")
    return db_pilot


@app.put("/pilots/{pilot_id}", response_model=schemas.Pilot)
def update_pilot(
    pilot_id: str, pilot: schemas.PilotCreate, db: Session = Depends(get_db)
):
    db_pilot = db.query(models.Pilot).filter(models.Pilot.id == pilot_id).first()
    if db_pilot is None:
        raise HTTPException(status_code=404, detail="Pilot not found")
    for key, value in pilot.dict().items():
        setattr(db_pilot, key, value)
    db.commit()
    db.refresh(db_pilot)
    return db_pilot


@app.post("/api/send-email")
async def send_email(
    recipients: list = Body(...),
    body: dict = Body(embed=True),
    subject: str = Body(embed=True),
    api_key: None = Depends(validate_token_query),
):
    try:
        # create message object instance
        msg = MIMEMultipart()
        msg["From"] = "HORIZON JET "
        msg["To"] = ", ".join(recipients)
        msg["Subject"] = subject

        # Logo de la empresa (ajusta la ruta a tu archivo de imagen)
        with open("logo_white.png", "rb") as image_file:
            img = Image.open(image_file)
            img = img.resize((120, 100))  # Redimensionar la imagen
            buffer = io.BytesIO()
            img.save(buffer, format="PNG")
            image_data = buffer.getvalue()

        image = MIMEImage(image_data, name="logo_white.png")
        msg.attach(image)

        # Contenido del mensaje
        message = f"""
        <html>
        <body>
        <table style="background-color: #770085; width: 100%;">
            <tr>
                <td>
                    <img src="cid:logo_white.png">
                </td>
                <td style="color: #fff; margin: 0">
                    <h1>{subject}</h1>
                </td>
            </tr>
        </table>
        <p style="font-family: 'Times New Roman'; font-size:20px;">Gracias por confiar en nosotros</p>
        <p style="font-family: 'Times New Roman'; font-size:16px;">A continuación, detallamos un resumen de su compra:</p>
        <div style="font-family: 'Times New Roman';">
        """
        for key, value in body.items():
            message += f'<p style = "margin: 1px 0px 0px 30px; font-size:12px;"><strong>{key}:</strong> {value}</p><br>'
        message += """
        </div>
        </body>
        </html>
        """

        # Agregar el mensaje al cuerpo del correo
        msg.attach(MIMEText(message, "html"))

        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        sender = "lizbethoa0612@gmail.com"
        password = "ermpvgxfyxpxltwf"

        context = ssl.create_default_context()

        s = smtplib.SMTP(smtp_server, smtp_port)
        s.starttls(context=context)

        s.ehlo()
        s.login(sender, password)

        s.sendmail(sender, recipients, msg.as_string())
        s.close()
        return {"message": "Email sent successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# if __name__ == "__main__":
#     uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
