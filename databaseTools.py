import json
import mysql.connector

connection = None
cursor = None

class databaseTools:
    def __init__(self):
        with open('E:\\Settings\\dbsettings.json') as json_file:
            dbsettings = json.load(json_file)
            global connection
            connection = mysql.connector.connect(
                host=dbsettings['hostname'],
                port=dbsettings['port'],
                user=dbsettings['username'],
                password=dbsettings['dbpassword']
            )
            global cursor
            cursor = connection.cursor(buffered=True)

    def testConnection(self):
        global connection
        return connection.is_connected()

    def findall(self, tableName):
        global cursor
        cursor.execute(f"SELECT * FROM {tableName};")
        result = cursor.fetchall()
        return result
    
    def orderedfindall(self, tableName, order):
        global cursor
        cursor.execute(f"SELECT * FROM {tableName} ORDER BY {order};")
        result = cursor.fetchall()
        return result
    
    def selectedfindall(self, tablename, columns):
        global cursor
        cursor.execute(f"SELECT {columns} FROM {tablename};")
        result = cursor.fetchall()
        return result
    
    def orderedselecectedfindall(self, tablename, columns, order):
        global cursor
        cursor.execute(f"SELECT {columns} FROM {tablename} ORDER BY {order};")
        result = cursor.fetchall()
        return result

    def find(self, tableName, columnName, value):
        global cursor
        cursor.execute(f"SELECT * FROM {tableName} WHERE {columnName} = '{value}';")
        result = cursor.fetchall()
        return result
    
    def orderedfind(self, tableName, columnName, value, order):
        global cursor
        cursor.execute(f"SELECT * FROM {tableName} WHERE {columnName} = '{value}' ORDER BY {order};")
        result = cursor.fetchall()
        return result
    
    def fuzzyfind(self, tableName, value, columnName):
        global cursor
        columnName = columnName.upper()
        value = value.upper().replace("\n", "") 
        cursor.execute(f"SELECT * FROM {tableName} WHERE UPPER({columnName}) LIKE UPPER('%{value}%');")
        result = cursor.fetchall()
        return result
    
    def describe(self, tableName):
        global cursor
        cursor.execute(f"DESCRIBE {tableName};")
        result = cursor.fetchall()
        return result
    
    def getprimarykey(self, tableName):
        global cursor
        cursor.execute(f"SHOW KEYS FROM {tableName} WHERE Key_name = 'PRIMARY';")
        result = cursor.fetchall()
        return result
    
    def insert(self, tableName, columnNames, columnValues, types):
        global cursor
        global connection
        columns = ''
        values = ''
        for index,columnName in enumerate(columnNames):
            columns += (str(columnName))
            if(index != len(columnNames) - 1):
                columns += (', ')
        for index,columnValue in enumerate(columnValues):
            if (types[index] == "string"):
                values += ('"' + str(columnValue))
            else:
                values += ('\'' + str(columnValue))
            if(index != len(columnValues) - 1):
                if (types[index] == "string"):
                    values += ('", ')
                else:
                    values += ('\', ')
            else:
                if (types[index] == "string"):
                    values += ('"')
                else:
                    values += ('\'')
        cursor.execute(f"INSERT INTO {tableName} ({columns}) VALUES ({values});")
        connection.commit()

    def delete(self, tableName, columnName, value):
        global cursor
        cursor.execute(f"DELETE FROM {tableName} WHERE {columnName} = '{value}';")
        connection.commit()

    def update(self, tableName, columnName, value, columnName2, value2):
        global cursor
        cursor.execute(f"UPDATE {tableName} SET {columnName} = '{value}' WHERE {columnName2} = '{value2}';")
        connection.commit()    

    def getSchemas(self):
        results = []
        global cursor
        cursor.execute("SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA;")
        schemas = cursor.fetchall()
        for schema in schemas:
            if schema[0] != "information_schema" and schema[0] != "mysql" and schema[0] != "performance_schema" and schema[0] != "sys": results.append(schema[0])
        return results
    
    def getTables(self):
        global cursor
        results = []
        cursor.execute("SELECT TABLE_SCHEMA, TABLE_NAME FROM information_schema.tables;")
        tables = cursor.fetchall()
        for table in tables:
            if table[0] != "information_schema" and table[0] != "mysql" and table[0] != "performance_schema" and table[0] != "sys": results.append(table[0] + "." + table[1])
        return results

    def close(self):
        connection.close()