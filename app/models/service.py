from sqlalchemy import Column, Integer, Boolean, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Service(Base):
    __tablename__ = "service"

    id = Column(Integer, primary_key=True, index=True)
    resort_id = Column(Integer, ForeignKey("resort.id"))
    name = Column(String(255))

    resort = relationship("Resort", back_populates="services")
