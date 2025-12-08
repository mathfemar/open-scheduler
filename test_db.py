import sys, traceback

try:
    from backend.init_db import *
    print("🚀 Initializing database...")
    init_db()
    print("🌱 Seeding initial data...")
    seed_data()
    print("✅ Database setup complete!")
except Exception:
    traceback.print_exc()
    sys.exit(1)
