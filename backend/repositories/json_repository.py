import json
import os
from typing import Dict, Any
from datetime import datetime

class JSONRepository:
    def __init__(self, data_file: str = "data/finance_data.json"):
        self.data_file = data_file
        os.makedirs(os.path.dirname(data_file), exist_ok=True)
    
    def load_data(self) -> Dict[str, Any]:
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return self._get_default_data()
        return self._get_default_data()
    
    def save_data(self, data: Dict[str, Any]):
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def _get_default_data(self) -> Dict[str, Any]:
        current_month = datetime.now().strftime("%Y-%m")
        return {
            'wallet': {
                'balance': 0.0,
                'history': []
            },
            'cards': {
                current_month: []
            },
            'expenses': {
                current_month: []
            }
        }