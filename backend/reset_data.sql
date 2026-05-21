-- =============================================
-- JAF CRM - LIMPAR TODOS OS DADOS
-- Execute no SQL Editor do Supabase (uma vez)
-- =============================================

-- Remove todos os registros de todas as tabelas
TRUNCATE TABLE public.clientes CASCADE;
TRUNCATE TABLE public.apolices CASCADE;
TRUNCATE TABLE public.leads CASCADE;
TRUNCATE TABLE public.propostas CASCADE;
TRUNCATE TABLE public.producao CASCADE;
TRUNCATE TABLE public.sinistros CASCADE;
TRUNCATE TABLE public.agenda CASCADE;

-- (Nao truncar whatsapp_messages - mantem historico)
