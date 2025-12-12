"""Test database and user creation"""
import sys
from database import engine, Base, get_db
from models import User as UserModel
from auth import get_password_hash

print("=" * 60)
print("Testing Database Setup")
print("=" * 60)

try:
    # Create tables
    print("\n1. Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("   ✅ Tables created successfully")
    
    # Test user creation
    print("\n2. Creating test user...")
    db = next(get_db())
    
    # Check if user already exists
    existing_user = db.query(UserModel).filter(UserModel.email == "test@example.com").first()
    if existing_user:
        print(f"   ⚠️  User already exists: {existing_user.username}")
        db.delete(existing_user)
        db.commit()
        print("   🗑️  Deleted existing user")
    
    # Create new user
    hashed_password = get_password_hash("password123")
    new_user = UserModel(
        email="test@example.com",
        username="testuser",
        full_name="Test User",
        hashed_password=hashed_password
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    print(f"   ✅ User created successfully!")
    print(f"      ID: {new_user.id}")
    print(f"      Email: {new_user.email}")
    print(f"      Username: {new_user.username}")
    print(f"      Full Name: {new_user.full_name}")
    print(f"      Is Active: {new_user.is_active}")
    print(f"      Created: {new_user.created_at}")
    
    # Query user back
    print("\n3. Querying user from database...")
    queried_user = db.query(UserModel).filter(UserModel.email == "test@example.com").first()
    if queried_user:
        print(f"   ✅ User found: {queried_user.username}")
    else:
        print("   ❌ User not found")
    
    db.close()
    
    print("\n" + "=" * 60)
    print("✅ All database tests passed!")
    print("=" * 60)
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
