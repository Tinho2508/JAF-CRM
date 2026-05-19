"""
WhatsApp Provider Adapter
Abstrai diferentes provedores de WhatsApp Business API.
Atualmente suporta: Twilio, WhatsApp Cloud API (Meta), Wavoip.
"""

import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

PROVIDER_TWILIO = "twilio"
PROVIDER_CLOUD_API = "cloud_api"
PROVIDER_WAVOIP = "wavoip"

def get_provider() -> str:
    return os.environ.get("WA_PROVIDER", PROVIDER_TWILIO)

def parse_webhook(data: dict, provider: str = None) -> dict | None:
    """
    Converte webhook de qualquer provedor para formato padrao:
    {
        "provider": "twilio|cloud_api|wavoip",
        "message_id": "...",
        "telefone": "5511999999999",
        "nome": "Nome do Remetente" or None,
        "mensagem": "texto da mensagem",
        "timestamp": "2025-01-01T12:00:00Z",
        "tipo": "texto|imagem|documento",
        "midia_url": None,
        "raw": { ... }
    }
    """
    provider = provider or get_provider()

    if provider == PROVIDER_TWILIO:
        return _parse_twilio(data)
    elif provider == PROVIDER_CLOUD_API:
        return _parse_cloud_api(data)
    elif provider == PROVIDER_WAVOIP:
        return _parse_wavoip(data)
    else:
        logger.warning(f"Unknown provider: {provider}")
        return None

def _parse_twilio(data: dict) -> dict | None:
    if not data.get("Body"):
        return None
    return {
        "provider": PROVIDER_TWILIO,
        "message_id": data.get("MessageSid", ""),
        "telefone": _normalize_phone(data.get("From", "")),
        "nome": data.get("ProfileName"),
        "mensagem": data.get("Body", ""),
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "tipo": "texto",
        "midia_url": data.get("MediaUrl0"),
        "raw": data,
    }

def _parse_cloud_api(data: dict) -> dict | None:
    entries = data.get("entry", [])
    for entry in entries:
        changes = entry.get("changes", [])
        for change in changes:
            value = change.get("value", {})
            messages = value.get("messages", [])
            for msg in messages:
                if msg.get("type") == "text":
                    text = msg.get("text", {}).get("body", "")
                else:
                    text = f"[{msg.get('type')}]"
                profile = value.get("contacts", [{}])[0].get("profile", {})
                return {
                    "provider": PROVIDER_CLOUD_API,
                    "message_id": msg.get("id", ""),
                    "telefone": _normalize_phone(msg.get("from", "")),
                    "nome": profile.get("name"),
                    "mensagem": text,
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "tipo": msg.get("type", "texto"),
                    "midia_url": None,
                    "raw": data,
                }
    return None

def _parse_wavoip(data: dict) -> dict | None:
    mensagem = data.get("message") or data.get("mensagem") or data.get("text")
    telefone = data.get("number") or data.get("from") or data.get("telefone")
    if not mensagem or not telefone:
        return None
    return {
        "provider": PROVIDER_WAVOIP,
        "message_id": data.get("id", ""),
        "telefone": _normalize_phone(telefone),
        "nome": data.get("name") or data.get("nome") or data.get("profileName"),
        "mensagem": mensagem,
        "timestamp": data.get("timestamp") or (datetime.utcnow().isoformat() + "Z"),
        "tipo": data.get("type", "texto"),
        "midia_url": data.get("mediaUrl") or data.get("midia"),
        "raw": data,
    }

def _normalize_phone(phone: str) -> str:
    cleaned = "".join(c for c in phone if c.isdigit())
    if cleaned.startswith("55") and len(cleaned) >= 12:
        return cleaned
    if not cleaned.startswith("55"):
        cleaned = "55" + cleaned
    return cleaned

def build_response(provider: str, to: str, message: str) -> dict:
    if provider == PROVIDER_TWILIO:
        return {"to": to, "body": message}
    elif provider == PROVIDER_CLOUD_API:
        return {
            "messaging_product": "whatsapp",
            "to": to.lstrip("55"),
            "type": "text",
            "text": {"body": message},
        }
    elif provider == PROVIDER_WAVOIP:
        return {"number": to, "message": message}
    return {"message": message}
