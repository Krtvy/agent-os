-- Tables in a schema — uses information_schema so the schema arg is a text
-- comparison, no identifier-injection surface.
SELECT
  table_schema,
  table_name,
  table_type
FROM information_schema.tables
WHERE table_schema = %(schema)s
ORDER BY table_type, table_name;
