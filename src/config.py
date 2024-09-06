import tomli
from typing import List

class Config:
    
    def __init__(self, config_file: str = 'config.toml'):
        self.config_file = config_file
        self._load_config()
    
    def _load_config(self):
        with open(self.config_file, 'rb') as file:
            config_data = tomli.load(file)
            self.database = config_data.get('database', {})
            self.telegram = config_data.get('telegram', {})
    
    def get_db_connection_string(self) -> str:
        return self.database['driver'] + self.database['db']
    
    def get_telegram_token(self) -> str:
        return self.telegram.get('token', '')
    
    def get_telegram_members(self) -> List[str]:
        return self.telegram.get('members', [])
    
    def __repr__(self) -> str:
        return (
            f"Config(database={self.database}, "
            f"telegram={{token=***, members={self.telegram.get('members', [])}}})")