"""Add sample jobs to database for testing."""
import os
import sys

# Prevent app from starting
os.environ['WERKZEUG_RUN_MAIN'] = 'true'

from datetime import datetime, timedelta
from backend.core.database import SessionLocal, init_db
from backend.core import models, schemas
import backend.core.api as api

def create_sample_jobs():
    """Create sample jobs in database."""
    db = SessionLocal()
    try:
        # Sample Python file (create a dummy one)
        sample_file = os.path.join(os.getcwd(), "sample_task.py")
        if not os.path.exists(sample_file):
            with open(sample_file, "w") as f:
                f.write("""#!/usr/bin/env python
# Sample task for testing
import time
print("Starting sample task...")
time.sleep(2)
print("Task completed successfully!")
""")
        
        # Create sample jobs
        jobs_data = [
            {
                "name": "Backup Database",
                "description": "Daily backup of main database to cloud storage",
                "file_path": sample_file,
                "schedule_type": "cron",
                "schedule_value": "0 2 * * *",  # Daily at 2 AM
                "status": "active",
                "timeout": 300,
            },
            {
                "name": "Data Sync API",
                "description": "Sync data with external API every 10 minutes",
                "file_path": sample_file,
                "schedule_type": "interval",
                "schedule_value": "600",  # 10 minutes
                "status": "active",
                "timeout": 60,
            },
            {
                "name": "Weekly Report",
                "description": "Generate and email weekly report",
                "file_path": sample_file,
                "schedule_type": "cron",
                "schedule_value": "0 8 * * 1",  # Mondays at 8 AM
                "status": "paused",
                "timeout": 180,
            },
            {
                "name": "Cache Cleanup",
                "description": "Clean up old cache files",
                "file_path": sample_file,
                "schedule_type": "interval",
                "schedule_value": "3600",  # 1 hour
                "status": "active",
                "timeout": 120,
            },
        ]
        
        created_jobs = []
        for job_data in jobs_data:
            # Check if job already exists
            existing = db.query(models.Job).filter(models.Job.name == job_data["name"]).first()
            if existing:
                print(f"ℹ️  Job '{job_data['name']}' already exists")
                created_jobs.append(existing)
                continue
            
            job = api.create_job(db, schemas.JobCreate(**job_data))
            created_jobs.append(job)
            print(f"✅ Created job: {job.name}")
        
        # Create some sample executions
        if created_jobs:
            print("\n📊 Creating sample executions...")
            now = datetime.utcnow()
            
            for i, job in enumerate(created_jobs[:2]):  # Only for first 2 jobs
                # Create 5 executions for each
                for j in range(5):
                    exec_time = now - timedelta(hours=(i * 5 + j + 1))
                    status = "success" if (i + j) % 3 != 0 else "failed"
                    
                    execution = models.Execution(
                        job_id=job.id,
                        started_at=exec_time,
                        ended_at=exec_time + timedelta(seconds=30),
                        status=status,
                        output=f"Sample output for {job.name}\nExecution completed.",
                        exit_code=0 if status == "success" else 1,
                        duration=30.0,
                    )
                    db.add(execution)
                
                # Update job last_run and last_status
                job.last_run = now - timedelta(hours=(i + 1))
                job.last_status = "success" if i % 2 == 0 else "failed"
                job.next_run = now + timedelta(minutes=(i + 1) * 10)
            
            db.commit()
            print("✅ Sample executions created")
        
        print(f"\n🎉 Sample data created! Total jobs: {len(created_jobs)}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    print("🚀 Creating sample jobs for testing...\n")
    init_db()
    create_sample_jobs()
    print("\n✅ Done! Run the app and check the Overview page.")
    sys.exit(0)
