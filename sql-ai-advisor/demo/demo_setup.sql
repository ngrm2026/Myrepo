/*  Demo database for trying the advisor on your laptop.
    Creates AdvisorDemo with ~500k orders, deliberately missing a useful index,
    enables Query Store, and runs a few slow queries so there is something to diagnose.
    Run in SSMS / Azure Data Studio against your LOCAL instance only.          */
USE master;
GO
IF DB_ID('AdvisorDemo') IS NULL CREATE DATABASE AdvisorDemo;
GO
ALTER DATABASE AdvisorDemo SET QUERY_STORE = ON;
ALTER DATABASE AdvisorDemo SET QUERY_STORE (OPERATION_MODE = READ_WRITE,
     INTERVAL_LENGTH_MINUTES = 15, QUERY_CAPTURE_MODE = ALL);
GO
USE AdvisorDemo;
GO
DROP TABLE IF EXISTS dbo.Orders;
DROP TABLE IF EXISTS dbo.Customers;
GO
CREATE TABLE dbo.Customers (
    CustomerID   int IDENTITY PRIMARY KEY,
    CustomerName nvarchar(100) NOT NULL,
    Region       varchar(20)   NOT NULL
);
CREATE TABLE dbo.Orders (
    OrderID     int IDENTITY PRIMARY KEY,
    CustomerID  int           NOT NULL,
    OrderDate   datetime2(0)  NOT NULL,
    Status      varchar(20)   NOT NULL,
    Amount      decimal(12,2) NOT NULL,
    Notes       nvarchar(200) NULL
);
GO
-- 20k customers
INSERT dbo.Customers (CustomerName, Region)
SELECT TOP (20000) CONCAT(N'Customer ', ROW_NUMBER() OVER (ORDER BY (SELECT NULL))),
       CHOOSE(ABS(CHECKSUM(NEWID())) % 4 + 1, 'North', 'South', 'East', 'West')
FROM sys.all_objects a CROSS JOIN sys.all_objects b;

-- 500k orders over ~3 years
INSERT dbo.Orders (CustomerID, OrderDate, Status, Amount, Notes)
SELECT TOP (500000)
       ABS(CHECKSUM(NEWID())) % 20000 + 1,
       DATEADD(MINUTE, -ABS(CHECKSUM(NEWID())) % 1500000, SYSDATETIME()),
       CHOOSE(ABS(CHECKSUM(NEWID())) % 5 + 1, 'New', 'Paid', 'Shipped', 'Cancelled', 'Returned'),
       ABS(CHECKSUM(NEWID())) % 100000 / 100.0,
       N'note'
FROM sys.all_objects a CROSS JOIN sys.all_objects b;
GO

-- Slow pattern 1: no index on CustomerID/OrderDate -> clustered index scan
CREATE OR ALTER PROCEDURE dbo.GetCustomerOrders @CustomerID int, @From datetime2(0)
AS
SELECT o.OrderID, o.OrderDate, o.Status, o.Amount
FROM dbo.Orders o
WHERE o.CustomerID = @CustomerID AND o.OrderDate >= @From
ORDER BY o.OrderDate DESC;
GO

-- Slow pattern 2: non-SARGable predicate (function on column) + implicit conversion
CREATE OR ALTER PROCEDURE dbo.GetRegionSales @Region nvarchar(20), @Year int
AS
SELECT c.Region, SUM(o.Amount) AS Total, COUNT(*) AS Orders
FROM dbo.Orders o
JOIN dbo.Customers c ON c.CustomerID = o.CustomerID
WHERE c.Region = @Region AND YEAR(o.OrderDate) = @Year
GROUP BY c.Region;
GO

-- Generate workload
DECLARE @i int = 0;
WHILE @i < 40
BEGIN
    DECLARE @cust int = ABS(CHECKSUM(NEWID())) % 20000 + 1;
    DECLARE @from datetime2(0) = DATEADD(DAY, -180, SYSDATETIME());
    EXEC dbo.GetCustomerOrders @cust, @from;
    EXEC dbo.GetRegionSales N'North', 2025;
    SET @i += 1;
END;
GO
EXEC sp_query_store_flush_db;
GO
PRINT 'AdvisorDemo ready. Point SQL_DATABASE=AdvisorDemo in .env and load top queries.';
