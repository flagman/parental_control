from db import keys, DB
db = DB('db.sql', 'defaults.yml')
db[keys.daily_time_spent]
