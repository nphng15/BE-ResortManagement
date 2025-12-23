from sqlalchemy import Column, Integer, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from app.database import Base


class Offer(Base):
    __tablename__ = "offer"

    id = Column(Integer, primary_key=True)
    room_type_id = Column(Integer, ForeignKey("room_type.id"))
    cost = Column(Numeric(12, 2))

    room_type = relationship("RoomType", back_populates="offers")
    booking_details = relationship("BookingDetail", back_populates="offer")