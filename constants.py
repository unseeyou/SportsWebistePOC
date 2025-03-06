from flask import Flask
from database.database_cmds import Database

app = Flask("app")
app.database = Database()