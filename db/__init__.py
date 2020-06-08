from sqlitedict import SqliteDict
import yaml


class DB():

    def __init__(self, db_path, defaults_path):
        self.dict = SqliteDict(db_path, autocommit=True)
        with open(defaults_path, 'r') as f:
            defaults = yaml.safe_load(f.read())
        for k in defaults:
            if k not in self.dict:
                self.dict[k] = defaults[k]

    def __getitem__(self, key):
        return self.dict[key]

    def __setitem__(self, key, value):
        self.dict[key] = value

    def close(self):
        self.dict.close()
