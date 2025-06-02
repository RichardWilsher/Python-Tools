import json
import mysql.connector
from mysql.connector import Error

# TODO: use describe to whitelist column names

def ensure_connection(method):
    def wrapper(self, *args, **kwargs):
        if not self.connection or not self.connection.is_connected():
            print(f"[DEBUG] Connection lost. Reconnecting for method: {method.__name__}")
            self.__init__(self.tablename)
        return method(self, *args, **kwargs)
    return wrapper

class orm:
    def __init__(self, table=None, settings_path=r'E:\Settings\dbsettings.json'):
        try:
            with open(settings_path) as json_file:
                dbsettings = json.load(json_file)
                self.connection = mysql.connector.connect(
                    host=dbsettings['hostname'],
                    port=dbsettings['port'],
                    user=dbsettings['username'],
                    password=dbsettings['dbpassword']
                )
                self.cursor = self.connection.cursor(buffered=True)
                self.tablename = table
        except Error as e:
            print(f"Error connecting to database: {e}")
            self.connection = None
            self.cursor = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def test_connection(self):
        if self.connection:
            return self.connection.is_connected()
        return False

    @ensure_connection
    def find(self, columns=None, column_name=None, value=None, order=None, fuzzy=False):
        try:
            if columns:
                if isinstance(columns, (list, tuple)):
                    columns_str = ", ".join([f"`{col.strip()}`" for col in columns])
                else:
                    columns_str = f"`{columns.strip()}`"
                query = f"SELECT {columns_str} FROM {self.tablename}"
            else:
                query = f"SELECT * FROM {self.tablename}"
            
            if column_name:
                if fuzzy:
                    query += f" WHERE {column_name} LIKE %s"
                    value = f"%{value}%"
                else:
                    query += f" WHERE {column_name} = %s"
        
            if order:
                query += f" ORDER BY {order}"
        
            if column_name:
                self.cursor.execute(query, (value,))
            else:
                self.cursor.execute(query)
            
            return self.cursor.fetchall()
        except Error as e:
            print("Query:", query)
            print("Value:", value)
            print(f"Error in find: {e}")
            return []
        
    @ensure_connection
    def describe(self):
        self.cursor.execute(f"DESCRIBE {self.tablename};")
        return self.cursor.fetchall()
    
    def getprimarykey(self):
        self.cursor.execute(f"SHOW KEYS FROM {self.tablename} WHERE Key_name = 'PRIMARY';")
        return self.cursor.fetchall()
    
    @ensure_connection
    def insert(self, column_names, column_values):
        try:
            columns = ", ".join([f"`{col}`" for col in column_names])
            placeholders = ", ".join(["%s"] * len(column_values))
            query = f"INSERT INTO {self.tablename} ({columns}) VALUES ({placeholders});"
            self.cursor.execute(query, column_values)
            self.connection.commit()
        except Error as e:
            self.connection.rollback()
            print(f"Error in insert: {e}")
            return False

    @ensure_connection
    def delete(self, column_name, value):
        try:
            query = f"DELETE FROM {self.tablename} WHERE `{column_name}` = %s;"
            self.cursor.execute(query, (value,))
            self.connection.commit()
        except Error as e:
            self.connection.rollback()
            print(f"Error in delete: {e}")
            return False

    @ensure_connection
    def update(self, set_column, set_value, where_column, where_value):
        try:
            query = f"UPDATE {self.tablename} SET `{set_column}` = %s WHERE `{where_column}` = %s;"
            self.cursor.execute(query, (set_value, where_value))
            self.connection.commit()
            return True
        except Error as e:
            self.connection.rollback()
            print(f"Error in update: {e}")
            return False  

    @ensure_connection
    def get_schemas(self):
        try:
            results = []
            self.cursor.execute("SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA;")
            schemas = self.cursor.fetchall()
            for schema in schemas:
                if schema[0] != "information_schema" and schema[0] != "mysql" and schema[0] != "performance_schema" and schema[0] != "sys": results.append(schema[0])
            return results
        except Error as e:
            print(f"Error in get_schemas: {e}")
            return []
    
    @ensure_connection
    def get_tables(self):
        try:
            results = []
            self.cursor.execute("SELECT TABLE_SCHEMA, TABLE_NAME FROM information_schema.tables;")
            tables = self.cursor.fetchall()
            for table in tables:
                if table[0] != "information_schema" and table[0] != "mysql" and table[0] != "performance_schema" and table[0] != "sys": results.append(table[0] + "." + table[1])
            return results
        except Error as e:
            print(f"Error in get_tables: {e}")
            return []

    def close(self):
        if self.connection:
            self.connection.close()