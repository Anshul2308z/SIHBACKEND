from sihbackend.db.database import engine, Base, SessionLocal
from sihbackend.db.models import ChatHistory, ExpertConsultation
import datetime

def test_database():
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Check if already populated (for ChatHistory)
        if not db.query(ChatHistory).first():
            print("Populating initial test data...")
            
            c1 = ChatHistory(query="Test query", jurisdiction="India", language="en", response={"msg": "hello"})
            e1 = ExpertConsultation(name="Test User", email="test@example.com", topic="Patent", context="Testing")
            
            db.add_all([c1, e1])
            db.commit()
            print("Records inserted.")
        
        # Verify read
        chats = db.query(ChatHistory).all()
        print(f"\n--- Chat Records ({len(chats)}) ---")
        for c in chats:
            print(f"Query: {c.query} | Date: {c.created_at}")
            
        experts = db.query(ExpertConsultation).all()
        print(f"\n--- Expert Consultations ({len(experts)}) ---")
        for e in experts:
            print(f"Name: {e.name} | Topic: {e.topic} | Date: {e.created_at}")
            
    finally:
        db.close()
        print("\nDatabase test completed.")

if __name__ == "__main__":
    test_database()
