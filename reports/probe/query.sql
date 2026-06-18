-- Probe — verifies portal → Supabase connectivity.
-- Returns one row, no parameters, no real data exposure.
SELECT
  1 AS ok,
  CURRENT_USER AS db_user,
  NOW() AT TIME ZONE 'Asia/Kolkata' AS server_time_ist;
