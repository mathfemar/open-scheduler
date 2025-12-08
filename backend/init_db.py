"""Initialize the database with tables and optional seed data."""
import os
from backend.core.database import init_db, SessionLocal
from backend.core.models import TrackedDirectory

def seed_data():
    """Add initial seed data."""
    db = SessionLocal()
    try:
        # Add default tracked directory (project root)
        project_root = os.path.abspath(".")
        existing = db.query(TrackedDirectory).filter_by(path=project_root).first()
        if not existing:
            tracked_dir = TrackedDirectory(path=project_root, active=True)
            db.add(tracked_dir)
            db.commit()
            print(f"✅ Added default tracked directory: {project_root}")
        else:
            print(f"ℹ️  Default tracked directory already exists: {project_root}")
    except Exception as e:
        print(f"❌ Error seeding data: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    print("🚀 Initializing database...")
    init_db()
    print("🌱 Seeding initial data...")
    seed_data()
    print("✅ Database setup complete!")
