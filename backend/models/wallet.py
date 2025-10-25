from dataclasses import dataclass
from datetime import datetime
from typing import List

@dataclass
class Transaction:
    date: str
    type: str
    amount: float
    description: str

@dataclass
class Wallet:
    balance: float = 0.0
    history: List[Transaction] = None
    
    def __post_init__(self):
        if self.history is None:
            self.history = []
    
    def add_transaction(self, transaction: Transaction):
        if transaction.type == "Entrada":
            self.balance += transaction.amount
        else:
            self.balance -= transaction.amount
        self.history.append(transaction)