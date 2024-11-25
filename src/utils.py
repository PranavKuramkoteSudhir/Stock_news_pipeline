import configparser
import os
import boto3

# Path to your config file
CONFIG_FILE = os.path.join(os.path.dirname(__file__), '..', 'config', 'config.conf')

# Read the config file
config = configparser.ConfigParser()
config.read(CONFIG_FILE)

# API Configuration
API_KEY = config.get('api', 'key', fallback='')
API_URL = config.get('api', 'url', fallback='') 

# Database Configuration
DB_HOST = config.get('database', 'host', fallback='localhost')
DB_PORT = config.getint('database', 'port', fallback=5432)
DB_NAME = config.get('database', 'name', fallback='')
DB_USER = config.get('database', 'user', fallback='')
DB_PASSWORD = config.get('database', 'password', fallback='')

# AWS Configuration
AWS_ACCESS_KEY_ID = config.get('aws', 'access_key_id', fallback='')
AWS_SECRET_ACCESS_KEY = config.get('aws', 'secret_access_key', fallback='')
AWS_SESSION_TOKEN = config.get('aws', 'session_token', fallback=None)
AWS_REGION = config.get('aws', 'region', fallback='us-east-1')

# Other configurations
DATA_DIRECTORY = config.get('paths', 'data_directory', fallback='/tmp/data')

def get_database_url():
    return f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

def get_aws_session():
    return boto3.Session(
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        aws_session_token=AWS_SESSION_TOKEN,
        region_name=AWS_REGION
    )
if __name__=='__main__':
    print(API_URL)
