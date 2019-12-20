from flask import Flask
from config import Config
import psycopg2
from flask_bootstrap import Bootstrap

app = Flask(__name__)
app.config.from_object(Config)
conn = psycopg2.connect(dbname='calculator_windows_and_doors', user='postgres', password='12345', host='localhost')
bootstrap = Bootstrap(app)

from app import routes



