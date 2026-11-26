"""Abre o link da vaga e tira dele cargo, empresa, local e descrição, para a
linha "Para avaliar" já chegar no Notion completa, sem copiar e colar.

Três caminhos, do mais confiável ao mais genérico:
  1. LinkedIn: o endpoint público de visitante (jobs-guest) devolve a vaga
     inteira sem login — o mesmo tipo de endpoint que o radar já usa nas
     buscas. O link normal (/jobs/view/123) é bloqueado para robôs.
  2. Páginas com dados estruturados (JSON-LD "JobPosting"): Gupy, Greenhouse,
     Lever, Workable, Inhire e a maioria dos sites de carreira publicam a vaga
     assim, para o Google Vagas.
  3. Qualquer outra página: título, nome do site e o texto visível.

Se nada der certo (site fora do ar, página só em JavaScript, bloqueio), a
vaga entra mesmo assim, com o que a mensagem trouxe — nunca se perde.
Só usa a biblioteca padrão + requests: roda no workflow leve, sem navegador.
"""

import json
import re
from html import unescape
from html.parser import HTMLParser

import requests

from core.logger import get_logger

logger = get_logger()

_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)
MAX_DESCRICAO = 8000

_BLOCOS = {"p", "div", "br", "li", "ul", "ol", "h1", "h2", "h3", "h4", "h5", "h6",
           "section", "article", "tr", "table", "header", "footer"}
_IGNORAR = {"script", "style", "noscript", "svg", "nav", "head", "template", "iframe", "form"}


# ---------------------------------------------------------------- funções puras

class _Texto(HTMLParser):
    def __init__(self):
        super().__init__()
        self.partes: list[str] = []
        self._ignorando = 0

    def handle_starttag(self, tag, attrs):
        if tag in _IGNORAR:
            self._ignorando += 1
        elif tag in _BLOCOS:
            self.partes.append("\n")
        if tag == "li" and not self._ignorando:
            self.partes.append("• ")

    def handle_endtag(self, tag):
        if tag in _IGNORAR and self._ignorando:
            self._ignorando -= 1
        elif tag in _BLOCOS:
            self.partes.append("\n")

    def handle_data(self, data):
        if not self._ignorando:
            self.partes.append(data)


def html_para_texto(html: str) -> str:
    """HTML vira texto legível, com quebras de linha nos blocos."""
    parser = _Texto()
    parser.feed(html or "")
    texto = "".join(parser.partes)
    texto = re.sub(r"[ \t\r\f\v]+", " ", texto)
    texto = re.sub(r" *\n *", "\n", texto)
    return re.sub(r"\n{3,}", "\n\n", texto).strip()


def id_vaga_linkedin(url: str) -> str | None:
    """Id numérico da vaga em links do LinkedIn (view, currentJobId, slug)."""
    if not url or "linkedin.com" not in url:
        return None
    for padrao in (r"currentJobId=(\d+)", r"/jobs/view/(?:[^/?#]*?-)?(\d{6,})"):
        achado = re.search(padrao, url)
        if achado:
            return achado.group(1)
    return None


def _classe(html: str, tag: str, classe: str) -> str:
    """Conteúdo do primeiro <tag class="... classe ..."> (sem tags aninhadas iguais)."""
    achado = re.search(
        rf'<{tag}[^>]*class="[^"]*\b{re.escape(classe)}\b[^"]*"[^>]*>(.*?)</{tag}>',
        html or "", re.S,
    )
    return html_para_texto(achado.group(1)) if achado else ""


def extrair_linkedin(html: str) -> dict:
    """Página do endpoint jobs-guest/jobPosting do LinkedIn."""
    return {
        "titulo": _classe(html, "h2", "top-card-layout__title") or _classe(html, "h1", "top-card-layout__title"),
        "empresa": _classe(html, "a", "topcard__org-name-link") or _classe(html, "span", "topcard__flavor"),
        "local": _classe(html, "span", "topcard__flavor--bullet"),
        "descricao": _classe(html, "div", "show-more-less-html__markup"),
    }


def _jobposting(dados):
    """Acha o objeto JobPosting dentro do JSON-LD (direto, em lista ou @graph)."""
    if isinstance(dados, list):
        for item in dados:
            achado = _jobposting(item)
            if achado:
                return achado
    elif isinstance(dados, dict):
        tipo = dados.get("@type")
        if tipo == "JobPosting" or (isinstance(tipo, list) and "JobPosting" in tipo):
            return dados
        if "@graph" in dados:
            return _jobposting(dados["@graph"])
    return None


def _local_jsonld(vaga: dict) -> str:
    locais = vaga.get("jobLocation")
    locais = locais if isinstance(locais, list) else [locais]
    nomes = []
    for local in locais:
        endereco = (local or {}).get("address") if isinstance(local, dict) else None
        if isinstance(endereco, dict):
            partes = [endereco.get(k) for k in ("addressLocality", "addressRegion", "addressCountry")]
            partes = [p.get("name") if isinstance(p, dict) else p for p in partes]
            nome = ", ".join(p for p in partes if p)
            if nome:
                nomes.append(nome)
    if vaga.get("jobLocationType") == "TELECOMMUTE":
        nomes.append("Remoto")
    return " · ".join(dict.fromkeys(nomes))


def _meta(html: str, nome: str) -> str:
    for padrao in (
        rf'<meta[^>]+(?:property|name)="{re.escape(nome)}"[^>]+content="([^"]*)"',
        rf'<meta[^>]+content="([^"]*)"[^>]+(?:property|name)="{re.escape(nome)}"',
    ):
        achado = re.search(padrao, html or "", re.I)
        if achado:
            return unescape(achado.group(1)).strip()
    return ""


def _palavras(texto: str) -> set[str]:
    return {p for p in re.split(r"[^a-z0-9à-ú]+", (texto or "").lower()) if len(p) > 2}


def _melhor_titulo(html: str, url: str, empresa: str) -> str:
    """Entre os <h1>/<h2> da página, o que mais se parece com o fim do link
    (vagas.site/vagas/product-designer → "Product Designer"). Evita pegar o
    nome do site, que muitas páginas usam no <title>."""
    cabecalhos = [html_para_texto(h) for h in re.findall(r"<h[12][^>]*>(.*?)</h[12]>", html or "", re.S | re.I)]
    cabecalhos = [h for h in cabecalhos if h and len(h) <= 150 and h.lower() != (empresa or "").lower()]
    fim_do_link = (url or "").rstrip("/").split("?")[0].rsplit("/", 1)[-1]
    alvo = _palavras(fim_do_link.replace("-", " ").replace("_", " "))
    if alvo and cabecalhos:
        melhor = max(cabecalhos, key=lambda h: len(_palavras(h) & alvo))
        if _palavras(melhor) & alvo:
            return melhor
    return ""


def extrair_generico(html: str, url: str = "") -> dict:
    """JSON-LD JobPosting quando existir; senão, metadados e texto da página."""
    for bloco in re.findall(r'<script[^>]+application/ld\+json[^>]*>(.*?)</script>', html or "", re.S | re.I):
        try:
            vaga = _jobposting(json.loads(bloco.strip()))
        except (ValueError, TypeError):
            continue
        if vaga:
            org = vaga.get("hiringOrganization")
            empresa = org.get("name", "") if isinstance(org, dict) else (org or "")
            extras = []
            if vaga.get("employmentType"):
                tipo = vaga["employmentType"]
                extras.append("Tipo: " + (", ".join(tipo) if isinstance(tipo, list) else str(tipo)))
            descricao = html_para_texto(unescape(str(vaga.get("description") or "")))
            return {
                "titulo": unescape(str(vaga.get("title") or "")).strip(),
                "empresa": unescape(str(empresa)).strip(),
                "local": _local_jsonld(vaga),
                "descricao": "\n".join(extras + [descricao]).strip(),
            }

    titulo_tag = re.search(r"<title[^>]*>(.*?)</title>", html or "", re.S | re.I)
    titulo = _meta(html, "og:title") or (unescape(titulo_tag.group(1)).strip() if titulo_tag else "")
    empresa = _meta(html, "og:site_name")
    # "Product Designer | MedCof" ou "Product Designer - MedCof": separa os dois.
    partes = re.split(r"\s+[|–—-]\s+", titulo)
    if len(partes) >= 2:
        titulo, empresa = partes[0], empresa or partes[-1]
    titulo = _melhor_titulo(html, url, empresa) or titulo
    corpo = re.search(r"<body[^>]*>(.*)</body>", html or "", re.S | re.I)
    texto = html_para_texto(corpo.group(1) if corpo else html or "")
    return {
        "titulo": titulo.strip(),
        "empresa": empresa.strip(),
        "local": "",
        "descricao": texto or _meta(html, "og:description") or _meta(html, "description"),
    }


def formatar_descricao(dados: dict) -> str:
    linhas = []
    if dados.get("local"):
        linhas.append(f"Local: {dados['local']}")
    if dados.get("descricao"):
        linhas.append(dados["descricao"])
    texto = "\n\n".join(linhas)
    return texto if len(texto) <= MAX_DESCRICAO else texto[: MAX_DESCRICAO - 1] + "…"


# ---------------------------------------------------------------- rede

def _baixar(url: str) -> str | None:
    try:
        resposta = requests.get(url, headers={"User-Agent": _UA, "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8"},
                                timeout=20)
    except requests.RequestException as e:
        logger.warning(f"Enriquecer: não abri a vaga ({type(e).__name__})")
        return None
    if not resposta.ok:
        logger.warning(f"Enriquecer: a página da vaga respondeu HTTP {resposta.status_code}")
        return None
    return resposta.text


def enriquecer(link: str | None) -> dict:
    """Dados da vaga a partir do link. Sempre devolve um dict (vazio se falhar)."""
    if not link:
        return {}
    try:
        if "lnkd.in/" in link:  # link curto do app do LinkedIn: descobre o destino
            resposta = requests.get(link, headers={"User-Agent": _UA}, timeout=20, allow_redirects=True)
            link = resposta.url or link
        id_linkedin = id_vaga_linkedin(link)
        if id_linkedin:
            html = _baixar(f"https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{id_linkedin}")
            dados = extrair_linkedin(html) if html else {}
        else:
            html = _baixar(link)
            dados = extrair_generico(html, link) if html else {}
    except Exception as e:  # nunca derruba o bot por causa de uma página estranha
        logger.warning(f"Enriquecer: falhou ao ler a vaga ({type(e).__name__})")
        return {}
    return {k: v for k, v in dados.items() if v}


if __name__ == "__main__":
    # Teste manual: python -m notifier.enriquecer <link> — mostra o que seria
    # gravado no Notion, sem gravar nada.
    import sys

    resultado = enriquecer(sys.argv[1] if len(sys.argv) > 1 else "")
    print(json.dumps({k: (v[:600] + "…" if isinstance(v, str) and len(v) > 600 else v)
                      for k, v in resultado.items()}, ensure_ascii=False, indent=2) or "{}")
