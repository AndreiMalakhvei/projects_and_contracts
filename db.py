import os
from typing import List, Tuple, Literal

import psycopg2
from dotenv import load_dotenv
from datetime import date
from psycopg2.extensions import AsIs

ContractStatus = Literal['draft', 'active', 'completed']


class PostgresqlDB():
    load_dotenv()
    DBNAME = os.getenv('DBNAME')
    USER = os.getenv('USER')
    PASSWORD = os.getenv('PASSWORD')
    HOST = os.getenv('HOST')

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(PostgresqlDB, cls).__new__(cls)
            if not cls.instance.db_exists[0][0]:
                cls.instance.create_app_tables()
        return cls.instance

    @property
    def db_exists(self) -> List[Tuple]:
        with psycopg2.connect(dbname=PostgresqlDB.DBNAME, user=PostgresqlDB.USER, password=PostgresqlDB.PASSWORD,
                              host=PostgresqlDB.HOST) as conn:
            with conn.cursor() as cur:
                cur.execute('''
                SELECT EXISTS (
                SELECT FROM 
                    information_schema.tables 
                WHERE            
                    table_name = 'projects'
                );
                ''')
                return cur.fetchall()

    @staticmethod
    def create_app_tables() -> None:
        with psycopg2.connect(dbname=PostgresqlDB.DBNAME, user=PostgresqlDB.USER, password=PostgresqlDB.PASSWORD,
                              host=PostgresqlDB.HOST) as conn:
            with conn.cursor() as cur:
                cur.execute('''
                    CREATE TABLE IF NOT EXISTS projects(
                        id serial PRIMARY KEY,
                        name CHARACTER VARYING(300) NOT NULL,
                        creat_date DATE  );                    
                    
                    CREATE TYPE contract_status AS ENUM ('draft', 'active', 'completed');
                    
                    CREATE TABLE IF NOT EXISTS contracts (
                        id serial PRIMARY KEY,
                        name CHARACTER VARYING(300) NOT NULL,
                        creat_date DATE,
                        act_date DATE,
                        status contract_status DEFAULT 'draft',
                        project_id INT,
                        CONSTRAINT fk_project
                            FOREIGN KEY(project_id)
                            REFERENCES projects(id)      
                        );                     
                       ''')

    @staticmethod
    def create_record(table: str, name: str) -> None:
        with psycopg2.connect(dbname=PostgresqlDB.DBNAME, user=PostgresqlDB.USER, password=PostgresqlDB.PASSWORD,
                              host=PostgresqlDB.HOST) as conn:
            with conn.cursor() as cur:
                cur.execute('''
                    INSERT INTO %s(name, creat_date)
                    VALUES (%s, %s); 
                        ''', (AsIs(table), name, date.today())
                            )

    @staticmethod
    def get_all_records(table: str) -> List[Tuple]:
        with psycopg2.connect(dbname=PostgresqlDB.DBNAME, user=PostgresqlDB.USER, password=PostgresqlDB.PASSWORD,
                              host=PostgresqlDB.HOST) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    ('''
                    SELECT * FROM %s                        
                        '''), (AsIs(table), )
                    )
                return cur.fetchall()

    @staticmethod
    def get_single_record(table: str, id: int) -> List[Tuple]:
        with psycopg2.connect(dbname=PostgresqlDB.DBNAME, user=PostgresqlDB.USER, password=PostgresqlDB.PASSWORD,
                              host=PostgresqlDB.HOST) as conn:
            with conn.cursor() as cur:
                cur.execute('''
                    SELECT * FROM %s
                    WHERE id = %s                    
                        ''', (AsIs(table), id))
                return cur.fetchall()

    @staticmethod
    def get_project_contracts(id: int) -> List[Tuple]:
        with psycopg2.connect(dbname=PostgresqlDB.DBNAME, user=PostgresqlDB.USER, password=PostgresqlDB.PASSWORD,
                              host=PostgresqlDB.HOST) as conn:
            with conn.cursor() as cur:
                cur.execute('''
                    SELECT * FROM contracts  
                    WHERE project_id = %s                    
                        ''', (id, ))
                return cur.fetchall()

    @staticmethod
    def get_contracts_by_status(status: ContractStatus = None, project_id: int = None,
                                exclude: bool = False) -> List[Tuple]:
        with psycopg2.connect(dbname=PostgresqlDB.DBNAME, user=PostgresqlDB.USER, password=PostgresqlDB.PASSWORD,
                              host=PostgresqlDB.HOST) as conn:
            with conn.cursor() as cur:
                if project_id:
                    if exclude:
                        cur.execute('''
                                    SELECT * FROM contracts
                                    WHERE status = %s AND (project_id != %s OR project_id IS NULL)                    
                                            ''', (status, project_id))
                    else:
                        cur.execute('''
                                    SELECT * FROM contracts
                                    WHERE status = %s AND project_id = %s                    
                                            ''', (status, project_id))
                else:
                    cur.execute('''
                                SELECT * FROM contracts  
                                WHERE status = %s                    
                                        ''', (status,))
                return cur.fetchall()

    @staticmethod
    def change_contract_status(id: int, status: ContractStatus ) -> None:
        if status == 'active':
            with psycopg2.connect(dbname=PostgresqlDB.DBNAME, user=PostgresqlDB.USER, password=PostgresqlDB.PASSWORD,
                                  host=PostgresqlDB.HOST) as conn:
                with conn.cursor() as cur:
                    cur.execute('''
                        UPDATE contracts SET
                                act_date = %s,
                                status = %s
                                WHERE id = %s            
                            ''', (date.today(), status, id))
        else:
            with psycopg2.connect(dbname=PostgresqlDB.DBNAME, user=PostgresqlDB.USER, password=PostgresqlDB.PASSWORD,
                                  host=PostgresqlDB.HOST) as conn:
                with conn.cursor() as cur:
                    cur.execute('''
                        UPDATE contracts SET
                                status = %s
                                WHERE id = %s            
                            ''', (status, id))

    @staticmethod
    def add_contract_to_project(project_id: int, contract_id: int) -> None:
        with psycopg2.connect(dbname=PostgresqlDB.DBNAME, user=PostgresqlDB.USER, password=PostgresqlDB.PASSWORD,
                              host=PostgresqlDB.HOST) as conn:
            with conn.cursor() as cur:
                cur.execute('''
                    UPDATE contracts SET
                                project_id = %s
                                WHERE id = %s                
                        ''', (project_id, contract_id))
