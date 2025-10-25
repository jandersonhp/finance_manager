from dataclasses import dataclass

@dataclass
class CreditCard:
    name: str
    limit: float
    used: float
    due_date: str
    
    @property
    def available(self) -> float:
        return self.limit - self.used