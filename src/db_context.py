from typing import Optional
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from models import Base

class DbContext:
    
    def __init__(self, db_connection):
        self.engine = create_engine(db_connection, echo=True)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.metadata = Base.metadata

    def get_session(self):
        return self.SessionLocal()

    def close_session(self, session):
        session.close()

    def create_all_tables(self):
        self.metadata.create_all(self.engine)

    def drop_all_tables(self):
        self.metadata.drop_all(self.engine)
        
    def show_all_tables(self) : 
        with self.engine.connect():
            self.metadata.reflect(bind=self.engine) 
            for table_name in self.metadata.tables:
                table = self.metadata.tables[table_name]
                print(f"Table: {table_name}")
                for column in table.columns:
                    print(f"  Column: {column.name} - Type: {column.type}")
                print()
            
    def execute_query(self, query: str, values: Optional[dict] = None) -> None:
        with self.engine.connect() as connection:
            result = connection.execute(query, values or {})
            for row in result:
                print(row)
                
    def table_exists(self, table_name: str) -> bool:
        with self.engine.connect():
            inspector = MetaData()
            inspector.reflect(bind=self.engine)
            return table_name in inspector.tables