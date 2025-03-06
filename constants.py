from flask import Flask
from database.database_cmds import Database


class CustomApp(Flask):
    def __init__(self, *args, **kwargs):
        super(CustomApp, self).__init__(*args, **kwargs)
        self.database = Database()


app = CustomApp("app")
