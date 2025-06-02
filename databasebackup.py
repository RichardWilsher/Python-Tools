# Program to read the contents of a MySQL database and write it to a SQL file
import orm
import time
import os

start_time = time.time()
output_path = "e:\\temp\\sql\\"

def writefile(filename, contents, prestring="", poststring=""):
    os.makedirs(output_path, exist_ok=True)
    new_filename = filename.replace('.', '_')
    filepath = os.path.join(output_path, new_filename + ".sql")

    with open(filepath, 'w', encoding="utf-8") as f:
        for line in contents:
            f.write(f"{prestring}{line}{poststring}\n")

def format_column_definition(column_tuple):
    """Extracts name and type from a column tuple for CREATE TABLE."""
    name, col_type = column_tuple[:2]
    name = name.strip("' ")
    col_type = col_type.strip("' ")
    return f"{name} {col_type if col_type else 'NULL'}"

def main():
    db = orm.orm()
    print("Backing up Schemas...")
    schemas = db.get_schemas()
    writefile("schemas", schemas, "CREATE SCHEMA `", "`;")

    tables = db.get_tables()
    for table in tables:
        print(f"Backing up {table}")
        temp_table = orm.orm(table)

        # Table structure
        table_results = temp_table.describe()
        table_array = [f"CREATE TABLE {table} ("]
        for i, col in enumerate(table_results):
            definition = format_column_definition(col)
            if i < len(table_results) - 1:
                definition += ","
            table_array.append(definition)
        table_array.append(");")

        # Table content
        for row in temp_table.find():
            row_str = str(row).replace("None", "NULL")
            table_array.append(f"INSERT INTO {table} VALUES {row_str};")

        # Primary key
        primary_key = temp_table.getprimarykey()
        if primary_key:
            col_name = primary_key[0][4]
            alter_stmt = (
                f"ALTER TABLE {table} CHANGE COLUMN {col_name} {col_name} INT NOT NULL AUTO_INCREMENT, "
                f"ADD PRIMARY KEY ({col_name});"
            )
            table_array.append(alter_stmt)

        writefile(table, table_array)

    db.close()
    print("Backup Complete")
    print("Completed in %.2f seconds" % (time.time() - start_time))

if __name__ == "__main__":
    main()
