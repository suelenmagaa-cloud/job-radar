import os
from dotenv import load_dotenv

load_dotenv()

# ============================================================
# ADAPTADO para busca de Product Design / UX / CX Design
# (perfil: Suelen Magalhães — Senior Product Designer, São Paulo,
# remoto desde 2021, C1 inglês, sem espanhol).
#
# Diferença chave da versão original (Dados/BI): aqui os títulos-alvo
# já são específicos o bastante (compostos, tipo "Senior Product
# Designer") que não precisei do mecanismo de cargo ambíguo +
# qualificador — deixei os dois vazios de propósito, simples até
# medir se algum título está gerando ruído real.
# ============================================================

# Cargo forte: título que identifica diretamente vaga de Product
# Design / UX / CX Design, em português e inglês (mercado BR usa os
# dois nos anúncios, às vezes no mesmo card).
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

# Deixado vazio de propósito: nenhum título curto o bastante pra
# precisar de qualificador junto (ver nota no topo do arquivo). Se
# no futuro você quiser entrar com "Designer" sozinho (pega vaga de
# designer gráfico/visual junto — MUITO ruído) ou "UX" sozinho, é
# aqui que entraria, junto com QUALIFICADORES_DADOS abaixo.
KEYWORDS_CARGO_AMBIGUO = []
QUALIFICADORES_DADOS = []

# Idem: nenhuma ferramenta isolada (ex: "Figma") entrou como núcleo
# de título — o risco de falso positivo (vaga de dev/consultor Figma
# sem ser design) é alto e o retorno é baixo, já que quase toda vaga
# de Product Design real já cai em KEYWORDS_CARGO_FORTE.
FERRAMENTAS_TITULO = []
QUALIFICADORES_CARGO = []

KEYWORDS = KEYWORDS_CARGO_FORTE + KEYWORDS_CARGO_AMBIGUO

# Termos mais amplos que a keyword exata, mantidos pra dar rede mais
# larga na BUSCA (o filtro de título continua sendo só KEYWORDS).
TERMOS_CARGO_EXTRA = [
    "product design",
    "ux writing",
    "design conversacional",
]

TERMOS_CARGO = sorted(set(k.lower() for k in KEYWORDS) | set(TERMOS_CARGO_EXTRA))

# Sem termos de ferramenta isolada por ora (ver FERRAMENTAS_TITULO
# acima) — todo o filtro de cargo já cobre o que interessa.
TERMOS_FERRAMENTA = []

TERMOS_BUSCA = TERMOS_CARGO + TERMOS_FERRAMENTA

# Mesmo mecanismo de rodízio do projeto original — bloco de termos
# por ciclo, pra não rodar a lista inteira toda vez.
TERMOS_POR_CICLO = 10

# Base real: São Paulo. Trocado da whitelist de cidades do Nordeste
# (projeto original) — se algum dia você quiser vaga presencial em
# outra cidade, é só adicionar aqui.
CIDADES = [
    "São Paulo",
    "Grande São Paulo",
    "Remoto",
]

# Não usado enquanto ATIVAR_EIXO_IBERICO_BR = False (ver abaixo) —
# mantido definido pra religar fácil se um dia você quiser vaga
# presencial/híbrida em Portugal/Espanha entrando no radar.
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

# DESLIGADO por decisão sua: só remoto de verdade entra no radar,
# nada de presencial/híbrido na Ibéria (mesmo com o caso
# Claranet/Xtedder no histórico).
ATIVAR_EIXO_IBERICO_BR = False

# Mercado "casa": São Paulo/Brasil, modalidade completa.
LOCATIONS_LINKEDIN = ["Brasil"]

# Mercados adicionais buscados só em modalidade remota (f_WT=2).
# Removi os países de língua espanhola (Argentina/Chile/México/
# Colômbia) da BUSCA por decisão sua ("nada de espanhol") — o
# aceite de "LATAM" como rótulo genérico continua em
# MERCADOS_REMOTO_ACEITOS abaixo, pra não perder vaga "Remote —
# LATAM" anunciada em inglês/português sem exigir espanhol.
#
# NÃO TESTADO ao vivo (diferente de Argentina/Chile/México/Colômbia/
# Espanha/Portugal, que o projeto original já validou contra o
# endpoint do LinkedIn): "Estados Unidos", "Reino Unido" e "Alemanha"
# são meu melhor palpite de nome aceito pelo location= do LinkedIn.
# Vale rodar uma vez com --once e olhar o log antes de deixar no
# cron automático — se algum não resolver, o scraper só loga 0
# vagas pra ele, não quebra o resto.
LOCATIONS_LINKEDIN_REMOTO_APENAS = ["Estados Unidos", "Reino Unido", "Alemanha", "Portugal"]

# Mercado que a vaga remota precisa aceitar quando o texto DECLARA um
# escopo geográfico ("Remote — US only", "Remote — India"). Vaga
# remota sem escopo declarado (a maioria) continua batendo normal.
#
# "LATAM" fica como rótulo aceito (cobre "Remote — LATAM" em inglês,
# comum em vaga de multinacional, sem exigir espanhol no anúncio).
# Não incluí os países específicos de língua espanhola aqui de
# propósito — se uma vaga declarar "Remote — Argentina only" ela cai
# fora, o que é a leitura mais fiel do "nada de espanhol".
MERCADOS_REMOTO_ACEITOS = ["Brasil", "LATAM", "Portugal", "Estados Unidos", "Reino Unido", "Europa", "Alemanha"]

# Idade máxima aceita pra vaga (dias), medida a partir do texto de
# publicação do card ("Há 2 meses", "11/08"). Vaga sem data exposta pela
# fonte (ex: Gupy nunca mostra isso) continua passando normalmente — sem
# base pra medir idade, não tem como rejeitar. 30 dias é ponto de partida;
# ajuste aqui se quiser mais rígido (ex: 14) ou mais frouxo (ex: 60).
IDADE_MAXIMA_DIAS = 30

INTERVALO_MINUTOS = int(os.getenv("INTERVALO_MINUTOS", 180))

# Mesmo limiar do projeto original — vale reavaliar depois de rodar
# umas semanas com dado real do seu jobs.db (ver comentário longo na
# versão original do config.py sobre como esse número foi medido).
LIMIAR_DIGEST_IMEDIATO = 7

DIGEST_HORA_UTC = 0

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "jobs.db")
