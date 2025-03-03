from flask import Flask
from database.database_cmds import Database

DATA_PATH = "uploads/realistic_data.xlsx"
app = Flask("app")
app.database = Database()