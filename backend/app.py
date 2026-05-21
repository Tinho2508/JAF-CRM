import os
import json
import logging
import time
from datetime import datetime

from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

from supabase_client import get_supabase, get_table, upsert_row, find_cliente, find_cliente_by_telefone
from gemini_client import triage_message, gerar_resposta
from wa_adapter import parse_webhook, build_response, get_provider
from auto_crm import processar_mensagem

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# ---------------------------------------------------------------------------
# Banco de dados - criar tabela de mensagens se não existir
# ---------------------------------------------------------------------------


def init_db():
    try:
        get_supabase().table("whatsapp_messages").select("id").limit(1).execute()
        logger.info("Tabela whatsapp_messages ja existe")
    except Exception:
        logger.warning("Tabela whatsapp_messages nao encontrada. Execute o SQL manualmente no Supabase SQL Editor:")
        logger.warning("https://supabase.com/dashboard/project/mtahebtububylnmauzsa/sql/new")
        logger.warning("Ou rode o arquivo backend/migration_whatsapp_messages.sql")

with app.app_context():
    init_db()

# ---------------------------------------------------------------------------
# Rate limiter simples (por telefone, 1 msg a cada 3s)
# ---------------------------------------------------------------------------

_rate_limit = {}

def _check_rate_limit(telefone: str) -> bool:
    now = time.time()
    last = _rate_limit.get(telefone, 0)
    if now - last < 3:
        return False
    _rate_limit[telefone] = now
    return True

# ---------------------------------------------------------------------------
# Webhook - receber mensagens do WhatsApp (provider-agnostic)
# ---------------------------------------------------------------------------

@app.route("/webhook/whatsapp", methods=["POST"])
def webhook_whatsapp():
    try:
        if request.form:
            raw = dict(request.form)
        else:
            raw = request.get_json(force=True, silent=True) or {}
        logger.info(f"Webhook recebido: {json.dumps(raw, ensure_ascii=False)[:500]}")

        parsed = parse_webhook(raw)
        if not parsed:
            return jsonify({"status": "ignored", "reason": "formato nao reconhecido"}), 200

        telefone = parsed["telefone"]
        mensagem = parsed["mensagem"]

        # Rate limit: max 1 msg por telefone a cada 3s
        if not _check_rate_limit(telefone):
            logger.info(f"Rate limit: ignorando msg repetida de {telefone}")
            return jsonify({"status": "ok", "rate_limited": True}), 200

        # Triagem com Gemini
        try:
            triagem = triage_message(telefone, mensagem)
        except Exception as e:
            logger.error(f"Erro no Gemini: {e}")
            triagem = {
                "intent": "outro",
                "nome_cliente": None,
                "telefone": telefone,
                "resumo": mensagem[:100],
                "urgencia": "baixa",
                "response_suggested": "Ola! Recebi sua mensagem e em breve retornarei o contato.",
            }

        # Buscar cliente no CRM pelo nome ou telefone
        cliente = None
        nome_cliente = triagem.get("nome_cliente")
        if nome_cliente:
            cliente = find_cliente(nome_cliente)
        if not cliente:
            cliente = find_cliente_by_telefone(telefone)

        # Gerar resposta sugerida
        try:
            response = gerar_resposta(
                triagem.get("intent", "outro"),
                nome_cliente or parsed.get("nome"),
                {"mensagem": mensagem, "telefone": telefone},
            )
        except Exception as e:
            logger.error(f"Erro ao gerar resposta: {e}")
            response = triagem.get("response_suggested", "Ola! Recebi sua mensagem.")

        # Auto-CRM: criar/atualizar registros baseado na intencao
        nome_para_crm = parsed.get("nome") or nome_cliente or (cliente.get("nome") if cliente else None)
        acoes = processar_mensagem(triagem, mensagem, telefone, nome_para_crm)

        # Salvar no Supabase
        msg_id = f"msg_{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}"
        row = {
            "id": msg_id,
            "provider": parsed["provider"],
            "telefone": telefone,
            "nome": nome_para_crm,
            "mensagem": mensagem,
            "tipo": parsed.get("tipo", "texto"),
            "midia_url": parsed.get("midia_url"),
            "intent": triagem.get("intent"),
            "urgencia": triagem.get("urgencia", "baixa"),
            "resumo": triagem.get("resumo", ""),
            "response_suggested": response,
            "cliente_id": cliente.get("id") if cliente else None,
            "acoes": acoes,
            "criado_em": datetime.utcnow().isoformat(),
        }
        try:
            upsert_row("whatsapp_messages", row)
        except Exception as e:
            logger.error(f"Erro ao salvar mensagem: {e}")

        return jsonify({
            "status": "ok",
            "message_id": msg_id,
            "intent": triagem.get("intent"),
            "urgencia": triagem.get("urgencia"),
            "response_suggested": response,
            "acoes": acoes,
        }), 200

    except Exception as e:
        logger.exception("Erro no webhook")
        return jsonify({"status": "error", "message": str(e)}), 500

# ---------------------------------------------------------------------------
# API - listar mensagens
# ---------------------------------------------------------------------------

@app.route("/api/messages", methods=["GET"])
def list_messages():
    limit = request.args.get("limit", 50, type=int)
    offset = request.args.get("offset", 0, type=int)
    provider = request.args.get("provider")
    intent = request.args.get("intent")
    urgencia = request.args.get("urgencia")

    try:
        q = get_supabase().table("whatsapp_messages").select("*").order("criado_em", desc=True)
        if provider:
            q = q.eq("provider", provider)
        if intent:
            q = q.eq("intent", intent)
        if urgencia:
            q = q.eq("urgencia", urgencia)
        q = q.range(offset, offset + limit - 1)
        res = q.execute()
        return jsonify({"data": res.data or [], "total": len(res.data or [])}), 200
    except Exception as e:
        logger.error(f"Erro ao listar mensagens: {e}")
        return jsonify({"data": [], "total": 0, "error": str(e)}), 200

# ---------------------------------------------------------------------------
# API - obter mensagem por ID
# ---------------------------------------------------------------------------

@app.route("/api/messages/<message_id>", methods=["GET"])
def get_message(message_id):
    res = get_supabase().table("whatsapp_messages").select("*").eq("id", message_id).execute()
    if res.data:
        return jsonify(res.data[0]), 200
    return jsonify({"error": "not found"}), 404

# ---------------------------------------------------------------------------
# API - marcar como lida
# ---------------------------------------------------------------------------

@app.route("/api/messages/<message_id>", methods=["DELETE"])
def delete_message(message_id):
    try:
        get_supabase().table("whatsapp_messages").delete().eq("id", message_id).execute()
        return jsonify({"status": "ok"}), 200
    except Exception as e:
        logger.error(f"Erro ao deletar mensagem {message_id}: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/messages", methods=["DELETE"])
def delete_all_messages():
    try:
        get_supabase().table("whatsapp_messages").delete().neq("id", "").execute()
        return jsonify({"status": "ok"}), 200
    except Exception as e:
        logger.error(f"Erro ao deletar mensagens: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/messages/<message_id>/read", methods=["POST"])
def mark_read(message_id):
    upsert_row("whatsapp_messages", {"id": message_id, "lido": True})
    return jsonify({"status": "ok"}), 200

# ---------------------------------------------------------------------------
# API - estatísticas de mensagens
# ---------------------------------------------------------------------------

@app.route("/api/messages/stats", methods=["GET"])
def message_stats():
    try:
        res = get_supabase().table("whatsapp_messages").select("*").execute()
        msgs = res.data or []
        stats = {
            "total": len(msgs),
            "nao_lidas": sum(1 for m in msgs if not m.get("lido")),
            "por_intent": {},
            "por_urgencia": {},
        }
        for m in msgs:
            i = m.get("intent", "outro")
            stats["por_intent"][i] = stats["por_intent"].get(i, 0) + 1
            u = m.get("urgencia", "baixa")
            stats["por_urgencia"][u] = stats["por_urgencia"].get(u, 0) + 1
        return jsonify(stats), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 200

# ---------------------------------------------------------------------------
# API - triagem manual (para testar sem webhook)
# ---------------------------------------------------------------------------

@app.route("/api/triage", methods=["POST"])
def triage():
    data = request.get_json(force=True, silent=True) or {}
    telefone = data.get("telefone", "5511999999999")
    mensagem = data.get("mensagem", "")
    if not mensagem:
        return jsonify({"error": "mensagem obrigatoria"}), 400
    try:
        result = triage_message(telefone, mensagem)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---------------------------------------------------------------------------
# API - testar auto-crm manualmente (simula webhook)
# ---------------------------------------------------------------------------

@app.route("/api/auto-crm/test", methods=["POST"])
def auto_crm_test():
    data = request.get_json(force=True, silent=True) or {}
    telefone = data.get("telefone", "5511999999999")
    mensagem = data.get("mensagem", "")
    nome = data.get("nome")
    intent = data.get("intent")

    if not mensagem:
        return jsonify({"error": "mensagem obrigatoria"}), 400

    if intent:
        triagem = {
            "intent": intent,
            "nome_cliente": nome,
            "telefone": telefone,
            "resumo": mensagem[:100],
            "urgencia": "media",
            "response_suggested": "...",
        }
    else:
        from gemini_client import triage_message as triage_fn
        triagem = triage_fn(telefone, mensagem)

    acoes = processar_mensagem(triagem, mensagem, telefone, nome)

    return jsonify({
        "triagem": triagem,
        "acoes": acoes,
        "total_acoes": len(acoes),
    }), 200

# ---------------------------------------------------------------------------
# API - health check
# ---------------------------------------------------------------------------

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "timestamp": datetime.utcnow().isoformat()}), 200

# ---------------------------------------------------------------------------

if __name__ == "__main__":
    host = os.environ.get("FLASK_HOST", "0.0.0.0")
    port = int(os.environ.get("FLASK_PORT", "5000"))
    debug = os.environ.get("FLASK_ENV", "development") == "development"
    logger.info(f"Starting JAF CRM Backend on {host}:{port}")
    app.run(host=host, port=port, debug=debug)
