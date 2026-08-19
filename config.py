import os
from dotenv import load_dotenv

load_dotenv()

KEYWORDS_CARGO_FORTE = [
    "Product Designer",
    "Senior Product Designer",
    "Sr Product Designer",
    "Sr. Product Designer",
    "Lead Product Designer",
    "Staff Product Designer",
    "Product Design Lead",
    "Designer de Produto",
    "Designer de Produto Sênior",
    "Designer de Produto Pleno",
    "Design de Produto",
    "UX Designer",
    "Senior UX Designer",
    "UX Designer Sênior",
    "UX/UI Designer",
    "UI/UX Designer",
    "Experience Designer",
    "Designer de Experiência",
    "CX Designer",
    "Customer Experience Designer",
    "Designer de Experiência do Cliente",
    "Conversational Designer",
    "Designer Conversacional",
    "UX Conversacional",
    "Conversation Designer",
]

KEYWORDS_CARGO_AMBIGUO = []
QUALIFICADORES_DADOS = []
FERRAMENTAS_TITULO = []
QUALIFICADORES_CARGO = []

KEYWORDS = KEYWORDS_CARGO_FORTE + KEYWORDS_CARGO_AMBIGUO

TERMOS_CARGO_EXTRA = [
    "product design",
    "ux writing",
    "design conversacional",
]

TERMOS_CARGO = sorted(set(k.lower() for k in KEYWORDS) | set(TERMOS_CARGO_EXTRA))
TERMOS_FERRAMENTA = []
TERMOS_BUSCA = TERMOS_CARGO + TERMOS_FERRAMENTA

# Termos que ELIMINAM a vaga imediatamente
KEYWORDS_NEGATIVAS = [
    "developer", "engineer", "desenvolvedor", "desenvolvedora",
    "manager", "gerente", "coordinator", "coordenador", "coordenadora",
    "researcher", "pesquisador", "pesquisadora",
    "qa", "tester", "estag", "estagio", "estágio", "intern", "junior", "jr",
    "us only", "usa only", "uk only", "eu only", "europe only", "canada only",
    "us citizen", "green card", "must reside", "apenas eua", "somente eua"
]

TERMOS_POR_CICLO = 10

CIDADES = [
    "São Paulo",
    "Grande São Paulo",
    "Remoto",
]

CIDADES_EUROPA_IBERICA = [
    "Portugal", "Lisboa", "Porto", "Braga",
    "Espanha", "España", "Spain", "Madrid", "Barcelona", "Valencia",
]

ATIVAR_EIXO_IBERICO_BR = False
LOCATIONS_LINKEDIN = ["Brasil"]
LOCATIONS_LINKEDIN_REMOTO_APENAS = ["Estados Unidos", "Reino Unido", "Alemanha", "Portugal"]

# Para quem está no Brasil, aceita apenas vagas com escopo explícito para Brasil ou LATAM
MERCADOS_REMOTO_ACEITOS = ["Brasil", "LATAM"]

IDADE_MAXIMA_DIAS = 30
INTERVALO_MINUTOS = int(os.getenv("INTERVALO_MINUTOS", 180))
LIMIAR_DIGEST_IMEDIATO = 7
DIGEST_HORA_UTC = 0

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
DB_PATH = os.path.join(os.path.dirname(__file__), "data", "jobs.db")
