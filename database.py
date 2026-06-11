from sqlalchemy import create_engine, Column, String, Integer, Float
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "sqlite:///./agri_records.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class LandRecord(Base):
    __tablename__ = "land_ownership"

    land_id = Column(String, primary_key=True, index=True)
    farmer_name = Column(String, nullable=False)
    phone_number = Column(String, nullable=False)
    nitrogen = Column(Integer, nullable=False)
    phosphorus = Column(Integer, nullable=False)
    potassium = Column(Integer, nullable=False)
    ph = Column(Float, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)

def init_db():
    """Initializes the database and seeds it with regional profiles if empty."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    if db.query(LandRecord).count() == 0:
        sample_records = [
            LandRecord(land_id="KA-12-101", farmer_name="Ramesh Kumar", phone_number="+919876543210", nitrogen=90, phosphorus=42, potassium=43, ph=6.5, latitude=12.9716, longitude=77.5946),
            LandRecord(land_id="MH-05-202", farmer_name="Anil Deshmukh", phone_number="+919876543211", nitrogen=25, phosphorus=15, potassium=20, ph=5.2, latitude=18.5204, longitude=73.8567),
            LandRecord(land_id="PB-02-303", farmer_name="Gurpreet Singh", phone_number="+919876543212", nitrogen=60, phosphorus=55, potassium=44, ph=8.4, latitude=31.3260, longitude=75.5762)
        ]
        db.add_all(sample_records)
        db.commit()
    db.close()
