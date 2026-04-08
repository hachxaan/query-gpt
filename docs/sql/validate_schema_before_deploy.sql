-- =============================================================================
-- Script de validación pre-deploy para vw_mailings_by_white_label_and_services
-- Ejecutar en la BD de dev ANTES de crear la vista.
-- =============================================================================

-- ============================================================
-- 1. Verificar que las columnas requeridas existen en el schema
-- ============================================================

-- 1a. users.last_login_date
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'users' AND column_name = 'last_login_date';
-- Esperado: 1 fila. Si vacío → la vista fallará.

-- 1b. companies.payroll_card
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'companies' AND column_name = 'payroll_card';
-- Esperado: 1 fila (boolean). Si vacío → la vista fallará.

-- 1c. users._flags (JSONB)
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'users' AND column_name = '_flags';
-- Esperado: 1 fila (jsonb). Si vacío → tags ActiveCardholder fallarán.

-- 1d. companies_sections existe y tiene section_id=9
SELECT COUNT(*) AS banking_sections_count
FROM companies_sections
WHERE section_id = 9;
-- Esperado: > 0. Si 0 → ninguna compañía tendrá banking.

-- ============================================================
-- 2. Consistencia: companies.banking vs companies_sections
-- ============================================================

-- 2a. Registros donde companies.banking difiere de companies_sections
SELECT c.id AS company_id,
       c.name,
       c.banking AS banking_column,
       COALESCE(cs.disabled = false, false) AS banking_from_sections,
       CASE
           WHEN c.banking = COALESCE(cs.disabled = false, false) THEN 'MATCH'
           ELSE 'MISMATCH'
       END AS status
FROM companies c
LEFT JOIN companies_sections cs ON cs.company_id = c.id AND cs.section_id = 9
WHERE c.banking != COALESCE(cs.disabled = false, false)
ORDER BY c.id;
-- Esperado: 0 filas (consistente). Si hay filas → documentar discrepancias.

-- 2b. Resumen de consistencia
SELECT
    COUNT(*) AS total_companies,
    SUM(CASE WHEN c.banking = COALESCE(cs.disabled = false, false) THEN 1 ELSE 0 END) AS matching,
    SUM(CASE WHEN c.banking != COALESCE(cs.disabled = false, false) THEN 1 ELSE 0 END) AS mismatching
FROM companies c
LEFT JOIN companies_sections cs ON cs.company_id = c.id AND cs.section_id = 9;

-- ============================================================
-- 3. Verificar existencia de tablas auxiliares
-- ============================================================

-- 3a. white_label
SELECT COUNT(*) FROM white_label;

-- 3b. customer_last_4
SELECT COUNT(*) FROM customer_last_4;

-- 3c. email_mailing_exclusion
SELECT COUNT(*) FROM email_mailing_exclusion;

-- 3d. companies_mailing_exclusion
SELECT COUNT(*) FROM companies_mailing_exclusion;

-- ============================================================
-- 4. Verificar versión de PostgreSQL (CROSS JOIN LATERAL requiere 9.3+)
-- ============================================================
SELECT version();
