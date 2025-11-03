"""
Create Demo Users for Testing
"""
import sys
sys.path.insert(0, '/workspaces/RAG-ENTERPRISE')

from api.database import SessionLocal
from api.models.user import User, UserStatus
from core.auth import AuthService

def create_demo_users():
    """Create demo users"""
    db = SessionLocal()
    
    try:
        # Check if users already exist
        existing_user = db.query(User).filter(User.email == "user@demo.com").first()
        existing_admin = db.query(User).filter(User.email == "admin@demo.com").first()
        
        if existing_user:
            print("⚠️  Demo user already exists")
        else:
            # Create regular user
            demo_user = User(
                email="user@demo.com",
                password=AuthService.get_password_hash("password123"),
                name="Demo User",
                role="user",
                status=UserStatus.ACTIVE
            )
            db.add(demo_user)
            print("✅ Created demo user: user@demo.com / password123")
        
        if existing_admin:
            print("⚠️  Demo admin already exists")
        else:
            # Create admin user
            demo_admin = User(
                email="admin@demo.com",
                password=AuthService.get_password_hash("admin123"),
                name="Demo Admin",
                role="admin",
                status=UserStatus.ACTIVE
            )
            db.add(demo_admin)
            print("✅ Created demo admin: admin@demo.com / admin123")
        
        db.commit()
        print("\n🎉 Demo users ready!")
        print("\n📝 Login credentials:")
        print("   User:  user@demo.com / password123")
        print("   Admin: admin@demo.com / admin123")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_demo_users()
