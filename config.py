import os

class Config(object):
	SECRET_KEY = os.environ.get('SECRET_KEY') or 'eto-moi-secret-key-i-you-ego-not-see'