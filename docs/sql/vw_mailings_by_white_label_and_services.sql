-- Vista: vw_mailings_by_white_label_and_services
-- Descripción: Audiences agrupadas por white_label_tag y code_service (no por compañía).
--              Incluye columna tag_mailing con tags múltiples por usuario separados por coma.
-- Basada en: vw_mailings_v5
-- Fecha: 2026-04-07
-- Requiere: companies_sections (section_id=9 para banking)

CREATE OR REPLACE VIEW public.vw_mailings_by_white_label_and_services
AS WITH user_exclusions AS (
    SELECT users.id
    FROM users
    WHERE users._password IS NOT NULL
      AND users.promotional_email = false
),
email_exclusions AS (
    SELECT email_mailing_exclusion.email
    FROM email_mailing_exclusion
),
excluded_companies AS (
    SELECT companies_mailing_exclusion.company_id
    FROM companies_mailing_exclusion
),
banking_status AS (
    -- Regla: sin registro en companies_sections → tiene banking (todas las secciones activas por defecto).
    --        con registro y disabled=true → NO tiene banking.
    --        con registro y disabled=false → SÍ tiene banking.
    SELECT cs.company_id,
           cs.disabled
    FROM companies_sections cs
    WHERE cs.section_id = 9
),
companies_filter AS (
    SELECT c1.id,
           c1.name AS company_name,
           COALESCE(c1.white_label_tag, 'multikrd'::character varying) AS white_label_tag,
           c1.payroll_active,
           -- NULL (sin registro) → COALESCE(NULL,false)=false → NOT false = true (tiene banking)
           -- disabled=true → COALESCE(true,false)=true → NOT true = false (sin banking)
           -- disabled=false → COALESCE(false,false)=false → NOT false = true (tiene banking)
           NOT COALESCE(bs.disabled, false) AS has_banking,
           COALESCE(c1.payroll_card, false) AS payroll_card,
           c1.mailing_group
    FROM companies c1
    LEFT JOIN banking_status bs ON bs.company_id = c1.id
    WHERE NOT (c1.id IN (SELECT company_id FROM excluded_companies))
),
users_filter AS (
    SELECT u_1.id,
           u_1.first_name,
           u_1._last_name,
           u_1._email,
           u_1.company_id,
           u_1.registration_date,
           u_1.signup_date,
           u_1._password,
           u_1.promotional_email,
           u_1.last_login_date,
           u_1._flags,
           CASE
               WHEN u_1._password IS NULL AND CURRENT_DATE <= (u_1.registration_date + '21 days'::interval)
                   THEN 'Welcome'::text
               -- NOTA: la precedencia OR es intencional, heredada de vw_mailings_v5.
               -- Evalúa: (password NOT NULL AND promotional_email) OR (fecha >= 21 días)
               WHEN (u_1._password IS NOT NULL AND u_1.promotional_email = true)
                    OR CURRENT_DATE >= (u_1.registration_date + '21 days'::interval)
                   THEN 'MailingSup'::text
               ELSE NULL::text
           END AS "Tags",
           CASE
               WHEN (c_1._flags ->> 'mass_activation'::text) IS NOT NULL
                   THEN concat('Mass_Activation_', to_char(((c_1._flags ->> 'mass_activation'::text)::date)::timestamp with time zone, 'YYYYMMDD'::text))
               ELSE ''::text
           END AS "Tags_2"
    FROM users u_1
    JOIN companies c_1 ON c_1.id = u_1.company_id
    WHERE u_1.inactive = false
      AND NOT (u_1.id IN (SELECT id FROM user_exclusions))
      AND NOT (u_1.company_id IN (SELECT company_id FROM excluded_companies))
      AND NOT (u_1.email_old::text IN (SELECT email FROM email_exclusions))
),
code_service_logic AS (
    SELECT c.id AS company_id,
           c.white_label_tag,
           c.has_banking,
           c.payroll_active,
           c.payroll_card,
           CASE
               WHEN c.has_banking AND c.payroll_active AND NOT c.payroll_card THEN 'ALL_Prepaid'
               WHEN c.has_banking AND c.payroll_active AND c.payroll_card     THEN 'ALL_Payroll'
               WHEN c.has_banking AND NOT c.payroll_active AND NOT c.payroll_card THEN 'NWA_Prepaid'
               WHEN c.has_banking AND NOT c.payroll_active AND c.payroll_card     THEN 'NWA_Payroll'
               WHEN NOT c.has_banking AND c.payroll_active                        THEN 'NB'
               WHEN NOT c.has_banking AND NOT c.payroll_active                    THEN 'MKTP'
               ELSE 'OTHER'
           END AS code_service
    FROM companies_filter c
),
tag_mailing_logic AS (
    SELECT u.id AS user_id,
           string_agg(tag, ',' ORDER BY tag) AS tag_mailing
    FROM users_filter u
    JOIN companies_filter c ON c.id = u.company_id
    CROSS JOIN LATERAL (
        VALUES
            -- Status tags
            (CASE WHEN u.signup_date IS NULL
                       AND CURRENT_DATE <= (u.registration_date + '21 days'::interval)
                  THEN 'WelcomeIntro' END),
            (CASE WHEN u.signup_date IS NULL
                       AND CURRENT_DATE > (u.registration_date + '21 days'::interval)
                  THEN 'NotSignedUp' END),
            (CASE WHEN u.signup_date IS NOT NULL OR u._password IS NOT NULL
                  THEN 'SignedUp' END),
            (CASE WHEN (u.signup_date IS NOT NULL OR u._password IS NOT NULL)
                       AND u.promotional_email = true
                       AND (u.last_login_date IS NOT NULL OR u._password IS NOT NULL)
                  THEN 'MailingActive' END),
            -- Service combination tags
            (CASE WHEN c.has_banking AND c.payroll_active AND NOT c.payroll_card
                  THEN 'ALLPrepaid' END),
            (CASE WHEN c.has_banking AND c.payroll_active AND c.payroll_card
                  THEN 'ALLPayroll' END),
            (CASE WHEN c.has_banking AND NOT c.payroll_active AND NOT c.payroll_card
                  THEN 'NWAPrepaid' END),
            (CASE WHEN c.has_banking AND NOT c.payroll_active AND c.payroll_card
                  THEN 'NWAPayroll' END),
            (CASE WHEN NOT c.has_banking AND NOT c.payroll_active
                  THEN 'MKTP' END),
            (CASE WHEN NOT c.has_banking AND c.payroll_active
                  THEN 'NB' END),
            -- Card type tags
            (CASE WHEN c.has_banking AND NOT c.payroll_card
                  THEN 'PrepaidCard' END),
            (CASE WHEN c.has_banking AND c.payroll_card
                  THEN 'PayrollCard' END),
            -- Active cardholder tags (flag existe solo como 'true' cuando aplica)
            (CASE WHEN (u._flags ->> 'has_cpayments_account') = 'true'
                       AND NOT c.payroll_card
                  THEN 'ActivePrepaidCardholder' END),
            (CASE WHEN (u._flags ->> 'has_cpayments_account') = 'true'
                       AND c.payroll_card
                  THEN 'ActivePayrollCardholder' END),
            -- Feature tags
            (CASE WHEN c.payroll_active THEN 'EWA' END),
            ('Remittances'),  -- Siempre true por ahora (solicitado por product owner)
            (CASE WHEN c.has_banking THEN 'Ding' END),
            (CASE WHEN c.white_label_tag <> 'insperity' THEN 'HealthInsurance' END)
    ) AS t(tag)
    WHERE tag IS NOT NULL
    GROUP BY u.id
),
file_name_logic AS (
    SELECT u.id AS user_id,
           CASE
               WHEN c.mailing_group = 'Do Not Send' THEN
                   concat(to_char(CURRENT_DATE::timestamp with time zone, 'YYYYMMDD'), '_DoNotSend_records.csv')
               WHEN c.mailing_group = 'CAUTION' THEN
                   concat(to_char(CURRENT_DATE::timestamp with time zone, 'YYYYMMDD'), '_CAUTION_records.csv')
               ELSE
                   concat(
                       to_char(CURRENT_DATE::timestamp with time zone, 'YYYYMMDD'),
                       '_',
                       c.white_label_tag,
                       '_',
                       cs.code_service,
                       '_',
                       COALESCE(u."Tags", 'NoTag'),
                       '_records.csv'
                   )
           END AS file_name
    FROM users_filter u
    JOIN companies_filter c ON c.id = u.company_id
    JOIN code_service_logic cs ON cs.company_id = c.id
)
SELECT u._email AS "Email Address",
       u.first_name AS "First Name",
       u._last_name AS "Last Name",
       u.id AS "User ID",
       wl.white_label_description AS "White Label",
       wl.customer_service AS "Label Customer Service",
       tm.tag_mailing AS "Tags",
       u."Tags_2",
       cl4.last_4 AS "Card Number",
       c.company_name AS "Company Name",
       u.registration_date,
       CURRENT_DATE::timestamp without time zone - u.registration_date AS diferencia,
       fn.file_name,
       u.signup_date,
       c.payroll_active,
       c.has_banking,
       c.id AS company_id,
       c.payroll_card
FROM users_filter u
JOIN companies_filter c ON c.id = u.company_id
JOIN code_service_logic cs ON cs.company_id = c.id
LEFT JOIN white_label wl ON wl.white_label_tag::text = c.white_label_tag::text
LEFT JOIN customer_last_4 cl4 ON cl4.user_id = u.id
LEFT JOIN file_name_logic fn ON fn.user_id = u.id
LEFT JOIN tag_mailing_logic tm ON tm.user_id = u.id;
