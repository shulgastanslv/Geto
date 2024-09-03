from typing import Callable
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from datetime import datetime

class Scheduler:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.scheduler.start()

    def schedule_daily_task(self, job_id: str, func: Callable[[], None],  hour: int, min: int, name: str = None):
        trigger = CronTrigger(hour=hour, minute=min)
        self.scheduler.add_job(
            func,
            trigger,
            id=job_id,
            name=name,
            replace_existing=True
        )
        print(f"Scheduled daily task '{job_id}' at {hour:02d}:{min:02d}.")

    def schedule_one_time_task(self, task_func, run_time: datetime, job_id: str, name: str = None):
        trigger = DateTrigger(run_date=run_time)
        self.scheduler.add_job(
            task_func,
            trigger,
            id=job_id,
            name=name,
            replace_existing=True
        )
        print(f"Scheduled one-time task '{name}' for {run_time}.")

    def remove_task(self, job_id: str):
        self.scheduler.remove_job(job_id)
        print(f"Removed scheduled task with job ID '{job_id}'.")

    def list_tasks(self):
        jobs = self.scheduler.get_jobs()
        return [(job.id, job.name, job.next_run_time) for job in jobs]

    def shutdown(self):
        self.scheduler.shutdown(wait=False)

