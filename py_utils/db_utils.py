from sqlalchemy import create_engine
from loguru import logger
from urllib.parse import quote
import os


class DbConnection:
    def __init__(self):
        try:
            self.host = os.getenv('ServerIp', "127.0.0.1")
            self.port = os.getenv('Port', "5432")
            self.database = os.getenv('Database', "postgres")
            self.username = os.getenv('UserId', "postgres")
            self.password = os.getenv('Password', "postgres")
            self.db_type = os.getenv("DbType", 'postgresql')
            self.conn_type = os.getenv("ConnType", 'psycopg2')
        except Exception as e:
            logger.error(f"The database env var has somme wrong. Here is full info {e}")
        self._generate_engine()

    def _generate_engine(self):
        engine_str = '{db_type}+{conn_type}://{username}:{password}@{host}:{port}/{database}'.format(
            db_type=self.db_type,
            conn_type=self.conn_type,
            username=quote(self.username),
            password=quote(self.password),
            host=self.host,
            port=self.port,
            database=self.database)
        self.conn_engine = create_engine(engine_str)
        logger.info('{host}:{port} - {database} engine are created successfully.'.format(host=self.host,
                                                                                         port=self.port,
                                                                                         database=self.database))