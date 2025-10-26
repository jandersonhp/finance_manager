import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime, timedelta
from backend.services.finance_service import FinanceService

class FinanceGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Gerenciador Financeiro - Sistema Completo")
        self.root.geometry("828x636")
        self.root.minsize(800, 600)
        
        self.root.lift()
        self.root.focus_force()
        
        self.finance_service = FinanceService()
        self.setup_ui()
    
    def setup_ui(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.create_wallet_tab()
        self.create_cards_tab()
        self.create_expenses_tab()
        
        self.update_displays()
    
    def create_wallet_tab(self):
        self.wallet_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.wallet_frame, text="Carteira")
        
        ttk.Label(self.wallet_frame, text="Saldo Total:", font=('Arial', 14, 'bold')).pack(pady=10)
        self.balance_label = ttk.Label(self.wallet_frame, text="R$ 0,00", font=('Arial', 18, 'bold'))
        self.balance_label.pack(pady=5)
        
        banks_frame = ttk.LabelFrame(self.wallet_frame, text="Saldos por Banco")
        banks_frame.pack(pady=10, padx=10, fill='x')
        
        self.banks_tree = ttk.Treeview(banks_frame, columns=('Banco', 'Saldo'), show='headings', height=4)
        self.banks_tree.heading('Banco', text='Banco')
        self.banks_tree.heading('Saldo', text='Saldo')
        self.banks_tree.column('Banco', width=150)
        self.banks_tree.column('Saldo', width=150)
        self.banks_tree.pack(pady=5, padx=5, fill='x')
        
        self.banks_context_menu = tk.Menu(self.root, tearoff=0)
        self.banks_context_menu.add_command(label="Editar Saldo", command=self.edit_bank_balance)
        self.banks_context_menu.add_command(label="Excluir Banco", command=self.delete_bank)
        
        self.banks_tree.bind("<Button-3>", self.show_banks_context_menu)
        
        button_frame = ttk.Frame(self.wallet_frame)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Registrar Entrada", command=self.add_income).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Registrar Saída", command=self.add_expense).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Ver Histórico", command=self.show_history).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Zerar Carteira", command=self.reset_wallet).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Adicionar Banco", command=self.add_bank).pack(side='left', padx=5)
        
        ttk.Label(self.wallet_frame, text="Últimas Transações:", font=('Arial', 12, 'bold')).pack(pady=(20, 5))
        
        columns = ('Data', 'Tipo', 'Valor', 'Descrição', 'Banco')
        self.history_tree = ttk.Treeview(self.wallet_frame, columns=columns, show='headings', height=8)
        
        for col in columns:
            self.history_tree.heading(col, text=col)
            self.history_tree.column(col, width=90)
        
        self.history_tree.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.history_context_menu = tk.Menu(self.root, tearoff=0)
        self.history_context_menu.add_command(label="Editar Transação", command=self.edit_transaction)
        self.history_context_menu.add_command(label="Excluir Transação", command=self.delete_transaction)
        
        self.history_tree.bind("<Button-3>", self.show_history_context_menu)
    
    def create_cards_tab(self):
        self.cards_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.cards_frame, text="Cartões")
        
        columns = ('Cartão', 'Limite Total', 'Limite Usado', 'Disponível Calculado', 'Disponível Ajustado', 'Data Fatura')
        self.cards_tree = ttk.Treeview(self.cards_frame, columns=columns, show='headings', height=10)
        
        column_widths = [120, 100, 100, 120, 120, 100]
        for i, col in enumerate(columns):
            self.cards_tree.heading(col, text=col)
            self.cards_tree.column(col, width=column_widths[i])
        
        self.cards_tree.pack(fill='both', expand=True, padx=10, pady=5)
        
        button_frame = ttk.Frame(self.cards_frame)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Adicionar Cartão", command=self.add_card).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Pagar Fatura", command=self.pay_card_invoice).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Adicionar Parcela", command=self.add_installment).pack(side='left', padx=5)
        
        self.cards_context_menu = tk.Menu(self.root, tearoff=0)
        self.cards_context_menu.add_command(label="Editar Limite Usado", command=self.edit_card_used)
        self.cards_context_menu.add_command(label="Editar Limite Total", command=self.edit_card_limit)
        self.cards_context_menu.add_command(label="Ajustar Disponível", command=self.edit_card_available)
        self.cards_context_menu.add_command(label="Editar Data da Fatura", command=self.edit_card_due_date)
        self.cards_context_menu.add_separator()
        self.cards_context_menu.add_command(label="Excluir Cartão", command=self.delete_card)
        
        self.cards_tree.bind("<Button-3>", self.show_cards_context_menu)
    
    def create_expenses_tab(self):
        self.expenses_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.expenses_frame, text="Despesas Mensais")
        
        month_frame = ttk.Frame(self.expenses_frame)
        month_frame.pack(pady=10)
        
        ttk.Label(month_frame, text="Mês/Ano:").pack(side='left')
        
        selector_frame = ttk.Frame(month_frame)
        selector_frame.pack(side='left', padx=5)
        
        self.year_var = tk.StringVar(value=str(datetime.now().year))
        year_combo = ttk.Combobox(selector_frame, textvariable=self.year_var, width=6, state="readonly")
        year_combo['values'] = [str(year) for year in range(2020, 2031)]
        year_combo.pack(side='left')
        year_combo.bind('<<ComboboxSelected>>', self.on_month_year_changed)
        
        ttk.Label(selector_frame, text="/").pack(side='left')
        
        self.month_var = tk.StringVar(value=f"{datetime.now().month:02d}")
        month_combo = ttk.Combobox(selector_frame, textvariable=self.month_var, width=3, state="readonly")
        month_combo['values'] = [f"{i:02d}" for i in range(1, 13)]
        month_combo.pack(side='left')
        month_combo.bind('<<ComboboxSelected>>', self.on_month_year_changed)
        
        totals_frame = ttk.Frame(month_frame)
        totals_frame.pack(side='left', padx=20)
        
        self.pagar_label = ttk.Label(totals_frame, text="À Pagar: R$ 0,00", font=('Arial', 9, 'bold'), foreground='red')
        self.pagar_label.pack()
        
        self.pago_label = ttk.Label(totals_frame, text="Pago: R$ 0,00", font=('Arial', 9, 'bold'), foreground='green')
        self.pago_label.pack()
        
        self.total_label = ttk.Label(totals_frame, text="Total: R$ 0,00", font=('Arial', 10, 'bold'))
        self.total_label.pack()
        
        ttk.Button(month_frame, text="Adicionar Despesa", command=self.add_monthly_expense).pack(side='left', padx=10)
        
        columns = ('Descrição', 'Valor', 'Vencimento', 'Paga', 'Recorrente')
        self.expenses_tree = ttk.Treeview(self.expenses_frame, columns=columns, show='headings', height=10)
        
        column_widths = [150, 80, 80, 50, 70]
        for i, col in enumerate(columns):
            self.expenses_tree.heading(col, text=col)
            self.expenses_tree.column(col, width=column_widths[i])
        
        self.expenses_tree.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.expenses_context_menu = tk.Menu(self.root, tearoff=0)
        self.expenses_context_menu.add_command(label="Marcar como Paga", command=self.toggle_expense_paid)
        self.expenses_context_menu.add_command(label="Marcar como Não Paga", command=self.toggle_expense_paid)
        self.expenses_context_menu.add_separator()
        self.expenses_context_menu.add_command(label="Editar Valor", command=self.edit_expense_amount)
        self.expenses_context_menu.add_command(label="Editar Data de Vencimento", command=self.edit_expense_due_date)
        self.expenses_context_menu.add_command(label="Editar Descrição", command=self.edit_expense_description)
        self.expenses_context_menu.add_separator()
        self.expenses_context_menu.add_command(label="Excluir Despesa", command=self.delete_expense)
        
        self.expenses_tree.bind("<Button-3>", self.show_expenses_context_menu)
    
    def get_current_month_year(self):
        return f"{self.year_var.get()}-{self.month_var.get()}"
    
    def on_month_year_changed(self, event=None):
        self.update_expenses_display()
    
    def update_displays(self):
        self.update_wallet_display()
        self.update_cards_display()
        self.update_expenses_display()
    
    def update_wallet_display(self):
        balance = self.finance_service.get_balance()
        self.balance_label.config(text=f"R$ {balance:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
        
        for item in self.banks_tree.get_children():
            self.banks_tree.delete(item)
        
        banks = self.finance_service.get_banks()
        for bank in banks:
            self.banks_tree.insert('', 'end', values=(
                bank.name,
                f"R$ {bank.balance:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
            ))
        
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        history = self.finance_service.get_transaction_history()[-8:]
        for transaction in reversed(history):
            self.history_tree.insert('', 'end', values=(
                transaction.date,
                transaction.type,
                f"R$ {transaction.amount:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'),
                transaction.description,
                transaction.bank
            ))
    
    def update_cards_display(self):
        for item in self.cards_tree.get_children():
            self.cards_tree.delete(item)
        
        cards = self.finance_service.get_cards()
        
        for i, card in enumerate(cards):
            self.cards_tree.insert('', 'end', iid=i, values=(
                card.name,
                f"R$ {card.limit:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'),
                f"R$ {card.used:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'),
                f"R$ {card.calculated_available:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'),
                f"R$ {card.available:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'),
                card.due_date
            ))
    
    def update_expenses_display(self):
        for item in self.expenses_tree.get_children():
            self.expenses_tree.delete(item)
        
        month_year = self.get_current_month_year()
        expenses = self.finance_service.get_expenses(month_year)
        
        total_pagar = sum(expense.amount for expense in expenses if not expense.paid)
        total_pago = sum(expense.amount for expense in expenses if expense.paid)
        total_geral = total_pagar + total_pago
        
        self.pagar_label.config(text=f"À Pagar: R$ {total_pagar:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
        self.pago_label.config(text=f"Pago: R$ {total_pago:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
        self.total_label.config(text=f"Total: R$ {total_geral:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
        
        for i, expense in enumerate(expenses):
            paid = "✓" if expense.paid else "✗"
            recurring = "✓" if expense.recurring else "✗"
            self.expenses_tree.insert('', 'end', iid=i, values=(
                expense.description,
                f"R$ {expense.amount:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'),
                expense.due_date,
                paid,
                recurring
            ))

    def show_banks_context_menu(self, event):
        item = self.banks_tree.identify_row(event.y)
        if item:
            self.banks_tree.selection_set(item)
            self.selected_bank_item = item
            self.banks_context_menu.post(event.x_root, event.y_root)
    
    def edit_bank_balance(self):
        if hasattr(self, 'selected_bank_item'):
            bank_name = self.banks_tree.item(self.selected_bank_item)['values'][0]
            current_balance = self.finance_service.get_bank_balance(bank_name)
            
            new_balance = simpledialog.askfloat(
                "Editar Saldo do Banco", 
                f"Novo saldo para {bank_name}:", 
                initialvalue=current_balance
            )
            
            if new_balance is not None:
                banks = self.finance_service.get_banks()
                for bank in banks:
                    if bank.name == bank_name:
                        bank.balance = new_balance
                        break
                
                total_balance = sum(bank.balance for bank in banks)
                self.finance_service.wallet.balance = total_balance
                self.finance_service.save_data()
                self.update_wallet_display()
                messagebox.showinfo("Sucesso", f"Saldo do {bank_name} atualizado!")
    
    def delete_bank(self):
        if hasattr(self, 'selected_bank_item'):
            bank_name = self.banks_tree.item(self.selected_bank_item)['values'][0]
            
            if bank_name == "Geral":
                messagebox.showwarning("Aviso", "Não é possível excluir o banco 'Geral'!")
                return
            
            confirm = messagebox.askyesno(
                "Confirmar Exclusão", 
                f"Tem certeza que deseja excluir o banco {bank_name}?\n\n"
                f"Todas as transações associadas a este banco serão movidas para 'Geral'."
            )
            
            if confirm:
                for transaction in self.finance_service.wallet.history:
                    if transaction.bank == bank_name:
                        transaction.bank = "Geral"
                
                self.finance_service.wallet.banks = [
                    bank for bank in self.finance_service.wallet.banks 
                    if bank.name != bank_name
                ]
                
                self.finance_service.save_data()
                self.update_wallet_display()
                messagebox.showinfo("Sucesso", f"Banco {bank_name} excluído!")

    def add_income(self):
        amount = self.ask_float_front("Entrada de Dinheiro", "Valor:")
        if amount and amount > 0:
            description = self.ask_string_front("Entrada de Dinheiro", "Descrição:")
            if description:
                banks = [b.name for b in self.finance_service.get_banks()]
                bank_window = tk.Toplevel(self.root)
                bank_window.title("Selecionar Banco")
                bank_window.geometry("300x150")
                bank_window.transient(self.root)
                bank_window.grab_set()
                
                ttk.Label(bank_window, text="Banco:").pack(pady=10)
                bank_var = tk.StringVar(value=banks[0] if banks else "Geral")
                bank_combo = ttk.Combobox(bank_window, textvariable=bank_var, values=banks, state="readonly")
                bank_combo.pack(pady=5)
                
                def confirm_bank():
                    bank = bank_var.get()
                    bank_window.destroy()
                    success = self.finance_service.add_income(amount, description, bank)
                    if success:
                        self.update_wallet_display()
                        messagebox.showinfo("Sucesso", "Entrada registrada com sucesso!")
                
                ttk.Button(bank_window, text="Confirmar", command=confirm_bank).pack(pady=10)
    
    def add_expense(self):
        amount = self.ask_float_front("Saída de Dinheiro", "Valor:")
        if amount and amount > 0:
            if amount > self.finance_service.get_balance():
                messagebox.showwarning("Atenção", "Saldo insuficiente!")
                return
            
            description = self.ask_string_front("Saída de Dinheiro", "Descrição:")
            if description:
                success = self.finance_service.add_expense(amount, description)
                if success:
                    self.update_wallet_display()
                    messagebox.showinfo("Sucesso", "Saída registrada com sucesso!")

    def ask_float_front(self, title, prompt):
        window = tk.Toplevel(self.root)
        window.title(title)
        window.geometry("300x120")
        window.transient(self.root)
        window.grab_set()
        
        result = [None]
        
        ttk.Label(window, text=prompt).pack(pady=10)
        entry_var = tk.StringVar()
        entry = ttk.Entry(window, textvariable=entry_var)
        entry.pack(pady=5)
        entry.focus()
        
        def confirm():
            try:
                result[0] = float(entry_var.get())
                window.destroy()
            except ValueError:
                messagebox.showerror("Erro", "Valor inválido!")
        
        def cancel():
            window.destroy()
        
        ttk.Button(window, text="OK", command=confirm).pack(side='left', padx=10, pady=10)
        ttk.Button(window, text="Cancelar", command=cancel).pack(side='right', padx=10, pady=10)
        
        entry.bind('<Return>', lambda e: confirm())
        
        window.wait_window()
        return result[0]
    
    def ask_string_front(self, title, prompt):
        window = tk.Toplevel(self.root)
        window.title(title)
        window.geometry("300x120")
        window.transient(self.root)
        window.grab_set()
        
        result = [None]
        
        ttk.Label(window, text=prompt).pack(pady=10)
        entry_var = tk.StringVar()
        entry = ttk.Entry(window, textvariable=entry_var)
        entry.pack(pady=5)
        entry.focus()
        
        def confirm():
            result[0] = entry_var.get()
            window.destroy()
        
        def cancel():
            window.destroy()
        
        ttk.Button(window, text="OK", command=confirm).pack(side='left', padx=10, pady=10)
        ttk.Button(window, text="Cancelar", command=cancel).pack(side='right', padx=10, pady=10)
        
        entry.bind('<Return>', lambda e: confirm())
        
        window.wait_window()
        return result[0]

    def show_history(self):
        history_window = tk.Toplevel(self.root)
        history_window.title("Histórico Completo")
        history_window.geometry("700x400")
        history_window.transient(self.root)
        
        columns = ('Data', 'Tipo', 'Valor', 'Descrição', 'Banco')
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
                transaction.description,
                transaction.bank
            ))
    
    def reset_wallet(self):
        confirm = messagebox.askyesno(
            "Zerar Carteira", 
            "Tem certeza que deseja ZERAR TODOS os dados da carteira?\n\n"
            "Isso irá:\n• Zerar saldo atual\n• Apagar todo histórico\n• Manter cartões e despesas\n\n"
            "Esta ação NÃO PODE ser desfeita!"
        )
        
        if confirm:
            success = self.finance_service.reset_wallet()
            if success:
                self.update_wallet_display()
                messagebox.showinfo("Sucesso", "Carteira zerada com sucesso!")
    
    def add_bank(self):
        bank_name = self.ask_string_front("Novo Banco", "Nome do banco:")
        if bank_name:
            success = self.finance_service.add_bank(bank_name)
            if success:
                self.update_wallet_display()
                messagebox.showinfo("Sucesso", "Banco adicionado com sucesso!")
    
    def show_history_context_menu(self, event):
        item = self.history_tree.identify_row(event.y)
        if item:
            self.history_tree.selection_set(item)
            self.selected_history_item = item
            self.history_context_menu.post(event.x_root, event.y_root)
    
    def edit_transaction(self):
        if hasattr(self, 'selected_history_item'):
            selected_iid = self.selected_history_item
            all_items = self.history_tree.get_children()
            
            try:
                transaction_index = all_items.index(selected_iid)
                history = self.finance_service.get_transaction_history()
                actual_index = len(history) - 1 - transaction_index
                
                if 0 <= actual_index < len(history):
                    transaction = history[actual_index]
                    
                    edit_window = tk.Toplevel(self.root)
                    edit_window.title("Editar Transação")
                    edit_window.geometry("400x300")
                    edit_window.transient(self.root)
                    edit_window.grab_set()
                    
                    ttk.Label(edit_window, text="Valor:").pack(pady=5)
                    amount_var = tk.StringVar(value=str(transaction.amount))
                    amount_entry = ttk.Entry(edit_window, textvariable=amount_var)
                    amount_entry.pack(pady=5)
                    amount_entry.focus()
                    
                    ttk.Label(edit_window, text="Descrição:").pack(pady=5)
                    desc_var = tk.StringVar(value=transaction.description)
                    desc_entry = ttk.Entry(edit_window, textvariable=desc_var)
                    desc_entry.pack(pady=5)
                    
                    ttk.Label(edit_window, text="Banco:").pack(pady=5)
                    banks = [b.name for b in self.finance_service.get_banks()]
                    bank_var = tk.StringVar(value=transaction.bank)
                    bank_combo = ttk.Combobox(edit_window, textvariable=bank_var, values=banks, state="readonly")
                    bank_combo.pack(pady=5)
                    
                    def save_edits():
                        try:
                            new_amount = float(amount_var.get())
                            new_description = desc_var.get()
                            new_bank = bank_var.get()
                            
                            if new_amount <= 0:
                                messagebox.showerror("Erro", "Valor deve ser positivo!")
                                return
                            
                            success = self.finance_service.edit_transaction(
                                actual_index, new_amount, new_description, new_bank
                            )
                            
                            if success:
                                self.update_wallet_display()
                                edit_window.destroy()
                                messagebox.showinfo("Sucesso", "Transação editada com sucesso!")
                        except ValueError:
                            messagebox.showerror("Erro", "Valor inválido!")
                    
                    ttk.Button(edit_window, text="Salvar", command=save_edits).pack(pady=10)
                    amount_entry.bind('<Return>', lambda e: save_edits())
                    
            except ValueError:
                messagebox.showerror("Erro", "Erro ao encontrar transação!")

    def delete_transaction(self):
        if hasattr(self, 'selected_history_item'):
            selected_iid = self.selected_history_item
            all_items = self.history_tree.get_children()
            
            try:
                transaction_index = all_items.index(selected_iid)
                history = self.finance_service.get_transaction_history()
                actual_index = len(history) - 1 - transaction_index
                
                if 0 <= actual_index < len(history):
                    transaction = history[actual_index]
                    
                    confirm = messagebox.askyesno(
                        "Confirmar Exclusão", 
                        f"Excluir transação de {transaction.date} - {transaction.description}?"
                    )
                    
                    if confirm:
                        del self.finance_service.wallet.history[actual_index]
                        
                        self.finance_service.wallet.balance = 0.0
                        for bank in self.finance_service.wallet.banks:
                            bank.balance = 0.0
                        
                        for trans in self.finance_service.wallet.history:
                            if trans.type == "Entrada":
                                self.finance_service.wallet.balance += trans.amount
                                for bank in self.finance_service.wallet.banks:
                                    if bank.name == trans.bank:
                                        bank.balance += trans.amount
                                        break
                            else:
                                self.finance_service.wallet.balance -= trans.amount
                                if trans.bank != "Geral":
                                    for bank in self.finance_service.wallet.banks:
                                        if bank.name == trans.bank:
                                            bank.balance -= trans.amount
                                            break
                        
                        self.finance_service.save_data()
                        self.update_wallet_display()
                        messagebox.showinfo("Sucesso", "Transação excluída!")
                        
            except ValueError:
                messagebox.showerror("Erro", "Erro ao encontrar transação!")

    def add_card(self):
        name = self.ask_string_front("Novo Cartão", "Nome do cartão:")
        if name:
            limit = self.ask_float_front("Novo Cartão", "Limite total:")
            if limit:
                due_date_window = tk.Toplevel(self.root)
                due_date_window.title("Selecionar Dia da Fatura")
                due_date_window.geometry("300x150")
                due_date_window.transient(self.root)
                due_date_window.grab_set()
                
                ttk.Label(due_date_window, text="Dia da fatura:").pack(pady=10)
                
                day_frame = ttk.Frame(due_date_window)
                day_frame.pack(pady=5)
                
                day_var = tk.StringVar(value="10")
                day_combo = ttk.Combobox(day_frame, textvariable=day_var, width=5, state="readonly")
                day_combo['values'] = [f"{i:02d}" for i in range(1, 32)]
                day_combo.pack(side='left', padx=5)
                
                ttk.Label(day_frame, text="/mm").pack(side='left')
                
                def confirm_due_date():
                    due_date = f"{day_var.get()}/mm"
                    due_date_window.destroy()
                    success = self.finance_service.add_card(name, limit, due_date)
                    if success:
                        self.update_cards_display()
                        messagebox.showinfo("Sucesso", "Cartão adicionado com sucesso!")
                
                ttk.Button(due_date_window, text="Confirmar", command=confirm_due_date).pack(pady=10)
    
    def pay_card_invoice(self):
        selection = self.cards_tree.selection()
        if selection:
            card_index = int(selection[0])
            card = self.finance_service.get_cards()[card_index]
            
            if card.used == 0:
                messagebox.showinfo("Info", "Não há fatura para pagar!")
                return
            
            confirm = messagebox.askyesno(
                "Confirmar Pagamento", 
                f"Pagar fatura de R$ {card.used:,.2f} do cartão {card.name}?"
            )
            
            if confirm:
                success = self.finance_service.pay_card_invoice(card_index)
                if success:
                    self.update_cards_display()
                    self.update_wallet_display()
                    self.update_expenses_display()
                    messagebox.showinfo("Sucesso", "Fatura paga com sucesso!")
                else:
                    messagebox.showerror("Erro", "Saldo insuficiente para pagar a fatura!")
    
    def add_installment(self):
        cards = self.finance_service.get_cards()
        if not cards:
            messagebox.showwarning("Aviso", "Adicione um cartão primeiro!")
            return
        
        card_names = [card.name for card in cards]
        
        installment_window = tk.Toplevel(self.root)
        installment_window.title("Nova Compra Parcelada")
        installment_window.geometry("400x350")
        installment_window.transient(self.root)
        installment_window.grab_set()
        
        ttk.Label(installment_window, text="Cartão:").pack(pady=5)
        card_var = tk.StringVar(value=card_names[0])
        card_combo = ttk.Combobox(installment_window, textvariable=card_var, values=card_names, state="readonly")
        card_combo.pack(pady=5)
        
        ttk.Label(installment_window, text="Descrição:").pack(pady=5)
        desc_var = tk.StringVar()
        desc_entry = ttk.Entry(installment_window, textvariable=desc_var)
        desc_entry.pack(pady=5)
        desc_entry.focus()
        
        ttk.Label(installment_window, text="Valor Total:").pack(pady=5)
        amount_var = tk.StringVar()
        amount_entry = ttk.Entry(installment_window, textvariable=amount_var)
        amount_entry.pack(pady=5)
        
        ttk.Label(installment_window, text="Número de Parcelas:").pack(pady=5)
        installments_var = tk.StringVar(value="1")
        installments_combo = ttk.Combobox(installment_window, textvariable=installments_var, 
                                         values=[str(i) for i in range(1, 13)], state="readonly")
        installments_combo.pack(pady=5)
        
        def confirm_installment():
            try:
                description = desc_var.get()
                total_amount = float(amount_var.get())
                installments = int(installments_var.get())
                card_name = card_var.get()
                
                if not description:
                    messagebox.showerror("Erro", "Descrição é obrigatória!")
                    return
                
                if total_amount <= 0:
                    messagebox.showerror("Erro", "Valor deve ser positivo!")
                    return
                
                success = self.finance_service.add_installment(
                    description, total_amount, installments, card_name
                )
                
                if success:
                    self.update_cards_display()
                    self.update_expenses_display()
                    installment_window.destroy()
                    messagebox.showinfo("Sucesso", f"Compra parcelada em {installments}x adicionada!")
            except ValueError:
                messagebox.showerror("Erro", "Valores inválidos!")
        
        ttk.Button(installment_window, text="Adicionar", command=confirm_installment).pack(pady=20)
        desc_entry.bind('<Return>', lambda e: confirm_installment())
    
    def show_cards_context_menu(self, event):
        item = self.cards_tree.identify_row(event.y)
        if item:
            self.cards_tree.selection_set(item)
            self.selected_card_item = item
            self.cards_context_menu.post(event.x_root, event.y_root)
    
    def edit_card_used(self):
        if hasattr(self, 'selected_card_item'):
            card_index = int(self.selected_card_item)
            cards = self.finance_service.get_cards()
            
            if 0 <= card_index < len(cards):
                card = cards[card_index]
                new_used = self.ask_float_front(
                    "Editar Limite Usado", 
                    f"Limite usado para {card.name}:"
                )
                if new_used is not None and new_used >= 0:
                    month_year = self.get_current_month_year()
                    success = self.finance_service.update_card_usage(card_index, new_used, month_year)
                    if success:
                        self.update_cards_display()
                        self.update_expenses_display()
                        messagebox.showinfo("Sucesso", "Limite usado atualizado!")
    
    def edit_card_limit(self):
        if hasattr(self, 'selected_card_item'):
            card_index = int(self.selected_card_item)
            cards = self.finance_service.get_cards()
            
            if 0 <= card_index < len(cards):
                card = cards[card_index]
                new_limit = self.ask_float_front(
                    "Editar Limite Total", 
                    f"Limite total para {card.name}:"
                )
                if new_limit is not None and new_limit > 0:
                    success = self.finance_service.update_card_limit(card_index, new_limit)
                    if success:
                        self.update_cards_display()
                        messagebox.showinfo("Sucesso", "Limite total atualizado!")
    
    def edit_card_available(self):
        if hasattr(self, 'selected_card_item'):
            card_index = int(self.selected_card_item)
            cards = self.finance_service.get_cards()
            
            if 0 <= card_index < len(cards):
                card = cards[card_index]
                new_available = self.ask_float_front(
                    "Ajustar Limite Disponível", 
                    f"Limite disponível ajustado para {card.name}:\n\n"
                    f"Limite Total: R$ {card.limit:,.2f}\n"
                    f"Limite Usado: R$ {card.used:,.2f}\n"
                    f"Disponível Calculado: R$ {card.calculated_available:,.2f}"
                )
                if new_available is not None and new_available >= 0:
                    success = self.finance_service.update_card_available(card_index, new_available)
                    if success:
                        self.update_cards_display()
                        messagebox.showinfo("Sucesso", "Limite disponível ajustado!")
    
    def edit_card_due_date(self):
        if hasattr(self, 'selected_card_item'):
            card_index = int(self.selected_card_item)
            cards = self.finance_service.get_cards()
            
            if 0 <= card_index < len(cards):
                card = cards[card_index]
                current_day = card.due_date.split('/')[0] if '/' in card.due_date else "10"
                
                due_date_window = tk.Toplevel(self.root)
                due_date_window.title("Editar Dia da Fatura")
                due_date_window.geometry("300x150")
                due_date_window.transient(self.root)
                due_date_window.grab_set()
                
                ttk.Label(due_date_window, text="Novo dia da fatura:").pack(pady=10)
                
                day_frame = ttk.Frame(due_date_window)
                day_frame.pack(pady=5)
                
                day_var = tk.StringVar(value=current_day)
                day_combo = ttk.Combobox(day_frame, textvariable=day_var, width=5, state="readonly")
                day_combo['values'] = [f"{i:02d}" for i in range(1, 32)]
                day_combo.pack(side='left', padx=5)
                
                ttk.Label(day_frame, text="/mm").pack(side='left')
                
                def confirm_new_due_date():
                    new_due_date = f"{day_var.get()}/mm"
                    due_date_window.destroy()
                    success = self.finance_service.update_card_due_date(card_index, new_due_date)
                    if success:
                        self.update_cards_display()
                        messagebox.showinfo("Sucesso", "Data da fatura atualizada!")
                
                ttk.Button(due_date_window, text="Confirmar", command=confirm_new_due_date).pack(pady=10)
    
    def delete_card(self):
        if hasattr(self, 'selected_card_item'):
            card_index = int(self.selected_card_item)
            cards = self.finance_service.get_cards()
            
            if 0 <= card_index < len(cards):
                card = cards[card_index]
                confirm = messagebox.askyesno(
                    "Confirmar Exclusão", 
                    f"Tem certeza que deseja excluir o cartão {card.name}?"
                )
                if confirm:
                    success = self.finance_service.delete_card(card_index)
                    if success:
                        self.update_cards_display()
                        messagebox.showinfo("Sucesso", "Cartão excluído!")

    def add_monthly_expense(self):
        description = self.ask_string_front("Nova Despesa", "Descrição:")
        if description:
            amount = self.ask_float_front("Nova Despesa", "Valor:")
            if amount:
                expense_window = tk.Toplevel(self.root)
                expense_window.title("Configurar Despesa")
                expense_window.geometry("400x300")
                expense_window.transient(self.root)
                expense_window.grab_set()
                
                ttk.Label(expense_window, text="Dia do vencimento:").pack(pady=5)
                
                day_frame = ttk.Frame(expense_window)
                day_frame.pack(pady=5)
                
                day_var = tk.StringVar(value="10")
                day_combo = ttk.Combobox(day_frame, textvariable=day_var, width=5, state="readonly")
                day_combo['values'] = [f"{i:02d}" for i in range(1, 32)]
                day_combo.pack(side='left', padx=5)
                
                ttk.Label(day_frame, text="/mm").pack(side='left')
                
                recurring_var = tk.BooleanVar(value=False)
                recurring_check = ttk.Checkbutton(expense_window, text="Despesa Recorrente", 
                                                variable=recurring_var)
                recurring_check.pack(pady=10)
                
                end_frame = ttk.Frame(expense_window)
                end_frame.pack(pady=5)
                
                ttk.Label(end_frame, text="Até:").pack(side='left')
                end_year_var = tk.StringVar(value=str(datetime.now().year + 1))
                end_year_combo = ttk.Combobox(end_frame, textvariable=end_year_var, width=6, state="readonly")
                end_year_combo['values'] = [str(year) for year in range(2020, 2031)]
                end_year_combo.pack(side='left', padx=5)
                
                ttk.Label(end_frame, text="/").pack(side='left')
                
                end_month_var = tk.StringVar(value="12")
                end_month_combo = ttk.Combobox(end_frame, textvariable=end_month_var, width=3, state="readonly")
                end_month_combo['values'] = [f"{i:02d}" for i in range(1, 13)]
                end_month_combo.pack(side='left')
                
                def confirm_expense():
                    due_date = f"{day_var.get()}/mm"
                    recurring = recurring_var.get()
                    end_date = f"{end_year_var.get()}-{end_month_var.get()}" if recurring else None
                    
                    expense_window.destroy()
                    month_year = self.get_current_month_year()
                    success = self.finance_service.add_expense_monthly(
                        month_year, description, amount, due_date, recurring, end_date
                    )
                    if success:
                        self.update_expenses_display()
                        messagebox.showinfo("Sucesso", "Despesa adicionada com sucesso!")
                
                ttk.Button(expense_window, text="Adicionar", command=confirm_expense).pack(pady=20)
    
    def show_expenses_context_menu(self, event):
        item = self.expenses_tree.identify_row(event.y)
        if item:
            self.expenses_tree.selection_set(item)
            self.selected_expense_item = item
            self.update_expenses_context_menu()
            self.expenses_context_menu.post(event.x_root, event.y_root)
    
    def update_expenses_context_menu(self):
        if hasattr(self, 'selected_expense_item'):
            month_year = self.get_current_month_year()
            expenses = self.finance_service.get_expenses(month_year)
            item_index = int(self.selected_expense_item)
            
            if 0 <= item_index < len(expenses):
                expense = expenses[item_index]
                
                if expense.paid:
                    self.expenses_context_menu.entryconfig(0, label="Marcar como Não Paga")
                    self.expenses_context_menu.entryconfig(1, label="Marcar como Paga")
                else:
                    self.expenses_context_menu.entryconfig(0, label="Marcar como Paga")
                    self.expenses_context_menu.entryconfig(1, label="Marcar como Não Paga")
    
    def toggle_expense_paid(self):
        if hasattr(self, 'selected_expense_item'):
            month_year = self.get_current_month_year()
            item_index = int(self.selected_expense_item)
            expenses = self.finance_service.get_expenses(month_year)
            
            if 0 <= item_index < len(expenses):
                expense = expenses[item_index]
                
                if not expense.paid:
                    banks = [b.name for b in self.finance_service.get_banks()]
                    bank_window = tk.Toplevel(self.root)
                    bank_window.title("Selecionar Banco para Pagamento")
                    bank_window.geometry("300x150")
                    bank_window.transient(self.root)
                    bank_window.grab_set()
                    
                    ttk.Label(bank_window, text=f"Pagando: {expense.description}").pack(pady=5)
                    ttk.Label(bank_window, text=f"Valor: R$ {expense.amount:,.2f}").pack(pady=5)
                    ttk.Label(bank_window, text="Banco:").pack(pady=5)
                    
                    bank_var = tk.StringVar(value=banks[0] if banks else "Geral")
                    bank_combo = ttk.Combobox(bank_window, textvariable=bank_var, values=banks, state="readonly")
                    bank_combo.pack(pady=5)
                    
                    def confirm_payment():
                        bank = bank_var.get()
                        bank_window.destroy()
                        
                        from backend.models.wallet import Transaction
                        
                        transaction = Transaction(
                            date=datetime.now().strftime("%d/%m/%Y %H:%M"),
                            type="Saída",
                            amount=expense.amount,
                            description=expense.description,
                            bank=bank
                        )
                        
                        bank_balance = self.finance_service.get_bank_balance(bank)
                        if expense.amount > bank_balance:
                            messagebox.showerror("Erro", f"Saldo insuficiente no {bank}!")
                            return
                        
                        self.finance_service.wallet.add_transaction(transaction)
                        expense.paid = True
                        self.finance_service.save_data()
                        
                        self.update_expenses_display()
                        self.update_wallet_display()
                        messagebox.showinfo("Sucesso", "Despesa paga com sucesso!")
                    
                    ttk.Button(bank_window, text="Confirmar Pagamento", command=confirm_payment).pack(pady=10)
                else:
                    expense.paid = False
                    self.finance_service.save_data()
                    self.update_expenses_display()
                    messagebox.showinfo("Sucesso", "Despesa marcada como não paga!")
    
    def edit_expense_amount(self):
        if hasattr(self, 'selected_expense_item'):
            month_year = self.get_current_month_year()
            expenses = self.finance_service.get_expenses(month_year)
            item_index = int(self.selected_expense_item)
            
            if 0 <= item_index < len(expenses):
                expense = expenses[item_index]
                new_amount = self.ask_float_front(
                    "Editar Valor", 
                    f"Novo valor para {expense.description}:"
                )
                if new_amount is not None and new_amount > 0:
                    success = self.finance_service.update_expense_amount(month_year, item_index, new_amount)
                    if success:
                        self.update_expenses_display()
                        messagebox.showinfo("Sucesso", "Valor da despesa atualizado!")
    
    def edit_expense_due_date(self):
        if hasattr(self, 'selected_expense_item'):
            month_year = self.get_current_month_year()
            expenses = self.finance_service.get_expenses(month_year)
            item_index = int(self.selected_expense_item)
            
            if 0 <= item_index < len(expenses):
                expense = expenses[item_index]
                current_day = expense.due_date.split('/')[0] if '/' in expense.due_date else "10"
                
                due_date_window = tk.Toplevel(self.root)
                due_date_window.title("Editar Dia do Vencimento")
                due_date_window.geometry("300x150")
                due_date_window.transient(self.root)
                due_date_window.grab_set()
                
                ttk.Label(due_date_window, text="Novo dia do vencimento:").pack(pady=10)
                
                day_frame = ttk.Frame(due_date_window)
                day_frame.pack(pady=5)
                
                day_var = tk.StringVar(value=current_day)
                day_combo = ttk.Combobox(day_frame, textvariable=day_var, width=5, state="readonly")
                day_combo['values'] = [f"{i:02d}" for i in range(1, 32)]
                day_combo.pack(side='left', padx=5)
                
                ttk.Label(day_frame, text="/mm").pack(side='left')
                
                def confirm_new_due_date():
                    new_due_date = f"{day_var.get()}/mm"
                    due_date_window.destroy()
                    success = self.finance_service.update_expense_due_date(month_year, item_index, new_due_date)
                    if success:
                        self.update_expenses_display()
                        messagebox.showinfo("Sucesso", "Data de vencimento atualizada!")
                
                ttk.Button(due_date_window, text="Confirmar", command=confirm_new_due_date).pack(pady=10)
    
    def edit_expense_description(self):
        if hasattr(self, 'selected_expense_item'):
            month_year = self.get_current_month_year()
            expenses = self.finance_service.get_expenses(month_year)
            item_index = int(self.selected_expense_item)
            
            if 0 <= item_index < len(expenses):
                expense = expenses[item_index]
                new_description = self.ask_string_front(
                    "Editar Descrição", 
                    f"Nova descrição para '{expense.description}':"
                )
                if new_description:
                    success = self.finance_service.update_expense_description(month_year, item_index, new_description)
                    if success:
                        self.update_expenses_display()
                        messagebox.showinfo("Sucesso", "Descrição atualizada!")
    
    def delete_expense(self):
        if hasattr(self, 'selected_expense_item'):
            month_year = self.get_current_month_year()
            expenses = self.finance_service.get_expenses(month_year)
            item_index = int(self.selected_expense_item)
            
            if 0 <= item_index < len(expenses):
                expense = expenses[item_index]
                confirm = messagebox.askyesno(
                    "Confirmar Exclusão", 
                    f"Tem certeza que deseja excluir a despesa '{expense.description}'?"
                )
                if confirm:
                    success = self.finance_service.delete_expense(month_year, item_index)
                    if success:
                        self.update_expenses_display()
                        messagebox.showinfo("Sucesso", "Despesa excluída!")

def main():
    root = tk.Tk()
    app = FinanceGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()