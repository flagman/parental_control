import signal
import atexit
from router import Router, RouterError
from db import keys, DB
import os
import time
import logging
import datetime

logging.basicConfig(level=logging.INFO)

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

db = DB(os.path.join(SCRIPT_DIR, 'db.sql'),
        os.path.join(SCRIPT_DIR, 'defaults.yml'))
router = Router(db[keys.router_ip],
                db[keys.router_password], db[keys.router_key])


def close_db(signum, frame):
    db.close()
    exit(0)


signal.signal(signal.SIGINT, close_db)
signal.signal(signal.SIGTERM, close_db)


def connected_controlled_devices(devices):
    controlled_devices = db[keys.mac_addresses]
    return [device for device in devices if device.mac in controlled_devices]


def devices_with_internet_on(devices):
    return [device for device in devices if device.is_enabled]


def devices_with_internet_off(devices):
    return [device for device in devices if device.is_enabled]


def disable_devices(devices):
    for device in devices:
        router.set_device_state(device, is_enabled=False)


def enable_devices(devices):
    for device in devices:
        router.set_device_state(device, is_enabled=True)


def increment_daily_usage_time(timestamp):
    db[keys.daily_time_spent] += time.time() - timestamp


def enable_disabled_devices(controlled_devices, enabled_devices):
    enable_devices(list(set(controlled_devices) - set(enabled_devices)))


def disable_internet_if_needed():
    if db[keys.daily_time_spent] >= db[keys.allowed_time_daily] * 60:
        db[keys.is_internet_on] = False


def start_of_day_timestamp():
    today = datetime.date.today()  # or datetime.now to use local timezone
    return datetime.datetime(year=today.year, month=today.month,
                             day=today.day, hour=6, second=0).timestamp()


def reset_daily_usage_if_needed():
    start_of_day = start_of_day_timestamp()
    if db[keys.today] != start_of_day:
        db[keys.today] = start_of_day
        db[keys.daily_time_spent] = 0


def sync_state(timestamp):
    try:
        devices = router.device_list()
    except RouterError:
        return

    controlled_devices = connected_controlled_devices(devices)
    enabled_devices = devices_with_internet_on(controlled_devices)

    if not controlled_devices:
        logging.info("All controlled devices is offline.")
        return

    if not db[keys.is_parental_control]:
        enable_disabled_devices(controlled_devices, enabled_devices)
        logging.info("Parental controll is off. All devices enabled")
        return

    if not db[keys.is_internet_on]:
        if not enabled_devices:
            logging.info("Internet is disabled all devices are disabled")
            return
        increment_daily_usage_time(timestamp)
        disable_devices(enabled_devices)
        logging.info(
            "Internet is disabled - some devices was active but now disabled")
        return

    if db[keys.is_internet_on]:
        logging.info("Internet is on... logging time")
        enable_disabled_devices(controlled_devices, enabled_devices)
        if enabled_devices:
            increment_daily_usage_time(timestamp)
        return


timestamp = time.time()
while True:
    reset_daily_usage_if_needed()
    disable_internet_if_needed()
    sync_state(timestamp)
    timestamp = time.time()
    time.sleep(10)
