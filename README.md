# Agente Claude com Ferramentas Customizadas

Agente conversacional em Python usando o SDK da Anthropic com ferramentas customizadas via `@beta_tool`.

## Ferramentas disponíveis

| Ferramenta | Descrição |
|---|---|
| `calculate` | Avalia expressões matemáticas com segurança (sem `eval`) |
| `save_note` | Salva anotações em arquivo local (`notes.json`) |
| `read_notes` | Lê todas as anotações salvas |
| `get_datetime` | Retorna a data e hora atuais |

## Requisitos

- Python 3.10+
- Chave de API da Anthropic

## Instalação

```bash
# Clone o repositório
git clone https://github.com/beatricewbp/claude-code-agents.git
cd claude-code-agents

# Crie e ative um ambiente virtual
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# Instale as dependências
pip install -r requirements.txt

# Configure a chave da API
cp .env.example .env
# Edite .env e adicione sua ANTHROPIC_API_KEY
```

## Uso

```bash
python agent.py
```

```
============================================================
  Agente Claude com Ferramentas Customizadas
============================================================
Ferramentas: calculate | save_note | read_notes | get_datetime
Digite 'sair' para encerrar.

Você: quanto é 2 ** 10?
Agente: 2 ** 10 = 1024

Você: salva uma nota chamada "lembrete" com o conteúdo "estudar Python"
Agente: Anotação 'lembrete' salva com sucesso.

Você: sair
Até logo!
```

## Estrutura

```
claude-code-agents/
├── agent.py          # Agente principal
├── requirements.txt  # Dependências
├── .env.example      # Template de configuração
└── .gitignore
```
