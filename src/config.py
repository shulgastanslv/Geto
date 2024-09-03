import tomllib
from typing import List

from db.db_context import DbContext

class Config:
    
    def __init__(self, config_file: str = 'config.toml'):
        self.config_file = config_file
        self._load_config()
    
    def _load_config(self):
        with open(self.config_file, 'rb') as file:
            config_data = tomllib.load(file)
            self.database = config_data.get('database', {})
            self.telegram = config_data.get('telegram', {})
    
    def get_db_connection_string(self) -> str:
        return (
            f"{str(self.database['host']) + ":" + 
            str(self.database['password']) + str(self.database['user']) 
            + ":" + str(self.database['port']) 
            + "/" + str(self.database['database_name'])}"
    )
    
    def get_telegram_token(self) -> str:
        return self.telegram.get('token', '')
    
    def get_telegram_members(self) -> List[str]:
        return self.telegram.get('members', [])
    
    def __repr__(self) -> str:
        return (
            f"Config(database={self.database}, "
            f"telegram={{token=***, members={self.telegram.get('members', [])}}})")