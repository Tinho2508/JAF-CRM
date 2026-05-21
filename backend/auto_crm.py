"""
Auto-CRM: cria/atualiza registros no CRM baseado na triagem do Gemini.

Cada funcao retorna uma lista de acoes realizadas, ex.:
    [{"tabela": "leads", "acao": "criado", "id": "...", "nome": "Joao", "resumo": "Lead criado via WhatsApp"}]
"""

import logging
import re
from datetime import datetime

from supabase_client import (
    criar_cliente, criar_lead, criar_sinistro, criar_tarefa,
    find_cliente_by_telefone, find_cliente, find_apolice,
    find_lead_by_telefone,
    get_table, atualizar_lead_para_proposta,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Detection helpers
# ---------------------------------------------------------------------------

def _extrair_numero_apolice(mensagem: str) -> str | None:
    """Tenta extrair numero de apolice da mensagem (AP-123, 123456, etc)."""
    patterns = [
        r"(?:ap[oó]lice|apolice|ap)\s*[:\s]*([A-Z0-9\-]{4,20})",
        r"(?:n[uú]mero|nr[oô]?|n\.?)\s*(?:da\s*)?ap[oó]lice\s*[:\s]*([A-Z0-9\-]{4,20})",
        r"\b(AP[-]?\d{3,10})\b",
    ]
    for p in patterns:
        m = re.search(p, mensagem, re.IGNORECASE)
        if m:
            return m.group(1).strip()
    return None

def _extrair_valor(mensagem: str) -> float | None:
    m = re.search(r"(?:R\$|r\$)?\s*([\d\.,]+)", mensagem)
    if m:
        try:
            v = m.group(1).replace(".", "").replace(",", ".")
            return float(v)
        except ValueError:
            pass
    return None

# ---------------------------------------------------------------------------
# Intent handlers
# ---------------------------------------------------------------------------

def handle_lead_novo(triagem: dict, mensagem: str, telefone: str, nome_msg: str | None) -> list[dict]:
    """Lead novo → criar lead + opcionalmente cliente."""
    acoes = []
    nome = triagem.get("nome_cliente") or nome_msg or f"Lead {telefone[-8:]}"
    interesse = mensagem[:100]

    lead = criar_lead(telefone, nome, interesse, mensagem)
    if lead:
        acoes.append({
            "tabela": "leads",
            "acao": "criado",
            "id": lead.get("id"),
            "nome": nome,
            "resumo": f"Lead criado: {nome} ({interesse})",
        })

    cliente = find_cliente(nome) or find_cliente_by_telefone(telefone)
    if not cliente:
        cli = criar_cliente(telefone, nome, mensagem)
        if cli:
            acoes.append({
                "tabela": "clientes",
                "acao": "criado",
                "id": cli.get("id"),
                "nome": nome,
                "resumo": f"Cliente criado: {nome}",
            })
    return acoes


def handle_sinistro(triagem: dict, mensagem: str, telefone: str, nome_msg: str | None) -> list[dict]:
    """Sinistro → criar sinistro + garantir cliente."""
    acoes = []
    nome = triagem.get("nome_cliente") or nome_msg or f"Cliente {telefone[-8:]}"

    tipo = _extrair_tipo_sinistro(mensagem)

    sinistro = criar_sinistro(nome, telefone, tipo, mensagem)
    if sinistro:
        acoes.append({
            "tabela": "sinistros",
            "acao": "criado",
            "id": sinistro.get("id"),
            "nome": nome,
            "resumo": f"Sinistro registrado: {tipo}",
        })

    cliente = find_cliente(nome) or find_cliente_by_telefone(telefone)
    if not cliente:
        cli = criar_cliente(telefone, nome, mensagem)
        if cli:
            acoes.append({
                "tabela": "clientes",
                "acao": "criado",
                "id": cli.get("id"),
                "nome": nome,
                "resumo": f"Cliente criado: {nome}",
            })

    return acoes


def handle_cobranca(triagem: dict, mensagem: str, telefone: str, nome_msg: str | None) -> list[dict]:
    """Cobranca → criar tarefa na agenda."""
    acoes = []
    nome = triagem.get("nome_cliente") or nome_msg or f"Cliente {telefone[-8:]}"
    descricao = f"Cobranca - {triagem.get('resumo') or mensagem[:200]}"
    tarefa = criar_tarefa(nome, telefone, "Cobranca", descricao)
    if tarefa:
        acoes.append({
            "tabela": "agenda",
            "acao": "criado",
            "id": tarefa.get("id"),
            "nome": nome,
            "resumo": "Tarefa de cobranca criada",
        })
    return acoes


def handle_renovacao(triagem: dict, mensagem: str, telefone: str, nome_msg: str | None) -> list[dict]:
    """Renovacao → criar tarefa na agenda + atualizar lead."""
    acoes = []
    nome = triagem.get("nome_cliente") or nome_msg or f"Cliente {telefone[-8:]}"

    apolice = find_apolice(nome)
    num_apolice = _extrair_numero_apolice(mensagem)
    if not apolice and num_apolice:
        apolice = find_apolice(nome, num_apolice)
    if not apolice:
        apolice = find_apolice(nome)

    descricao = f"Renovacao - {triagem.get('resumo') or mensagem[:200]}"
    if apolice:
        descricao += f" | Apolice: {apolice.get('numero_apolice', '?')}"

    tarefa = criar_tarefa(nome, telefone, "Renovacao", descricao)
    if tarefa:
        acoes.append({
            "tabela": "agenda",
            "acao": "criado",
            "id": tarefa.get("id"),
            "nome": nome,
            "resumo": f"Tarefa de renovacao criada{' para apolice ' + (apolice.get('numero_apolice','') if apolice else '')}",
        })

    cliente = find_cliente(nome) or find_cliente_by_telefone(telefone)
    if not cliente:
        cli = criar_cliente(telefone, nome, mensagem)
        if cli:
            acoes.append({
                "tabela": "clientes",
                "acao": "criado",
                "id": cli.get("id"),
                "nome": nome,
                "resumo": f"Cliente criado: {nome}",
            })

    return acoes


def handle_proposta(triagem: dict, mensagem: str, telefone: str, nome_msg: str | None) -> list[dict]:
    """Proposta → atualizar lead para 'Proposta Enviada' + criar tarefa."""
    acoes = []
    nome = triagem.get("nome_cliente") or nome_msg or f"Cliente {telefone[-8:]}"

    lead = atualizar_lead_para_proposta(nome, telefone)
    if lead:
        acoes.append({
            "tabela": "leads",
            "acao": "atualizado",
            "id": lead.get("id"),
            "nome": nome,
            "resumo": "Lead atualizado para Proposta Enviada",
        })

    tarefa = criar_tarefa(nome, telefone, "Ligacao", f"Acompanhar proposta - {triagem.get('resumo') or mensagem[:200]}")
    if tarefa:
        acoes.append({
            "tabela": "agenda",
            "acao": "criado",
            "id": tarefa.get("id"),
            "nome": nome,
            "resumo": "Tarefa de acompanhamento criada",
        })

    return acoes


def handle_informacao(triagem: dict, mensagem: str, telefone: str, nome_msg: str | None) -> list[dict]:
    """Informacao → criar lead simples se nao existir."""
    acoes = []
    nome = triagem.get("nome_cliente") or nome_msg or f"Lead {telefone[-8:]}"

    if not find_lead_by_telefone(telefone):
        interesse = mensagem[:100]
        lead = criar_lead(telefone, nome, interesse, mensagem)
        if lead:
            acoes.append({
                "tabela": "leads",
                "acao": "criado",
                "id": lead.get("id"),
                "nome": nome,
                "resumo": f"Lead informacional criado: {interesse}",
            })
    return acoes


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

INTENT_MAP = {
    "lead_novo": handle_lead_novo,
    "sinistro": handle_sinistro,
    "cobranca": handle_cobranca,
    "renovacao": handle_renovacao,
    "proposta": handle_proposta,
    "informacao": handle_informacao,
}

def _extrair_tipo_sinistro(msg: str) -> str:
    msg_low = msg.lower()
    tipos = {
        "colisao": ["colisao", "batida", "bati", "acidente"],
        "Roubo/Furto": ["roubo", "furto", "roubaram", "furtaram"],
        "Incendio": ["incendio", "fogo", "queimou"],
        "Alagamento": ["alagamento", "enchente", "inundacao"],
        "Danos a Terceiros": ["terceiro", "terceiros"],
        "Vidros": ["vidro", "para-brisa", "parabrisa"],
    }
    for tipo, keywords in tipos.items():
        for kw in keywords:
            if kw in msg_low:
                return tipo
    return "Outros"

# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def processar_mensagem(triagem: dict, mensagem: str, telefone: str, nome_msg: str | None = None) -> list[dict]:
    """
    Processa a mensagem apos triagem do Gemini e executa acoes no CRM.
    Retorna lista de acoes realizadas.
    """
    intent = triagem.get("intent", "outro")
    handler = INTENT_MAP.get(intent)
    if not handler:
        logger.info(f"Nenhum handler para intent: {intent}")
        return []

    try:
        acoes = handler(triagem, mensagem, telefone, nome_msg)
        logger.info(f"Auto-CRM: {len(acoes)} acao(oes) para intent={intent}")
        return acoes
    except Exception as e:
        logger.exception(f"Erro no auto-crm para intent={intent}: {e}")
        return []
