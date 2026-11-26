"""Só a parte do bot, sem buscar vagas: lê o Telegram (👍/👎 e as mensagens
que ela manda) e grava "Para avaliar" no Notion.

Roda no workflow leve .github/workflows/bot-rapido.yml, a cada 10 minutos
e no botão "Run workflow", para a vaga não esperar o ciclo completo do
radar (07:17 e 17:17). É a mesma função que o main.py chama no começo de
cada ciclo, então os dois nunca discordam sobre o que fazer.
"""

import sys

from database.database import BancoVazioSuspeito, iniciar_db
from notifier.telegram import processar_feedback_pendente


def main() -> int:
    try:
        iniciar_db()
    except BancoVazioSuspeito as e:
        print(f"Banco suspeito, não vou mexer em nada: {e}")
        return 1
    processar_feedback_pendente()
    print("Bot processado.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
