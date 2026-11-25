"""Envio de vagas para o Notion ("Job Applications") com status "Para avaliar".

Duas portas de entrada, as duas decididas por ela no Telegram:
  · 👍 numa vaga que o radar notificou (ver processar_feedback_pendente);
  · uma mensagem que ela mesma manda ou encaminha para o bot (post do
    LinkedIn, vaga de grupo do WhatsApp, texto de recrutador).

O radar NUNCA aplica, nunca muda status de linha existente e nunca decide
nada: só cria a linha "Para avaliar". A avaliação continua humana.

Segurança: o token (NOTION_TOKEN) vem de um secret do GitHub e só enxerga o
que foi conectado à integração no Notion (só o banco Job Applications).
Igual ao Telegram, nada aqui loga o token nem os cabeçalhos da requisição.

Tudo que é função pura (montar propriedades, extrair link, quebrar texto)
fica separado da chamada de rede, para ser testável sem mock.
"""

import re

import requests

from core.config import NOTION_DATABASE_ID, NOTION_TOKEN
from core.logger import get_logger

logger = get_logger()

_API = "https://api.notion.com/v1"
_VERSAO_API = "2022-06-28"

STATUS_ENTRADA = "Para avaliar"
# Se o Notion recusar criar a opção nova no select (integração sem permissão
# de alterar o schema), cai para uma opção que já existe no banco.
STATUS_RESERVA = "Saved"

# Limites da API: 2000 caracteres por bloco de texto, 100 blocos por campo.
_MAX_TRECHO = 2000
_MAX_TRECHOS = 100
_MAX_TITULO = 120

_RE_URL = re.compile(r"https?://[^\s<>\"']+")


# ---------------------------------------------------------------- funções puras

def notion_configurado() -> bool:
    return bool(NOTION_TOKEN and NOTION_DATABASE_ID)


def extrair_link(texto: str) -> str | None:
    """Primeiro link http(s) do texto, sem pontuação colada no fim."""
    achado = _RE_URL.search(texto or "")
    if not achado:
        return None
    return achado.group(0).rstrip(").,;!?]")


def titulo_da_mensagem(texto: str) -> str:
    """Primeira linha com conteúdo, sem links, cortada em _MAX_TITULO."""
    for linha in (texto or "").splitlines():
        limpa = _RE_URL.sub("", linha).strip(" \t-–—•*:|")
        if limpa:
            return limpa if len(limpa) <= _MAX_TITULO else limpa[: _MAX_TITULO - 1].rstrip() + "…"
    return "Vaga enviada pelo Telegram"


def _rich_text(texto: str) -> list[dict]:
    texto = (texto or "").strip()
    if not texto:
        return []
    trechos = [texto[i:i + _MAX_TRECHO] for i in range(0, len(texto), _MAX_TRECHO)]
    return [{"type": "text", "text": {"content": t}} for t in trechos[:_MAX_TRECHOS]]


def montar_propriedades(titulo: str, empresa: str = "", link: str | None = None,
                        descricao: str = "", status: str = STATUS_ENTRADA) -> dict:
    """Propriedades da linha nova, com os nomes exatos do banco Job Applications."""
    props = {
        "Application": {"title": _rich_text(titulo or "Vaga sem título")},
        "Status": {"select": {"name": status}},
    }
    if empresa:
        props["Company"] = {"rich_text": _rich_text(empresa)}
    if link:
        props["Job Link"] = {"url": link}
    if descricao:
        props["Descrição da vaga"] = {"rich_text": _rich_text(descricao)}
    return props


def descricao_da_vaga_do_radar(vaga: dict) -> str:
    """Resumo do que o radar sabe da vaga (o texto do anúncio não fica salvo)."""
    partes = ["Origem: radar de vagas (👍 no Telegram)"]
    for rotulo, chave in (("Cargo", "titulo"), ("Empresa", "empresa"), ("Local", "local"),
                          ("Modalidade", "modalidade"), ("Site", "site"),
                          ("Relevância do radar", "relevancia")):
        valor = vaga.get(chave)
        if valor not in (None, ""):
            partes.append(f"{rotulo}: {valor}")
    return "\n".join(partes)


# ---------------------------------------------------------------- rede

def _cabecalhos() -> dict:
    return {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Notion-Version": _VERSAO_API,
        "Content-Type": "application/json",
    }


def _post(caminho: str, corpo: dict) -> requests.Response | None:
    try:
        return requests.post(f"{_API}{caminho}", headers=_cabecalhos(), json=corpo, timeout=20)
    except requests.RequestException as e:
        # Sem `{e}`: a mensagem do requests pode trazer detalhes da requisição.
        logger.error(f"Notion {caminho}: {type(e).__name__} (falha de conexão)")
        return None


def ja_esta_no_notion(link: str | None) -> bool:
    """True se já existe linha com esse Job Link. Sem link, não dá para checar."""
    if not link or not notion_configurado():
        return False
    resposta = _post(f"/databases/{NOTION_DATABASE_ID}/query", {
        "filter": {"property": "Job Link", "url": {"equals": link}},
        "page_size": 1,
    })
    if resposta is None or not resposta.ok:
        status = resposta.status_code if resposta is not None else "sem resposta"
        logger.error(f"Notion: não consegui checar duplicata (HTTP {status})")
        return False
    return bool(resposta.json().get("results"))


def criar_para_avaliar(titulo: str, empresa: str = "", link: str | None = None,
                       descricao: str = "") -> str:
    """Cria a linha "Para avaliar". Devolve 'criada', 'duplicada', 'desligado' ou 'erro'."""
    if not notion_configurado():
        logger.warning("Notion não configurado (NOTION_TOKEN ausente). Pulando envio.")
        return "desligado"
    if ja_esta_no_notion(link):
        return "duplicada"

    for status in (STATUS_ENTRADA, STATUS_RESERVA):
        resposta = _post("/pages", {
            "parent": {"database_id": NOTION_DATABASE_ID},
            "properties": montar_propriedades(titulo, empresa, link, descricao, status),
        })
        if resposta is not None and resposta.ok:
            return "criada"
        codigo = resposta.status_code if resposta is not None else "sem resposta"
        # 400 pode ser só a opção "Para avaliar" que a integração não pôde
        # criar: tenta de novo com a opção de reserva. Outro erro, desiste.
        if codigo != 400:
            break
        logger.warning(f"Notion recusou status '{status}' (HTTP 400), tentando reserva")
    logger.error(f"Notion: não consegui criar a linha (HTTP {codigo})")
    return "erro"
