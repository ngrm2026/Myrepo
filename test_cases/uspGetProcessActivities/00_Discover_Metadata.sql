/*
    Metadata discovery for [WorkFlow].[uspGetProcessActivities]
    Run this before 01_Run_TestCases.sql to:
      - confirm parameter names, types and defaults
      - confirm the column layout of the table-valued parameter (TVP) types
      - see the first result set's shape
      - get the procedure source, so the expected results can be checked against it
    Read-only: it queries catalog views only.
*/
SET NOCOUNT ON;

-- 1. Procedure parameters
SELECT  p.parameter_id,
        p.name                         AS ParameterName,
        TYPE_NAME(p.user_type_id)      AS DataType,
        SCHEMA_NAME(t.schema_id)       AS TypeSchema,
        p.max_length,
        p.is_readonly                  AS IsTVP,
        p.has_default_value
FROM    sys.parameters p
JOIN    sys.types t ON t.user_type_id = p.user_type_id
WHERE   p.object_id = OBJECT_ID(N'[WorkFlow].[uspGetProcessActivities]')
ORDER BY p.parameter_id;

-- 2. TVP column layouts (the test harness assumes the column order shown here)
SELECT  SCHEMA_NAME(tt.schema_id) + '.' + tt.name AS TvpType,
        c.column_id,
        c.name                    AS ColumnName,
        TYPE_NAME(c.user_type_id) AS DataType,
        c.max_length,
        c.is_nullable
FROM    sys.table_types tt
JOIN    sys.columns c ON c.object_id = tt.type_table_object_id
WHERE   (SCHEMA_NAME(tt.schema_id) = N'Tag'      AND tt.name = N'TagModelTVP')
   OR   (SCHEMA_NAME(tt.schema_id) = N'WorkFlow' AND tt.name = N'ProcessActivityFilterValueTVP')
ORDER BY TvpType, c.column_id;

-- 3. First result set shape
SELECT  column_ordinal, name, system_type_name, is_nullable
FROM    sys.dm_exec_describe_first_result_set_for_object(OBJECT_ID(N'[WorkFlow].[uspGetProcessActivities]'), 0);

-- 4. Procedure source (copy into TestCases.md review if needed)
SELECT  OBJECT_DEFINITION(OBJECT_ID(N'[WorkFlow].[uspGetProcessActivities]')) AS ProcedureDefinition;

-- 5. Objects the procedure depends on (tables to look in for test data)
SELECT DISTINCT
        referenced_schema_name,
        referenced_entity_name
FROM    sys.dm_sql_referenced_entities(N'WorkFlow.uspGetProcessActivities', N'OBJECT')
WHERE   referenced_minor_id = 0
ORDER BY referenced_schema_name, referenced_entity_name;
