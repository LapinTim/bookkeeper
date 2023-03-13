from dataclasses import dataclass
from datetime import datetime
from inspect import get_annotations
import sqlite3


# @dataclass
# class Test:
#     name: str
#     created: datetime
#     pk: int = 0



class SQLiteRepository(AbstractRepository[T]):
    def __init__(self, db_file: str, cls: type) -> None:
        self.db_file = db_file
        self.table_name = cls.__name__.lower()
        self.cls = cls
        self.fields = get_annotations(cls, eval_str=True)
        self.fields.pop('pk')
        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()
            res = cur.execute('SELECT name FROM sqlite_master')
            db_tables = [t[0].lower() for t in res.fetchall()]
            if self.table_name not in db_tables:
                col_names = ', '.join(self.fields.keys())
                q = f'CREATE TABLE {self.table_name} (' \
                    f'"pk" INTEGER PRIMARY KEY AUTOINCREMENT, {col_names})'
                cur.execute(q)
        con.close()

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

    def __generate_object(self, db_row: tuple) -> T:
        obj = self.cls(self.fields)
        for field, value in zip(self.fields, db_row[1:]):
            setattr(obj, field, value)
        obj.pk = db_row[0]
        return obj

    def get(self, pk: int) -> T | None:
        """ Получить объект по id """
        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()
            query_text = f'SELECT * FROM {self.table_name} WHERE PK = {pk}'
            row = cur.execute(query_text).fetchone()
        con.close()

        if row is None:
            return None

        return self.__generate_object(row)

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
            rows = cur.fetchall()
        con.close()

        if not rows:
            return None

        return [self.__generate_object(row) for row in rows]

    def update(self, obj: T) -> None:
        """ Обновить данные об объекте. Объект должен содержать поле pk. """
        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()
            query_text = f'UPDATE {self.table_name} SET '
            for name in self.fields.keys():
                query_text += f'{name} = {getattr(obj, self.fields[name])}'
            f' WHERE PK = {obj.pk}'
            cur.execute(query_text)
        con.close()

    def delete(self, pk: int) -> None:
        """ Удалить запись """
        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()
            query_text = f'DELETE FROM {self.table_name} WHERE PK = {pk}'
            cur.execute(query_text)
        con.close()

    @classmethod
    def repository_factory(cls):
        return {
            Category: cls('test.sqlite', Category),
            Expense: cls('test.sqlite', Expense),
            Budget: cls('test.sqlite', Budget)
        }
        