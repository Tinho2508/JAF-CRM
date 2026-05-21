-- =============================================
-- JAF CRM - RLS Policies for CRM Tables
-- Execute no SQL Editor do Supabase
-- =============================================

-- Helper: drop old policies, create per-operation policies
DO $$
DECLARE
    tbl text;
    tables text[] := ARRAY['clientes','apolices','leads','propostas','producao','sinistros','agenda'];
BEGIN
    FOREACH tbl IN ARRAY tables
    LOOP
        EXECUTE format('ALTER TABLE %I ENABLE ROW LEVEL SECURITY;', tbl);
        -- Drop old policy if exists (FOR ALL without WITH CHECK)
        EXECUTE format('DROP POLICY IF EXISTS "Allow authenticated all" ON %I;', tbl);
        -- SELECT
        EXECUTE format('CREATE POLICY "auth_select" ON %I FOR SELECT USING (auth.role() = ''authenticated'');', tbl);
        -- INSERT
        EXECUTE format('CREATE POLICY "auth_insert" ON %I FOR INSERT WITH CHECK (auth.role() = ''authenticated'');', tbl);
        -- UPDATE
        EXECUTE format('CREATE POLICY "auth_update" ON %I FOR UPDATE USING (auth.role() = ''authenticated'') WITH CHECK (auth.role() = ''authenticated'');', tbl);
        -- DELETE
        EXECUTE format('CREATE POLICY "auth_delete" ON %I FOR DELETE USING (auth.role() = ''authenticated'');', tbl);
    END LOOP;
END $$;
