"""Configuração do JobRadar adaptada para vagas de UX / Product Design.

Base: core/config.py original (perfil Dados/BI). Os NOMES das constantes
foram mantidos de propósito — perfis.py, config_intl.py, os scrapers e os
testes importam por nome. Só os VALORES mudaram. Em especial,
QUALIFICADORES_DADOS continua com esse nome, mas agora guarda os
qualificadores de UX/produto (renomear exigiria mexer em 3+ arquivos).
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# Filtro de cargo (o filtro lê só o TÍTULO da vaga, casando palavra inteira)
# ---------------------------------------------------------------------------

# Cargo forte: título que, sozinho, já indica vaga de UX / produto / design
# conversacional. As variantes com barra ("UX/UI") estão listadas à parte
# porque "UX Designer" não casa dentro de "UX/UI Designer".
KEYWORDS_CARGO_FORTE = [
    # Product design
    "Product Designer",
    "Product Design",
    "Designer de Produto",
    "Design de Produto",
    # UX / UI
    "UX Designer",
    "UI Designer",
    "UX/UI Designer",
    "UI/UX Designer",
    "UX UI Designer",
    "Designer UX",
    "Designer UI",
    "Designer UX/UI",
    "Designer UI/UX",
    "Designer de UX",
    "Designer de UX/UI",
    "UX Design",
    # Experiência / interação / serviço
    "Designer de Experiência",
    "Experience Designer",
    "Interaction Designer",
    "Designer de Interação",
    "Service Designer",
    # Design conversacional (o diferencial)
    "Conversation Designer",
    "Conversational Designer",
    "Conversational UX",
    "Conversation Design",
    "Designer de Conversação",
    "Designer Conversacional",
    # Conteúdo
    "UX Writer",
    "UX Writing",
    "Content Designer",
    "UX Content Designer",
    # Pesquisa — remova este bloco se não quiser vaga de pesquisa
    "UX Researcher",
    "UX Research",
    "Pesquisador UX",
    "Pesquisador de UX",
    "Design Researcher",
]

# Cargo ambíguo: "Designer" existe em gráfico, moda, interiores, etc. Só
# conta se o título TAMBÉM tiver um qualificador abaixo (mesmo mecanismo do
# "Analyst" na versão original).
KEYWORDS_CARGO_AMBIGUO = [
    "Designer",
]

# Qualificadores que confirmam que o "Designer" é de produto digital.
# (Nome mantido por compatibilidade — ver docstring.)
QUALIFICADORES_DADOS = [
    "ux",
    "ui",
    "product",
    "produto",
    "experience",
    "experiência",
    "interaction",
    "interação",
    "conversational",
    "conversation",
    "conversacional",
    "chatbot",
    "design system",
    "design systems",
]

# Sem caminho "ferramenta + cargo" neste perfil: "Figma" no título puxaria
# designer gráfico. Listas vazias são aceitas pelo RegrasFiltro (o perfil
# internacional já as usa vazias).
FERRAMENTAS_TITULO = []
QUALIFICADORES_CARGO = []

KEYWORDS = KEYWORDS_CARGO_FORTE + KEYWORDS_CARGO_AMBIGUO

# ---------------------------------------------------------------------------
# Termos de busca (rede larga enviada a cada site)
# ---------------------------------------------------------------------------

# Rodam em TODO ciclo, fora do rodízio. Têm de estar em TERMOS_BUSCA — por
# isso entram na construção de TERMOS_CARGO logo abaixo.
TERMOS_PRIORITARIOS = [
    "product designer",
    "ux designer",
    "designer de produto",
    "conversation designer",
    "ux ui designer",
]

TERMOS_CARGO_EXTRA = [
    "ux ui designer",
]

# Derivado das keywords FORTES (e não das ambíguas): buscar "designer" puro
# traria todo tipo de design e gastaria o orçamento do ciclo. O filtro
# continua usando "Designer" + qualificador sobre o que a busca trouxer.
TERMOS_CARGO = sorted(
    {k.lower() for k in KEYWORDS_CARGO_FORTE}
    | set(TERMOS_CARGO_EXTRA)
    | set(TERMOS_PRIORITARIOS)
)

# Termos de ferramenta/prática: acham vaga com título atípico, mas só viram
# notificação se o título também bater uma keyword de cargo.
TERMOS_FERRAMENTA = [
    "figma",
    "design system",
]

TERMOS_BUSCA = TERMOS_CARGO + TERMOS_FERRAMENTA

# Tamanho do bloco de termos por ciclo (rodízio salvo no jobs.db).
TERMOS_POR_CICLO = 10

# ---------------------------------------------------------------------------
# Onde aceitar vaga
# ---------------------------------------------------------------------------

# Whitelist de cidades para vaga HÍBRIDA/PRESENCIAL, mais "Remoto" (a porta
# de entrada da regra de modalidade remota — ver _FLAGS_REMOTO em job.py).
#
# ATENÇÃO: o filtro casa o NOME da cidade no texto do local. LinkedIn
# escreve "Campinas, São Paulo, Brazil" — o estado "São Paulo" pode fazer
# vaga de outra cidade do estado passar como se fosse da capital. Se
# aparecer, o conserto é uma entrada em _UF_DA_CIDADE (job.py), como foi
# feito com Fortaleza.
CIDADES = [
    "Remoto",
    "São Paulo",
]

# Mantida porque config_intl.py e perfis.py importam. Eixo desligado.
CIDADES_EUROPA_IBERICA = [
    "Portugal",
    "Lisboa",
    "Porto",
    "Braga",
    "Espanha",
    "España",
    "Spain",
    "Madrid",
    "Barcelona",
    "Valencia",
]
ATIVAR_EIXO_IBERICO_BR = False

# LinkedIn: o endpoint de visitante NÃO resolve "Brasil" e devolve vagas dos
# EUA sem dar erro — tem de ser "Brazil" (medido na versão original).
LOCATIONS_LINKEDIN = ["Brazil"]

# Busca só-remota em outros países: vazio por enquanto. A versão original
# buscava mercados de língua espanhola; para UX, mercado internacional (em
# inglês) é um perfil à parte, ainda por definir.
LOCATIONS_LINKEDIN_REMOTO_APENAS = []

# Busca por cidade no LinkedIn, derivada de CIDADES (sem "Remoto").
LOCATIONS_LINKEDIN_CIDADES_PRESENCIAL = [c for c in CIDADES if c != "Remoto"]

# Mercados aceitos quando a vaga remota DECLARA um escopo geográfico
# ("Remote — US only" é rejeitada; remoto sem escopo declarado passa).
MERCADOS_REMOTO_ACEITOS = ["Brasil", "LATAM"]

# ---------------------------------------------------------------------------
# Ciclo, digest e infraestrutura
# ---------------------------------------------------------------------------

INTERVALO_MINUTOS = int(os.getenv("INTERVALO_MINUTOS", 180))

# Nota mínima (Job.pontuar_relevancia) para notificar na hora; abaixo disso
# a vaga espera o digest diário. A versão original usava 4, calibrado contra
# o histórico de Dados/BI dela. Aqui volta para 7 (o padrão anterior) porque
# ainda não há histórico de UX para medir — e o score pode estar calibrado
# para Dados. Reavalie depois de uma semana de dados reais.
LIMIAR_DIGEST_IMEDIATO = 7

# Hora UTC a partir da qual o digest diário pode sair (09 UTC = 06h em SP).
DIGEST_HORA_UTC = 9

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

# Caminho ancorado na RAIZ do projeto (não na pasta deste arquivo): o banco
# já se perdeu uma vez quando config.py mudou de pasta. JOBRADAR_DB_PATH
# aponta um banco descartável para testes.
_RAIZ_PROJETO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.getenv("JOBRADAR_DB_PATH") or os.path.join(_RAIZ_PROJETO, "data", "jobs.db")
