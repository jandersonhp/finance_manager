from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime

@dataclass
class CreditCard:
    name: str
    limit: float
    used: float = 0.0
    due_date: str = ""
    id: Optional[str] = None
    available: float = 0.0  # Novo campo para limite disponível personalizado
    
    def __post_init__(self):
        if self.id is None:
            self.id = f"{self.name}_{id(self)}"
        if self.available == 0.0:
            self.available = self.limit - self.used
    
    @property
    def calculated_available(self) -> float:
        return self.limit - self.used

@dataclass
class Installment:
    """Representa uma compra parcelada"""
    description: str
    total_amount: float
    installments: int
    current_installment: int
    installment_value: float
    purchase_date: str
    card_name: str