from sqlalchemy import create_engine, Column, String, Integer, Float
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import inspect

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
    db = SessionLocal()
    inspector = inspect(engine)
    
    # 1. Thread-safe table initialization check
    if not inspector.has_table("land_ownership"):
        Base.metadata.create_all(bind=engine)
        print("📁 Database tables created fresh.")
    else:
        print("📁 Database tables already exist. Skipping creation.")
        
    # Multi-worker proof record injection verification
    # Individually check for the existence of each sample primary key before pushing duplicates
    sample_profiles = [
        {"id": "KA-12-101", "name": "Ramesh Kumar", "phone": "+919876543210", "n": 90, "p": 42, "k": 43, "ph": 6.5, "lat": 12.9716, "lon": 77.5946},
        {"id": "MH-05-202", "name": "Anil Deshmukh", "phone": "+919876543211", "n": 25, "p": 15, "k": 20, "ph": 5.2, "lat": 18.5204, "lon": 73.8567},
        {"id": "PB-02-303", "name": "Gurpreet Singh", "phone": "+919876543212", "n": 60, "p": 55, "k": 44, "ph": 8.4, "lat": 31.3260, "lon": 75.5762}
    ]
    
    records_to_add = []
    for p in sample_profiles:
        exists = db.query(LandRecord).filter(LandRecord.land_id == p["id"]).first()
        if not exists:
            new_record = LandRecord(
                land_id=p["id"], farmer_name=p["name"], phone_number=p["phone"],
                nitrogen=p["n"], phosphorus=p["p"], potassium=p["k"], ph=p["ph"],
                latitude=p["lat"], longitude=p["lon"]
            )
            records_to_add.append(new_record)
            
    if records_to_add:
        try:
            db.add_all(records_to_add)
            db.commit()
            print(f"🌱 Successfully seeded {len(records_to_add)} missing test records.")
        except Exception as e:
            db.rollback()
            print(f"⚠️ Insertion collision bypassed cleanly: {str(e)}")
    else:
        print("🌱 All base records already verified in registry table. No seeding required.")
        
    db.close()
