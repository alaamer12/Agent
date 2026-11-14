-- =============================================================================
-- Template: Universal Idempotent Migration Verification Script
-- Usage: Execute via database CLI or SQL Editor to test DDL changes safely in a transaction
-- =============================================================================

BEGIN;

-- -----------------------------------------------------------------------------
-- 1. Example DDL Operation (Column additions, type changes, nullability)
-- -----------------------------------------------------------------------------
-- ALTER TABLE public.example_table ADD COLUMN IF NOT EXISTS status VARCHAR(50) DEFAULT 'active';
-- ALTER TABLE public.example_table ALTER COLUMN optional_field DROP NOT NULL;

-- -----------------------------------------------------------------------------
-- 2. Example Index Creation
-- -----------------------------------------------------------------------------
-- CREATE INDEX IF NOT EXISTS idx_example_table_created_at ON public.example_table(created_at DESC);

-- -----------------------------------------------------------------------------
-- 3. Example Role Permissions & Grants
-- -----------------------------------------------------------------------------
-- GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE public.example_table TO authenticated;
-- GRANT SELECT ON TABLE public.example_table TO anon;

-- -----------------------------------------------------------------------------
-- 4. Example Row Level Security (RLS) Policy Setup
-- -----------------------------------------------------------------------------
-- ALTER TABLE public.example_table ENABLE ROW LEVEL SECURITY;
-- DROP POLICY IF EXISTS "Users can manage their own records" ON public.example_table;
-- CREATE POLICY "Users can manage their own records"
-- ON public.example_table
-- FOR ALL
-- TO authenticated
-- USING (auth.uid() = user_id)
-- WITH CHECK (auth.uid() = user_id);

-- -----------------------------------------------------------------------------
-- 5. Example Hardened SECURITY DEFINER Function
-- -----------------------------------------------------------------------------
-- CREATE OR REPLACE FUNCTION public.execute_safe_operation(p_id uuid)
-- RETURNS boolean
-- LANGUAGE plpgsql
-- SECURITY DEFINER
-- SET search_path = public, pg_temp
-- AS $$
-- BEGIN
--   -- Function implementation logic here
--   RETURN true;
-- END;
-- $$;
-- REVOKE ALL ON FUNCTION public.execute_safe_operation(uuid) FROM PUBLIC, anon;
-- GRANT EXECUTE ON FUNCTION public.execute_safe_operation(uuid) TO authenticated, service_role;

-- -----------------------------------------------------------------------------
-- 6. Verification Assertion (Query catalog inside transaction to confirm change)
-- -----------------------------------------------------------------------------
-- SELECT column_name, data_type, is_nullable
-- FROM information_schema.columns
-- WHERE table_name = 'example_table';

-- Dry-run safety: keep ROLLBACK for testing; switch to COMMIT when applying permanently.
ROLLBACK;
