from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, DB_PATH, CIDADES_EUROPA_IBERICA, IDADE_MAXIMA_DIAS

KEYWORDS_INTL = [
    "Product Designer",
    "Senior Product Designer",
    "Sr Product Designer",
    "Lead Product Designer",
    "Staff Product Designer",
    "Product Design Lead",
    "UX Designer",
    "Senior UX Designer",
    "UX/UI Designer",
    "UI/UX Designer",
    "Experience Designer",
    "CX Designer",
    "Customer Experience Designer",
    "Conversational Designer",
    "Conversation Designer",
    "Designer de Produto",
    "Designer de Produto Sênior",
]

TERMOS_BUSCA_INTL = [
    "product designer remote",
    "senior product designer remote",
    "product designer remote brazil",
    "product designer remote latam",
    "product designer portuguese speaker",
    "bilingual product designer portuguese",
    "ux designer remote",
    "senior ux designer remote",
    "conversational designer remote",
    "cx designer remote",
]

# Removido "english" genérico para barrar vagas locais dos EUA/Europa sem escopo declarado
IDIOMAS_EXIGIDOS_INTL = [
    "portuguese",
    "português",
    "portugues",
    "latam",
    "latin america",
    "america latina",
    "lusofono",
    "lusófono",
    "worldwide",
    "anywhere",
    "global",
]

# Exclusão estrita de restrições geográficas internacionais e cargos indesejados
KEYWORDS_NEGATIVAS_INTL = [
    "developer", "engineer", "software",
    "manager", "head of", "director",
    "researcher", "qa", "tester", "intern", "junior", "jr",
    "us only", "usa only", "uk only", "eu only", "europe only", "canada only",
    "us citizen", "green card", "must reside", "work permit required",
    "sponsorship not available", "us timezone", "est timezone", "pst timezone"
]

TERMOS_POR_CICLO_INTL = 10

LOCATIONS_INTL = [
    "United States",
    "United Kingdom",
    "Germany",
    "Netherlands",
    "Ireland",
]

CIDADES_INTL = ["Remote", "Remoto"]

# Aceita apenas vagas que declararem abertamente escopo para LATAM, Brasil ou Global
MERCADOS_REMOTO_ACEITOS_INTL = [
    "LATAM",
    "Brasil",
    "Worldwide",
    "Global",
    "Anywhere",
]

ATIVAR_EIXO_IBERICO = False

DOMINIOS_INDEED_INTL = {
    "Estados Unidos": "www.indeed.com",
    "Reino Unido": "uk.indeed.com",
    "Alemanha": "de.indeed.com",
    "Holanda": "nl.indeed.com",
    "Irlanda": "ie.indeed.com",
    "Portugal": "pt.indeed.com",
}
