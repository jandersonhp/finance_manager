from dataclasses import dataclass
from typing import Optional

@dataclass
class CreditCard:
    name: str
    limit: float
    used: float = 0.0
    due_date: str = ""
    id: Optional[str] = None
    
    def __post_init__(self):
        if self.id is None:
            self.id = f"{self.name}_{id(self)}"
    
    @property
    def available(self) -> float:
        return self.limit - self.used