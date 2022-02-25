SECURE_VIEW_SQL = """
CREATE SECURE VIEW {database}.{schema}.{view} AS
(SELECT * FROM {table}
    WHERE
    {clauses});
"""


def create_secure_view(
    database,
    schema,
    view,
	table_name,
    logical_statements,
	allowed_roles=[],
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
    :param logical_statements: a series of logical statements to be joined together with OR
    :type logical_statements: list
    :param allowed_roles: roles that should have access to all rows regardless of logic
    :type allowed_roles: list
    """
    allowed_roles_sql = '\nOR '.join(['CURRENT_ROLE() = ' + x for x in allowed_roles])
    clauses = '\n OR '.join(logical_statements)
    if allowed_roles_sql:
        clauses += '\nOR ' + allowed_roles_sql
    secure_view_sql = SECURE_VIEW_SQL.format(
        database=database,
        schema=schema,
        view=view,
        table=table_name,
        clauses=clauses,
    )
    return secure_view_sql
