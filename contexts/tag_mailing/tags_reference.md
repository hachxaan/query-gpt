# Referencia de Tags — tag_mailing

Fecha de creación: 2026-04-08
Vista: `vw_mailings_by_white_label_and_services`

## Tags actuales (18)

### Status del usuario

| Tag | Condición SQL | Significado de negocio |
|-----|--------------|----------------------|
| `WelcomeIntro` | `signup_date IS NULL AND CURRENT_DATE <= registration_date + 21 days` | Menos de 21 días desde registro, no se ha inscrito |
| `NotSignedUp` | `signup_date IS NULL AND CURRENT_DATE > registration_date + 21 days` | Más de 21 días desde registro, no se ha inscrito |
| `SignedUp` | `signup_date IS NOT NULL OR _password IS NOT NULL` | Se inscribió en la plataforma |
| `MailingActive` | `(signup_date IS NOT NULL OR _password IS NOT NULL) AND promotional_email = true AND (last_login_date IS NOT NULL OR _password IS NOT NULL)` | Inscrito y acepta emails de marketing |

### Combinación de servicios (por compañía)

| Tag | Condición SQL | Significado de negocio |
|-----|--------------|----------------------|
| `ALLPrepaid` | `has_banking AND payroll_active AND NOT payroll_card` | Todos los servicios con tarjeta prepaid |
| `ALLPayroll` | `has_banking AND payroll_active AND payroll_card` | Todos los servicios con tarjeta payroll |
| `NWAPrepaid` | `has_banking AND NOT payroll_active AND NOT payroll_card` | Banking sin wage access, prepaid |
| `NWAPayroll` | `has_banking AND NOT payroll_active AND payroll_card` | Banking sin wage access, payroll |
| `MKTP` | `NOT has_banking AND NOT payroll_active` | Solo marketplace, sin banking ni EWA |
| `NB` | `NOT has_banking AND payroll_active` | Sin banking pero con EWA |

### Tipo de tarjeta

| Tag | Condición SQL | Significado de negocio |
|-----|--------------|----------------------|
| `PrepaidCard` | `has_banking AND NOT payroll_card` | Tiene/puede aplicar a tarjeta prepaid |
| `PayrollCard` | `has_banking AND payroll_card` | Tiene/puede aplicar a tarjeta payroll |

### Tarjeta activa

| Tag | Condición SQL | Significado de negocio |
|-----|--------------|----------------------|
| `ActivePrepaidCardholder` | `_flags->>'has_cpayments_account' = 'true' AND NOT payroll_card` | Ya tiene tarjeta prepaid activa |
| `ActivePayrollCardholder` | `_flags->>'has_cpayments_account' = 'true' AND payroll_card` | Ya tiene tarjeta payroll activa |

### Features

| Tag | Condición SQL | Significado de negocio |
|-----|--------------|----------------------|
| `EWA` | `payroll_active` | Tiene Early Wage Access (acceso anticipado a nómina) |
| `Remittances` | *(siempre true)* | Remesas habilitadas. **Nota**: PO solicitó que aplique a todos por ahora |
| `Ding` | `has_banking` | Mobile Top-ups habilitado (requiere banking) |
| `HealthInsurance` | `white_label_tag <> 'insperity'` | Seguro de salud habilitado (excluye Insperity) |

## Distribución actual en producción (2026-04-08)

Combinaciones más frecuentes:
- `Ding,NotSignedUp,NWAPrepaid,PrepaidCard,Remittances` — 31,080 usuarios
- `ALLPrepaid,Ding,EWA,NotSignedUp,PrepaidCard,Remittances` — 15,021 usuarios
- `ALLPrepaid,Ding,EWA,HealthInsurance,NotSignedUp,PrepaidCard,Remittances` — 5,708 usuarios
- `MKTP,NotSignedUp,Remittances` — 2,471 usuarios

Total de registros en la vista: 62,275

## Notas para futuras adiciones

- Si necesitas un campo nuevo de `users` o `companies`, asegúrate de que esté expuesto en el CTE `users_filter` o `companies_filter` respectivamente.
- Si necesitas una tabla nueva (ej: `users_features`), agrégala como LEFT JOIN en el CTE relevante.
- Si el tag depende de una relación 1:N, resuélvelo en un CTE previo con agregación antes de usar en `tag_mailing_logic`.
- El flag `_flags->>'has_cpayments_account'` se compara como string `= 'true'`, NO como `::boolean`, para evitar errores de runtime con datos inesperados en JSONB.
