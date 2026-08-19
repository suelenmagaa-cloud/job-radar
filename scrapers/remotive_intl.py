import json
import urllib.request
from job import Job
from logger import get_logger
from scrapers.base import BaseScraper

logger = get_logger()


class RemotiveIntlScraper(BaseScraper):
    """Busca vagas remotas internacionais na API pública e gratuita da Remotive."""

    def __init__(self, termos_busca: list[str]):
        self.termos_busca = termos_busca

    def buscar_vagas(self) -> list[Job]:
        logger.info("[Remotive] Buscando vagas via API...")
        vagas: list[Job] = []
        url = "https://remotive.com/api/remote-jobs?category=design"

        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "Mozilla/5.0"}
            )
            with urllib.request.urlopen(req, timeout=15) as response:
                data = json.loads(response.read().decode("utf-8"))
                jobs_data = data.get("jobs", [])

                for item in jobs_data:
                    titulo = item.get("title", "")
                    empresa = item.get("company_name", "")
                    local_requerido = item.get("candidate_required_location", "") or "Worldwide"
                    link = item.get("url", "")
                    publicado_em = (item.get("publication_date") or "")[:10]

                    vagas.append(Job(
                        titulo=titulo,
                        empresa=empresa,
                        local=f"Remote ({local_requerido})",
                        link=link,
                        site="Remotive",
                        publicado_em=publicado_em,
                        modalidade="Remoto"
                    ))
        except Exception as e:
            logger.error(f"[Remotive] Erro ao buscar vagas na API: {e}")

        logger.info(f"[Remotive] {len(vagas)} vaga(s) encontrada(s) no total")
        return vagas