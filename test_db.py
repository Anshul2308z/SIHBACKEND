from sihbackend.db.database import engine, Base, SessionLocal
from sihbackend.db.models import Plant, Source, Jurisdiction, UserSession
import datetime

def test_database():
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Check if already populated
        if not db.query(Plant).first():
            print("Populating initial reference data...")
            
            p1 = Plant(id="neem", name="Neem", botanical_name="Azadirachta indica", family="Meliaceae", tkdl_status=True, abs_risk="High")
            p2 = Plant(id="ashwagandha", name="Ashwagandha", botanical_name="Withania somnifera", family="Solanaceae", tkdl_status=True, abs_risk="High")
            
            s1 = Source(id="tkdl", name="Traditional Knowledge Digital Library", authority="CSIR", jurisdiction="India", url="https://tkdl.res.in", last_verified="2026-08-28")
            
            j1 = Jurisdiction(id="IN", name="India", regulator="CGPDTM")
            
            u1 = UserSession(user_id="test_user_1", query="Ashwagandha formulation", report_data={"confidence": 88, "status": "processed"})
            
            db.add_all([p1, p2, s1, j1, u1])
            db.commit()
            print("Records inserted.")
        
        # Verify read
        plants = db.query(Plant).all()
        print(f"\n--- Plant Records ({len(plants)}) ---")
        for p in plants:
            print(f"{p.name} ({p.botanical_name}) - Family: {p.family}")
            
        sessions = db.query(UserSession).all()
        print(f"\n--- User Sessions ({len(sessions)}) ---")
        for s in sessions:
            print(f"User: {s.user_id} | Query: {s.query} | Date: {s.created_at}")
            
    finally:
        db.close()
        print("\nDatabase test completed.")

if __name__ == "__main__":
    test_database()
