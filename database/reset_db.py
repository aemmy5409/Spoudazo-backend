from database.db import engine, Base
from database import models  # ✅ Make sure all models are imported so SQLAlchemy knows them

if __name__ == "__main__":
    # ⚠️ Drop all tables (use carefully, this deletes all data!)
    # print("⚠️ Dropping all tables...")
    # Base.metadata.drop_all(bind=engine)

    # ✅ Create all tables again
    print("✅ Creating all tables...")
    Base.metadata.create_all(bind=engine)

    print("🎉 Database reset complete.")
