/*  Least-privilege login for the advisor on a shared / non-local server.
    Not needed on your laptop if you use Windows authentication as sysadmin.
    Replace the password and database name before running.                */
USE master;
GO
CREATE LOGIN sql_ai_advisor WITH PASSWORD = 'Change_Me_Strong#2026';
GRANT VIEW SERVER STATE TO sql_ai_advisor;          -- wait stats, plan cache
GO
USE AdvisorDemo;   -- repeat for each database to analyse
GO
CREATE USER sql_ai_advisor FOR LOGIN sql_ai_advisor;
GRANT VIEW DATABASE STATE TO sql_ai_advisor;        -- Query Store, partition stats
GRANT VIEW DEFINITION TO sql_ai_advisor;            -- columns and indexes
-- No db_datareader, no write permissions: the tool never reads business data.
GO
