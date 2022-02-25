MASKING_POLICY_SQL = """
CREATE MASKING POLICY PROD.ACCESS_POLICIES.{field_name}_MASK AS
({field_name} {field_type}) RETURNS {field_type} ->
CASE 
{body}
END;
"""

APPLY_POLICY_SQL = """
ALTER TABLE {table_name}
MODIFY COLUMN {column_name}
SET MASKING POLICY PROD.ACCESS_POLICIES.{field_name};
"""

WHEN_CLAUSE_SQL = "WHEN CURRENT_ROLE() = '{role}' THEN {return_val}"


def create_column_masking_policy(
	table_name,
	field_name,
    field_type,
    columns,
    role_mapping,
    allowed_roles,
    else_value
    ):
    """
    :param table_name: the fully qualified table name
    :type table_name: str
    :param field_name: the type of value i.e., 'phone' or 'email'
    :type field_name: str
    :param field_type: the snowflake type of the field
    :type field_name: str
    :param columns: the columns to apply the policy to
    :type columns: list
    :param role_mapping: logical statements and their return value. i.e., [{'role': "current_role() = 'HR_ADMIN'", 'return_val': 'phone'}]
    :type role_mapping: list
    :param allowed_roles: roles that should always see the unmasked column
    :type allowed_roles: list
    :param else_value: the value that should be returned if not an allowed role
    :type else_value: string
    """
    for role in allowed_roles:
        role_mapping.append({'role': role, 'return_val': field_name})
    when_clauses = '\n'.join([WHEN_CLAUSE_SQL.format(role=x['role'], return_val=x['return_val']) for x in role_mapping])
    else_case = 'ELSE ' + else_value
    body = when_clauses + '\n' + else_case
    mask_sql = MASKING_POLICY_SQL.format(
        field_name=field_name,
        field_type=field_type,
        body=body,
    )
    apply_sql = []
    for column in columns:
        apply_sql.append(APPLY_POLICY_SQL.format(
            table_name=table_name,
            column_name=column,
            field_name=field_name,
        ))
    return mask_sql, '\n'.join(apply_sql)

m,a = create_column_masking_policy(
    table_name='tbl_name',
    field_name='phone',
    field_type='varchar',
    columns=['employee_phone'],
    role_mapping=[{'role': 'HR_ADMIN', 'return_val': 'phone'}],
    allowed_roles=['SYSADMIN'],
    else_value="'***READACTED***'"
    )
print(m)
print(a)   