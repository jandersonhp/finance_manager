# 💰 Gerenciador Financeiro Pessoal

Um sistema completo de gerenciamento financeiro pessoal com interface gráfica, desenvolvido em Python com arquitetura backend/frontend separada. **Sistema totalmente integrado** onde cartões, despesas e carteira se sincronizam automaticamente.

## 🚀 Funcionalidades

### 💳 Aba Carteira

* **Visualizar saldo atual** em tempo real
* **Registrar entradas e saídas** de dinheiro
* **Histórico completo** de transações
* Controle automático do fluxo de caixa

### 💳 Aba Cartões de Crédito

* **Cartões fixos** - Mesmos cartões para todos os meses
* **Controle de limites** total, usado e disponível
* **Data da fatura** personalizável
* **Pagamento de faturas** com registro automático na carteira

### 📅 Aba Despesas Mensais

* **Despesas recorrentes** organizadas por mês
* **Marcar como pagas/não pagas** com um clique
* **Datas de vencimento** configuráveis
* **Navegação temporal** entre diferentes meses

## 🔄 Sistema Integrado Automático

### ⚡ Sincronização Inteligente

* **Cartão → Despesa**: Ao atualizar limite usado, cria despesa automaticamente
* **Despesa → Carteira**: Ao marcar despesa como paga, registra saída na carteira
* **Cartão → Carteira**: Ao pagar fatura, registra saída e reseta limite

### 🖱️ Interface Avançada

* **Menus de contexto** com botão direito para ações rápidas
* **Seletores de data** nativos (mês/ano e dias)
* **Validações automáticas** de saldo e dados
* **Feedback visual** imediato

## 🛠️ Tecnologias Utilizadas

* **Python 3.8+** - Linguagem principal
* **TKinter** - Interface gráfica nativa
* **JSON** - Persistência de dados
* **Dataclasses** - Modelagem de dados
* **Arquitetura em Camadas** - Separação backend/frontend

## 📦 Estrutura do Projeto

```
finance_manager/
├── backend/
│   ├── models/        # Entidades de dados
│   ├── services/      # Lógica de negócio
│   └── repositories/  # Persistência
├── frontend/
│   └── gui.py         # Interface gráfica
├── main.py            # Ponto de entrada
└── data/              # Dados da aplicação
```

## 🚀 Instalação e Execução

### Pré-requisitos

* Python 3.8 ou superior
* Pip (gerenciador de pacotes do Python)

### Passos para executar:

1. **Clone ou baixe o projeto**
2. **Navegue até a pasta do projeto**

```bash
cd finance_manager
```

3. **Execute o programa**

```bash
python -m main
```

> Observação: A primeira execução criará a pasta `data/` automaticamente e um arquivo `finance_data.json` com estrutura inicial.

## 💡 Como Usar

### 💰 Gerenciando sua Carteira

* **Ver Saldo:** Saldo atualizado automaticamente no topo
* **Registrar Entrada:** Clique em "Registrar Entrada" → Informe valor e descrição
* **Registrar Saída:** Clique em "Registrar Saída" → Sistema valida saldo automaticamente
* **Histórico Completo:** Clique em "Ver Histórico" → Visualize todas as transações

### 💳 Gerenciando Cartões

* **Adicionar Cartão:** Clique em "Adicionar Cartão" → Informe Nome, Limite Total, Dia da Fatura
* **Atualizar Limite Usado:** Botão direito no cartão → "Editar Limite Usado" → Cria despesa correspondente automaticamente
* **Pagar Fatura:** Selecione cartão → "Pagar Fatura" → Registra saída na carteira e reseta limite

### 📊 Gerenciando Despesas Mensais

* **Adicionar Despesa:** Selecione mês/ano → Clique em "Adicionar Despesa" → Informe Descrição, Valor, Dia do Vencimento
* **Marcar como Paga:** Botão direito na despesa → "Marcar como Paga" → Registra saída na carteira
* **Navegar entre Meses:** Use os selectores de mês e ano → Dados são mantidos separados por mês

### 🎯 Recursos Especiais

* **🔄 Sync Automático:** Cartão vira despesa automaticamente; pagamentos registram na carteira automaticamente
* **🖱️ Menus de Contexto:** Botão direito em qualquer item para menu rápido
* **📅 Selectores de Data:** Comboboxes nativos para mês/ano e dias, validação automática

### 🗂️ Estrutura de Dados

Os dados são salvos em `data/finance_data.json`:

```json
{
  "wallet": {
    "balance": 1500.0,
    "history": [
      {
        "date": "15/11/2024 10:30",
        "type": "Entrada",
        "amount": 1000.0,
        "description": "Salário"
      }
    ]
  },
  "cards": [
    {
      "id": "Nubank_123456",
      "name": "Nubank",
      "limit": 5000.0,
      "used": 1500.0,
      "due_date": "10/mm"
    }
  ],
  "expenses": {
    "2024-11": [
      {
        "description": "Aluguel",
        "amount": 1200.0,
        "due_date": "05/mm",
        "paid": false
      }
    ]
  }
}
```

### 🔧 Arquitetura

Frontend (GUI) → FinanceService → JSONRepository → Arquivo JSON

```
TKinter      Lógica Negócio    Persistência
```

**Camadas:**

* Frontend: Interface gráfica com TKinter
* Services: Lógica de negócio e regras
* Models: Estruturas de dados com dataclasses
* Repositories: Persistência em JSON

### 🐛 Solução de Problemas

* **Erro ao Executar:** `python -m main`
* **Dados Não Carregam:** Verifique permissões da pasta `data/` e se `finance_data.json` não está corrompido
* **Sync Não Funciona:** Feche e reabra o programa; verifique saldo suficiente

## 📄 Licença

Este projeto é open-source e está sob a licença MIT.

## 👨‍💻 Desenvolvimento

Para contribuir:

* Faça um fork do repositório
* Crie uma branch para sua feature
* Commit suas mudanças
* Push para a branch
* Abra um Pull Request

## 🆕 Changelog

* **Versão 2.0:** Sistema totalmente integrado, Cartões fixos, Sync automático, Menus de contexto, Migração automática de dados antigos
* **Versão 1.0:** Controle básico de carteira, Cartões por mês, Despesas mensais, Interface gráfica inicial
