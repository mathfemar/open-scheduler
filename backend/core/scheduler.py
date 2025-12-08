"""Scheduler wrapper with job persistence and re-registration."""
import logging
from datetime import datetime, timedelta
from typing import Optional
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.date import DateTrigger
from croniter import croniter
from backend.core.database import SessionLocal
from backend.core import models, api, schemas

logger = logging.getLogger(__name__)


class Scheduler:
    """Scheduler wrapper for managing scheduled jobs."""
    
    def __init__(self):
        self._sched = BackgroundScheduler()
        self._job_map = {}  # Maps job_id -> APScheduler job

    def start(self):
        """Start scheduler and re-register persisted jobs."""
        if not self._sched.running:
            self._sched.start()
            self._reregister_jobs()
            logger.info("✅ Scheduler started")

    def shutdown(self):
        """Shutdown scheduler."""
        if self._sched.running:
            self._sched.shutdown()
            logger.info("⏸ Scheduler stopped")

    def _reregister_jobs(self):
        """Re-register active jobs from database."""
        db = SessionLocal()
        try:
            active_jobs = api.get_jobs(db, status="active")
            for job in active_jobs:
                try:
                    self.register_job(job.id, job.schedule_type, job.schedule_value, job.timezone)
                    logger.info(f"✅ Re-registered job: {job.name}")
                except Exception as e:
                    logger.error(f"❌ Failed to re-register job {job.name}: {e}")
        finally:
            db.close()

    def register_job(self, job_id: str, schedule_type: str, schedule_value: str, timezone: str = "UTC"):
        """Register a job in the scheduler."""
        from backend.core.executor import execute_job
        
        # Parse schedule and create trigger
        trigger = self._create_trigger(schedule_type, schedule_value, timezone)
        
        # Add job to APScheduler
        apscheduler_job = self._sched.add_job(
            execute_job,
            trigger,
            args=[job_id],
            id=job_id,
            replace_existing=True,
            timezone=timezone,
        )
        
        self._job_map[job_id] = apscheduler_job
        
        # Update next_run in database
        self._update_next_run(job_id, apscheduler_job.next_run_time)
        
        logger.info(f"✅ Registered job {job_id}, next run: {apscheduler_job.next_run_time}")

    def unregister_job(self, job_id: str):
        """Unregister a job from scheduler."""
        try:
            self._sched.remove_job(job_id)
            self._job_map.pop(job_id, None)
            logger.info(f"✅ Unregistered job {job_id}")
        except Exception as e:
            logger.warning(f"⚠️ Failed to unregister job {job_id}: {e}")

    def pause_job(self, job_id: str):
        """Pause a job (unregister from scheduler)."""
        self.unregister_job(job_id)

    def resume_job(self, job_id: str):
        """Resume a paused job."""
        db = SessionLocal()
        try:
            job = api.get_job(db, job_id)
            if job:
                self.register_job(job.id, job.schedule_type, job.schedule_value, job.timezone)
        finally:
            db.close()

    def run_now(self, job_id: str):
        """Execute job immediately (outside schedule)."""
        from backend.core.executor import execute_job
        execute_job(job_id)

    def _create_trigger(self, schedule_type: str, schedule_value: str, timezone: str):
        """Create APScheduler trigger from schedule config."""
        if schedule_type == "cron":
            return CronTrigger.from_crontab(schedule_value, timezone=timezone)
        elif schedule_type == "interval":
            # Parse interval (seconds, minutes, hours, days)
            seconds = int(schedule_value)
            return IntervalTrigger(seconds=seconds, timezone=timezone)
        elif schedule_type == "once":
            # Parse datetime
            run_date = datetime.fromisoformat(schedule_value)
            return DateTrigger(run_date=run_date, timezone=timezone)
        else:
            raise ValueError(f"Unknown schedule type: {schedule_type}")

    def _update_next_run(self, job_id: str, next_run_time: Optional[datetime]):
        """Update next_run in database."""
        db = SessionLocal()
        try:
            api.update_job(db, job_id, schemas.JobUpdate(next_run=next_run_time))
        finally:
            db.close()

    def get_next_run(self, job_id: str) -> Optional[datetime]:
        """Get next run time for a job."""
        apscheduler_job = self._job_map.get(job_id)
        if apscheduler_job:
            return apscheduler_job.next_run_time
        return None


# Global scheduler instance
_scheduler = None


def get_scheduler() -> Scheduler:
    """Get global scheduler instance."""
    global _scheduler
    if _scheduler is None:
        _scheduler = Scheduler()
    return _scheduler
