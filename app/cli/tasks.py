from apscheduler.schedulers.blocking import BlockingScheduler

from app import app, tasks


@app.cli.group("tasks")
def group():
    pass


@group.command("run")
def run():
    tasks.run_all()

    if app.debug:
        return

    scheduler = BlockingScheduler()
    for fn, trigger, trigger_kwargs in tasks.TASKS:
        scheduler.add_job(fn, trigger, **trigger_kwargs)
    scheduler.start()
