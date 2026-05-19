import os
import json
import requests
from urllib.parse import urljoin

WORKER_URL = os.environ.get(
    "GEMINI_WORKER_URL",
    "https://jaf-crm-gemini-proxy.joseailton-ailtontinho.workers.dev/",
)

TRIAGE_PROMPT = """Você é um assistente de CRM de seguros. Analise a mensagem recebida e extraia:

1. **intent** - a intenção principal (escolha UMA):
   - lead_novo: pessoa interessada em contratar seguro
   - renovacao: quer renovar apólice existente
   - sinistro: comunicando/acompanhando sinistro
   - cobranca: dúvida sobre pagamento/boleto
   - proposta: acompanhando proposta enviada
   - informacao: pedindo informações gerais
   - reclamacao: reclamação
   - outro: não se encaixa nos acima

2. **nome_cliente** - nome do cliente mencionado (ou null se não identificar)

3. **telefone** - telefone do remetente (fornecido separadamente)

4. **resumo** - resumo de 1 frase do assunto

5. **urgencia** - 'alta', 'media' ou 'baixa'
   - alta: sinistro, reclamação, vencimento hoje
   - media: renovação próxima, proposta, cobrança
   - baixa: informação, lead novo

6. **response_suggested** - sugestão de resposta (em português, tom profissional e cordial)

Responda APENAS com JSON válido, sem formatação extra:
{"intent": "...", "nome_cliente": null, "telefone": "...", "resumo": "...", "urgencia": "...", "response_suggested": "..."}
"""

def _call_gemini(prompt: str) -> str:
    url = WORKER_URL.rstrip("/") + "/"
    body = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.1, "maxOutputTokens": 500},
    }
    resp = requests.post(url, json=body, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    candidates = data.get("candidates")
    if candidates and len(candidates) > 0:
        parts = candidates[0].get("content", {}).get("parts", [])
        if parts:
            return parts[0].get("text", "")
    return data.get("response") or data.get("text") or resp.text

def triage_message(telefone: str, mensagem: str) -> dict:
    prompt = TRIAGE_PROMPT + f"\n\nTelefone do remetente: {telefone}\nMensagem recebida: {mensagem}"
    text = _call_gemini(prompt)
    text = text.strip()
    text = text.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    return json.loads(text)

def gerar_resposta(intent: str, nome: str | None, contexto: dict) -> str:
    prompt = f"""Você é um corretor de seguros chamado JAF. Gere uma resposta cordial e profissional.

Intenção do cliente: {intent}
Nome: {nome or "Não identificado"}
Contexto adicional: {json.dumps(contexto, ensure_ascii=False)}

Regras:
- Se for lead_novo: seja acolhedor, peça mais detalhes sobre o que precisa
- Se for renovação: confirme recebimento, informe que vai verificar a melhor proposta
- Se for sinistro: mostre empatia, peça fotos/documentos, informe que vai abrir o sinistro
- Se for cobrança: peça o número da apólice para verificar
- Se for informação: responda de forma clara e objetiva
- Se for reclamação: peça desculpas, informe que vai buscar resolver

Seja breve (máximo 3 parágrafos), em português."""
    return _call_gemini(prompt)
