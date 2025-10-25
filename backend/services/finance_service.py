from datetime import datetime
from typing import List, Dict, Any
from ..models.wallet import Wallet, Transaction
from ..models.cards import CreditCard
from ..models.expenses import MonthlyExpense
from ..repositories.json_repository import JSONRepository

class FinanceService:
    def __init__(self):
        self.repository = JSONRepository()
        self._load_data()
    
    def _load_data(self):
        data = self.repository.load_data()
        
        # Load wallet
        wallet_data = data.get('wallet', {})
        self.wallet = Wallet(
            balance=wallet_data.get('balance', 0.0),
            history=[Transaction(**t) for t in wallet_data.get('history', [])]
        )
        
        # Load cards and expenses by month
        self.cards: Dict[str, List[CreditCard]] = {}
        self.expenses: Dict[str, List[MonthlyExpense]] = {}
        
        for month, cards_data in data.get('cards', {}).items():
            self.cards[month] = [CreditCard(**c) for c in cards_data]
        
        for month, expenses_data in data.get('expenses', {}).items():
            self.expenses[month] = [MonthlyExpense(**e) for e in expenses_data]
    
    def save_data(self):
        data = {
            'wallet': {
                'balance': self.wallet.balance,
                'history': [{
                    'date': t.date,
                    'type': t.type,
                    'amount': t.amount,
                    'description': t.description
                } for t in self.wallet.history]
            },
            'cards': {
                month: [{
                    'name': c.name,
                    'limit': c.limit,
                    'used': c.used,
                    'due_date': c.due_date
                } for c in cards]
                for month, cards in self.cards.items()
            },
            'expenses': {
                month: [{
                    'description': e.description,
                    'amount': e.amount,
                    'due_date': e.due_date,
                    'paid': e.paid
                } for e in expenses]
                for month, expenses in self.expenses.items()
            }
        }
        self.repository.save_data(data)
    
    # Wallet operations
    def get_balance(self) -> float:
        return self.wallet.balance
    
    def add_income(self, amount: float, description: str) -> bool:
        if amount <= 0:
            return False
        
        transaction = Transaction(
            date=datetime.now().strftime("%d/%m/%Y %H:%M"),
            type="Entrada",
            amount=amount,
            description=description
        )
        self.wallet.add_transaction(transaction)
        self.save_data()
        return True
    
    def add_expense(self, amount: float, description: str) -> bool:
        if amount <= 0 or amount > self.wallet.balance:
            return False
        
        transaction = Transaction(
            date=datetime.now().strftime("%d/%m/%Y %H:%M"),
            type="Saída",
            amount=amount,
            description=description
        )
        self.wallet.add_transaction(transaction)
        self.save_data()
        return True
    
    def get_transaction_history(self) -> List[Transaction]:
        return self.wallet.history
    
    # Cards operations
    def get_cards(self, month_year: str) -> List[CreditCard]:
        if month_year not in self.cards:
            self.cards[month_year] = []
        return self.cards[month_year]
    
    def add_card(self, month_year: str, name: str, limit: float, due_date: str) -> bool:
        if month_year not in self.cards:
            self.cards[month_year] = []
        
        card = CreditCard(name=name, limit=limit, used=0.0, due_date=due_date)
        self.cards[month_year].append(card)
        self.save_data()
        return True
    
    def update_card_usage(self, month_year: str, card_index: int, used: float) -> bool:
        if month_year in self.cards and 0 <= card_index < len(self.cards[month_year]):
            self.cards[month_year][card_index].used = used
            self.save_data()
            return True
        return False
    
    # Expenses operations
    def get_expenses(self, month_year: str) -> List[MonthlyExpense]:
        if month_year not in self.expenses:
            self.expenses[month_year] = []
        return self.expenses[month_year]
    
    def add_expense_monthly(self, month_year: str, description: str, amount: float, due_date: str) -> bool:
        if month_year not in self.expenses:
            self.expenses[month_year] = []
        
        expense = MonthlyExpense(description=description, amount=amount, due_date=due_date)
        self.expenses[month_year].append(expense)
        self.save_data()
        return True
    
    def toggle_expense_paid(self, month_year: str, expense_index: int) -> bool:
        if month_year in self.expenses and 0 <= expense_index < len(self.expenses[month_year]):
            self.expenses[month_year][expense_index].paid = not self.expenses[month_year][expense_index].paid
            self.save_data()
            return True
        return False