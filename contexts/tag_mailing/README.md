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
- **Helper Python**: `query_builder_app/helpers/audiences.py` (post-processing cardholder payroll override)

## Cómo agregar un nuevo tag

1. Abrir `docs/sql/vw_mailings_by_white_label_and_services.sql`
2. Localizar el CTE `tag_mailing_logic`, sección `VALUES (...)`
3. Agregar una nueva línea con el formato:
   ```sql
   (CASE WHEN <condición> THEN '<NombreTag>' END),
   ```
3.5. Si el tag depende de datos en otra BD (como `cardholder`), implementar la lógica en `helpers/audiences.py` como post-procesamiento
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
- Usuarios con `companies.mailing_group = 'Do Not Send'` se agrupan en un solo archivo: `YYYYMMDD_DoNotSend_records.csv`
- Usuarios con `companies.mailing_group = 'CAUTION'` se agrupan en un solo archivo: `YYYYMMDD_CAUTION_records.csv`

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

## Regla de Payroll/Prepaid (cardholder override)
La clasificación Prepaid/Payroll tiene dos fuentes, con prioridad:

1. **Si el usuario tiene registro en `cardholder`** (tabla en BD `banking_operation`):
   - `cardholder.program_id` contiene 'PAYROLL' (case-insensitive) → **Payroll**
   - `cardholder.program_id` NO contiene 'PAYROLL' → **Prepaid**
2. **Si NO tiene cardholder** → se usa `companies.payroll_card` (true=Payroll, false=Prepaid)

Este override se aplica en Python (`helpers/audiences.py`), no en la vista SQL, porque `cardholder` está en una BD distinta (`banking_operation`).

Tags afectados por el override: `ALLPrepaid`↔`ALLPayroll`, `NWAPrepaid`↔`NWAPayroll`, `PrepaidCard`↔`PayrollCard`, `ActivePrepaidCardholder`↔`ActivePayrollCardholder`.

Conexión banking_operation vía env vars:
- `NAME_BANKING_OPERATION_READ_ONLY`
- `USER_BANKING_OPERATION_READ_ONLY`
- `PASSWORD_BANKING_OPERATION_READ_ONLY`
- `HOST_BANKING_OPERATION_READ_ONLY`
- `PORT_BANKING_OPERATION_READ_ONLY`
- `SCHEMA_BANKING_OPERATION_READ_ONLY`
