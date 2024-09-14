# Program to read the contents of a MySQL database and write it to a SQL file
import databaseTools

import time

start_time = time.time()

path = "e:\\temp\\sql\\"

def writefile(filename, contents, prestring, poststring):
    new_filename = filename.replace('.', '_')
    output_path = path + new_filename + ".sql"
    output_file = open(output_path, 'w', encoding="utf-8")
    for line in contents:
        output_file.write(prestring + str(line) + poststring + "\n")
    output_file.close()

dbt = databaseTools.databaseTools()
print("Backing up Schemas...")
schemas = dbt.getSchemas()
writefile("schemas", schemas, "CREATE SCHEMA `", "`;")
tables = dbt.getTables()
for table in tables:
    print("Backing up " + table)
    table_results = dbt.describe(table)
    table_array = []
    table_array.append("CREATE TABLE " + table + " (")
    for index, table_result in enumerate(table_results):
        initial_format = str(table_result)
        bracket_removal = initial_format[1:-1]
        stripped_str = ','.join(str(bracket_removal).split(',')[:2])
        formatted_str = stripped_str.replace("'", "")
        final_str = formatted_str.replace(",", "")
        table_sql = str(final_str).replace("None", "NULL")
        if index != len(table_results) - 1:
            table_sql += ","
        table_array.append(table_sql)
    table_array.append(");")
    table_contents = dbt.findall(table)
    for table_content in table_contents:
        table_sql = "INSERT INTO " + table + " VALUES " + str(table_content).replace("None", "NULL") + ";"
        table_array.append(table_sql)
    primarykey = dbt.getprimarykey(table)
    # print(primarykey)
    if primarykey != None:
       query = ("ALTER TABLE " + table + " CHANGE COLUMN " + primarykey[0][4] + " " + primarykey[0][4] + " INT NOT NULL AUTO_INCREMENT , ADD PRIMARY KEY (" + primarykey[0][4] + ");")
       table_array.append(query)
    writefile(table, table_array, "", "")
    
dbt.close()
print("Backup Complete")
print("Completed in %.2f seconds" % (time.time() - start_time))