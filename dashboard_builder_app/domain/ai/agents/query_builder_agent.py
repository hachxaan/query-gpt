import re
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from .llm_base import LlmBase

# Load environment variables
load_dotenv()

DB_CONTEXT = """
DATABASE CONTEXT:
- **credit_status**: id (PRIMARY KEY), name, description, disabled, uuid (UNIQUE)
- **companies**: id (PRIMARY KEY), name (UNIQUE), url, tier, active, created, payroll_active, peo_company, peo_company_id, updated, logo_name, licensing_fee, unique_provider_id, white_label, worked_hours, external_id, white_label_tag, time_clock, hourly_limit_wa, timecard_connection_id, pct_hours, white_label_description, has_normal_hours
- **credits**: id (PRIMARY KEY), credit, tip, created, updated, disapproved, rating, rating_score, credit_max, instant, account_id, card_id, user_id (FOREIGN KEY REFERENCES users(id)), status_id (FOREIGN KEY REFERENCES credit_status(id)), tip_from_cashback, fee, level_id, tier_id, approval_code, transaction_id, error_message, tabapay_network_rc, deduction_check_key (UNIQUE), type, due_date, status, pending_credit, pending_fee, user_balance, paid_date, f_operation
- **users**: id (PRIMARY KEY), first_name, last_name, employment_date, cashback_balance, cashback_updated, registration_date, updated, inactive, city, state, zip_code, longitude, latitude, terms_conditions, promotional_sms, promotional_email, last_login_date, confirmed_email, cashadvance_guid (UNIQUE), users_codes_id, company_id (FOREIGN KEY REFERENCES companies(id)), admin_company, admin_multikrd, admin_peo, payroll_active, payroll_last_date, cashback_level, payroll_type, photo_name, promotional_phone_calls, last_sms_code, onboarding, cashback_historic, cashback_pending, level_id, tier_id, tier_expiration, wage_access_program, badge_points, key, payroll_frequency, connection_id, connection_data, tabapay_account_key, failed_login, admin_api, external_id, worked_hours, termination_date, end_stop_date, promotional_code, signup_date, direct_deposit, net_fees, time_management_key, provider_connections, last_extenal_token, email (UNIQUE), email_hash (UNIQUE), last_name, birthdate, street_address, address_line_2, mobile_phone, payroll_daily, payroll_hourly, payroll_salary, admin_level_1, admin_level_2, admin_report_1, admin_report_2, direct_deposit_id (UNIQUE), admin_multikrd_2, flags, customer_uuid

BUSINESS CONTEXT:
- **usuarios** = clientes, **usuario** = cliente, **empleado** = user
- **creditos** = credito = Wage Access = wage access = WA = wa = EWA
- **fee** = comisión, **fees** = comisiones
- Para saber si un usuario tiene banking, revisar si el campo users.customer_uuid no es nulo.
- Para white label, revisar el campo companies.white_label_tag.
- Relaciones de tablas:
  - users.company_id = companies.id
  - credits.user_id = users.id
  - credits.status_id = credit_status.id
- **credits.status_id** valores:
  - 1: created = ACH pendiente
  - 12: failed = failed
  - 13: approved = Wage access concedido o crédito aprobado o ACH pagado o creíto otorgado
  - 14: wage_deduction = Deducción o deducción de crédito o deducción de WA o deducción aplicada
  - 15: canceled = Cancelado
  - 16: wa_promotional_credit = Crédito Promocional WA
  - 17: wa_refund = Reembolso WA
- **credits.instant** valores:
  - True: crédito normal
  - False: ACH
  - NULL: deducciones
- **credits.status** valores:
  - 'ach': ACH
  - 'pending': pendientes
  - 'paid': pagados
  - 'pastDue': en past due
  - 'chargedOff': charge off
  - 'not_applied': deducción no aplica status
  - 'applied': deducción aplicada
- **users.payroll_type** valores:
  - 1: Daily
  - 2: Hourly
- **credits.type** valores:
  - 'Recurrent Solid Credit': Auto wage access vía Solid
  - 'Recurrent Tabapay Credit': Auto wage access vía Tabapay
  - 'Regular ACH Credit': ACH vía Tabapay
  - 'Regular Solid Credit': Instantáneo vía Solid
  - 'Regular Tabapay Credit': Instantáneo vía Tabapay
  - 'wage_access': Sin catalogar, pudieron ser Auto wage access o instantáneo, ambos vía Tabapay
""" 

class QueryBuilderAgent(LlmBase):
    def __init__(self, model="gpt-3.5-turbo-0125", dashboard_uuid=None, user_id=None, execute_actions_tool=True):
    # def __init__(self, model="gpt-4o", dashboard_uuid=None, user_id=None, execute_actions_tool=True):
        self.dashboard_uuid = dashboard_uuid.value
        self.user_id = user_id
        self.fields_list = None
        self.llm = ChatOpenAI(model=model)
        if execute_actions_tool:
            self.llm_with_tools = self.llm.bind_tools([self.execute_actions_tool])
        else:
            self.llm_with_tools = self.llm.bind_tools([self.test_query])

    def save_metadata(self, query, fields_list=None):
        """Callback para actualizar la última consulta ejecutada."""
        self.fields_list = fields_list

    def fix_query_callback(self, query, context, exception_message):
        """Corrige una consulta SQL con un contexto específico."""
        try:
            INSTRUCTIONS = (
                '- **Corrige la consulta SQL según el contexto proporcionado y la excepción optenida:**\n'
                '1. Usa el esquema en la sección "DATABASE CONTEXT".\n'
                '2. Asegúrate de que los campos sean correctos y estén en el orden correcto.\n'
                '3. Asegúrate de que las tablas y los campos existan en la base de datos.\n'
                '4. Asegúrate de que las relaciones entre tablas sean correctas.\n'
                '5. Asegúrate de que la sección "GROUP BY" tenga los campos correctos.\n'
                '6. Revisa el mensaje de excepción para corregir la consulta.\n'
                '- **Mensaje de excepción:**\n' + exception_message + '\n' +
                DB_CONTEXT + '\n' + context + '\n'
                'Bad SQL Query:\n' + query + '\n\n'
            )

            sql_agent = QueryBuilderAgent(dashboard_uuid=self.dashboard_uuid, user_id=self.user_id, execute_actions_tool=False)
            print(INSTRUCTIONS)
            response = sql_agent.fix_query(INSTRUCTIONS)
        except Exception as e:
            print(f'\033[91m{str(e)}\033[0m')
            response = self.fix_query_callback(response['query'], context, str(e))
        return {
            "query": response['query'],
            "data": response['data']
        }

    @staticmethod
    @tool
    def execute_actions_tool(
        query, 
        dashboard_uuid, 
        connection_platform, 
        connection_dashboard_builder, 
        save_metadata, 
        fields_list, 
        explain, 
        datatables_columns_config, 
        summary_context, 
        fix_query_callback, 
        save_session_context
    ):
        """Ejecuta una consulta SQL en la base de datos PostgreSQL y devuelve los resultados."""
        save_metadata(query, fields_list)
        try:
            with connection_platform.cursor() as cursor:
                cursor.execute(query)
                data = cursor.fetchall()
                final_query = query
        except Exception as e:
            print(f'\033[91m{str(e)}\033[0m')

            save_session_context(
                dashboard_uuid=dashboard_uuid, 
                chat_record=query, 
                connection=connection_dashboard_builder, 
                author='Model',
                close_connection=False
            )
            full_message = str(e)
            
            match = re.search(r"^(.*?)(?:\s+LINE\s+\d+:)?$", full_message, re.DOTALL)
            if match:
                exception_message = match.group(1)
            else:
                exception_message = full_message

            save_session_context(
                dashboard_uuid=dashboard_uuid, 
                chat_record=exception_message, 
                connection=connection_dashboard_builder, 
                author='Database'
            )
            response = fix_query_callback(query, summary_context, str(e))
            final_query = response['query']
            data = response['data']
        finally:
            connection_platform.close()

        return {
            "data": data,
            "fields_list": fields_list,
            "query": final_query,
            "explain": explain,
            "datatables_columns_config": datatables_columns_config,
            "summary_context": summary_context
        }

    def get_data(self, user_request):

        chat_history = self.retrieve_session_context(dashboard_uuid=self.dashboard_uuid, connection=self.connect_to('dashboard_builder'))

        self.save_session_context(
            dashboard_uuid=self.dashboard_uuid, 
            chat_record=user_request, 
            connection=self.connect_to('dashboard_builder'),
            author='Users'
        )
        user_instructions = "\n\nNEXT USER INSTRUCTIONS:\n**(" + user_request + ")**\n\n"

        if chat_history:
            instruction_1 = (
                "INSTRUCTIONS:\n"
                "1. Actualiza la última consulta generada ('NEXT USER INSTRUCTIONS' está haciendo referencia a la ultima consulta generada) y ejecútala con 'execute_actions_tool' según los requisitos del usuario, utilizando el esquema en la sección 'DATABASE CONTEXT'.\n"
            )
            chat_history = "CHAT CONTEXT (HISTORY):\n" + chat_history
        else:
            instruction_1 = (
                "INSTRUCTIONS:\n"
                "1. Crea una nueva consulta y ejecútala con 'execute_actions_tool' según los requisitos del usuario, utilizando el esquema en la sección 'DATABASE CONTEXT'.\n"
            )

        instructions = instruction_1 + (
            "2. Usa 'execute_actions_tool' con los siguientes parámetros, siempre debe trae valores los parámetros solicitados, todos son obligatorios y en el formato solicitado:\n"
            "     - **fields_list**: La lista de campos.\n"
            "     - **explain**: Tu explicación de SQL.\n"
            "     - **datatables_columns_config**: El objeto de columnas de DataTables con los campos obtenidos (datos y título),\n"
            "     para el título, usa nombres amigables para el usuario. Ejemplo: [{ data: 'id', title: 'ID' }, { data: 'email', title: 'Correo electrónico' }...].\n"
            "     - **summary_context**: Un resumen del contexto de la conversación.\n"
            "3. **IMPORTANTE:** No pidas confirmación ni respondas en 'contenido', ejecuta las instrucciones directamente sin confirmación, siempre usa tu 'execute_actions_tool'.\n"
            "4. Responde en el idioma que el usuario utiliza en sus requisitos.\n"
            "5. **IMPORTANTE:** Siempre usa la siguiente herramienta: 'execute_actions_tool'.\n"
            "6. **IMPORTANTE:** Usa la siguiente herramienta: 'execute_actions_tool'.\n"
            "7. **IMPORTANTE:** Usa siempre el alias de las tablas para evitar las referencias ambiguas cuando exista el mismo nombre de campo entre tablas'.\n"
            "8. **IMPORTANTE:** Pon atención cuando haya GROUP BY, beben estar los campos necesarios'.\n"
        )

        complete_context_with_query = DB_CONTEXT + "\n" + (chat_history if chat_history else "") + user_instructions + instructions

        print('............................................................')
        print(f'\033[92m{complete_context_with_query}\033[0m')
        print('............................................................')

        def transform_input(x):
            try:
                if not x.tool_calls:
                    raise ValueError(x.content)
                query = x.tool_calls[0]['args']["query"]
                fields_list = x.tool_calls[0]['args']["fields_list"]
                explain = x.tool_calls[0]['args']["explain"]
                datatables_columns_config = x.tool_calls[0]['args']["datatables_columns_config"]
                summary_context = x.tool_calls[0]['args']["summary_context"]
                return {
                    "query": query,
                    "dashboard_uuid": self.dashboard_uuid,  
                    "connection_platform": self.connect_to_platform(),
                    "connection_dashboard_builder": self.connect_to('dashboard_builder'),
                    "save_metadata": self.save_metadata,
                    "fields_list": fields_list,
                    "explain": explain,
                    "datatables_columns_config": datatables_columns_config,
                    "summary_context": summary_context,
                    "fix_query_callback": self.fix_query_callback,
                    "save_session_context": self.save_session_context
                }
            except Exception as e:
                print(f'\033[91m{str(e)}\033[0m')

        chain = self.llm_with_tools | transform_input | self.execute_actions_tool

        results = chain.invoke(complete_context_with_query)

        self.save_session_context(
            dashboard_uuid=self.dashboard_uuid, 
            chat_record= results['query'], 
            connection=self.connect_to('dashboard_builder'), 
            author='Model'
        )

        data_list_dict = [dict(zip(results['fields_list'], record)) for record in results['data']]

        print(f'\033[92m{results["query"]}\033[0m')
        return {
            "data": data_list_dict,
            "fields_list": results['fields_list'],
            "query": results['query'],
            "explain": results['explain'],
            "datatables_columns_config": results['datatables_columns_config'],
            "data_tupla": results['data']
        }

    def save_session_context(self, dashboard_uuid, chat_record, connection, author, close_connection=False):
        """Guarda el contexto de la sesión en la base de datos."""
        try:
            new_data = f"\n- **{author}**: {chat_record}"
            with connection.cursor() as cursor:
                cursor.execute("INSERT INTO sql_chat (dashboard_uuid, chat_context) VALUES (%s, %s) ON CONFLICT (dashboard_uuid) DO UPDATE SET chat_context = sql_chat.chat_context || %s", 
                               (dashboard_uuid, new_data, new_data))
                connection.commit()
        except Exception as e:
            print(str(e))
        finally:
            if close_connection:
                connection.close()

    def retrieve_session_context(self, dashboard_uuid, connection):
        """Recupera el contexto de la sesión de la base de datos."""
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT chat_context FROM sql_chat WHERE dashboard_uuid = %s", (dashboard_uuid,))
                result = cursor.fetchone()
                return result[0] if result else None
        finally:
            connection.close()

    @staticmethod
    @tool
    def test_query(query, connection_platform):
        """Ejecuta una consulta SQL en la base de datos PostgreSQL y devuelve los resultados."""
        with connection_platform.cursor() as cursor:
            cursor.execute(query)
            data = cursor.fetchall()
            return {
                "data": data,
                "query": query
            }

    def fix_query(self, instructions):
        complete_context_with_query = instructions + (
            "7. Usa la herramienta 'test_query' para verificar la consulta con los parámetros:\n"
            "     - **query**: Consulta corregida.\n"
            "8. No pidas confirmación en 'contenido', ejecuta las instrucciones directamente sin confirmación, siempre usa tu herramienta 'test_query'.\n"
        )

        print('............................................................')
        print(f'\033[92m{complete_context_with_query}\033[0m')
        print('............................................................')

        def transform_input(x):
            try:
                if not x.tool_calls:
                    raise ValueError(x.content)
                query = x.tool_calls[0]['args']["query"]
                return {
                    "query": query,
                    "connection_platform": self.connect_to_platform()
                }
            except Exception as e:
                print(f'\033[91m{str(e)}\033[0m')

        chain = self.llm_with_tools | transform_input | self.test_query
        return chain.invoke(complete_context_with_query)
