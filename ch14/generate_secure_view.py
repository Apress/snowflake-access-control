SECURE_VIEW_SQL = """
CREATE SECURE VIEW {database}.{schema}.{view} AS
(SELECT 
    {columns}
 FROM {table}
);
"""

def get_table_columns(database, schema, table_name):
    return ['employee_name', 'email', 'phone']

def create_secure_view(
    database,
    schema,
    view,
	table_name,
    column_role_mappings,
    ):
    """
    :param database: the database for the view
    :type database: str
    :param schema: the schema for the view
    :type schema: str
    :param view: the name of the view
    :type view: str
    :param table_name: the fully qualified table name
    :type table_name: str
    :param column_role_mappings: a column and its role to output mapping i.e.,
        {'email': {'role_maps': [{'role': 'HR_ADMIN', 'return_val': 'email'}], 'else': 'NULL'}}
    :type logical_statements: dict
    """
    cols = get_table_columns(database, schema, table_name)
    select_clause = []
    for col in cols:
        if column_role_mappings.get(col):
            col_logic = ['CASE ']
            mappings = column_role_mappings.get(col).get('role_maps')
            for mapping in mappings:
                col_logic.append(
                    'WHEN CURRENT_ROLE() = {r} THEN {v}'.format(
                        r=mapping['role'],
                        v=mapping['return_val'],
                    )
                )
            col_logic.append('ELSE {v}'.format(v=column_role_mappings.get(col).get('else', 'NULL')))
            col_logic.append('END AS {c}'.format(c=col))
            select_clause.append('\n'.join(col_logic))
        else:
            select_clause.append('col')
    select_clause_sql = ',\n'.join(select_clause)
    secure_view_sql = SECURE_VIEW_SQL.format(
        database=database,
        schema=schema,
        view=view,
        columns=select_clause_sql,
        table=table_name,
    )
    return secure_view_sql

s = create_secure_view(
    database='prod',
    schema='employees',
    view='contacts_cleaned',
    table_name='contacts',
    column_role_mappings={'email': {'role_maps': 
        [{'role': 'HR_ADMIN', 'return_val': 'email'},{'role': 'HR_USER', 'return_val': '*****@domain.com'}]},
        'else': 'NULL'},
    )
print(s)