from dataclasses import dataclass
from datetime import datetime
from typing import List

@dataclass
class Bank:
    name: str
    balance: float = 0.0

@dataclass
class Transaction:
    date: str
    type: str
    amount: float
    description: str
    bank: str = "Geral"  # Novo campo para identificar o banco

@dataclass
class Wallet:
    balance: float = 0.0
    history: List[Transaction] = None
    banks: List[Bank] = None
    
    def __post_init__(self):
        if self.history is None:
            self.history = []
        if self.banks is None:
            self.banks = [Bank(name="Geral")]
    
    def add_transaction(self, transaction: Transaction):
        if transaction.type == "Entrada":
            self.balance += transaction.amount
            # Atualiza saldo do banco específico
            for bank in self.banks:
                if bank.name == transaction.bank:
                    bank.balance += transaction.amount
                    break
        else:
            self.balance -= transaction.amount
            # Deduz do banco geral ou específico
            if transaction.bank != "Geral":
                for bank in self.banks:
                    if bank.name == transaction.bank:
                        bank.balance -= transaction.amount
                        break
        self.history.append(transaction)
    
    def get_bank_balance(self, bank_name: str) -> float:
        for bank in self.banks:
            if bank.name == bank_name:
                return bank.balance
        return 0.0
    
    def add_bank(self, bank_name: str):
        if not any(bank.name == bank_name for bank in self.banks):
            self.banks.append(Bank(name=bank_name))
    
    def edit_transaction(self, transaction_index: int, new_amount: float, new_description: str, new_bank: str):
        """Edita uma transação existente"""
        if 0 <= transaction_index < len(self.history):
            old_transaction = self.history[transaction_index]
            
            # Reverte transação antiga
            if old_transaction.type == "Entrada":
                self.balance -= old_transaction.amount
                for bank in self.banks:
                    if bank.name == old_transaction.bank:
                        bank.balance -= old_transaction.amount
                        break
            else:
                self.balance += old_transaction.amount
            
            # Aplica nova transação
            new_transaction = Transaction(
                date=old_transaction.date,
                type=old_transaction.type,
                amount=new_amount,
                description=new_description,
                bank=new_bank
            )
            
            if new_transaction.type == "Entrada":
                self.balance += new_amount
                for bank in self.banks:
                    if bank.name == new_bank:
                        bank.balance += new_amount
                        break
            else:
                self.balance -= new_amount
            
            self.history[transaction_index] = new_transaction