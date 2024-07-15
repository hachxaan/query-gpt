# query_builder_app/models/query.py

import re
from django.db import models
import sqlparse
from query_builder_app.models.allow_fields import AllowedField
from query_builder_app.models.allow_tables import AllowedTable
from query_builder_app.utils.fernet import FernetSingleton
from backoffice.settings import openai_adapter

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


class Query(models.Model):
    class Meta:
        db_table = 'query'

    id = models.AutoField(primary_key=True)
    title = models.CharField(db_column='title', max_length=64, blank=True, null=False) 
    description = models.TextField()
    author_id = models.IntegerField()
    active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)
    sql_query = models.TextField()
    is_public = models.BooleanField(default=False)

    class Meta:
        permissions = [("execute_query", "Can execute queries")]

    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.pk:  # Solo asignar el autor si es un nuevo objeto (creación)
            self.author_id = self.request.user.id
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

        # for k, v in replacements.items():
        #     self.sql_query = re.sub(rf"\b{k}\b", v, self.sql_query)

        # self.is_query_allowed()
        # self.analyze_with_chat_gpt(self.sql_query)
        
        super().save(*args, **kwargs)
