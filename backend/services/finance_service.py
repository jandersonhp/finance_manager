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
        
        # Load cards - CORREÇÃO AQUI
        self.cards: List[CreditCard] = []
        cards_data = data.get('cards', [])
        
        # Verifica se cards_data é uma lista (novo formato) ou dict (formato antigo)
        if isinstance(cards_data, list):
            # Novo formato: lista de cartões fixos
            for card_data in cards_data:
                if isinstance(card_data, dict):
                    # Garante que tem ID
                    if 'id' not in card_data:
                        card_data['id'] = f"{card_data['name']}_{datetime.now().timestamp()}"
                    self.cards.append(CreditCard(**card_data))
        elif isinstance(cards_data, dict):
            # Formato antigo: cartões por mês - converte para novo formato
            self._migrate_old_cards_format(cards_data)
        
        # Load expenses por mês
        self.expenses: Dict[str, List[MonthlyExpense]] = {}
        expenses_data = data.get('expenses', {})
        for month, expenses_list in expenses_data.items():
            if isinstance(expenses_list, list):
                self.expenses[month] = [MonthlyExpense(**e) for e in expenses_list]
    
    def _migrate_old_cards_format(self, old_cards_data: Dict[str, List[Dict]]):
        """Migra do formato antigo (cartões por mês) para o novo (cartões fixos)"""
        all_cards = {}
        
        # Coleta todos os cartões únicos de todos os meses
        for month, cards_list in old_cards_data.items():
            if isinstance(cards_list, list):
                for card_data in cards_list:
                    if isinstance(card_data, dict) and 'name' in card_data:
                        card_name = card_data['name']
                        if card_name not in all_cards:
                            # Usa o cartão do último mês disponível ou o primeiro encontrado
                            all_cards[card_name] = card_data
        
        # Converte para o novo formato
        for card_data in all_cards.values():
            if 'id' not in card_data:
                card_data['id'] = f"{card_data['name']}_{datetime.now().timestamp()}"
            self.cards.append(CreditCard(**card_data))
        
        print(f"Migrados {len(self.cards)} cartões para o novo formato")
    
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
            'cards': [{
                'id': c.id,
                'name': c.name,
                'limit': c.limit,
                'used': c.used,
                'due_date': c.due_date
            } for c in self.cards],
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
    
    # Cards operations (agora cartões são fixos)
    def get_cards(self) -> List[CreditCard]:
        return self.cards
    
    def add_card(self, name: str, limit: float, due_date: str) -> bool:
        card = CreditCard(name=name, limit=limit, due_date=due_date)
        self.cards.append(card)
        self.save_data()
        return True
    
    def update_card_usage(self, card_index: int, used: float, month_year: str) -> bool:
        """Atualiza limite usado E cria/atualiza despesa correspondente"""
        if 0 <= card_index < len(self.cards):
            card = self.cards[card_index]
            old_used = card.used
            card.used = used
            
            # Se o limite usado aumentou, cria/atualiza despesa
            if used > old_used and used > 0:
                self._sync_card_to_expenses(card, month_year)
            
            self.save_data()
            return True
        return False
    
    def _sync_card_to_expenses(self, card: CreditCard, month_year: str):
        """Sincroniza cartão com despesas mensais"""
        if month_year not in self.expenses:
            self.expenses[month_year] = []
        
        expense_description = f"Fatura {card.name}"
        
        # Verifica se já existe despesa para este cartão neste mês
        existing_expense_index = None
        for i, expense in enumerate(self.expenses[month_year]):
            if expense.description == expense_description:
                existing_expense_index = i
                break
        
        if existing_expense_index is not None:
            # Atualiza despesa existente
            self.expenses[month_year][existing_expense_index].amount = card.used
            self.expenses[month_year][existing_expense_index].due_date = card.due_date
        else:
            # Cria nova despesa
            expense = MonthlyExpense(
                description=expense_description,
                amount=card.used,
                due_date=card.due_date,
                paid=False
            )
            self.expenses[month_year].append(expense)
    
    def pay_card_invoice(self, card_index: int) -> bool:
        """Marca fatura como paga e registra saída na carteira"""
        if 0 <= card_index < len(self.cards):
            card = self.cards[card_index]
            
            if card.used > 0:
                # Registra saída na carteira
                transaction = Transaction(
                    date=datetime.now().strftime("%d/%m/%Y %H:%M"),
                    type="Saída",
                    amount=card.used,
                    description=f"Fatura {card.name}"
                )
                
                if transaction.amount > self.wallet.balance:
                    return False  # Saldo insuficiente
                
                self.wallet.add_transaction(transaction)
                
                # Reseta o limite usado do cartão
                card.used = 0.0
                
                # Remove a despesa correspondente da fatura
                self._remove_card_expense(card.name)
                
                self.save_data()
                return True
        return False
    
    def _remove_card_expense(self, card_name: str):
        """Remove despesa de fatura de cartão de todos os meses"""
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
            # Remove despesas associadas a este cartão
            card_name = self.cards[card_index].name
            self._remove_card_expense(card_name)
            
            # Remove o cartão
            del self.cards[card_index]
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
        
        # Verifica se já existe uma despesa com mesma descrição neste mês
        for expense in self.expenses[month_year]:
            if expense.description == description and not expense.description.startswith("Fatura "):
                messagebox.showwarning("Aviso", f"Já existe uma despesa com a descrição '{description}' neste mês!")
                return False
        
        expense = MonthlyExpense(description=description, amount=amount, due_date=due_date)
        self.expenses[month_year].append(expense)
        self.save_data()
        return True
    
    def toggle_expense_paid(self, month_year: str, expense_index: int) -> bool:
        """Alterna status da despesa E registra na carteira se for marcar como paga"""
        if month_year in self.expenses and 0 <= expense_index < len(self.expenses[month_year]):
            expense = self.expenses[month_year][expense_index]
            
            # Se está marcando como PAGA (antes estava não paga)
            if not expense.paid:
                # Verifica se é uma fatura de cartão
                is_card_invoice = expense.description.startswith("Fatura ")
                
                # Registra saída na carteira
                transaction = Transaction(
                    date=datetime.now().strftime("%d/%m/%Y %H:%M"),
                    type="Saída",
                    amount=expense.amount,
                    description=expense.description
                )
                
                if transaction.amount > self.wallet.balance and not is_card_invoice:
                    return False  # Saldo insuficiente (apenas para despesas normais)
                
                if not is_card_invoice:  # Só registra se não for fatura de cartão
                    self.wallet.add_transaction(transaction)
                
                # Se é fatura de cartão, encontra o cartão correspondente e reseta
                if is_card_invoice:
                    card_name = expense.description.replace("Fatura ", "")
                    for card in self.cards:
                        if card.name == card_name:
                            card.used = 0.0  # Reseta o limite usado
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