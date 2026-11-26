"""Leitura da página da vaga (notifier/enriquecer.py), só a parte sem rede."""

import pytest

from notifier.enriquecer import (
    extrair_generico,
    extrair_linkedin,
    formatar_descricao,
    html_para_texto,
    id_vaga_linkedin,
)


@pytest.mark.parametrize("url,esperado", [
    ("https://www.linkedin.com/jobs/view/4490039635/?trk=eml-email_job_alert", "4490039635"),
    ("https://br.linkedin.com/jobs/view/product-designer-at-acme-4490039635", "4490039635"),
    ("https://www.linkedin.com/jobs/collections/recommended/?currentJobId=4123456789", "4123456789"),
    ("https://www.linkedin.com/posts/fulano_vaga-ux-activity-7123", None),
    ("https://vagas.medcof.tech/vagas/product-designer", None),
])
def test_id_vaga_linkedin(url, esperado):
    assert id_vaga_linkedin(url) == esperado


LINKEDIN = """
<section><h2 class="top-card-layout__title font-sans">Product Designer Sênior</h2>
<a class="topcard__org-name-link topcard__flavor--black-link" href="x">
  Acme Saúde </a>
<span class="topcard__flavor topcard__flavor--bullet"> São Paulo, SP (Remoto) </span>
<div class="show-more-less-html__markup relative">
<p>Sobre a vaga</p><ul><li>Figma</li><li>Pesquisa com usuários</li></ul></div></section>
"""


def test_extrair_linkedin():
    dados = extrair_linkedin(LINKEDIN)
    assert dados["titulo"] == "Product Designer Sênior"
    assert dados["empresa"] == "Acme Saúde"
    assert dados["local"] == "São Paulo, SP (Remoto)"
    assert "• Figma" in dados["descricao"] and "Sobre a vaga" in dados["descricao"]


JSONLD = """<html><head><script type="application/ld+json">
{"@context":"https://schema.org","@graph":[{"@type":"Organization","name":"X"},
{"@type":"JobPosting","title":"UX Writer","hiringOrganization":{"@type":"Organization","name":"Verity"},
"employmentType":"FULL_TIME","jobLocationType":"TELECOMMUTE",
"jobLocation":{"@type":"Place","address":{"addressLocality":"São Paulo","addressRegion":"SP","addressCountry":"BR"}},
"description":"&lt;p&gt;Escrever microcopy&lt;/p&gt;&lt;ul&gt;&lt;li&gt;Tom de voz&lt;/li&gt;&lt;/ul&gt;"}]}
</script></head><body>menu</body></html>"""


def test_extrair_jsonld_jobposting():
    dados = extrair_generico(JSONLD)
    assert dados["titulo"] == "UX Writer"
    assert dados["empresa"] == "Verity"
    assert dados["local"] == "São Paulo, SP, BR · Remoto"
    assert "Escrever microcopy" in dados["descricao"] and "• Tom de voz" in dados["descricao"]
    assert dados["descricao"].startswith("Tipo: FULL_TIME")


PAGINA_SIMPLES = """<html><head><title>Product Designer | MedCof</title>
<style>.x{}</style><script>var a=1;</script></head>
<body><nav>Início Vagas</nav><h1>Product Designer</h1><p>Remoto · PJ</p>
<h2>Requisitos</h2><ul><li>Design system</li></ul></body></html>"""


def test_extrair_pagina_sem_dados_estruturados():
    dados = extrair_generico(PAGINA_SIMPLES)
    assert dados["titulo"] == "Product Designer"
    assert dados["empresa"] == "MedCof"
    assert "Remoto · PJ" in dados["descricao"] and "• Design system" in dados["descricao"]
    assert "var a" not in dados["descricao"] and "Início Vagas" not in dados["descricao"]


def test_og_site_name_tem_prioridade_sobre_o_titulo():
    html = '<head><meta property="og:title" content="Designer - Vaga"><meta property="og:site_name" content="Empresa Real"></head><body>x</body>'
    assert extrair_generico(html)["empresa"] == "Empresa Real"


def test_html_estranho_nao_quebra():
    assert extrair_generico("<<<>>>")["titulo"] == ""
    assert html_para_texto("") == ""


def test_descricao_e_cortada():
    texto = formatar_descricao({"local": "SP", "descricao": "x" * 20000})
    assert len(texto) <= 8000 and texto.startswith("Local: SP")
