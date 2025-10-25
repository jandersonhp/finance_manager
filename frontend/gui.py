import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime, timedelta
from backend.services.finance_service import FinanceService

class FinanceGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Gerenciador Financeiro - Sistema Integrado")
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
        
        # Treeview para cartões (agora cartões são fixos, não por mês)
        columns = ('Cartão', 'Limite Total', 'Limite Usado', 'Disponível', 'Data Fatura')
        self.cards_tree = ttk.Treeview(self.cards_frame, columns=columns, show='headings', height=12)
        
        for col in columns:
            self.cards_tree.heading(col, text=col)
            self.cards_tree.column(col, width=100)
        
        self.cards_tree.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Botões
        button_frame = ttk.Frame(self.cards_frame)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Adicionar Cartão", command=self.add_card).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Pagar Fatura", command=self.pay_card_invoice).pack(side='left', padx=5)
        
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
        
        # Controles de mês/ano COM SELECTOR PERSONALIZADO
        month_frame = ttk.Frame(self.expenses_frame)
        month_frame.pack(pady=10)
        
        ttk.Label(month_frame, text="Mês/Ano:").pack(side='left')
        
        # Selector de mês e ano
        selector_frame = ttk.Frame(month_frame)
        selector_frame.pack(side='left', padx=5)
        
        # Ano
        self.year_var = tk.StringVar(value=str(datetime.now().year))
        year_combo = ttk.Combobox(selector_frame, textvariable=self.year_var, width=6, state="readonly")
        year_combo['values'] = [str(year) for year in range(2020, 2031)]
        year_combo.pack(side='left')
        year_combo.bind('<<ComboboxSelected>>', self.on_month_year_changed)
        
        ttk.Label(selector_frame, text="/").pack(side='left')
        
        # Mês
        self.month_var = tk.StringVar(value=f"{datetime.now().month:02d}")
        month_combo = ttk.Combobox(selector_frame, textvariable=self.month_var, width=3, state="readonly")
        month_combo['values'] = [f"{i:02d}" for i in range(1, 13)]
        month_combo.pack(side='left')
        month_combo.bind('<<ComboboxSelected>>', self.on_month_year_changed)
        
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
    
    def get_current_month_year(self):
        """Retorna o mês/ano atual no formato YYYY-MM"""
        return f"{self.year_var.get()}-{self.month_var.get()}"
    
    def on_month_year_changed(self, event=None):
        """Quando mês ou ano é alterado"""
        self.update_expenses_display()
    
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
        
        cards = self.finance_service.get_cards()
        
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
        
        month_year = self.get_current_month_year()
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
                # Janela para selecionar dia da fatura
                due_date_window = tk.Toplevel(self.root)
                due_date_window.title("Selecionar Dia da Fatura")
                due_date_window.geometry("300x150")
                
                ttk.Label(due_date_window, text="Dia da fatura:").pack(pady=10)
                
                day_frame = ttk.Frame(due_date_window)
                day_frame.pack(pady=5)
                
                day_var = tk.StringVar(value="10")
                day_combo = ttk.Combobox(day_frame, textvariable=day_var, width=5, state="readonly")
                day_combo['values'] = [f"{i:02d}" for i in range(1, 32)]
                day_combo.pack(side='left', padx=5)
                
                ttk.Label(day_frame, text="/mm").pack(side='left')
                
                def confirm_due_date():
                    due_date = f"{day_var.get()}/mm"  # Formato dd/mm
                    due_date_window.destroy()
                    success = self.finance_service.add_card(name, limit, due_date)
                    if success:
                        self.update_cards_display()
                        messagebox.showinfo("Sucesso", "Cartão adicionado com sucesso!")
                    else:
                        messagebox.showerror("Erro", "Erro ao adicionar cartão!")
                
                ttk.Button(due_date_window, text="Confirmar", command=confirm_due_date).pack(pady=10)
    
    def pay_card_invoice(self):
        """Paga fatura do cartão selecionado"""
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
                    # Atualiza despesas do mês atual também
                    self.update_expenses_display()
                    messagebox.showinfo("Sucesso", "Fatura paga com sucesso!")
                else:
                    messagebox.showerror("Erro", "Saldo insuficiente para pagar a fatura!")
    
    def show_cards_context_menu(self, event):
        """Mostra menu de contexto para cartões"""
        item = self.cards_tree.identify_row(event.y)
        if item:
            self.cards_tree.selection_set(item)
            self.selected_card_item = item
            self.cards_context_menu.post(event.x_root, event.y_root)
    
    def edit_card_used(self):
        """Edita o limite usado do cartão e sincroniza com despesas"""
        if hasattr(self, 'selected_card_item'):
            card_index = int(self.selected_card_item)
            cards = self.finance_service.get_cards()
            
            if 0 <= card_index < len(cards):
                card = cards[card_index]
                new_used = simpledialog.askfloat(
                    "Editar Limite Usado", 
                    f"Limite usado para {card.name}:", 
                    initialvalue=card.used
                )
                if new_used is not None and new_used >= 0:
                    month_year = self.get_current_month_year()
                    success = self.finance_service.update_card_usage(card_index, new_used, month_year)
                    if success:
                        self.update_cards_display()
                        self.update_expenses_display()
                        messagebox.showinfo("Sucesso", "Limite usado atualizado e despesa sincronizada!")
                    else:
                        messagebox.showerror("Erro", "Erro ao atualizar limite usado!")
    
    def edit_card_limit(self):
        """Edita o limite total do cartão"""
        if hasattr(self, 'selected_card_item'):
            card_index = int(self.selected_card_item)
            cards = self.finance_service.get_cards()
            
            if 0 <= card_index < len(cards):
                card = cards[card_index]
                new_limit = simpledialog.askfloat(
                    "Editar Limite Total", 
                    f"Limite total para {card.name}:", 
                    initialvalue=card.limit
                )
                if new_limit is not None and new_limit > 0:
                    success = self.finance_service.update_card_limit(card_index, new_limit)
                    if success:
                        self.update_cards_display()
                        messagebox.showinfo("Sucesso", "Limite total atualizado!")
                    else:
                        messagebox.showerror("Erro", "Erro ao atualizar limite total!")
    
    def edit_card_due_date(self):
        """Edita a data da fatura do cartão"""
        if hasattr(self, 'selected_card_item'):
            card_index = int(self.selected_card_item)
            cards = self.finance_service.get_cards()
            
            if 0 <= card_index < len(cards):
                card = cards[card_index]
                
                # Extrai o dia atual da data (formato dd/mm)
                current_day = card.due_date.split('/')[0] if '/' in card.due_date else "10"
                
                due_date_window = tk.Toplevel(self.root)
                due_date_window.title("Editar Dia da Fatura")
                due_date_window.geometry("300x150")
                
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
                    else:
                        messagebox.showerror("Erro", "Erro ao atualizar data da fatura!")
                
                ttk.Button(due_date_window, text="Confirmar", command=confirm_new_due_date).pack(pady=10)
    
    def delete_card(self):
        """Exclui um cartão"""
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
                    else:
                        messagebox.showerror("Erro", "Erro ao excluir cartão!")
    
    def add_monthly_expense(self):
        description = simpledialog.askstring("Nova Despesa", "Descrição:")
        if description:
            amount = simpledialog.askfloat("Nova Despesa", "Valor:")
            if amount:
                # Janela para selecionar dia do vencimento
                due_date_window = tk.Toplevel(self.root)
                due_date_window.title("Selecionar Dia do Vencimento")
                due_date_window.geometry("300x150")
                
                ttk.Label(due_date_window, text="Dia do vencimento:").pack(pady=10)
                
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
                    month_year = self.get_current_month_year()
                    success = self.finance_service.add_expense_monthly(month_year, description, amount, due_date)
                    if success:
                        self.update_expenses_display()
                        messagebox.showinfo("Sucesso", "Despesa adicionada com sucesso!")
                    else:
                        messagebox.showerror("Erro", "Erro ao adicionar despesa!")
                
                ttk.Button(due_date_window, text="Confirmar", command=confirm_due_date).pack(pady=10)
    
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
            month_year = self.get_current_month_year()
            expenses = self.finance_service.get_expenses(month_year)
            item_index = int(self.selected_expense_item)
            
            if 0 <= item_index < len(expenses):
                expense = expenses[item_index]
                
                # Atualiza labels do menu baseado no status
                if expense.paid:
                    self.expenses_context_menu.entryconfig(0, label="Marcar como Não Paga")
                    self.expenses_context_menu.entryconfig(1, label="Marcar como Paga")
                else:
                    self.expenses_context_menu.entryconfig(0, label="Marcar como Paga")
                    self.expenses_context_menu.entryconfig(1, label="Marcar como Não Paga")
    
    def toggle_expense_paid(self):
        """Alterna status da despesa e atualiza carteira"""
        if hasattr(self, 'selected_expense_item'):
            month_year = self.get_current_month_year()
            item_index = int(self.selected_expense_item)
            
            success = self.finance_service.toggle_expense_paid(month_year, item_index)
            if success:
                self.update_expenses_display()
                self.update_wallet_display()
                messagebox.showinfo("Sucesso", "Status da despesa atualizado e carteira sincronizada!")
            else:
                messagebox.showerror("Erro", "Saldo insuficiente para pagar esta despesa!")
    
    def edit_expense_amount(self):
        """Edita o valor da despesa"""
        if hasattr(self, 'selected_expense_item'):
            month_year = self.get_current_month_year()
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
            month_year = self.get_current_month_year()
            expenses = self.finance_service.get_expenses(month_year)
            item_index = int(self.selected_expense_item)
            
            if 0 <= item_index < len(expenses):
                expense = expenses[item_index]
                
                # Extrai o dia atual
                current_day = expense.due_date.split('/')[0] if '/' in expense.due_date else "10"
                
                due_date_window = tk.Toplevel(self.root)
                due_date_window.title("Editar Dia do Vencimento")
                due_date_window.geometry("300x150")
                
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
                    else:
                        messagebox.showerror("Erro", "Erro ao atualizar data!")
                
                ttk.Button(due_date_window, text="Confirmar", command=confirm_new_due_date).pack(pady=10)
    
    def edit_expense_description(self):
        """Edita a descrição da despesa"""
        if hasattr(self, 'selected_expense_item'):
            month_year = self.get_current_month_year()
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
            month_year = self.get_current_month_year()
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