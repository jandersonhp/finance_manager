from dataclasses import dataclass
from typing import Optional

@dataclass
class MonthlyExpense:
    description: str
    amount: float
    due_date: str
    paid: bool = False
    recurring: bool = False  # Nova: se repete automaticamente
    end_date: Optional[str] = None  # Nova: até quando se repete