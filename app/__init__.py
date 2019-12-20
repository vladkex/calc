from flask import Flask
from config import Config
import psycopg2
from flask_bootstrap import Bootstrap

app = Flask(__name__)
app.config.from_object(Config)
conn = psycopg2.connect(dbname='d9tapmbgnodji3', user='myrprjlwezkjmr', password='d3a1dbd005ebdab311213e835004ddddaf4772c89b1bbf0cc3bfa9bd3bd44c79', host='ec2-174-129-255-37.compute-1.amazonaws.com')
bootstrap = Bootstrap(app)

from app import routes



