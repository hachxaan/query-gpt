# src\shared\tools\utils.py

import hashlib

from sqlalchemy import inspect
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.ext.hybrid import hybrid_property


from sqlalchemy import inspect
from sqlalchemy.orm import class_mapper


from sqlalchemy import inspect
from sqlalchemy.orm import class_mapper


def row2dict(r, follow_backrefs=False):
    mapper = class_mapper(r.__class__)
    result = {column.key: getattr(r, column.key) for column in mapper.columns}

    for name, relation in mapper.relationships.items():
        if not follow_backrefs and relation.backref:
            continue
        related_obj = getattr(r, name)
        if related_obj is not None:
            if relation.uselist:
                result[name] = [
                    row2dict(obj, follow_backrefs=follow_backrefs) for obj in related_obj]
            else:
                result[name] = row2dict(
                    related_obj, follow_backrefs=follow_backrefs)
    return result


def row2dict_naa(r):
    mapper = inspect(r)
    columns = r.__table__.columns
    hybrid_properties = [key for key, value in mapper.__dict__.items(
    ) if isinstance(value, (InstrumentedAttribute, hybrid_property))]

    result = {c.name: getattr(r, c.name) for c in columns}

    for prop_name in hybrid_properties:
        value = getattr(r, prop_name)
        if value is not None:
            result[prop_name] = value

    return result


def row2dict_old(r):
    columns = r.__table__.columns
    hybrid_properties = inspect(type(r)).all_orm_descriptors.values()
    hybrid_property_names = [
        prop.__name__ for prop in hybrid_properties if isinstance(prop, property)]

    result = {c.name: getattr(r, c.name) for c in columns}

    for prop_name in hybrid_property_names:
        value = getattr(r, prop_name)
        if value is not None:
            result[prop_name] = value

    return result


class HashGenerator:
    _instance = None
    _hash_length = 10  # Default length of the hash

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def set_hash_length(cls, length):
        cls._hash_length = length

    def generate_hash(self, input_number):
        input_str = str(input_number)
        hasher = hashlib.sha256()
        hasher.update(input_str.encode('utf-8'))
        hash_hex = hasher.hexdigest()
        return hash_hex[:self._hash_length]


def row2dict_dep(r): return {c.name: getattr(r, c.name)
                             for c in r.__table__.columns}
