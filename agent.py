"""
Agente Claude com ferramentas customizadas usando o tool runner beta.
Claude agent with custom tools using the beta tool runner.

Ferramentas / Tools:
  - calculate    : avalia expressões matemáticas seguras
  - save_note    : salva anotações em arquivo local
  - read_notes   : lê as anotações salvas
  - get_datetime : retorna data e hora atuais
"""

import ast
import json
import operator
import os
from datetime import datetime
from pathlib import Path

import anthropic
from anthropic import beta_tool
from dotenv import load_dotenv

load_dotenv()

MODEL = "claude-opus-4-6"
NOTES_FILE = Path("notes.json")

SYSTEM_PROMPT = """Você é um assistente inteligente com acesso a ferramentas customizadas.
Você pode fazer cálculos matemáticos, salvar e recuperar anotações, e verificar a data/hora atual.
Responda sempre em português, de forma clara e concisa.
Quando usar ferramentas, explique brevemente o que está fazendo."""


# ---------------------------------------------------------------------------
# Ferramentas customizadas / Custom tools
# ---------------------------------------------------------------------------

@beta_tool
def calculate(expression: str) -> str:
    """Avalia uma expressão matemática de forma segura e retorna o resultado.

    Args:
        expression: Expressão matemática, ex: '2 + 2', '(10 * 5) / 2', '2 ** 8'.
    """
    allowed_operators = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Pow: operator.pow,
        ast.Mod: operator.mod,
        ast.FloorDiv: operator.floordiv,
        ast.USub: operator.neg,
    }

    def _eval(node):
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in allowed_operators:
            return allowed_operators[type(node.op)](_eval(node.left), _eval(node.right))
        if isinstance(node, ast.UnaryOp) and type(node.op) in allowed_operators:
            return allowed_operators[type(node.op)](_eval(node.operand))
        raise ValueError(f"Operação não permitida: {ast.dump(node)}")

    try:
        tree = ast.parse(expression, mode="eval")
        result = _eval(tree.body)
        return f"{expression} = {result}"
    except ZeroDivisionError:
        return "Erro: divisão por zero."
    except Exception as e:
        return f"Erro ao calcular '{expression}': {e}"


@beta_tool
def save_note(title: str, content: str) -> str:
    """Salva uma anotação com título e conteúdo em arquivo local.

    Args:
        title: Título da anotação.
        content: Conteúdo/texto da anotação.
    """
    notes: dict = {}
    if NOTES_FILE.exists():
        notes = json.loads(NOTES_FILE.read_text(encoding="utf-8"))

    timestamp = datetime.now().isoformat(timespec="seconds")
    notes[title] = {"content": content, "saved_at": timestamp}
    NOTES_FILE.write_text(json.dumps(notes, ensure_ascii=False, indent=2), encoding="utf-8")
    return f"Anotação '{title}' salva com sucesso em {timestamp}."


@beta_tool
def read_notes() -> str:
    """Lê e retorna todas as anotações salvas. Não requer parâmetros."""
    if not NOTES_FILE.exists():
        return "Nenhuma anotação encontrada."

    notes: dict = json.loads(NOTES_FILE.read_text(encoding="utf-8"))
    if not notes:
        return "Nenhuma anotação encontrada."

    lines = []
    for title, data in notes.items():
        lines.append(f"## {title} (salvo em {data['saved_at']})")
        lines.append(data["content"])
        lines.append("")
    return "\n".join(lines)


@beta_tool
def get_datetime() -> str:
    """Retorna a data e hora atuais do sistema. Não requer parâmetros."""
    now = datetime.now()
    return now.strftime("Data: %d/%m/%Y | Hora: %H:%M:%S")


# ---------------------------------------------------------------------------
# Loop do agente / Agent loop
# ---------------------------------------------------------------------------

def run_agent(user_message: str, conversation_history: list) -> str:
    """Executa uma rodada do agente com o tool runner beta."""
    client = anthropic.Anthropic()

    conversation_history.append({"role": "user", "content": user_message})

    runner = client.beta.messages.tool_runner(
        model=MODEL,
        max_tokens=4096,
        thinking={"type": "adaptive"},
        system=SYSTEM_PROMPT,
        tools=[calculate, save_note, read_notes, get_datetime],
        messages=conversation_history,
    )

    final_message = None
    for message in runner:
        final_message = message

    if final_message is None:
        return "Sem resposta do agente."

    response_text = ""
    for block in final_message.content:
        if block.type == "text":
            response_text += block.text

    conversation_history.append({"role": "assistant", "content": final_message.content})
    return response_text


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("Erro: ANTHROPIC_API_KEY não definida.")
        print("Copie .env.example para .env e adicione sua chave.")
        return

    print("=" * 60)
    print("  Agente Claude com Ferramentas Customizadas")
    print("=" * 60)
    print("Ferramentas: calculate | save_note | read_notes | get_datetime")
    print("Digite 'sair' para encerrar.\n")

    conversation_history: list = []

    while True:
        try:
            user_input = input("Você: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nEncerrando...")
            break

        if not user_input:
            continue
        if user_input.lower() in ("sair", "quit", "exit"):
            print("Até logo!")
            break

        print("Agente: ", end="", flush=True)
        print(run_agent(user_input, conversation_history))
        print()


if __name__ == "__main__":
    main()
