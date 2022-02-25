ROW_ACCESS_POLICY_SQL = """
CREATE ROW ACCESS POLICY ACCOUNT_OBJECTS.ACCESS_POLICIES.{table_name} AS
({input_cols_typed}) RETURNS BOOLEAN ->
{allowed_roles_clause}
{optional_or}
EXISTS (
  SELECT 1 FROM {mapping_table}
  WHERE {column_mappings_sql}
);
"""

APPLY_POLICY_SQL = """
ALTER TABLE {table_name}
ADD ROW ACCESS POLICY ACCOUNT_OBJECTS.ACCESS_POLICIES.{table_name}
ON ({input_cols_named});
"""

def create_row_access_policy(
	table_name,
	input_columns,
	mapping_table,
	column_mappings,
	allowed_roles,
    ):
    """
    :param table_name: the fully qualified table name
    :type table_name: str
    :param input_columns: the arguments to the policy in form [{'name': col_name, 'type': col_type},]
    :type input_columns: list
    :param mapping_table: the fully qualified table name for mapping values
    :type mapping_table: str
    :param column_mappings: mapping column names in the target table to the matching columns in the mapping table in form [(target_col1, mapping_col1),]
    :type column_mappings: list
    :param allowed_roles: roles that should have access to all rows regardless of logic
    :type allowed_roles: list
    """
    input_cols_named = ', '.join(x['name'] for x in input_columns)
    input_cols_typed = ', '.join([x['name'] + ' ' + x['type'] for x in input_columns])
    column_mappings_sql = '\nAND '.join([x[0] + ' = ' + x[1] for x in column_mappings])
    allowed_roles_clause = '\nOR '.join(["CURRENT_ROLE() = '{r}'".format(r=x) for x in allowed_roles])
    access_policy_sql = ROW_ACCESS_POLICY_SQL.format(
        table_name=table_name,
    	input_cols_typed=input_cols_typed,
	    allowed_roles_clause=allowed_roles_clause,
	    optional_or='OR ' if allowed_roles_clause else '',
	    mapping_table=mapping_table,
	    column_mappings_sql=column_mappings_sql,
    )
    apply_sql = APPLY_POLICY_SQL.format(
        table_name=table_name,
        input_cols_named=input_cols_named,
    )
    return access_policy_sql, apply_sql
