"""Testes da ida ao Notion (notifier/notion.py) e da leitura das mensagens
que ela manda ao bot (notifier/telegram.py) — só a parte sem rede."""

import pytest

from notifier.notion import (
    STATUS_ENTRADA,
    descricao_da_vaga_do_radar,
    extrair_link,
    montar_propriedades,
    titulo_da_mensagem,
)
from notifier.telegram import _texto_e_link_da_mensagem


@pytest.mark.parametrize("texto,esperado", [
    ("Vaga UX https://www.linkedin.com/posts/abc-123 bora", "https://www.linkedin.com/posts/abc-123"),
    ("Olha essa (https://lnkd.in/xyz).", "https://lnkd.in/xyz"),
    ("primeiro http://a.com/1 depois https://b.com/2", "http://a.com/1"),
    ("sem link nenhum", None),
    ("", None),
])
def test_extrair_link(texto, esperado):
    assert extrair_link(texto) == esperado


def test_titulo_pula_linha_so_com_link():
    texto = "https://lnkd.in/abc\n\nProduct Designer Sênior — Empresa X\nRemoto"
    assert titulo_da_mensagem(texto) == "Product Designer Sênior — Empresa X"


def test_titulo_vazio_tem_padrao():
    assert titulo_da_mensagem("https://lnkd.in/abc") == "Vaga enviada pelo Telegram"


def test_titulo_longo_e_cortado():
    titulo = titulo_da_mensagem("a" * 300)
    assert len(titulo) <= 120 and titulo.endswith("…")


def test_propriedades_usam_os_nomes_do_banco():
    props = montar_propriedades("UX Writer", "Empresa", "https://x.com/v", "texto")
    assert props["Application"]["title"][0]["text"]["content"] == "UX Writer"
    assert props["Company"]["rich_text"][0]["text"]["content"] == "Empresa"
    assert props["Job Link"] == {"url": "https://x.com/v"}
    assert props["Status"] == {"select": {"name": STATUS_ENTRADA}}
    assert "Descrição da vaga" in props


def test_propriedades_sem_campos_opcionais():
    props = montar_propriedades("Só título")
    assert set(props) == {"Application", "Status"}


def test_texto_longo_vira_varios_trechos_de_ate_2000():
    props = montar_propriedades("t", descricao="x" * 4500)
    trechos = props["Descrição da vaga"]["rich_text"]
    assert [len(t["text"]["content"]) for t in trechos] == [2000, 2000, 500]


def test_descricao_do_radar_ignora_campos_vazios():
    texto = descricao_da_vaga_do_radar({"titulo": "Product Designer", "empresa": "", "relevancia": 8})
    assert "Cargo: Product Designer" in texto
    assert "Empresa" not in texto
    assert "Relevância do radar: 8" in texto


def test_mensagem_com_link_no_texto():
    texto, link = _texto_e_link_da_mensagem({"text": "Vaga boa https://lnkd.in/abc"})
    assert texto == "Vaga boa https://lnkd.in/abc" and link == "https://lnkd.in/abc"


def test_mensagem_com_link_escondido_em_palavra():
    mensagem = {"text": "Confira esta vaga", "entities": [{"type": "text_link", "url": "https://x.com/v"}]}
    assert _texto_e_link_da_mensagem(mensagem) == ("Confira esta vaga", "https://x.com/v")


def test_mensagem_com_legenda_de_foto():
    texto, link = _texto_e_link_da_mensagem({"caption": "Print da vaga https://a.com/b"})
    assert texto.startswith("Print da vaga") and link == "https://a.com/b"
