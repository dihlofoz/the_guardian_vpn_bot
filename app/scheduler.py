import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.tasks.tasks import (
    cleanup_expired_subscriptions,
    cleanup_expired_trials,
    expired_subscriptions_notifier1,
    trial_reminder_task
)

scheduler = AsyncIOScheduler(
    timezone=pytz.utc,
    job_defaults={
        "misfire_grace_time": 3600  
    }
)


def setup_scheduler(bot):
    scheduler.add_job(
        cleanup_expired_subscriptions,
        trigger="interval",
        hours=1,
        id="cleanup_expired_subscriptions",
        max_instances=1,
        replace_existing=True,
    )

    scheduler.add_job(
        cleanup_expired_trials,
        trigger="interval",
        hours=1,
        id="cleanup_expired_trials",
        max_instances=1,
        replace_existing=True,
    )

    scheduler.add_job(
        expired_subscriptions_notifier1,
        trigger="interval",
        hours=1,
        args=[bot],
        id="expired_subscriptions_notifier",
        max_instances=1,
        replace_existing=True,
    )

    scheduler.add_job(
        trial_reminder_task,
        trigger="interval",
        hours=6,
        args=[bot],
        id="trial_reminder_task",
        max_instances=1,
        replace_existing=True,
    )

    scheduler.start()

def shutdown_scheduler(bot):
    scheduler.shutdown(wait=True)