import json        

cadena = '```json\n{\n    "respueta_chat": "Lista de usuarios inactivos",\n    "query": "SELECT id, first_name, _email, _birthdate, registration_date, last_login_date, mobile_phone, state, company_id, payroll_frequency, payroll_last_date, signup_date, inactive, terms_conditions, promotional_sms, promotional_email, _street_address, _address_line_2, _payroll_daily, _payroll_hourly, _payroll_salary, payroll_type, city, zip_code, promotional_code, payroll_active, _last_name FROM users WHERE inactive = true",\n    "field_info": "id, first_name, _email, _birthdate, registration_date, last_login_date, mobile_phone, state, company_id, payroll_frequency, payroll_last_date, signup_date, inactive, terms_conditions, promotional_sms, promotional_email, _street_address, _address_line_2, _payroll_daily, _payroll_hourly, _payroll_salary, payroll_type, city, zip_code, promotional_code, payroll_active, _last_name"\n}\n```'

cadena = cadena.replace('```json\n', '').replace('\n```', '')


resultado = json.loads(cadena)

print(json.dumps(resultado, indent=4))