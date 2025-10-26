from datetime import datetime, timedelta
from typing import List, Dict, Any
from tkinter import messagebox
from ..models.wallet import Wallet, Transaction, Bank
from ..models.cards import CreditCard, Installment
from ..models.expenses import MonthlyExpense
from ..repositories.json_repository import JSONRepository

class FinanceService:
    def __init__(self):
        self.repository = JSONRepository()
        self.installments: List[Installment] = []
        self._load_data()
    
    def _load_data(self):
        data = self.repository.load_data()
        
        # Load wallet
        wallet_data = data.get('wallet', {})
        banks_data = wallet_data.get('banks', [])
        banks = [Bank(**b) for b in banks_data] if banks_data else [Bank(name="Geral")]
        
        self.wallet = Wallet(
            balance=wallet_data.get('balance', 0.0),
            history=[Transaction(**t) for t in wallet_data.get('history', [])],
            banks=banks
        )
        
        # Load cards
        self.cards: List[CreditCard] = []
        cards_data = data.get('cards', [])
        
        if isinstance(cards_data, list):
            for card_data in cards_data:
                if isinstance(card_data, dict):
                    if 'id' not in card_data:
                        card_data['id'] = f"{card_data['name']}_{datetime.now().timestamp()}"
                    self.cards.append(CreditCard(**card_data))
        elif isinstance(cards_data, dict):
            self._migrate_old_cards_format(cards_data)
        
        # Load expenses
        self.expenses: Dict[str, List[MonthlyExpense]] = {}
        expenses_data = data.get('expenses', {})
        for month, expenses_list in expenses_data.items():
            if isinstance(expenses_list, list):
                self.expenses[month] = [MonthlyExpense(**e) for e in expenses_list]
        
        # Load installments
        self.installments = [Installment(**i) for i in data.get('installments', [])]
    
    def _migrate_old_cards_format(self, old_cards_data: Dict[str, List[Dict]]):
        """Migra do formato antigo (cartões por mês) para o novo (cartões fixos)"""
        all_cards = {}
        
        for month, cards_list in old_cards_data.items():
            if isinstance(cards_list, list):
                for card_data in cards_list:
                    if isinstance(card_data, dict) and 'name' in card_data:
                        card_name = card_data['name']
                        if card_name not in all_cards:
                            all_cards[card_name] = card_data
        
        for card_data in all_cards.values():
            if 'id' not in card_data:
                card_data['id'] = f"{card_data['name']}_{datetime.now().timestamp()}"
            if 'available' not in card_data:
                card_data['available'] = card_data.get('limit', 0) - card_data.get('used', 0)
            self.cards.append(CreditCard(**card_data))
    
    def save_data(self):
        data = {
            'wallet': {
                'balance': self.wallet.balance,
                'history': [{
                    'date': t.date,
                    'type': t.type,
                    'amount': t.amount,
                    'description': t.description,
                    'bank': t.bank
                } for t in self.wallet.history],
                'banks': [{
                    'name': b.name,
                    'balance': b.balance
                } for b in self.wallet.banks]
            },
            'cards': [{
                'id': c.id,
                'name': c.name,
                'limit': c.limit,
                'used': c.used,
                'due_date': c.due_date,
                'available': c.available
            } for c in self.cards],
            'expenses': {
                month: [{
                    'description': e.description,
                    'amount': e.amount,
                    'due_date': e.due_date,
                    'paid': e.paid,
                    'recurring': e.recurring,
                    'end_date': e.end_date
                } for e in expenses]
                for month, expenses in self.expenses.items()
            },
            'installments': [{
                'description': i.description,
                'total_amount': i.total_amount,
                'installments': i.installments,
                'current_installment': i.current_installment,
                'installment_value': i.installment_value,
                'purchase_date': i.purchase_date,
                'card_name': i.card_name
            } for i in self.installments]
        }
        self.repository.save_data(data)

    # Wallet operations
    def get_balance(self) -> float:
        return self.wallet.balance
    
    def add_income(self, amount: float, description: str, bank: str = "Geral") -> bool:
        if amount <= 0:
            return False
        
        if bank != "Geral" and not any(b.name == bank for b in self.wallet.banks):
            self.add_bank(bank)
        
        transaction = Transaction(
            date=datetime.now().strftime("%d/%m/%Y %H:%M"),
            type="Entrada",
            amount=amount,
            description=description,
            bank=bank
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
            description=description,
            bank="Geral"
        )
        self.wallet.add_transaction(transaction)
        self.save_data()
        return True
    
    def get_transaction_history(self) -> List[Transaction]:
        return self.wallet.history
    
    def edit_transaction(self, transaction_index: int, new_amount: float, 
                        new_description: str, new_bank: str) -> bool:
        if 0 <= transaction_index < len(self.wallet.history):
            self.wallet.edit_transaction(transaction_index, new_amount, new_description, new_bank)
            self.save_data()
            return True
        return False
    
    def reset_wallet(self):
        self.wallet.balance = 0.0
        self.wallet.history = []
        for bank in self.wallet.banks:
            bank.balance = 0.0
        self.save_data()
        return True

    # Banks operations
    def add_bank(self, bank_name: str) -> bool:
        self.wallet.add_bank(bank_name)
        self.save_data()
        return True
    
    def get_banks(self) -> List[Bank]:
        return self.wallet.banks
    
    def get_bank_balance(self, bank_name: str) -> float:
        return self.wallet.get_bank_balance(bank_name)

    # Cards operations
    def get_cards(self) -> List[CreditCard]:
        return self.cards
    
    def add_card(self, name: str, limit: float, due_date: str) -> bool:
        card = CreditCard(name=name, limit=limit, due_date=due_date)
        self.cards.append(card)
        self.save_data()
        return True
    
    def update_card_usage(self, card_index: int, used: float, month_year: str) -> bool:
        if 0 <= card_index < len(self.cards):
            card = self.cards[card_index]
            old_used = card.used
            card.used = used
            
            if used > old_used and used > 0:
                self._sync_card_to_expenses(card, month_year)
            
            self.save_data()
            return True
        return False
    
    def update_card_available(self, card_index: int, new_available: float) -> bool:
        if 0 <= card_index < len(self.cards):
            self.cards[card_index].available = new_available
            self.save_data()
            return True
        return False
    
    def _sync_card_to_expenses(self, card: CreditCard, month_year: str):
        if month_year not in self.expenses:
            self.expenses[month_year] = []
        
        expense_description = f"Fatura {card.name}"
        
        existing_expense_index = None
        for i, expense in enumerate(self.expenses[month_year]):
            if expense.description == expense_description:
                existing_expense_index = i
                break
        
        if existing_expense_index is not None:
            self.expenses[month_year][existing_expense_index].amount = card.used
            self.expenses[month_year][existing_expense_index].due_date = card.due_date
        else:
            expense = MonthlyExpense(
                description=expense_description,
                amount=card.used,
                due_date=card.due_date,
                paid=False
            )
            self.expenses[month_year].append(expense)
    
    def pay_card_invoice(self, card_index: int) -> bool:
        if 0 <= card_index < len(self.cards):
            card = self.cards[card_index]
            
            if card.used > 0:
                transaction = Transaction(
                    date=datetime.now().strftime("%d/%m/%Y %H:%M"),
                    type="Saída",
                    amount=card.used,
                    description=f"Fatura {card.name}"
                )
                
                if transaction.amount > self.wallet.balance:
                    return False
                
                self.wallet.add_transaction(transaction)
                card.used = 0.0
                card.available = card.limit
                
                self._remove_card_expense(card.name)
                
                self.save_data()
                return True
        return False
    
    def _remove_card_expense(self, card_name: str):
        expense_description = f"Fatura {card_name}"
        for month in self.expenses:
            self.expenses[month] = [e for e in self.expenses[month] if e.description != expense_description]
    
    def update_card_limit(self, card_index: int, new_limit: float) -> bool:
        if 0 <= card_index < len(self.cards):
            self.cards[card_index].limit = new_limit
            self.save_data()
            return True
        return False
    
    def update_card_due_date(self, card_index: int, new_due_date: str) -> bool:
        if 0 <= card_index < len(self.cards):
            self.cards[card_index].due_date = new_due_date
            self.save_data()
            return True
        return False
    
    def delete_card(self, card_index: int) -> bool:
        if 0 <= card_index < len(self.cards):
            card_name = self.cards[card_index].name
            self._remove_card_expense(card_name)
            del self.cards[card_index]
            self.save_data()
            return True
        return False

    # Installments operations
    def add_installment(self, description: str, total_amount: float, installments: int, 
                       card_name: str, purchase_date: str = None) -> bool:
        if purchase_date is None:
            purchase_date = datetime.now().strftime("%d/%m/%Y")
        
        installment_value = total_amount / installments
        
        installment = Installment(
            description=description,
            total_amount=total_amount,
            installments=installments,
            current_installment=1,
            installment_value=installment_value,
            purchase_date=purchase_date,
            card_name=card_name
        )
        
        self.installments.append(installment)
        
        for card in self.cards:
            if card.name == card_name:
                card.used += installment_value
                self._sync_card_to_expenses(card, datetime.now().strftime("%Y-%m"))
                break
        
        self.save_data()
        return True
    
    def process_installments(self, month_year: str):
        current_month = datetime.now().strftime("%Y-%m")
        if month_year != current_month:
            return
        
        for installment in self.installments[:]:
            if installment.current_installment < installment.installments:
                installment.current_installment += 1
                
                for card in self.cards:
                    if card.name == installment.card_name:
                        card.used += installment.installment_value
                        self._sync_card_to_expenses(card, month_year)
                        break
            else:
                self.installments.remove(installment)
        
        self.save_data()

    # Expenses operations
    def get_expenses(self, month_year: str) -> List[MonthlyExpense]:
        if month_year not in self.expenses:
            self.expenses[month_year] = []
        return self.expenses[month_year]
    
    def get_monthly_expenses_total(self, month_year: str) -> float:
        if month_year not in self.expenses:
            return 0.0
        return sum(expense.amount for expense in self.expenses[month_year])
    
    def add_expense_monthly(self, month_year: str, description: str, amount: float, 
                          due_date: str, recurring: bool = False, end_date: str = None) -> bool:
        if month_year not in self.expenses:
            self.expenses[month_year] = []
        
        for expense in self.expenses[month_year]:
            if expense.description == description and not expense.description.startswith("Fatura "):
                return False
        
        expense = MonthlyExpense(
            description=description,
            amount=amount,
            due_date=due_date,
            recurring=recurring,
            end_date=end_date
        )
        self.expenses[month_year].append(expense)
        self.save_data()
        
        if recurring:
            self._create_recurring_expenses(month_year, description, amount, due_date, end_date)
        
        return True
    
    def _create_recurring_expenses(self, start_month: str, description: str, amount: float, 
                                 due_date: str, end_date: str = None):
        current_date = datetime.strptime(start_month + "-01", "%Y-%m-%d")
        end_date_obj = datetime.strptime(end_date + "-01", "%Y-%m-%d") if end_date else current_date.replace(year=current_date.year + 1)
        
        while current_date <= end_date_obj:
            month_year = current_date.strftime("%Y-%m")
            if month_year != start_month and month_year not in self.expenses:
                self.expenses[month_year] = []
            
            exists = any(e.description == description for e in self.expenses.get(month_year, []))
            if not exists:
                expense = MonthlyExpense(
                    description=description,
                    amount=amount,
                    due_date=due_date,
                    recurring=True,
                    end_date=end_date
                )
                if month_year not in self.expenses:
                    self.expenses[month_year] = []
                self.expenses[month_year].append(expense)
            
            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year + 1, month=1)
            else:
                current_date = current_date.replace(month=current_date.month + 1)
    
    def toggle_expense_paid(self, month_year: str, expense_index: int) -> bool:
        if month_year in self.expenses and 0 <= expense_index < len(self.expenses[month_year]):
            expense = self.expenses[month_year][expense_index]
            
            if not expense.paid:
                is_card_invoice = expense.description.startswith("Fatura ")
                
                transaction = Transaction(
                    date=datetime.now().strftime("%d/%m/%Y %H:%M"),
                    type="Saída",
                    amount=expense.amount,
                    description=expense.description
                )
                
                if transaction.amount > self.wallet.balance and not is_card_invoice:
                    return False
                
                if not is_card_invoice:
                    self.wallet.add_transaction(transaction)
                
                if is_card_invoice:
                    card_name = expense.description.replace("Fatura ", "")
                    for card in self.cards:
                        if card.name == card_name:
                            card.used = 0.0
                            break
            
            expense.paid = not expense.paid
            self.save_data()
            return True
        return False
    
    def update_expense_amount(self, month_year: str, expense_index: int, new_amount: float) -> bool:
        if month_year in self.expenses and 0 <= expense_index < len(self.expenses[month_year]):
            self.expenses[month_year][expense_index].amount = new_amount
            self.save_data()
            return True
        return False
    
    def update_expense_due_date(self, month_year: str, expense_index: int, new_due_date: str) -> bool:
        if month_year in self.expenses and 0 <= expense_index < len(self.expenses[month_year]):
            self.expenses[month_year][expense_index].due_date = new_due_date
            self.save_data()
            return True
        return False
    
    def update_expense_description(self, month_year: str, expense_index: int, new_description: str) -> bool:
        if month_year in self.expenses and 0 <= expense_index < len(self.expenses[month_year]):
            self.expenses[month_year][expense_index].description = new_description
            self.save_data()
            return True
        return False
    
    def delete_expense(self, month_year: str, expense_index: int) -> bool:
        if month_year in self.expenses and 0 <= expense_index < len(self.expenses[month_year]):
            del self.expenses[month_year][expense_index]
            self.save_data()
            return True
        return False