import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime, timedelta
from backend.services.finance_service import FinanceService

class FinanceGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Gerenciador Financeiro - Backend Refatorado")
        self.root.geometry("800x600")
        
        # Injeção de dependência - Service do backend
        self.finance_service = FinanceService()
        
        self.setup_ui()
    
    def setup_ui(self):
        # Notebook (abas)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Criar abas
        self.create_wallet_tab()
        self.create_cards_tab()
        self.create_expenses_tab()
        
        # Atualizar dados iniciais
        self.update_displays()
    
    def create_wallet_tab(self):
        self.wallet_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.wallet_frame, text="Carteira")
        
        # Saldo atual
        ttk.Label(self.wallet_frame, text="Saldo Atual:", font=('Arial', 14, 'bold')).pack(pady=10)
        self.balance_label = ttk.Label(self.wallet_frame, text="R$ 0,00", font=('Arial', 18, 'bold'))
        self.balance_label.pack(pady=5)
        
        # Botões
        button_frame = ttk.Frame(self.wallet_frame)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Registrar Entrada", command=self.add_income).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Registrar Saída", command=self.add_expense).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Ver Histórico", command=self.show_history).pack(side='left', padx=5)
        
        # Histórico
        ttk.Label(self.wallet_frame, text="Últimas Transações:", font=('Arial', 12, 'bold')).pack(pady=(20, 5))
        
        columns = ('Data', 'Tipo', 'Valor', 'Descrição')
        self.history_tree = ttk.Treeview(self.wallet_frame, columns=columns, show='headings', height=10)
        
        for col in columns:
            self.history_tree.heading(col, text=col)
            self.history_tree.column(col, width=120)
        
        self.history_tree.pack(fill='both', expand=True, padx=10, pady=5)
    
    def create_cards_tab(self):
        self.cards_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.cards_frame, text="Cartões")
        
        # Controles de mês/ano
        month_frame = ttk.Frame(self.cards_frame)
        month_frame.pack(pady=10)
        
        ttk.Label(month_frame, text="Mês/Ano:").pack(side='left')
        self.cards_month_var = tk.StringVar(value=datetime.now().strftime("%Y-%m"))
        self.cards_month_combo = ttk.Combobox(month_frame, textvariable=self.cards_month_var, 
                                            values=self.get_month_year_list(), state="readonly")
        self.cards_month_combo.pack(side='left', padx=5)
        self.cards_month_combo.bind('<<ComboboxSelected>>', self.on_cards_month_changed)
        
        ttk.Button(month_frame, text="Adicionar Cartão", command=self.add_card).pack(side='left', padx=10)
        
        # Treeview para cartões
        columns = ('Cartão', 'Limite Total', 'Limite Usado', 'Disponível', 'Data Fatura', 'Ações')
        self.cards_tree = ttk.Treeview(self.cards_frame, columns=columns, show='headings', height=12)
        
        for col in columns:
            self.cards_tree.heading(col, text=col)
            self.cards_tree.column(col, width=100)
        
        self.cards_tree.pack(fill='both', expand=True, padx=10, pady=5)
        self.cards_tree.bind('<Double-1>', self.on_card_edit)
    
    def create_expenses_tab(self):
        self.expenses_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.expenses_frame, text="Despesas Mensais")
        
        # Controles de mês/ano
        month_frame = ttk.Frame(self.expenses_frame)
        month_frame.pack(pady=10)
        
        ttk.Label(month_frame, text="Mês/Ano:").pack(side='left')
        self.expenses_month_var = tk.StringVar(value=datetime.now().strftime("%Y-%m"))
        self.expenses_month_combo = ttk.Combobox(month_frame, textvariable=self.expenses_month_var,
                                               values=self.get_month_year_list(), state="readonly")
        self.expenses_month_combo.pack(side='left', padx=5)
        self.expenses_month_combo.bind('<<ComboboxSelected>>', self.on_expenses_month_changed)
        
        ttk.Button(month_frame, text="Adicionar Despesa", command=self.add_monthly_expense).pack(side='left', padx=10)
        
        # Treeview para despesas
        columns = ('Descrição', 'Valor', 'Vencimento', 'Paga', 'Ações')
        self.expenses_tree = ttk.Treeview(self.expenses_frame, columns=columns, show='headings', height=12)
        
        for col in columns:
            self.expenses_tree.heading(col, text=col)
            self.expenses_tree.column(col, width=120)
        
        self.expenses_tree.pack(fill='both', expand=True, padx=10, pady=5)
        self.expenses_tree.bind('<Double-1>', self.on_expense_edit)
    
    def get_month_year_list(self):
        """Retorna lista dos últimos 12 meses"""
        months = []
        current = datetime.now()
        for i in range(12):
            date = current - timedelta(days=30*i)
            months.append(date.strftime("%Y-%m"))
        return months
    
    def update_displays(self):
        self.update_wallet_display()
        self.update_cards_display()
        self.update_expenses_display()
    
    def update_wallet_display(self):
        balance = self.finance_service.get_balance()
        self.balance_label.config(text=f"R$ {balance:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
        
        # Atualizar histórico
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        history = self.finance_service.get_transaction_history()[-10:]
        for transaction in reversed(history):
            self.history_tree.insert('', 'end', values=(
                transaction.date,
                transaction.type,
                f"R$ {transaction.amount:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'),
                transaction.description
            ))
    
    def update_cards_display(self):
        for item in self.cards_tree.get_children():
            self.cards_tree.delete(item)
        
        month_year = self.cards_month_var.get()
        cards = self.finance_service.get_cards(month_year)
        
        for i, card in enumerate(cards):
            self.cards_tree.insert('', 'end', iid=i, values=(
                card.name,
                f"R$ {card.limit:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'),
                f"R$ {card.used:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'),
                f"R$ {card.available:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'),
                card.due_date,
                "Editar"
            ))
    
    def update_expenses_display(self):
        for item in self.expenses_tree.get_children():
            self.expenses_tree.delete(item)
        
        month_year = self.expenses_month_var.get()
        expenses = self.finance_service.get_expenses(month_year)
        
        for i, expense in enumerate(expenses):
            paid = "✓" if expense.paid else "✗"
            self.expenses_tree.insert('', 'end', iid=i, values=(
                expense.description,
                f"R$ {expense.amount:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'),
                expense.due_date,
                paid,
                "Editar"
            ))
    
    def add_income(self):
        amount = simpledialog.askfloat("Entrada de Dinheiro", "Valor:")
        if amount and amount > 0:
            description = simpledialog.askstring("Entrada de Dinheiro", "Descrição:")
            if description:
                success = self.finance_service.add_income(amount, description)
                if success:
                    self.update_wallet_display()
                    messagebox.showinfo("Sucesso", "Entrada registrada com sucesso!")
                else:
                    messagebox.showerror("Erro", "Erro ao registrar entrada!")
    
    def add_expense(self):
        amount = simpledialog.askfloat("Saída de Dinheiro", "Valor:")
        if amount and amount > 0:
            if amount > self.finance_service.get_balance():
                messagebox.showwarning("Atenção", "Saldo insuficiente!")
                return
            
            description = simpledialog.askstring("Saída de Dinheiro", "Descrição:")
            if description:
                success = self.finance_service.add_expense(amount, description)
                if success:
                    self.update_wallet_display()
                    messagebox.showinfo("Sucesso", "Saída registrada com sucesso!")
                else:
                    messagebox.showerror("Erro", "Erro ao registrar saída!")
    
    def show_history(self):
        history_window = tk.Toplevel(self.root)
        history_window.title("Histórico Completo")
        history_window.geometry("600x400")
        
        columns = ('Data', 'Tipo', 'Valor', 'Descrição')
        tree = ttk.Treeview(history_window, columns=columns, show='headings')
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120)
        
        tree.pack(fill='both', expand=True, padx=10, pady=10)
        
        history = self.finance_service.get_transaction_history()
        for transaction in reversed(history):
            tree.insert('', 'end', values=(
                transaction.date,
                transaction.type,
                f"R$ {transaction.amount:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'),
                transaction.description
            ))
    
    def add_card(self):
        name = simpledialog.askstring("Novo Cartão", "Nome do cartão:")
        if name:
            limit = simpledialog.askfloat("Novo Cartão", "Limite total:")
            if limit:
                due_date = simpledialog.askstring("Novo Cartão", "Data da fatura (dd/mm):")
                if due_date:
                    month_year = self.cards_month_var.get()
                    success = self.finance_service.add_card(month_year, name, limit, due_date)
                    if success:
                        self.update_cards_display()
                        messagebox.showinfo("Sucesso", "Cartão adicionado com sucesso!")
                    else:
                        messagebox.showerror("Erro", "Erro ao adicionar cartão!")
    
    def on_card_edit(self, event):
        item = self.cards_tree.selection()[0]
        month_year = self.cards_month_var.get()
        
        used = simpledialog.askfloat("Editar Cartão", "Limite utilizado:")
        if used is not None:
            success = self.finance_service.update_card_usage(month_year, int(item), used)
            if success:
                self.update_cards_display()
                messagebox.showinfo("Sucesso", "Cartão atualizado com sucesso!")
            else:
                messagebox.showerror("Erro", "Erro ao atualizar cartão!")
    
    def add_monthly_expense(self):
        description = simpledialog.askstring("Nova Despesa", "Descrição:")
        if description:
            amount = simpledialog.askfloat("Nova Despesa", "Valor:")
            if amount:
                due_date = simpledialog.askstring("Nova Despesa", "Data de vencimento (dd/mm):")
                if due_date:
                    month_year = self.expenses_month_var.get()
                    success = self.finance_service.add_expense_monthly(month_year, description, amount, due_date)
                    if success:
                        self.update_expenses_display()
                        messagebox.showinfo("Sucesso", "Despesa adicionada com sucesso!")
                    else:
                        messagebox.showerror("Erro", "Erro ao adicionar despesa!")
    
    def on_expense_edit(self, event):
        item = self.expenses_tree.selection()[0]
        month_year = self.expenses_month_var.get()
        
        success = self.finance_service.toggle_expense_paid(month_year, int(item))
        if success:
            self.update_expenses_display()
            messagebox.showinfo("Sucesso", "Despesa atualizada com sucesso!")
        else:
            messagebox.showerror("Erro", "Erro ao atualizar despesa!")
    
    def on_cards_month_changed(self, event):
        self.update_cards_display()
    
    def on_expenses_month_changed(self, event):
        self.update_expenses_display()