-- =============================================
-- JAF CRM - RLS Policies for CRM Tables
-- Execute no SQL Editor do Supabase
-- =============================================

-- Helper: drop existing policy if any, then create
DO $$
DECLARE
    tbl text;
    tables text[] := ARRAY['clientes','apolices','leads','propostas','producao','sinistros','agenda'];
BEGIN
    FOREACH tbl IN ARRAY tables
    LOOP
        EXECUTE format('ALTER TABLE %I ENABLE ROW LEVEL SECURITY;', tbl);
        EXECUTE format('DROP POLICY IF EXISTS "Allow authenticated all" ON %I;', tbl);
        EXECUTE format('CREATE POLICY "Allow authenticated all" ON %I FOR ALL USING (auth.role() = ''authenticated'');', tbl);
    END LOOP;
END $$;
