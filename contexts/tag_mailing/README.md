# tag_mailing — Contexto de segmentación

## Qué es
Columna de la vista `vw_mailings_by_white_label_and_services` que contiene **tags múltiples por usuario**, separados por coma. Cada tag representa una condición de negocio del usuario o su compañía.

Ejemplo de valor: `ALLPrepaid,Ding,EWA,HealthInsurance,SignedUp,MailingActive,PrepaidCard,Remittances`

## Para qué sirve
Mailchimp usa estos tags para segmentar campañas. El PO puede filtrar audiencias por combinaciones de tags (ej: enviar campaña solo a usuarios con `SignedUp` + `PrepaidCard` + `HealthInsurance`).

## Dónde vive
- **Vista SQL**: `public.vw_mailings_by_white_label_and_services`
- **Archivo SQL**: `docs/sql/vw_mailings_by_white_label_and_services.sql`
- **CTE responsable**: `tag_mailing_logic` (usa `CROSS JOIN LATERAL` + `string_agg`)

## Cómo agregar un nuevo tag

1. Abrir `docs/sql/vw_mailings_by_white_label_and_services.sql`
2. Localizar el CTE `tag_mailing_logic`, sección `VALUES (...)`
3. Agregar una nueva línea con el formato:
   ```sql
   (CASE WHEN <condición> THEN '<NombreTag>' END),
   ```
4. Si el tag es incondicional (siempre aplica), usar:
   ```sql
   ('<NombreTag>'),
   ```
5. Actualizar este contexto: agregar el tag en `tags_reference.md`
6. Ejecutar `CREATE OR REPLACE VIEW` en la BD
7. Validar con:
   ```sql
   SELECT tag_mailing, count(*) FROM vw_mailings_by_white_label_and_services
   WHERE tag_mailing LIKE '%NuevoTag%' GROUP BY tag_mailing LIMIT 10;
   ```

## Reglas importantes

- Los tags se ordenan **alfabéticamente** dentro del CSV (`string_agg(tag, ',' ORDER BY tag)`)
- Un usuario puede tener **1 a N tags simultáneamente** — no son mutuamente excluyentes
- Tags NULL se filtran automáticamente (`WHERE tag IS NOT NULL`)
- Los tags NO cambian el agrupamiento de archivos (eso lo hace `code_service_logic`)
- Los tags son **independientes** del `code_service` del nombre del archivo — un usuario en un archivo `MKTP` puede tener tags como `Remittances, HealthInsurance`

## Dependencias de datos

| Fuente | Tabla/Columna | Uso |
|--------|--------------|-----|
| Signup | `users.signup_date` | WelcomeIntro, NotSignedUp, SignedUp |
| Password | `users._password` | SignedUp, MailingActive |
| Promotional email | `users.promotional_email` | MailingActive |
| Last login | `users.last_login_date` | MailingActive |
| Registration date | `users.registration_date` | WelcomeIntro, NotSignedUp (umbral 21 días) |
| Banking | `companies_sections` (section_id=9) | ALLPrepaid/Payroll, NWAPrepaid/Payroll, Ding, PrepaidCard, PayrollCard |
| Payroll active | `companies.payroll_active` | ALLPrepaid/Payroll, NB, MKTP, EWA |
| Payroll card | `companies.payroll_card` | Distingue Prepaid vs Payroll |
| Active card | `users._flags->>'has_cpayments_account'` | ActivePrepaidCardholder, ActivePayrollCardholder |
| White label | `companies.white_label_tag` | HealthInsurance (excluye insperity) |

## Regla de banking (crítica)
Determinada por `companies_sections` con `section_id = 9`:
- **Sin registro** → SÍ tiene banking (todas las secciones activas por defecto)
- **`disabled = false`** → SÍ tiene banking
- **`disabled = true`** → NO tiene banking

SQL: `NOT COALESCE(bs.disabled, false) AS has_banking`
