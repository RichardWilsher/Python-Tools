# Program to convert a CSV file to a SQL file
import csv

def csv_to_sql_insert(file_path, output_file):
    with open(file_path, 'r') as file:
        reader = csv.reader(file)
        field_names = next(reader)  # Read the field names from the first row

        sql_statements = []
        for row in reader:
            columns = ', '.join(field_names[:]) 
            values = ', '.join(["'{}'".format(value) for value in row[:]])
            table_name = 'staff'

            sql_statement = f"INSERT INTO {table_name} ({columns}) VALUES ({values});"
            sql_statements.append(sql_statement)

    with open(output_file, 'w') as output:
        for statement in sql_statements:
            output.write(statement + '\n')

# Usage example
csv_path = 'E:\\temp\\Moch_Data\\MOCK_DATA.csv'
sql_path = 'E:\\temp\\Moch_Data\\MOCK_DATA.sql'
csv_to_sql_insert(csv_path, sql_path)