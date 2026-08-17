# Config do programa internacional (busca vaga 100% remota fora do
# Brasil) — ADAPTADO para Product Design/UX/CX, escopo EUA + Europa +
# LATAM (rótulo genérico) em inglês/português, sem espanhol.
#
# Credenciais do Telegram e caminho do banco reaproveitados de
# config.py — mesmo esquema do projeto original.
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, DB_PATH, CIDADES_EUROPA_IBERICA  # noqa: F401

# Cargo em inglês e português — vaga internacional pode vir anunciada
# nos dois, dependendo de quem contratou. Nada em espanhol de
# propósito (decisão sua).
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

# Termos de busca: cargo + sinal de idioma (português/bilíngue) ou de
# mercado (LATAM, remote Europe/USA). Nada com "spanish"/"español" —
# removido de propósito nesta adaptação.
TERMOS_BUSCA_INTL = [
    "product designer remote",
    "senior product designer remote",
    "product designer remote brazil",
    "product designer remote latam",
    "product designer portuguese speaker",
    "product designer portuguese speaking",
    "bilingual product designer portuguese",
    "ux designer remote",
    "senior ux designer remote",
    "remote product designer europe",
    "remote product designer usa",
    "conversational designer remote",
    "cx designer remote",
    "customer experience designer remote",
    # Termos "soltos" (sem idioma/mercado combinado na frase) — seguros
    # aqui porque toda busca já roda escopada por país aceito via
    # LOCATIONS_INTL (nunca é busca global sem filtro nenhum).
    "product designer",
    "senior product designer",
    "ux designer",
]

# Usado só quando a vaga é remota SEM mercado declarado no texto (ver
# RegrasFiltro.idiomas_exigidos / extrair_escopo_remoto em job.py) —
# quando o escopo já é um país aceito, esta lista nem entra em jogo.
# Sem entradas de espanhol de propósito.
IDIOMAS_EXIGIDOS_INTL = [
    "portuguese",
    "português",
    "portugues",
    "latam",
    "latin america",
    "america latina",
    "lusofono",
    "lusófono",
    "english",
]

TERMOS_POR_CICLO_INTL = 10

# Mercados pesquisados por rodada de busca (parâmetro location do
# LinkedIn / subdomínio do Indeed). Troquei os países hispanofalantes
# do projeto original (Mexico/Colombia/Argentina/Chile) por EUA +
# Europa, por decisão sua.
#
# NÃO TESTADO ao vivo contra o endpoint do LinkedIn (diferente de
# Spain/Portugal, que o projeto original já validou): "United
# States", "United Kingdom", "Germany", "Netherlands", "Ireland" são
# meu melhor palpite de nome de location aceito. Rode uma vez com
# --once e confira o log antes de deixar no cron — se algum não
# resolver, o scraper só loga 0 vagas pra aquele país, não quebra o
# resto.
LOCATIONS_INTL = [
    "United States",
    "United Kingdom",
    "Portugal",
    "Germany",
    "Netherlands",
    "Ireland",
]

# Whitelist de local aceito — mesmo raciocínio do projeto original:
# "Remote"/"Remoto" cobre a maioria dos cards.
CIDADES_INTL = ["Remote", "Remoto"]

# O que ACEITAR quando a vaga declara escopo geográfico no texto
# (custo zero — só comparação de string, cobre mais países do que os
# 6 buscados em LOCATIONS_INTL). Removi todo país de língua espanhola
# específico (México, Colômbia, Argentina, Chile, Peru, Uruguai,
# Paraguai, Bolívia, Equador, Venezuela, Costa Rica, Panamá,
# Guatemala, Honduras, El Salvador, Nicarágua, República Dominicana,
# Porto Rico, Cuba) do projeto original — se uma vaga declarar
# "Remote — Argentina only" ela agora é rejeitada, fiel ao "nada de
# espanhol".
#
# "LATAM" continua aceito como rótulo genérico (cobre "Remote —
# LATAM" anunciado em inglês, comum em vaga de multinacional, sem
# exigir espanhol no anúncio). Não inclui "Brasil" — o perfil BR
# (config.py/main.py) já cobre isso.
MERCADOS_REMOTO_ACEITOS_INTL = [
    "Estados Unidos",
    "Reino Unido",
    "Alemanha",
    "Portugal",
    "Europa",
    "LATAM",
]

# DESLIGADO — mesma decisão do eixo BR em config.py: só remoto de
# verdade entra no radar, nada de presencial/híbrido na Ibéria.
ATIVAR_EIXO_IBERICO = False

# Indeed usa subdomínio por país. es.indeed.com/mx.indeed.com/etc.
# (mercado hispanofalante) removidos por decisão sua. Adicionei os
# domínios EUA/Reino Unido/Alemanha/Holanda/Irlanda — o projeto
# original tinha removido de propósito o domínio dos EUA/Reino Unido
# porque o público-alvo daquela versão (Dados/BI) não falava inglês
# fluente; não é o seu caso (C1), então reincluí.
#
# Mesmo aviso do projeto original: Indeed tem proteção anti-bot que
# pode bloquear acesso automatizado, principalmente de IP de
# nuvem/datacenter (como o runner do GitHub Actions), mesmo
# funcionando em teste manual.
DOMINIOS_INDEED_INTL = {
    "Estados Unidos": "www.indeed.com",
    "Reino Unido": "uk.indeed.com",
    "Alemanha": "de.indeed.com",
    "Holanda": "nl.indeed.com",
    "Irlanda": "ie.indeed.com",
    "Portugal": "pt.indeed.com",
}
