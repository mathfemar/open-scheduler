"""Executor for running Python files and capturing output."""
import subprocess
import time
import logging
from datetime import datetime
from typing import Dict, Optional
from backend.core.database import SessionLocal
from backend.core import models, schemas, api

logger = logging.getLogger(__name__)

# Maximum output size (50KB)
MAX_OUTPUT_SIZE = 50 * 1024


def run_file(path: str, args: Optional[str] = None, env: Optional[dict] = None, timeout: int = 60) -> Dict:
    """Run a Python file and return result dict.
    
    Args:
        path: Absolute path to Python file
        args: CLI arguments (space-separated string)
        env: Environment variables dict
        timeout: Execution timeout in seconds
    
    Returns:
        Dict with keys: exit_code, output, duration, status
    """
    import sys
    import os
    
    cmd = [sys.executable, path]
    if args:
        cmd.extend(args.split())
    
    # Merge environment variables
    exec_env = os.environ.copy()
    if env:
        exec_env.update(env)
    
    started = time.time()
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            env=exec_env,
            timeout=timeout,
            cwd=os.path.dirname(path),
        )
        ended = time.time()
        
        output = (proc.stdout or '') + (proc.stderr or '')
        if len(output) > MAX_OUTPUT_SIZE:
            output = output[:MAX_OUTPUT_SIZE] + f"\n\n[Output truncated at {MAX_OUTPUT_SIZE} bytes]"
        
        status = "success" if proc.returncode == 0 else "failed"
        
        return {
            'exit_code': proc.returncode,
            'output': output,
            'duration': ended - started,
            'status': status,
        }
    except subprocess.TimeoutExpired as exc:
        output = (exc.stdout or '').decode('utf-8', errors='replace') if isinstance(exc.stdout, bytes) else (exc.stdout or '')
        output += (exc.stderr or '').decode('utf-8', errors='replace') if isinstance(exc.stderr, bytes) else (exc.stderr or '')
        output += f'\n\n[Execution timed out after {timeout}s]'
        
        if len(output) > MAX_OUTPUT_SIZE:
            output = output[:MAX_OUTPUT_SIZE] + f"\n\n[Output truncated]"
        
        return {
            'exit_code': -1,
            'output': output,
            'duration': time.time() - started,
            'status': 'timeout',
        }
    except Exception as e:
        return {
            'exit_code': -2,
            'output': f'Executor error: {str(e)}',
            'duration': time.time() - started,
            'status': 'failed',
        }


def execute_job(job_id: str, retry_attempt: int = 0):
    """Execute a scheduled job and record execution.
    
    This is called by APScheduler when a job is triggered.
    """
    db = SessionLocal()
    try:
        job = api.get_job(db, job_id)
        if not job:
            logger.error(f"❌ Job {job_id} not found")
            return
        
        logger.info(f"▶️ Executing job: {job.name} (attempt {retry_attempt + 1})")
        
        execution = api.create_execution(
            db,
            schemas.ExecutionCreate(job_id=job_id, status="running")
        )
        
        result = run_file(
            path=job.file_path,
            args=job.args,
            env=job.env_vars,
            timeout=job.timeout,
        )
        
        api.update_execution(
            db,
            execution.id,
            ended_at=datetime.utcnow(),
            status=result['status'],
            output=result['output'],
            exit_code=result['exit_code'],
            duration=result['duration'],
        )
        
        api.update_job(
            db,
            job_id,
            schemas.JobUpdate(
                last_run=datetime.utcnow(),
                last_status=result['status'],
            )
        )
        
        if result['status'] in ('failed', 'timeout') and retry_attempt < job.retry_max:
            logger.warning(f"⚠️ Job {job.name} failed, retrying in {job.retry_delay}s")
            import threading
            def delayed_retry():
                time.sleep(job.retry_delay)
                execute_job(job_id, retry_attempt + 1)
            threading.Thread(target=delayed_retry, daemon=True).start()
        elif result['status'] == 'success':
            logger.info(f"✅ Job {job.name} completed successfully ({result['duration']:.2f}s)")
        else:
            logger.error(f"❌ Job {job.name} failed after {retry_attempt + 1} attempts")
        
    except Exception as e:
        logger.exception(f"❌ Error executing job {job_id}: {e}")
    finally:
        db.close()
