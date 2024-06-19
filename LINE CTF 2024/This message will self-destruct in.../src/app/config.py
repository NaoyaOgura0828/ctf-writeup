import os

FILE_SAVE_PATH = 'files/'
URLBASE = os.getenv('URLBASE', 'http://localhost')
MYSQL_HOST = os.getenv('MYSQL_HOST', 'mysql')
MYSQL_USER = os.getenv('MYSQL_USER', 'mysql')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', 'mysql')
TRIAL_IMAGE = os.getenv('TRIAL_IMAGE')
DESTRUCTION_SECONDS = int(os.getenv('DESTRUCTION_SECONDS', 10))