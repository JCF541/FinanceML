from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import yaml, os
from .base import Base

def get_db_config():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
    config_path = os.path.join(base_dir, 'src', 'config', 'config.yml')

    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    return config['database']

db_conf = get_db_config()

DATABASE_URL = (
    f"postgresql://{db_conf['user']}:{db_conf['password']}@"
    f"{db_conf['host']}:{db_conf['port']}/{db_conf['dbname']}"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def get_session():
    return SessionLocal()
