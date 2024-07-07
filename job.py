import logging
import signal
import sys
import time
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler

from auto_unpack import App

logger = logging.getLogger(__name__)

# 时间间隔 单位秒
job_interval_seconds = 60 * 60  # 1 hour

scheduler = BackgroundScheduler()


def signal_handler(_sig, _frame):
    logger.info('Received signal, shutting down scheduler...')
    scheduler.shutdown(wait=False)
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


app = App()

scheduler.add_job(
    app.run,
    trigger='interval',
    seconds=job_interval_seconds,
    next_run_time=datetime.now()
)


if __name__ == '__main__':
    scheduler.start()
    while True:
        time.sleep(60 * 5)
