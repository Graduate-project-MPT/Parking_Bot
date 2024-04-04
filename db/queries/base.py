from sqlalchemy import BooleanClauseList
from ..classes import session

# Добавляет запись
def sql_add(data):
    try:
        session.add(data)
        session.commit()
        session.close()
        return True
    except Exception as e:
        print("\n\nsql_add\n", e, "\n\n\n")
        return False

# Удаляет запись
def sql_delete(data):
    try:
        session.delete(data)
        session.commit()
        session.close()
    except Exception as e:
        print("\n\sql_delete\n", e, "\n\n\n")

# Получения записей
def sql_query(class_example, filter_condition: BooleanClauseList):
    try:
        query_result = session.query(class_example).filter(filter_condition)
        session.close()
        return (query_result)
    except Exception as e:
        print("\n\sql_query\n", e, "\n\n\n")
        return None
