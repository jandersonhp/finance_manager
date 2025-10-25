from dataclasses import dataclass

@dataclass
class MonthlyExpense:
    description: str
    amount: float
    due_date: str
    paid: bool = False