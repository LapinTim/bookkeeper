from dataclasses import dataclass
from datetime import datetime
from inspect import get_annotations
import sqlite3


# @dataclass
# class Test:
#     name: str
#     created: datetime
#     pk: int = 0



class SQLiteRepository:
    def __init__(self, db_file: str, cls: type) -> None:
        self.db_file = db_file
        self.table_name = cls.__name__.lower()
        self.fields = get_annotations(cls, eval_str=True)
        self.fields.pop('pk')

    def add(self, obj) -> int:
        names = ', '.join(self.fields.keys())
        placeholders = ', '.join("?" * len(self.fields))
        values = [getattr(obj, x) for x in self.fields]
        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()
            cur.execute('PRAGMA foreign keys = ON')
            cur.execute(
                f'INSERT INTO {self.table_name} ({names}) VALUES ({placeholders})',
                values
            )
            obj.pk = cur.lastrowid
        con.close()
        return obj.pk

    def get(self, pk: int) -> T | None:
        """ Получить объект по id """
        pass

    def get_all(self, where: dict[str, any] | None = None) -> list[T]:
        """
        Получить все записи по некоторому условию
        where - условие в виде словаря {'название_поля': значение}
        если условие не задано (по умолчанию), вернуть все записи
        """
        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()
            query_text = f'SELECT * FROM {self.table_name} WHERE 1=1'
            for key in where.keys():
                query_text += f'AND {key} = {where[key]}'
            cur.execute(query_text)
            res = cur.fetchall()
        con.close()
        return res

    def update(self, obj: T) -> None:
        """ Обновить данные об объекте. Объект должен содержать поле pk. """
        pass

    def delete(self, pk: int) -> None:
        """ Удалить запись """
        pass

    @classmethod
    def repository_factory(cls):
        return {
            Category: cls('test.sqlite', Category),
            Expense: cls('test.sqlite', Expense),
            Budget: cls('test.sqlite', Budget)
        }

    # def get(self, id) -> Query:
    #     return SelectQuery(fields=..., table=...)


r = SQLiteRepository('test.sqlite', Test)
o = Test('John')
r.add(o)
