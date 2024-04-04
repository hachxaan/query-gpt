import os
import re
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.contrib.auth import get_user_model
from django.db import models
from rolepermissions.roles import AbstractUserRole
import sqlparse
from sqlparse.sql import Identifier
from marketing_queries.settings import openai_adapter
from cryptography.fernet import Fernet

replacements = {
    'email': '_email',
    'last_name': '_last_name',
    'birthdate': '_birthdate',
    'street_address': '_street_address',
    'address_line_2': '_address_line_2',
    'mobile_phone': '_mobile_phone',
    'payroll_daily': '_payroll_daily',
    'payroll_hourly': '_payroll_hourly',
    'payroll_salary': '_payroll_salary'
}

class FernetSingleton:
    class __FernetSingleton:
        def __init__(self):
            key_str = os.getenv('DB_KEY')
            key_bytes = key_str.encode('utf-8')
            key_base64 = key_bytes.decode()
            self.fernet = Fernet(key_base64)
    instance = None

    def __init__(self):
        if not FernetSingleton.instance:
            FernetSingleton.instance = FernetSingleton.__FernetSingleton().fernet

    def __getattr__(self, name):
        return getattr(self.instance, name)        

# Definición de los roles
class AdminMultikrd(AbstractUserRole):
    available_permissions = {
        "administer_users": True,
        "administer_queries": True,
    }


class AdminMarketing(AbstractUserRole):
    available_permissions = {
        "manage_queries": True,
    }


class UserMarketing(AbstractUserRole):
    available_permissions = {
        "execute_queries": True,
    }


# Definición del modelo de usuario
class User(AbstractUser):
    ROLES = (
        ("AdminMultikrd", "AdminMultikrd"),
        ("AdminMarketing", "AdminMarketing"),
        ("UserMarketing", "UserMarketing"),
    )

    role = models.CharField(
        "role", max_length=15, choices=ROLES, default="UserMarketing"
    )

    groups = models.ManyToManyField(
        Group, blank=True, related_name="custom_user_groups"
    )
    user_permissions = models.ManyToManyField(
        Permission, blank=True, related_name="custom_user_permissions"
    )


class process(models.Model):
    id = models.AutoField(primary_key=True)
    query = models.TextField()
    table_template = models.TextField()
    chart_template = models.TextField()
    chat_history = models.JSONField()
    javasctipt_code = models.TextField()

    def add_formatted_message_to_chat_history(self, message_json):
        """
        Agrega un mensaje al historial de chat, formateando según el contenido del mensaje.
        
        :param message_json: Un diccionario que representa el mensaje.
        """
        # Inicializa el mensaje formateado
        formatted_message = {   
            "sender": message_json.get("sender", ""),
            "text": message_json.get("text", "")
        }
        
        # Si el mensaje tiene un request_type de 1 o 2 y contiene una clave 'query'
        if message_json.get("request_type") in ["1", "2"] and "query" in message_json:
            # Formatea el mensaje como un código
            formatted_message["text"] = f"{message_json.get('text', '')}\nEsta es la consulta:\n<code>{message_json['query']}</code>"
        
        # Agrega el mensaje formateado al historial de chat
        self.add_message_to_chat_history(formatted_message)

    # Métodos get y set para query
    def get_query(self):
        return self.query
    
    def set_query(self, query):
        self.query = query
        self.save()

    # Métodos get y set para table_template
    def get_table_template(self):
        return self.table_template
    
    def set_table_template(self, table_template):
        self.table_template = table_template
        self.save()

    # Métodos get y set para chart_template
    def get_chart_template(self):
        return self.chart_template
    
    def set_chart_template(self, chart_template):
        self.chart_template = chart_template
        self.save() 
    
    # Métodos get y set para chat_history
    def get_chat_history(self):
        return self.chat_history
    
    def set_chat_history(self, chat_history):
        self.chat_history = chat_history
        self.save()
    
    # Métodos específicos para chat_history
    def add_message_to_chat_history(self, message):
        if self.chat_history is None:
            self.chat_history = []
        self.chat_history.append(message)
        self.save()
        
    def get_last_message_from_chat_history(self):
        return self.chat_history[-1] if self.chat_history else None
    
    @classmethod
    def get_or_create_by_id(cls, id, **kwargs):
        try:
            # Intenta buscar el registro por id
            instance = cls.objects.get(id=id)
        except cls.DoesNotExist:
            # Si no se encuentra el registro, se crea uno nuevo sin los argumentos adicionales
            instance = cls.objects.create(id=id)
            
            # Usa los argumentos adicionales para agregar un mensaje al historial del chat
            instance.add_formatted_message_to_chat_history(kwargs)
            
        return instance

# Definición del modelo de consulta
class Query(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(db_column='title', max_length=64, blank=True, null=False) 
    description = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)
    sql_query = models.TextField()

    class Meta:
        permissions = [("execute_query", "Can execute queries")]

    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.pk:  # Solo asignar el autor si es un nuevo objeto (creación)
            self.author = self.request.user
        super().save(*args, **kwargs)

    def replace_fields(self, query, replacements):
        for old, new in replacements.items():
            query = query.replace(old, new)
        return query

    def get_identifiers(self, tables, fields, query):
        pattern = re.compile(r'concat\((.*?)\)', re.IGNORECASE | re.DOTALL)

        # Parsea la consulta
        parsed_query = sqlparse.parse(query)[0]

        if parsed_query.get_type() != 'SELECT':
            raise ValueError("Only allowed SELECT sentence")
    
        if '*' in str(query):
            raise ValueError("Only specified fields are allowed")

        # Extrae las tablas y los campos de la consulta

        from_seen = False
        for token in parsed_query.tokens:
            # if token.value.upper() == 'CONCAT':
            #     print(token)
            if not from_seen:
                if token.ttype is None and isinstance(token, sqlparse.sql.IdentifierList):
                    for identifier in token.get_identifiers():
                        match = pattern.search(identifier.value)

                        if match:
                            # Extraer el grupo que contiene los nombres de los campos
                            fields_string = match.group(1)
                            # Limpiar y separar los nombres de campo basados en comas, excluyendo literales entre comillas
                            raw_fields = [field.strip() for field in fields_string.split(',') if not field.strip().startswith(("'", '"'))]
                            
                            # Añadir nombres de campo al conjunto, eliminando posibles prefijos de tabla/alias
                            for field in raw_fields:
                                # Excluye las cadenas literales que puedan estar presentes
                                if "'" not in field and '"' not in field:
                                    field_name = field.split('.')[-1]  # Tomar solo el nombre del campo, ignorando alias de tabla
                                    fields.add(field_name)


                        elif '.' in str(identifier):
                            _, field = str(identifier).split('.')
                            fields.add(field)
                        else:
                            fields.add(str(identifier))
                elif token.ttype is None and isinstance(token, sqlparse.sql.Identifier):
                    if '.' in str(token):
                        fields.add(field)
                    else:
                        fields.add(str(token))
                elif token.ttype is None and isinstance(token, sqlparse.sql.Where):
                    from_seen = False
                    for identifier in token.tokens:
                        if isinstance(identifier, sqlparse.sql.Comparison):
                            for id in identifier.get_identifiers():
                                if '.' in str(id):
                                    fields.add(field)
                                else:
                                    fields.add(str(id))
                                    
            if token.ttype is None and token.is_group:
                if from_seen:
                    if isinstance(token, sqlparse.sql.Identifier):
                        tables.add(token.get_real_name())
                    else:
                        
                        if isinstance(token, sqlparse.sql.Parenthesis):
                            tables, fields = self.get_identifiers( tables, fields, str(token.value).strip('()') )
                        # else:
                        #     if not isinstance(token, sqlparse.sql.Comparison) and not isinstance(token, sqlparse.sql.Where):
                        #         for identifier in token.get_identifiers():
                        #             tables.add(str(identifier))

            else:
                if token.ttype is sqlparse.tokens.Keyword and token.value.upper() == 'FROM':
                    from_seen = True
        
        return tables, fields
       

    def is_query_allowed(self):
        def remove_tables_from_fields(fields, tables):
            fields_set = set(fields)
            tables_set = set(tables)
            return fields_set.difference(tables_set)
        # Reemplaza los campos en la consulta
        replacements_reverse = {value: key for key, value in replacements.items()}
        query = self.replace_fields(self.sql_query, replacements_reverse)

        
        tables = set()
        fields = set()
        tables, fields = self.get_identifiers(tables, fields, query)


        # Verifica que las tablas estén permitidas
        for table in tables:
            if not AllowedTable.objects.filter(name=table).exists():
                raise ValueError("Table is not allowed")


        fields = remove_tables_from_fields(fields, tables)
        # Verifica que los campos estén permitidos
        for field in fields:
            # Verifica si el campo existe en alguna de las tablas permitidas
            exists = False
            for table in tables:
                table_obj = AllowedTable.objects.get(name=table)
                if AllowedField.objects.filter(table=table_obj, name=field).exists():
                    exists = True
                    break
            if not exists:
                raise ValueError(f"Field '{field}' is not allowed")

        return True

    def analyze_with_chat_gpt(self, query):
        tables = self.get_allowed_tables()
        fields = self.get_allowed_fields()
        response = openai_adapter.validate_query(tables, fields, query)
        status, *message = response.split(" ", 1)
        print(status)
        if re.search(re.compile(r"error", re.IGNORECASE), message[0]):
            raise ValueError(f"The query is invalid: {message[0]}")
        elif not re.search(re.compile(r"OK", re.IGNORECASE), message[0]):
            raise ValueError(f"unexpected answer: {response}")

    def get_allowed_tables(self):
        allowed_tables = AllowedTable.objects.values_list("name", flat=True)
        formatted_tuple = tuple(allowed_tables)
        return str(formatted_tuple)

    def get_allowed_fields(self):
        allowed_fields = AllowedField.objects.values_list("name", "description")
        formatted_tuple = tuple(f"{replacements.get(name, name)}: {description}" for name, description in allowed_fields)
        formatted_string = ", ".join(formatted_tuple)
        return formatted_string
        
    def decrypt(self, data: bytes):
        fernet = FernetSingleton()
        if data:
            return fernet.decrypt(data).decode()
        else:
            return None
 
    def save(self, *args, **kwargs):

        for k, v in replacements.items():
            self.sql_query = re.sub(rf"\b{k}\b", v, self.sql_query)

        self.is_query_allowed()
        # self.analyze_with_chat_gpt(self.sql_query)
        
        super().save(*args, **kwargs)


class AllowedTable(models.Model):
    name = models.CharField(max_length=128, unique=True)

    def __str__(self):
        return self.name


class AllowedField(models.Model):
    table = models.ForeignKey(AllowedTable, on_delete=models.CASCADE)
    name = models.CharField(max_length=128)
    description = models.TextField()

    class Meta:
        unique_together = ("table", "name")

    def __str__(self):
        return f"{self.table.name}.{self.name}"
