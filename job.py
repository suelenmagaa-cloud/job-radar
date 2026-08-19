
from dataclasses import dataclass, field
from datetime import date
from urllib.parse import urlsplit, urlunsplit
import hashlib
import re
import unicodedata


def _normalizar(texto: str) -> str:
    sem_acento = unicodedata.normalize("NFKD", texto.lower())
    return "".join(c for c in sem_acento if not unicodedata.combining(c))


def _contem_termo(termo: str, texto: str, aceitar_plural: bool = False) -> bool:
    sufixo = "s?" if aceitar_plural else ""
    return re.search(rf"(?<!\w){re.escape(termo)}{sufixo}(?!\w)", texto) is not None


TERMOS_REMOTO = [
    "remot", "home office", "work from home", "trabalhe de casa",
    "teletrabalho", "teletrabajo", "trabajo a distancia", "desde casa", "anywhere",
]


def _e_remoto(texto: str) -> bool:
    return any(termo in texto for termo in TERMOS_REMOTO)


_TERMOS_TITULO_HIBRIDO = ["hybrid", "hibrido"]
_TERMOS_TITULO_PRESENCIAL = ["on-site", "onsite", "on site", "presencial"]


def _modalidade_pelo_titulo(titulo: str, local: str = "") -> str | None:
    texto_norm = _normalizar(f"{titulo} {local}")
    if any(termo in texto_norm for termo in _TERMOS_TITULO_HIBRIDO):
        return "Híbrido"
    if any(termo in texto_norm for termo in _TERMOS_TITULO_PRESENCIAL):
        return "Presencial"
    return None


_MERCADOS_REMOTO = {
    "us": "Estados Unidos", "usa": "Estados Unidos", "united states": "Estados Unidos", "estados unidos": "Estados Unidos", "eua": "Estados Unidos",
    "uk": "Reino Unido", "united kingdom": "Reino Unido", "reino unido": "Reino Unido",
    "india": "Índia", "brazil": "Brasil", "brasil": "Brasil", "portugal": "Portugal",
    "spain": "Espanha", "espanha": "Espanha", "espana": "Espanha",
    "mexico": "México", "colombia": "Colômbia", "argentina": "Argentina", "chile": "Chile", "canada": "Canadá",
    "germany": "Alemanha", "alemanha": "Alemanha", "latam": "LATAM", "latin america": "LATAM", "america latina": "LATAM",
    "europe": "Europa", "europa": "Europa", "emea": "EMEA",
}

_CIDADES_MERCADO = {
    "lisboa": "Portugal", "lisbon": "Portugal", "porto": "Portugal",
    "madrid": "Espanha", "barcelona": "Espanha", "valencia": "Espanha",
}

_MERCADOS_SEM_RESTRICAO = {"anywhere", "worldwide", "global"}
_PALAVRAS_IGNORAR_ESCOPO = {"only", "based", "timezone", "timezones", "time", "zone", "zones", "somente", "apenas", "greater", "metropolitan", "metropolitana", "area", "provincia"}
_PALAVRAS_REGIAO_BR = {"cidade", "cidades", "regiao", "distrito", "condado"}
_PADRAO_ESCOPO_SEPARADOR = re.compile(r"remot[eoa]\w*\s*[–—\-,(:]+\s*")
_PLACEHOLDER_LOCAL_AUSENTE = "nao informado"
_PADRAO_VOCABULARIO_MODALIDADE = re.compile("|".join(r"remot\w*" if termo == "remot" else re.escape(termo) for termo in TERMOS_REMOTO))


def _remover_ruido_escopo(texto: str) -> str:
    texto = _PADRAO_VOCABULARIO_MODALIDADE.sub(" ", texto)
    texto = texto.replace(_PLACEHOLDER_LOCAL_AUSENTE, " ")
    texto = texto.replace("(", " ").replace(")", " ")
    return re.sub(r"\s+", " ", texto).strip()


_SIGLAS_ESTADOS_EUA = {"al", "ak", "az", "ar", "ca", "co", "ct", "de", "fl", "ga", "hi", "id", "il", "in", "ia", "ks", "ky", "la", "me", "md", "ma", "mi", "mn", "ms", "mo", "mt", "ne", "nv", "nh", "nj", "nm", "ny", "nc", "nd", "oh", "ok", "or", "pa", "ri", "sc", "sd", "tn", "tx", "ut", "vt", "va", "wa", "wv", "wi", "wy", "dc"}
_SIGLAS_UF_BRASIL = {"ac", "al", "ap", "am", "ba", "ce", "df", "es", "go", "ma", "mt", "ms", "mg", "pa", "pb", "pr", "pe", "pi", "rj", "rn", "rs", "ro", "rr", "sc", "sp", "se", "to"}
_SIGLAS_UF_AMBIGUAS = {"al", "ma", "mt", "ms", "pa", "sc"}
_CAPITAIS_BRASIL = {"rio branco", "maceio", "macapa", "manaus", "salvador", "fortaleza", "brasilia", "vitoria", "goiania", "sao luis", "cuiaba", "campo grande", "belo horizonte", "belem", "joao pessoa", "curitiba", "recife", "teresina", "rio de janeiro", "natal", "porto alegre", "porto velho", "boa vista", "florianopolis", "sao paulo", "aracaju", "palmas"}


def _mercados_correspondentes(candidato: str) -> set[str]:
    if not candidato or candidato in _MERCADOS_SEM_RESTRICAO:
        return set()
    encontrados = {nome for chave, nome in _MERCADOS_REMOTO.items() if re.search(rf"\b{re.escape(chave)}\b", candidato)}
    if encontrados:
        return encontrados
    return {candidato}


def extrair_escopo_remoto(texto_local: str, modalidade: str = "") -> set[str]:
    texto_norm = _normalizar(texto_local).replace(".", "")
    modalidade_norm = _normalizar(modalidade)
    m = _PADRAO_ESCOPO_SEPARADOR.search(texto_norm)
    if m:
        resto = texto_norm[m.end():]
        resto = re.split(r"[)\n]", resto)[0]
    elif modalidade_norm in ("remoto", "remota"):
        resto = _remover_ruido_escopo(texto_norm)
        if not resto:
            return set()
    else:
        return set()

    segmentos = [s.strip(" .") for s in resto.split(",")]
    cidade = segmentos[0] if segmentos else ""
    for seg in segmentos[1:]:
        if seg in _SIGLAS_UF_BRASIL:
            if seg not in _SIGLAS_UF_AMBIGUAS or cidade in _CAPITAIS_BRASIL:
                return {"Brasil"}
        if seg in _SIGLAS_ESTADOS_EUA:
            return {"Estados Unidos"}

    palavras = [p for p in resto.replace(",", " ").split() if p not in _PALAVRAS_IGNORAR_ESCOPO and not p.isdigit()]
    if len(set(palavras)) == 1:
        palavras = palavras[:1]

    candidato = " ".join(palavras).strip()
    if not candidato:
        return set()

    if any(p in _PALAVRAS_REGIAO_BR for p in candidato.split()):
        return set()

    if candidato in _CAPITAIS_BRASIL:
        return {"Brasil"}
    if candidato in _CIDADES_MERCADO:
        return {_CIDADES_MERCADO[candidato]}

    return _mercados_correspondentes(candidato)


_PADRAO_DATA_ABSOLUTA = re.compile(r"publicad[ao]\s+(?:em|há)?\s*:?\s*(\d{1,2}\s+de\s+\w+(?:\s+de\s+\d{2,4})?|\d{1,2}/\d{1,2}(?:/\d{2,4})?)", re.IGNORECASE)
_PADRAO_DATA_RELATIVA = re.compile(r"há\s+\d+\s+(?:dias?|semanas?|m[êe]s(?:es)?|anos?)", re.IGNORECASE)
_PADRAO_HOJE_ONTEM = re.compile(r"\b(hoje|ontem)\b", re.IGNORECASE)


def extrair_data_publicacao(texto_card: str) -> str:
    for padrao in (_PADRAO_DATA_ABSOLUTA, _PADRAO_DATA_RELATIVA, _PADRAO_HOJE_ONTEM):
        m = padrao.search(texto_card)
        if m:
            return m.group(0).strip()
    return ""


_PADRAO_IDADE_RELATIVA = re.compile(r"ha\s+(\d+)\s+(dias?|semanas?|meses?|anos?)")
_PADRAO_IDADE_ABSOLUTA = re.compile(r"(\d{1,2})/(\d{1,2})(?:/(\d{2,4}))?")


def idade_em_dias(publicado_em: str, hoje: date | None = None) -> int | None:
    if not publicado_em:
        return None
    hoje = hoje or date.today()
    texto = _normalizar(publicado_em)

    if "hoje" in texto:
        return 0
    if "ontem" in texto:
        return 1

    m = _PADRAO_IDADE_RELATIVA.search(texto)
    if m:
        qtd, unidade = int(m.group(1)), m.group(2)
        if unidade.startswith("dia"): return qtd
        if unidade.startswith("semana"): return qtd * 7
        if unidade.startswith("mes"): return qtd * 30
        return qtd * 365

    m = _PADRAO_IDADE_ABSOLUTA.search(texto)
    if m:
        dia, mes = int(m.group(1)), int(m.group(2))
        ano = int(m.group(3)) if m.group(3) else hoje.year
        if ano < 100: ano += 2000
        try:
            data_pub = date(ano, mes, dia)
        except ValueError:
            return None
        if data_pub > hoje:
            data_pub = data_pub.replace(year=ano - 1)
        return (hoje - data_pub).days

    return None


_NIVEIS_SENIORIDADE = [
    ("Estágio/Trainee", (r"estagi[ao]", r"estagio", r"trainee")),
    ("Júnior", (r"junior", r"jr\.?")),
    ("Pleno", (r"pleno", r"pl\.?")),
    ("Sênior", (r"senior", r"sr\.?", r"sênior")),
    ("Especialista", (r"especialista", r"specialist")),
    ("Liderança", (r"coordenador", r"coordenadora", r"gerente", r"manager", r"head")),
]


def _detectar_senioridade(titulo: str) -> str:
    titulo_norm = _normalizar(titulo)
    for nivel, padroes in _NIVEIS_SENIORIDADE:
        for padrao in padroes:
            if re.search(rf"(?<!\w){padrao}(?!\w)", titulo_norm):
                return nivel
    numeral = re.search(r"(?<!\w)(i{1,3}|iv)(?!\w)", titulo_norm)
    if numeral:
        return f"Nível {numeral.group(1).upper()}"
    return "Não especificado"


@dataclass
class RegrasFiltro:
    keywords_forte: list[str]
    keywords_ambiguo: list[str]
    qualificadores_dados: list[str]
    ferramentas_titulo: list[str]
    qualificadores_cargo: list[str]
    cidades: list[str]
    mercados_remoto_aceitos: list[str] | None = None
    idiomas_exigidos: list[str] | None = None
    idade_maxima_dias: int | None = None
    keywords_negativas: list[str] = field(default_factory=list)


@dataclass
class _Avaliacao:
    aprovada: bool
    bate_forte: bool
    bate_ambiguo: bool
    bate_ferramenta: bool
    bate_remoto: bool
    escopos: set[str]
    mercado_confirmado: bool
    idioma_bateu_titulo: bool
    bate_idade: bool


_PESO_CARGO_FORTE = 3
_PESO_CARGO_AMBIGUO = 2
_PESO_FERRAMENTA = 2
_PESO_SENIORIDADE_ALVO = 2
_PESO_SENIORIDADE_NEUTRA = 1
_PESO_SENIORIDADE_ABAIXO_DO_ALVO = -2
_PESO_MERCADO = 2
_PESO_MERCADO_NAO_CONFIRMADO = 1
_PESO_IDIOMA = 1

_NIVEIS_SENIORIDADE_ALVO = {"Sênior", "Especialista"}
_NIVEIS_SENIORIDADE_ABAIXO_DO_ALVO = {"Júnior", "Pleno"}


@dataclass
class Job:
    titulo: str
    empresa: str
    local: str
    link: str
    site: str
    publicado_em: str = ""
    modalidade: str = ""
    escopo_indefinido: bool = False
    relevancia: int = 0
    motivo: str = ""

    def __post_init__(self):
        modalidade_real = _modalidade_pelo_titulo(self.titulo, self.local)
        if modalidade_real and self.modalidade == "Remoto":
            self.modalidade = modalidade_real

    @property
    def id(self) -> str:
        partes = urlsplit(self.link)
        link_normalizado = urlunsplit((partes.scheme, partes.netloc, partes.path, "", ""))
        return hashlib.md5(link_normalizado.encode()).hexdigest()

    @property
    def chave_secundaria(self) -> str:
        return f"{_normalizar(self.empresa)}|{_normalizar(self.titulo)}"

    @property
    def senioridade(self) -> str:
        return _detectar_senioridade(self.titulo)

    @property
    def publicacao_antiga(self) -> bool:
        texto = _normalizar(self.publicado_em)
        return "mes" in texto or "ano" in texto

    @property
    def escopo_remoto(self) -> set[str]:
        if self.escopo_indefinido:
            return set()
        return extrair_escopo_remoto(self.local, self.modalidade)

    def combina_com(self, regras: RegrasFiltro) -> bool:
        return self._avaliar(regras).aprovada

    def _avaliar(self, regras: RegrasFiltro) -> _Avaliacao:
        titulo_norm = _normalizar(self.titulo)
        local_norm = _normalizar(self.local)
        modalidade_norm = _normalizar(self.modalidade)

        # Regra de corte por palavra negativa (blacklist)
        bate_negativa = any(
            _contem_termo(_normalizar(neg), titulo_norm) or _contem_termo(_normalizar(neg), local_norm)
            for neg in regras.keywords_negativas
        )
        if bate_negativa:
            return _Avaliacao(
                aprovada=False, bate_forte=False, bate_ambiguo=False, bate_ferramenta=False,
                bate_remoto=False, escopos=set(), mercado_confirmado=False,
                idioma_bateu_titulo=False, bate_idade=False
            )

        bate_forte = any(_contem_termo(_normalizar(k), titulo_norm) for k in regras.keywords_forte)
        bate_ambiguo = any(_normalizar(k) in titulo_norm for k in regras.keywords_ambiguo) and any(_contem_termo(_normalizar(q), titulo_norm, aceitar_plural=True) for q in regras.qualificadores_dados)
        bate_ferramenta = any(_normalizar(f) in titulo_norm for f in regras.ferramentas_titulo) and any(_contem_termo(_normalizar(q), titulo_norm, aceitar_plural=True) for q in regras.qualificadores_cargo)

        bate_keyword = bate_forte or bate_ambiguo or bate_ferramenta

        _FLAGS_REMOTO = ("remoto", "remota", "remote")
        quer_remoto = any(_normalizar(c) in _FLAGS_REMOTO for c in regras.cidades)
        bate_remoto = quer_remoto and modalidade_norm in ("remoto", "remota")

        escopos = self.escopo_remoto if bate_remoto else set()

        if bate_remoto and regras.mercados_remoto_aceitos is not None:
            if escopos:
                mercados_aceitos_norm = {_normalizar(m) for m in regras.mercados_remoto_aceitos}
                escopos_norm = {_normalizar(e) for e in escopos}
                if not (escopos_norm & mercados_aceitos_norm):
                    bate_remoto = False

        idioma_bateu_titulo = regras.idiomas_exigidos is not None and any(
            _contem_termo(_normalizar(i), titulo_norm) for i in regras.idiomas_exigidos
        )

        if bate_remoto and regras.idiomas_exigidos is not None and not escopos:
            if not idioma_bateu_titulo:
                bate_remoto = False

        bate_cidade = bate_remoto or any(
            _contem_termo(_normalizar(c), local_norm) for c in regras.cidades if _normalizar(c) not in _FLAGS_REMOTO
        )

        idade = idade_em_dias(self.publicado_em)
        bate_idade = (regras.idade_maxima_dias is None or idade is None or idade <= regras.idade_maxima_dias)

        return _Avaliacao(
            aprovada=bate_keyword and bate_cidade and bate_idade,
            bate_forte=bate_forte, bate_ambiguo=bate_ambiguo, bate_ferramenta=bate_ferramenta,
            bate_remoto=bate_remoto, escopos=escopos, mercado_confirmado=bate_remoto and bool(escopos),
            idioma_bateu_titulo=idioma_bateu_titulo, bate_idade=bate_idade,
        )

    def pontuar_relevancia(self, regras: RegrasFiltro) -> int:
        av = self._avaliar(regras)
        pontos_cargo = _PESO_CARGO_FORTE if av.bate_forte else (_PESO_CARGO_AMBIGUO if av.bate_ambiguo else 0)
        pontos_ferramenta = _PESO_FERRAMENTA if av.bate_ferramenta else 0

        nivel = self.senioridade
        if nivel in _NIVEIS_SENIORIDADE_ALVO:
            pontos_senioridade = _PESO_SENIORIDADE_ALVO
        elif nivel in _NIVEIS_SENIORIDADE_ABAIXO_DO_ALVO:
            pontos_senioridade = _PESO_SENIORIDADE_ABAIXO_DO_ALVO
        elif nivel == "Não especificado" or nivel.startswith("Nível "):
            pontos_senioridade = _PESO_SENIORIDADE_NEUTRA
        else:
            pontos_senioridade = 0

        pontos_mercado = _PESO_MERCADO if (not av.bate_remoto or av.mercado_confirmado) else _PESO_MERCADO_NAO_CONFIRMADO
        pontos_idioma = _PESO_IDIOMA if av.idioma_bateu_titulo else 0

        return pontos_cargo + pontos_ferramenta + pontos_senioridade + pontos_mercado + pontos_idioma

    def motivo_aprovacao(self, regras: RegrasFiltro) -> str:
        av = self._avaliar(regras)
        if av.bate_forte: motivo = "Cargo forte"
        elif av.bate_ambiguo: motivo = "Cargo ambíguo + qualificador"
        else: motivo = "Ferramenta + cargo"
        if av.bate_remoto and not av.escopos and av.idioma_bateu_titulo:
            motivo += " · idioma sem mercado"
        return motivo

    def escopo_rejeitado_por_mercado(self, regras: RegrasFiltro) -> set[str] | None:
        if regras.mercados_remoto_aceitos is None: return None
        modalidade_norm = _normalizar(self.modalidade)
        _FLAGS_REMOTO = ("remoto", "remota", "remote")
        quer_remoto = any(_normalizar(c) in _FLAGS_REMOTO for c in regras.cidades)
        if not (quer_remoto and modalidade_norm in ("remoto", "remota")): return None
        escopos = self.escopo_remoto
        if not escopos: return None
        mercados_aceitos_norm = {_normalizar(m) for m in regras.mercados_remoto_aceitos}
        escopos_norm = {_normalizar(e) for e in escopos}
        if escopos_norm & mercados_aceitos_norm: return None
        return escopos
