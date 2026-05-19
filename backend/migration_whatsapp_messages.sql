-- =============================================
-- JAF CRM - Tabela de Mensagens WhatsApp
-- Execute no SQL Editor do Supabase
-- =============================================

CREATE TABLE IF NOT EXISTS whatsapp_messages (
    id TEXT PRIMARY KEY,
    provider TEXT NOT NULL DEFAULT 'unknown',
    telefone TEXT NOT NULL,
    nome TEXT,
    mensagem TEXT NOT NULL,
    tipo TEXT DEFAULT 'texto',
    midia_url TEXT,
    intent TEXT,
    urgencia TEXT DEFAULT 'baixa',
    resumo TEXT,
    response_sent TEXT,
    response_suggested TEXT,
    cliente_id TEXT,
    criado_em TIMESTAMPTZ DEFAULT NOW(),
    lido BOOLEAN DEFAULT FALSE,
    acoes JSONB DEFAULT '[]'::jsonb
);

-- Índices para consultas rápidas
CREATE INDEX IF NOT EXISTS idx_whatsapp_telefone ON whatsapp_messages(telefone);
CREATE INDEX IF NOT EXISTS idx_whatsapp_intent ON whatsapp_messages(intent);
CREATE INDEX IF NOT EXISTS idx_whatsapp_criado_em ON whatsapp_messages(criado_em DESC);
CREATE INDEX IF NOT EXISTS idx_whatsapp_lido ON whatsapp_messages(lido);

-- Adicionar coluna acoes em tabelas existentes (opcional)
ALTER TABLE whatsapp_messages ADD COLUMN IF NOT EXISTS acoes JSONB DEFAULT '[]'::jsonb;

-- RLS: para desenvolvimento
ALTER TABLE whatsapp_messages ENABLE ROW LEVEL SECURITY;

-- Se usar service_role key no backend:
-- CREATE POLICY "service_role access" ON whatsapp_messages FOR ALL USING (true);

-- Se usar anon key (mais simples para teste):
DROP POLICY IF EXISTS "Allow anon all" ON whatsapp_messages;
CREATE POLICY "Allow anon all" ON whatsapp_messages FOR ALL USING (true);
