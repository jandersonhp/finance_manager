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
        
        # Combobox com meses dinâmicos (não limitado aos registrados)
        self.cards_month_var = tk.StringVar(value=datetime.now().strftime("%Y-%m"))
        self.cards_month_combo = ttk.Combobox(month_frame, textvariable=self.cards_month_var, state="normal")
        self.cards_month_combo.pack(side='left', padx=5)
        self.cards_month_combo.bind('<<ComboboxSelected>>', self.on_cards_month_changed)
        self.cards_month_combo.bind('<KeyRelease>', self.on_cards_month_key)
        self.cards_month_combo.bind('<FocusOut>', self.on_cards_month_focus_out)
        
        # Botão para ir para o mês digitado
        ttk.Button(month_frame, text="Ir", command=self.update_cards_display).pack(side='left', padx=5)
        ttk.Button(month_frame, text="Adicionar Cartão", command=self.add_card).pack(side='left', padx=10)
        
        # Treeview para cartões
        columns = ('Cartão', 'Limite Total', 'Limite Usado', 'Disponível', 'Data Fatura')
        self.cards_tree = ttk.Treeview(self.cards_frame, columns=columns, show='headings', height=12)
        
        for col in columns:
            self.cards_tree.heading(col, text=col)
            self.cards_tree.column(col, width=100)
        
        self.cards_tree.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Menu de contexto para cartões
        self.cards_context_menu = tk.Menu(self.root, tearoff=0)
        self.cards_context_menu.add_command(label="Editar Limite Usado", command=self.edit_card_used)
        self.cards_context_menu.add_command(label="Editar Limite Total", command=self.edit_card_limit)
        self.cards_context_menu.add_command(label="Editar Data da Fatura", command=self.edit_card_due_date)
        self.cards_context_menu.add_separator()
        self.cards_context_menu.add_command(label="Excluir Cartão", command=self.delete_card)
        
        self.cards_tree.bind("<Button-3>", self.show_cards_context_menu)
    
    def create_expenses_tab(self):
        self.expenses_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.expenses_frame, text="Despesas Mensais")
        
        # Controles de mês/ano
        month_frame = ttk.Frame(self.expenses_frame)
        month_frame.pack(pady=10)
        
        ttk.Label(month_frame, text="Mês/Ano:").pack(side='left')
        
        # Combobox com meses dinâmicos
        self.expenses_month_var = tk.StringVar(value=datetime.now().strftime("%Y-%m"))
        self.expenses_month_combo = ttk.Combobox(month_frame, textvariable=self.expenses_month_var, state="normal")
        self.expenses_month_combo.pack(side='left', padx=5)
        self.expenses_month_combo.bind('<<ComboboxSelected>>', self.on_expenses_month_changed)
        self.expenses_month_combo.bind('<KeyRelease>', self.on_expenses_month_key)
        self.expenses_month_combo.bind('<FocusOut>', self.on_expenses_month_focus_out)
        
        # Botão para ir para o mês digitado
        ttk.Button(month_frame, text="Ir", command=self.update_expenses_display).pack(side='left', padx=5)
        ttk.Button(month_frame, text="Adicionar Despesa", command=self.add_monthly_expense).pack(side='left', padx=10)
        
        # Treeview para despesas
        columns = ('Descrição', 'Valor', 'Vencimento', 'Paga')
        self.expenses_tree = ttk.Treeview(self.expenses_frame, columns=columns, show='headings', height=12)
        
        for col in columns:
            self.expenses_tree.heading(col, text=col)
            self.expenses_tree.column(col, width=120)
        
        self.expenses_tree.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Menu de contexto para despesas
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
    
    def get_month_year_suggestions(self):
        """Retorna sugestões de meses/anos (últimos 24 meses + meses com dados)"""
        suggestions = set()
        
        # Últimos 24 meses
        current = datetime.now()
        for i in range(24):
            date = current - timedelta(days=30*i)
            suggestions.add(date.strftime("%Y-%m"))
        
        # Meses que já têm dados registrados
        suggestions.update(self.finance_service.cards.keys())
        suggestions.update(self.finance_service.expenses.keys())
        
        return sorted(suggestions, reverse=True)
    
    def update_month_comboboxes(self):
        """Atualiza as sugestões dos comboboxes"""
        suggestions = self.get_month_year_suggestions()
        
        self.cards_month_combo['values'] = suggestions
        self.expenses_month_combo['values'] = suggestions
    
    def on_cards_month_key(self, event):
        """Atualiza sugestões quando digita no combobox de cartões"""
        self.update_month_comboboxes()
    
    def on_cards_month_focus_out(self, event):
        """Valida o formato do mês quando perde o foco"""
        self.validate_month_format(self.cards_month_var)
    
    def on_expenses_month_key(self, event):
        """Atualiza sugestões quando digita no combobox de despesas"""
        self.update_month_comboboxes()
    
    def on_expenses_month_focus_out(self, event):
        """Valida o formato do mês quando perde o foco"""
        self.validate_month_format(self.expenses_month_var)
    
    def validate_month_format(self, month_var):
        """Valida se o formato do mês/ano está correto"""
        value = month_var.get()
        try:
            datetime.strptime(value + "-01", "%Y-%m-%d")
            return True
        except ValueError:
            # Se formato inválido, volta para o mês atual
            month_var.set(datetime.now().strftime("%Y-%m"))
            return False
    
    def show_cards_context_menu(self, event):
        """Mostra menu de contexto para cartões"""
        item = self.cards_tree.identify_row(event.y)
        if item:
            self.cards_tree.selection_set(item)
            self.selected_card_item = item
            self.cards_context_menu.post(event.x_root, event.y_root)
    
    def show_expenses_context_menu(self, event):
        """Mostra menu de contexto para despesas"""
        item = self.expenses_tree.identify_row(event.y)
        if item:
            self.expenses_tree.selection_set(item)
            self.selected_expense_item = item
            self.update_expenses_context_menu()
            self.expenses_context_menu.post(event.x_root, event.y_root)
    
    def update_expenses_context_menu(self):
        """Atualiza o menu de contexto baseado no status da despesa"""
        if hasattr(self, 'selected_expense_item'):
            month_year = self.expenses_month_var.get()
            expenses = self.finance_service.get_expenses(month_year)
            item_index = int(self.selected_expense_item)
            
            if 0 <= item_index < len(expenses):
                expense = expenses[item_index]
                
                # Atualiza labels do menu baseado no status
                if expense.paid:
                    self.expenses_context_menu.entryconfig(0, label="Marcar como Não Paga")
                else:
                    self.expenses_context_menu.entryconfig(0, label="Marcar como Paga")
    
    def update_displays(self):
        self.update_month_comboboxes()
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
                card.due_date
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
                paid
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
    
    def edit_card_used(self):
        """Edita o limite usado do cartão"""
        if hasattr(self, 'selected_card_item'):
            month_year = self.cards_month_var.get()
            cards = self.finance_service.get_cards(month_year)
            item_index = int(self.selected_card_item)
            
            if 0 <= item_index < len(cards):
                card = cards[item_index]
                new_used = simpledialog.askfloat(
                    "Editar Limite Usado", 
                    f"Limite usado para {card.name}:", 
                    initialvalue=card.used
                )
                if new_used is not None and new_used >= 0:
                    success = self.finance_service.update_card_usage(month_year, item_index, new_used)
                    if success:
                        self.update_cards_display()
                        messagebox.showinfo("Sucesso", "Limite usado atualizado!")
                    else:
                        messagebox.showerror("Erro", "Erro ao atualizar limite usado!")
    
    def edit_card_limit(self):
        """Edita o limite total do cartão"""
        if hasattr(self, 'selected_card_item'):
            month_year = self.cards_month_var.get()
            cards = self.finance_service.get_cards(month_year)
            item_index = int(self.selected_card_item)
            
            if 0 <= item_index < len(cards):
                card = cards[item_index]
                new_limit = simpledialog.askfloat(
                    "Editar Limite Total", 
                    f"Limite total para {card.name}:", 
                    initialvalue=card.limit
                )
                if new_limit is not None and new_limit > 0:
                    # Para atualizar o limite, precisamos recriar o cartão
                    success = self.finance_service.update_card_limit(month_year, item_index, new_limit)
                    if success:
                        self.update_cards_display()
                        messagebox.showinfo("Sucesso", "Limite total atualizado!")
                    else:
                        messagebox.showerror("Erro", "Erro ao atualizar limite total!")
    
    def edit_card_due_date(self):
        """Edita a data da fatura do cartão"""
        if hasattr(self, 'selected_card_item'):
            month_year = self.cards_month_var.get()
            cards = self.finance_service.get_cards(month_year)
            item_index = int(self.selected_card_item)
            
            if 0 <= item_index < len(cards):
                card = cards[item_index]
                new_due_date = simpledialog.askstring(
                    "Editar Data da Fatura", 
                    f"Data da fatura para {card.name} (dd/mm):", 
                    initialvalue=card.due_date
                )
                if new_due_date:
                    success = self.finance_service.update_card_due_date(month_year, item_index, new_due_date)
                    if success:
                        self.update_cards_display()
                        messagebox.showinfo("Sucesso", "Data da fatura atualizada!")
                    else:
                        messagebox.showerror("Erro", "Erro ao atualizar data da fatura!")
    
    def delete_card(self):
        """Exclui um cartão"""
        if hasattr(self, 'selected_card_item'):
            month_year = self.cards_month_var.get()
            cards = self.finance_service.get_cards(month_year)
            item_index = int(self.selected_card_item)
            
            if 0 <= item_index < len(cards):
                card = cards[item_index]
                confirm = messagebox.askyesno(
                    "Confirmar Exclusão", 
                    f"Tem certeza que deseja excluir o cartão {card.name}?"
                )
                if confirm:
                    success = self.finance_service.delete_card(month_year, item_index)
                    if success:
                        self.update_cards_display()
                        messagebox.showinfo("Sucesso", "Cartão excluído!")
                    else:
                        messagebox.showerror("Erro", "Erro ao excluir cartão!")
    
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
    
    def toggle_expense_paid(self):
        """Alterna entre pago/não pago"""
        if hasattr(self, 'selected_expense_item'):
            month_year = self.expenses_month_var.get()
            item_index = int(self.selected_expense_item)
            
            success = self.finance_service.toggle_expense_paid(month_year, item_index)
            if success:
                self.update_expenses_display()
                messagebox.showinfo("Sucesso", "Status da despesa atualizado!")
            else:
                messagebox.showerror("Erro", "Erro ao atualizar despesa!")
    
    def edit_expense_amount(self):
        """Edita o valor da despesa"""
        if hasattr(self, 'selected_expense_item'):
            month_year = self.expenses_month_var.get()
            expenses = self.finance_service.get_expenses(month_year)
            item_index = int(self.selected_expense_item)
            
            if 0 <= item_index < len(expenses):
                expense = expenses[item_index]
                new_amount = simpledialog.askfloat(
                    "Editar Valor", 
                    f"Novo valor para {expense.description}:", 
                    initialvalue=expense.amount
                )
                if new_amount is not None and new_amount > 0:
                    success = self.finance_service.update_expense_amount(month_year, item_index, new_amount)
                    if success:
                        self.update_expenses_display()
                        messagebox.showinfo("Sucesso", "Valor da despesa atualizado!")
                    else:
                        messagebox.showerror("Erro", "Erro ao atualizar valor!")
    
    def edit_expense_due_date(self):
        """Edita a data de vencimento da despesa"""
        if hasattr(self, 'selected_expense_item'):
            month_year = self.expenses_month_var.get()
            expenses = self.finance_service.get_expenses(month_year)
            item_index = int(self.selected_expense_item)
            
            if 0 <= item_index < len(expenses):
                expense = expenses[item_index]
                new_due_date = simpledialog.askstring(
                    "Editar Data de Vencimento", 
                    f"Nova data de vencimento para {expense.description} (dd/mm):", 
                    initialvalue=expense.due_date
                )
                if new_due_date:
                    success = self.finance_service.update_expense_due_date(month_year, item_index, new_due_date)
                    if success:
                        self.update_expenses_display()
                        messagebox.showinfo("Sucesso", "Data de vencimento atualizada!")
                    else:
                        messagebox.showerror("Erro", "Erro ao atualizar data!")
    
    def edit_expense_description(self):
        """Edita a descrição da despesa"""
        if hasattr(self, 'selected_expense_item'):
            month_year = self.expenses_month_var.get()
            expenses = self.finance_service.get_expenses(month_year)
            item_index = int(self.selected_expense_item)
            
            if 0 <= item_index < len(expenses):
                expense = expenses[item_index]
                new_description = simpledialog.askstring(
                    "Editar Descrição", 
                    f"Nova descrição:", 
                    initialvalue=expense.description
                )
                if new_description:
                    success = self.finance_service.update_expense_description(month_year, item_index, new_description)
                    if success:
                        self.update_expenses_display()
                        messagebox.showinfo("Sucesso", "Descrição atualizada!")
                    else:
                        messagebox.showerror("Erro", "Erro ao atualizar descrição!")
    
    def delete_expense(self):
        """Exclui uma despesa"""
        if hasattr(self, 'selected_expense_item'):
            month_year = self.expenses_month_var.get()
            expenses = self.finance_service.get_expenses(month_year)
            item_index = int(self.selected_expense_item)
            
            if 0 <= item_index < len(expenses):
                expense = expenses[item_index]
                confirm = messagebox.askyesno(
                    "Confirmar Exclusão", 
                    f"Tem certeza que deseja excluir a despesa {expense.description}?"
                )
                if confirm:
                    success = self.finance_service.delete_expense(month_year, item_index)
                    if success:
                        self.update_expenses_display()
                        messagebox.showinfo("Sucesso", "Despesa excluída!")
                    else:
                        messagebox.showerror("Erro", "Erro ao excluir despesa!")
    
    def on_cards_month_changed(self, event):
        self.update_cards_display()
    
    def on_expenses_month_changed(self, event):
        self.update_expenses_display()