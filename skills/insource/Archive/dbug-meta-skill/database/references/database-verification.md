# Universal Database Catalog & Verification Queries

This reference contains standard catalog queries for inspecting database schemas, column definitions, constraints, foreign keys, indexes, Row Level Security (RLS) policies, and permissions across PostgreSQL, MySQL, and SQLite.

---

## 1. PostgreSQL & Supabase

### Table Columns & Data Types
```sql
SELECT 
  column_name, 
  data_type, 
  udt_name,
  is_nullable, 
  column_default
FROM information_schema.columns
WHERE table_schema = 'public' 
  AND table_name = 'your_table_name'
ORDER BY ordinal_position;
```

### Constraints, Primary Keys & Foreign Keys
```sql
SELECT
  tc.constraint_name,
  tc.constraint_type,
  kcu.column_name,
  ccu.table_name AS foreign_table_name,
  ccu.column_name AS foreign_column_name
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
  ON tc.constraint_name = kcu.constraint_name
  AND tc.table_schema = kcu.table_schema
LEFT JOIN information_schema.constraint_column_usage AS ccu
  ON ccu.constraint_name = tc.constraint_name
  AND ccu.table_schema = tc.table_schema
WHERE tc.table_schema = 'public'
  AND tc.table_name = 'your_table_name';
```

### Indexes
```sql
SELECT
  indexname AS index_name,
  indexdef AS index_definition
FROM pg_indexes
WHERE schemaname = 'public'
  AND tablename = 'your_table_name';
```

### Row Level Security (RLS) Policies
```sql
-- Check RLS status
SELECT relname AS table_name, relrowsecurity AS rls_enabled
FROM pg_class
WHERE relnamespace = 'public'::regnamespace
  AND relname = 'your_table_name';

-- List all policies on table
SELECT
  pol.polname AS policy_name,
  CASE pol.polcmd
    WHEN 'r' THEN 'SELECT'
    WHEN 'a' THEN 'INSERT'
    WHEN 'w' THEN 'UPDATE'
    WHEN 'd' THEN 'DELETE'
    WHEN '*' THEN 'ALL'
  END AS command,
  pg_catalog.array_to_string(
    ARRAY(
      SELECT rolname FROM pg_roles WHERE oid = ANY(pol.polroles)
    ), ', '
  ) AS target_roles,
  pg_get_expr(pol.polqual, pol.polrelid) AS using_expression,
  pg_get_expr(pol.polwithcheck, pol.polrelid) AS with_check_expression
FROM pg_policy pol
JOIN pg_class cls ON pol.polrelid = cls.oid
WHERE cls.relnamespace = 'public'::regnamespace
  AND cls.relname = 'your_table_name';
```

### Function Search Paths & SECURITY DEFINER
```sql
SELECT 
  p.proname AS function_name,
  pg_get_function_identity_arguments(p.oid) AS arguments,
  p.prosecdef AS is_security_definer,
  p.proconfig AS search_path_config
FROM pg_proc p
JOIN pg_namespace n ON p.pronamespace = n.oid
WHERE n.nspname = 'public';
```

---

## 2. MySQL / MariaDB

### Table Columns & Data Types
```sql
SELECT 
  COLUMN_NAME, 
  DATA_TYPE, 
  COLUMN_TYPE, 
  IS_NULLABLE, 
  COLUMN_DEFAULT, 
  EXTRA
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = DATABASE() 
  AND TABLE_NAME = 'your_table_name'
ORDER BY ORDINAL_POSITION;
```

### Constraints & Foreign Keys
```sql
SELECT 
  CONSTRAINT_NAME, 
  CONSTRAINT_TYPE
FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS
WHERE TABLE_SCHEMA = DATABASE() 
  AND TABLE_NAME = 'your_table_name';

SELECT 
  k.CONSTRAINT_NAME,
  k.COLUMN_NAME,
  k.REFERENCED_TABLE_NAME,
  k.REFERENCED_COLUMN_NAME
FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE k
WHERE k.TABLE_SCHEMA = DATABASE()
  AND k.TABLE_NAME = 'your_table_name'
  AND k.REFERENCED_TABLE_NAME IS NOT NULL;
```

---

## 3. SQLite

### Table Schema & PRAGMA Inspection
```sql
-- Inspect columns, types, nullability, defaults, primary keys
PRAGMA table_info('your_table_name');

-- Inspect foreign keys
PRAGMA foreign_key_list('your_table_name');

-- Inspect indexes
PRAGMA index_list('your_table_name');

-- View full DDL statement
SELECT sql FROM sqlite_master WHERE type = 'table' AND name = 'your_table_name';
```
