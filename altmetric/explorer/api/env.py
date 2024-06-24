import os
import sys

from dotenv import load_dotenv

APP_ENV = os.environ.get('APP_ENV', 'development')

for envfile in ('.env', f'.env.{APP_ENV}', f'.env.{APP_ENV}.local'):
    envpath = os.path.abspath(f'{envfile}')
    if os.path.isfile(envpath):
        print(f'Found env file at {envpath}', file=sys.stderr)
        load_dotenv(envpath)

API_KEY = os.environ.get('API_KEY')
API_SECRET = os.environ.get('API_SECRET')
