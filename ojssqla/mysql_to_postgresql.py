import os
import sys

import ojs
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, MetaData, inspect, Table, Column, Boolean, DateTime, Float
from sqlalchemy.types import TIMESTAMP as POSTGRES_TIMESTAMP, TEXT as POSTGRES_TEXT, VARCHAR as POSTGRES_VARCHAR
from sqlalchemy.dialects.postgresql import BIT as POSTGRES_BIT
from sqlalchemy.dialects.mysql.base import TINYINT, VARCHAR, DATETIME, TIMESTAMP, DOUBLE, TEXT, BIT
from sqlalchemy.ext.declarative import declarative_base

from sshtunnel import SSHTunnelForwarder

username = os.getenv('MYSQL_USER')
password = os.getenv('MYSQL_PASSWORD')
host = os.getenv('MYSQL_HOST')
port = int(os.getenv('MYSQL_PORT', '3306'))
localhost = '127.0.0.1'

class Tunnel(object):
    def __init__(self,
                 ssh_host,
                 ssh_port,
                 ssh_username,
                 remote_host,
                 remote_port,
                 ssh_pkey='{}/.ssh/id_rsa'.format(os.getenv('HOME'))):
        self._tunnel = SSHTunnelForwarder((ssh_host, ssh_port),
                                          ssh_username=ssh_username,
                                          ssh_pkey=ssh_pkey,
                                          remote_bind_address=(remote_host,
                                                               remote_port),
                                          set_keepalive=1.0)

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, stype, svalue, straceback):
        self.stop()

    def start(self):
        self._tunnel.start()

    def get_local_bind_port(self):
        return self._tunnel.local_bind_port

    def stop(self):
        self._tunnel.stop()


def copy_table_schemas_to_postgresdb(mysql_base, postgres_engine):
    
    postgres_engine._metadata = MetaData(bind=postgres_engine)
    
    for klass in mysql_base.classes:
        table = Table(klass.__table__.name, postgres_engine._metadata)
        for column in klass.__table__.columns:
            if isinstance(column.type, TEXT):
                table.append_column(Column(column.name, POSTGRES_TEXT(collation=''), nullable=column.nullable))
            elif isinstance(column.type, VARCHAR):
                table.append_column(Column(column.name, POSTGRES_VARCHAR(length=column.type.length, collation=''), nullable=column.nullable))
            elif isinstance(column.type, TINYINT):
                table.append_column(Column(column.name, Boolean(), nullable=column.nullable))
            elif isinstance(column.type, DATETIME):
                table.append_column(Column(column.name, DateTime(), nullable=column.nullable))
            elif isinstance(column.type, TIMESTAMP):
                table.append_column(Column(column.name, POSTGRES_TIMESTAMP(), nullable=column.nullable))
            elif isinstance(column.type, DOUBLE):
                table.append_column(Column(column.name, Float(), nullable=column.nullable))
            elif isinstance(column.type, BIT):
                table.append_column(Column(column.name, POSTGRES_BIT(length=column.type.length), nullable=column.nullable))
            else:
                table.append_column(column.copy())
                
        print table.name
        table.create()

def quick_mapper(table):
    Base = declarative_base()
    class GenericMapper(Base):
        __table__ = table
    return GenericMapper
    
def copy_table_data_to_postgresdb(mysql_base, mysql_engine, postgres_engine):
    postgres_engine.execute("SET CLIENT_ENCODING TO 'LATIN1';")
    PostgresSession = sessionmaker(bind=postgres_engine, autoflush=False)
    postgres_session = PostgresSession()
    MySQLSession = sessionmaker(bind=mysql_engine)
    mysql_session = MySQLSession()

    
    
    for klass in mysql_base.classes:
        print klass.__table__.name
        dest_table = Table(klass.__table__.name, MetaData(bind=postgres_engine), autoload=True)
        dest_columns = dest_table.columns.keys()
    
        table = Table(klass.__table__.name, MetaData(bind=mysql_engine), autoload=True)
        NewRecord = quick_mapper(table)

        for record in mysql_session.query(table).all():
            data = {}
            for column in dest_columns:
                value = getattr(record, column)
                if isinstance(table.columns[column].type, TINYINT):
                    value = bool(value)
                elif isinstance(value, str):
                    value = value.decode('latin8')
                    
                data[str(column)] = value
            postgres_session.merge(NewRecord(**data))
        postgres_session.commit()

    
    
def copy_from_mysqldb_to_postgresdb(db_name, from_host, to_host):
    with Tunnel(from_host, 22, '', host, port) as tunnel:
        mysql_engine = create_engine(
            'mysql+pymysql://{}:{}@{}:{}/{}'.format(
                username,
                password,
                localhost,
                tunnel.get_local_bind_port(),
                db_name
            )
        )

        postgres_engine = create_engine(
            'postgresql+psycopg2://{}:{}@{}/{}'.format(
                'ojs',
                'ojs',
                to_host,
                'ojs'
            )
        )
        
        mysql_base = automap_base()
        mysql_base.prepare(mysql_engine, reflect=True)
    
        copy_table_schemas_to_postgresdb(mysql_base, postgres_engine)
        copy_table_data_to_postgresdb(mysql_base, mysql_engine, postgres_engine)
    

    

if __name__ == '__main__':
    copy_from_mysqldb_to_postgresdb(sys.argv[1], 'dbfs-1.uplabs0.com', sys.argv[2])
