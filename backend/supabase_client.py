import os
import re
import logging
from datetime import datetime, timezone
from supabase import create_client, Client

logger = logging.getLogger(__name__)

_supabase: Client | None = None

def get_supabase() -> Client:
    global _supabase
    if _supabase is None:
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_SERVICE_KEY") or os.environ.get("SUPABASE_ANON_KEY")
        if not url or not key:
            raise RuntimeError("SUPABASE_URL and SUPABASE_SERVICE_KEY (or SUPABASE_ANON_KEY) must be set")
        _supabase = create_client(url, key)
        logger.info(f"Supabase connected ({'service_role' if os.environ.get('SUPABASE_SERVICE_KEY') else 'anon'})")
    return _supabase

TABELAS = ["clientes", "apolices", "leads", "propostas", "producao", "sinistros", "agenda"]

def _next_id() -> str:
    return datetime.utcnow().strftime("%Y%m%d%H%M%S%f") + str(abs(hash(str(datetime.utcnow()))))[:6]

def _now_iso() -> str:
    return datetime.utcnow().isoformat()

def _today_str() -> str:
    return datetime.utcnow().strftime("%Y-%m-%d")

def _clean_phone(num: str) -> str:
    return re.sub(r"\D", "", num) if num else ""

# ---------------------------------------------------------------------------
# Generic helpers
# ---------------------------------------------------------------------------

def get_table(table: str, filters: dict = None) -> list[dict]:
    q = get_supabase().table(table).select("*")
    if filters:
        for k, v in filters.items():
            q = q.eq(k, v)
    res = q.execute()
    return res.data or []

def upsert_row(table: str, row: dict) -> dict:
    res = get_supabase().table(table).upsert(row, on_conflict="id").execute()
    return res.data[0] if res.data else row

def delete_rows(table: str, ids: list[str]):
    get_supabase().table(table).delete().in_("id", ids).execute()

# ---------------------------------------------------------------------------
# Find helpers
# ---------------------------------------------------------------------------

def find_cliente(nome: str) -> dict | None:
    rows = get_table("clientes", {"nome": nome})
    return rows[0] if rows else None

def find_cliente_by_telefone(telefone: str) -> dict | None:
    num = _clean_phone(telefone)
    rows = get_table("clientes")
    for c in rows:
        if _clean_phone(c.get("telefone")) == num or _clean_phone(c.get("whatsapp")) == num:
            return c
    return None

def find_lead_by_telefone(telefone: str) -> dict | None:
    num = _clean_phone(telefone)
    rows = get_table("leads")
    for l in rows:
        if _clean_phone(l.get("telefone")) == num or _clean_phone(l.get("whatsapp")) == num:
            return l
    return None

def find_apolice(cliente_nome: str, numero: str = None) -> dict | None:
    rows = get_table("apolices", {"nome_cliente": cliente_nome})
    if numero:
        for a in rows:
            if a.get("numero_apolice") == numero:
                return a
    return rows[0] if rows else None

# ---------------------------------------------------------------------------
# CRM creation helpers
# ---------------------------------------------------------------------------

def criar_cliente(telefone: str, nome: str = None, mensagem: str = None) -> dict | None:
    if not nome:
        nome = f"Lead WhatsApp {telefone[-8:]}"
    existing = find_cliente_by_telefone(telefone) or find_cliente(nome)
    if existing:
        return existing
    row = {
        "id": _next_id(),
        "nome": nome,
        "telefone": telefone,
        "whatsapp": telefone,
        "status": "Ativo",
        "observacoes": f"Auto-criado via WhatsApp: {(mensagem or '')[ :200]}",
        "criado_em": _now_iso(),
    }
    try:
        created = upsert_row("clientes", row)
        logger.info(f"Cliente criado: {nome} ({telefone})")
        return created
    except Exception as e:
        logger.error(f"Erro ao criar cliente: {e}")
        return None

def criar_lead(telefone: str, nome: str, interesse: str = None, mensagem: str = None) -> dict | None:
    existing = find_lead_by_telefone(telefone)
    if existing:
        logger.info(f"Lead ja existe: {existing.get('nome_cliente')}")
        return existing
    row = {
        "id": _next_id(),
        "nome_cliente": nome,
        "telefone": telefone,
        "whatsapp": telefone,
        "interesse": interesse or (mensagem or "")[:100],
        "origem": "WhatsApp",
        "status": "Novo",
        "observacoes": f"Mensagem: {(mensagem or '')[:300]}",
        "criado_em": _now_iso(),
    }
    try:
        created = upsert_row("leads", row)
        logger.info(f"Lead criado: {nome} - {interesse}")
        return created
    except Exception as e:
        logger.error(f"Erro ao criar lead: {e}")
        return None

def criar_sinistro(cliente_nome: str, telefone: str, tipo: str = None, mensagem: str = None) -> dict | None:
    row = {
        "id": _next_id(),
        "data": _today_str(),
        "cliente": cliente_nome,
        "tipo": tipo or "Outros",
        "status": "Registrado",
        "observacoes": f"Auto-criado via WhatsApp. Mensagem: {(mensagem or '')[:500]}",
        "criado_em": _now_iso(),
    }
    try:
        created = upsert_row("sinistros", row)
        logger.info(f"Sinistro criado para {cliente_nome}: {tipo}")
        return created
    except Exception as e:
        logger.error(f"Erro ao criar sinistro: {e}")
        return None

def criar_tarefa(cliente_nome: str, telefone: str, tipo: str, descricao: str, data: str = None) -> dict | None:
    row = {
        "id": _next_id(),
        "data": data or _today_str(),
        "cliente": cliente_nome,
        "telefone": telefone,
        "tipo": tipo,
        "descricao": descricao[:300],
        "status": "Agendado",
        "criado_em": _now_iso(),
    }
    try:
        created = upsert_row("agenda", row)
        logger.info(f"Tarefa criada: {tipo} para {cliente_nome}")
        return created
    except Exception as e:
        logger.error(f"Erro ao criar tarefa: {e}")
        return None

def atualizar_lead_para_proposta(nome_cliente: str, telefone: str, ramo: str = None) -> dict | None:
    lead = find_lead_by_telefone(telefone)
    if not lead:
        lead = find_lead_by_telefone(telefone) or find_lead_by_telefone(telefone)
    if lead:
        lead["status"] = "Proposta Enviada"
        if ramo:
            lead["interesse"] = ramo
        upsert_row("leads", lead)
        logger.info(f"Lead atualizado para Proposta Enviada: {nome_cliente}")
    return lead
