# Azure Data Engineering Interview Prep: ADF + Databricks Pipeline

This guide covers an end-to-end Azure data pipeline built with **Azure Data Factory (ADF)**, **Azure Databricks**, **PySpark**, **Delta Lake**, cluster/compute tuning and the **Spark UI**. It contains:

1. [Project fact sheet](#1-project-fact-sheet): the one project story every answer uses
2. [How to deliver an answer](#2-how-to-deliver-an-answer)
3. [39 interview questions with model answers](#3-interview-questions-and-model-answers)
4. [Schema drift: general approach](#4-schema-drift-general-approach-bronze--silver--delta)
5. [Schema drift in ADF](#5-schema-drift-in-adf)
6. [Silver and gold layer code, explained line by line](#6-silver-and-gold-layer-code-line-by-line)
7. [Execution order and one-line summaries](#7-execution-order-and-one-line-summaries)
8. [Practice tools](#8-practice-tools)

> **Important:** the store count, table counts, data sizes, timings and incidents are realistic **examples**. Replace them with your real project's numbers before the interview. Interviewers will ask "how did you find that?" right after any number you give.

---

## 1. Project fact sheet

| Item | Detail |
|---|---|
| **Business** | Retail chain, ~420 stores. Sales, inventory and customer analytics for Power BI (replaced slow SSIS jobs). |
| **Sources** | On-prem SQL Server ERP (38 tables), Salesforce REST API (4 objects), vendor CSV files on SFTP (15–20/day). |
| **Volume** | ~25M changed rows/day, ~60 GB raw/day. Sales fact ~1.8B rows (~1.1 TB Delta). Inventory ~600M rows. Customer dim ~12M rows. |
| **Schedule & SLA** | Starts 01:00 IST, finishes ~04:15. Gold ready by 06:00; Power BI refresh 06:30. |
| **Orchestration** | ADF, metadata-driven (control table in Azure SQL DB), self-hosted IR on 2 VMs, tumbling window + storage event triggers. |
| **Compute** | Databricks job clusters, DBR 14.3 LTS. Workers Standard_E8ds_v5 (8 cores, 64 GB), driver D8ds_v5, autoscale 2–10, Photon on gold. |
| **Storage** | ADLS Gen2, Delta Lake, Unity Catalog. Bronze / silver / gold catalogs. |
| **Security** | Key Vault for all secrets, managed identities, UC storage credential through the Access Connector. No mounts. |
| **Team & role** | 5 data engineers. I owned the ingestion framework, silver/gold sales models and performance tuning. |
| **Headline results** | Pipeline 5.5 h to 3 h 15 m; silver MERGE 2 h 10 m to 28 m; compute cost −30% nightly, Databricks spend −35% over two quarters. |

**Flow**

```
SQL Server / Salesforce API / SFTP
   → ADF Copy (self-hosted IR, metadata-driven, watermark)
   → ADLS landing (Parquet/CSV)
   → Bronze (Auto Loader, raw + audit columns)
   → Silver (cast, standardise, DQ + quarantine, dedupe, MERGE, SCD2 dims)
   → Gold (star schema, SCD2 as-of keys, aggregates, OPTIMIZE/ZORDER)
   → Databricks SQL warehouse → Power BI
```

**Stories to have ready**

| Incident | Before → after |
|---|---|
| Silver MERGE with no date pruning, 350k small files, 80 GB spill | 2 h 10 m → 28 m |
| Null customer IDs (walk-ins) skewing the join | 35 m → 6 m |
| Product dim (180 MB) not broadcast | 14 m → < 4 m |
| Bronze vendor table with 400k × 2 MB files | query 3 min → 10 s |
| Per-notebook job clusters → one Workflows job cluster | −40 min start-up per night |
| Photon on the gold fact build | 48 m → 26 m |
| Python UDFs replaced with built-ins / broadcast lookup | 18 m → < 2 m |
| Revenue 0.8% low: UTC vs IST business date | fixed + daily reconciliation |
| `toPandas()` on 40M rows → driver OOM | aggregated in Spark instead |
| Region stopped sending data (volume check −18%) | alert at 3 AM, before business hours |
| ERP renamed `cust_no` → `customer_id` | caught by schema-drift check, fixed by config |

---

## 2. How to deliver an answer

- Use this order: **one line of context → what *I* did → a number → a trade-off or lesson.** That's what makes an answer sound like real experience.
- Say **"I"** for the work you owned and **"we"** for team decisions.
- Keep each answer to **1–2 minutes** and let the interviewer pull you deeper.
- Pick 2–3 incidents you can explain in full detail: how you found it, what you changed, and what you'd do differently.

---

## 3. Interview questions and model answers

### Project overview

#### Q1. Walk me through your pipeline end to end.

I worked on the analytics platform for a retail chain with around 420 stores. The goal was to give business teams one trusted source for sales, inventory and customer reporting in Power BI, replacing a set of slow SSIS jobs.

We have three kinds of sources: an on-prem SQL Server ERP with 38 tables we need, Salesforce for customer data through its REST API, and vendor CSV files dropped on SFTP. Azure Data Factory orchestrates everything. It reads a control table in Azure SQL DB that lists each source table, its load type and its watermark column, and copies the data incrementally into a landing zone in ADLS Gen2 through a self-hosted integration runtime.

From landing, Databricks takes over with a medallion design. Bronze is raw data in Delta, ingested with Auto Loader, plus audit columns like load timestamp and source file name. Silver is cleaned and conformed: data types fixed, duplicates removed, and records merged on business keys, with SCD Type 2 for customer and product. Gold is a star schema with fact sales, fact inventory and conformed dimensions, plus some pre-aggregated tables that Power BI reads through a Databricks SQL warehouse.

The whole run starts at 1 AM and usually finishes around 4:15, against a 6 AM SLA. My ownership was the ingestion framework, the silver and gold sales models, and most of the performance tuning.

#### Q2. Why ADF for orchestration and Databricks for transformation?

Each tool is strongest at a different job. ADF is very good at connectivity and orchestration. It has 90-plus connectors, the self-hosted integration runtime to reach our on-prem SQL Server behind the firewall, built-in retries, scheduling and monitoring. Copying data with the Copy activity is also cheap compared with running a Spark cluster just to move bytes.

Databricks is where the heavy transformation happens: joins across a 1.8-billion-row sales fact, MERGE operations, SCD2, window functions. Doing that in ADF mapping data flows would have cost more and given us less control. With Databricks we write PySpark and SQL that we can version in Git, unit test, and tune using the Spark UI.

So ADF moves data and decides when things run. Databricks decides what the data becomes. We did consider running everything in Databricks Workflows. We kept ADF because the enterprise already used it for other teams, the SHIR was already set up and approved by the network team, and the operations team monitors ADF centrally.

#### Q3. Data volumes, number of tables, SLA?

Daily we bring in around 25 million new or changed rows, about 60 GB of raw data. Most of that comes from the sales and inventory tables. The ERP gives us 38 tables, Salesforce 4 objects, and vendors send roughly 15 to 20 CSV files a day.

The biggest table is the sales line fact at about 1.8 billion rows, roughly 1.1 TB in Delta. Inventory snapshots are around 600 million rows. The dimensions are small; customer is about 12 million rows.

The SLA is that gold tables are refreshed before 6 AM IST, because the Power BI datasets refresh at 6:30 and regional managers look at the reports at 9. The pipeline starts at 1 AM. When I joined, the run took about five and a half hours and we breached the SLA a few times a month. After the tuning work I'll talk about, it runs in about three hours fifteen minutes.


### Azure Data Factory

#### Q4. Linked services, datasets and integration runtimes? When do you need a self-hosted IR?

Our linked services were: SQL Server on-prem, ADLS Gen2, Azure SQL DB for the control table, Key Vault, Azure Databricks, REST for Salesforce, and SFTP for the vendor files. All of them except Key Vault get their secrets from Key Vault, and ADLS and Databricks use ADF's managed identity, so there are no keys in ADF itself.

For datasets we kept it generic. Instead of 38 datasets for 38 tables, we have one parameterized SQL Server dataset that takes schema and table name, and one parameterized Parquet dataset for ADLS that takes container, folder and file name. The control table fills those parameters at runtime.

For integration runtimes, cloud-to-cloud copies use the Azure AutoResolve IR. The on-prem SQL Server and the SFTP server sit inside the corporate network, so we use a self-hosted IR installed on two Windows VMs in that network. Two nodes give us high availability and let copies run in parallel. You need a self-hosted IR whenever the source is on-prem or in a private network that the Azure IR can't reach. The other option is a managed VNet IR with private endpoints, but that only works for Azure-hosted sources.

#### Q5. How did you build a metadata-driven pipeline?

We have a control table in Azure SQL DB with one row per source object. The columns are source system, schema, table name, load type (full or incremental), watermark column, last watermark value, target path, primary key columns, an active flag and a load group.

The master pipeline starts with a Lookup activity that reads active rows for a given load group. That output goes into a ForEach activity, with sequential turned off and batch count set to 8, so eight tables copy in parallel. Inside the ForEach, a child pipeline does the per-table work. A second Lookup gets the current max watermark from the source. A Copy activity runs a dynamic query like select star from table where modified_date greater than old watermark and less than or equal to new watermark, and writes Parquet to landing. Then a Stored Procedure activity updates the watermark in the control table, and only on success.

The big benefit is that onboarding a new table is just an insert into the control table. When the business asked for six more ERP tables, it took us half a day instead of a sprint. We also log row counts, duration and status to an audit table from the same pipeline.

#### Q6. How do you implement incremental loads?

It depends on the source. For most ERP tables we used a high-watermark approach on a last-modified timestamp column. We store the last successful watermark in the control table. Each run we read the current max value from the source first and copy the rows between the old and new value. The upper bound matters: if rows are inserted while the copy is running, they're picked up next time instead of being missed.

Some tables had no reliable modified date. For two big ones we enabled SQL Server Change Tracking with the DBA team and read the changes using the version number as the watermark. That also gives us deletes, which a timestamp watermark can't. Small reference tables, under a hundred thousand rows, we just full-load every night. It isn't worth the complexity.

For vendor files on SFTP, the Copy activity filters by last modified date, using the trigger window start and end. Downstream, Auto Loader keeps track of which files it has already processed. One lesson: always confirm the watermark column is indexed on the source. Our first incremental query on the sales table did a full scan and the DBA team noticed very quickly.

#### Q7. How do you pass parameters from ADF to a notebook and return a value?

In the Databricks Notebook activity we set base parameters. In our case these were things like load date, source table name, batch id and environment, filled with ADF expressions such as the pipeline trigger time or an item from the ForEach. In the notebook I read them with `dbutils.widgets.get`, and I define the widgets with defaults so the notebook still runs on its own during development.

To send something back, the notebook ends with `dbutils.notebook.exit` and a JSON string, for example the rows inserted, rows updated and a status. In ADF that's available as `@activity('nb_silver_sales').output.runOutput`. The next activity uses it: we write those counts to the audit table, and an If Condition fails the pipeline when rows read is zero for a table that should never be empty.

```python
dbutils.widgets.text("load_date", "")
load_date = dbutils.widgets.get("load_date")
# ... processing ...
dbutils.notebook.exit(json.dumps({"rows_in": n_in, "rows_merged": n_merged, "status": "OK"}))
```

#### Q8. Schedule, tumbling window or storage event trigger?

We used two kinds. The main nightly ERP load runs on a tumbling window trigger with a 24-hour window. I chose it over a schedule trigger because tumbling windows keep state for each window. If a run fails, I can rerun exactly that window, and backfill is built in: when we onboarded history, I set the start date in the past and it created one run per day. It also passes window start and window end as parameters, which map neatly to our incremental filter. And it supports dependencies between triggers and a max concurrency setting.

The vendor files arrive at unpredictable times, so for those we use a storage event trigger on blob created in the landing container, filtered on the folder path and a `.csv` suffix. It uses Event Grid behind the scenes, so the subscription has to be registered. A schedule trigger would only make sense for simple fire-and-forget jobs that don't need backfill.

#### Q9. How do you handle failures in ADF?

Several layers. Every Copy and Notebook activity has a retry count of 2 with a 5-minute interval. That handles most transient problems, like a SHIR node restart or a throttled API. Inside the ForEach, each table runs in its own child pipeline, so one failing table doesn't stop the others.

On the failure path of each child pipeline, we log the error message and the table name to the audit table and call a Logic App that posts to our Teams support channel. Critical failures also go to email. Azure Monitor alerts on failed pipeline runs act as a backup.

For reruns, because each table has its own watermark that's only updated on success, I can rerun the master pipeline and only the failed tables actually move new data. The successful ones copy nothing new. ADF also has "rerun from failed activity" in the monitor, which we used for one-off issues. The key design rule was idempotency. Every step can be rerun safely, so on-call doesn't have to work out what partly ran.

#### Q10. How did you promote ADF from dev to test to prod?

Only the dev factory is connected to Git, an Azure DevOps repo. Developers work in feature branches and raise a pull request into the main collaboration branch, and one reviewer must approve. Test and prod factories are never edited by hand.

Instead of clicking Publish in the UI, we used the automated publish approach. Our build pipeline uses the ADF utilities npm package to validate the factory and generate the ARM templates from main. The release pipeline then deploys those templates to test and, after approval, to prod. Environment-specific values such as Key Vault URLs, the Databricks workspace URL and the storage account name are parameterized in the ARM template parameters file and overridden for each stage. We also used global parameters for the environment name.

One detail people miss: triggers must be stopped before deployment and started again after. We used the Microsoft pre- and post-deployment PowerShell script for that, and it also deletes resources that were removed in dev. Databricks notebooks were deployed separately through Databricks Asset Bundles in the same release.

#### Q11. How are secrets handled?

Nothing is stored in ADF or in notebooks. All passwords, the SQL Server credentials, the Salesforce client secret and the SFTP key are in Azure Key Vault. ADF has a Key Vault linked service, and every other linked service references a secret by name. ADF's system-assigned managed identity has the Key Vault Secrets User role, which only allows reading secrets.

Where possible we avoid secrets entirely. ADF connects to ADLS and Databricks with its managed identity. Databricks reaches ADLS through a Unity Catalog storage credential backed by the Access Connector's managed identity, so no storage keys exist anywhere.

In Databricks, the few secrets we need, like the Salesforce API secret, come from a Key Vault-backed secret scope with `dbutils.secrets.get`, and Databricks redacts them in notebook output. Each environment has its own Key Vault, so dev engineers can never read prod secrets.


### Databricks and compute

#### Q12. All-purpose versus job cluster: which did ADF use?

Production runs on job clusters only. A job cluster is created for the run and terminated when it finishes, and job compute is billed at a much lower DBU rate than all-purpose compute, roughly less than half. It's also isolated: one job's libraries or memory problems can't affect another job.

All-purpose clusters are for development and ad-hoc analysis, with auto-termination at 30 minutes and a cluster policy that limits their size.

One improvement I made: originally ADF had a separate Notebook activity for each silver table, each creating a new job cluster. That's about five minutes of start-up each time, and with 15 notebooks a lot of time was wasted. I moved the silver and gold logic into a Databricks Workflows job, where all tasks share one job cluster, and ADF triggers that job. That alone saved about 40 minutes of cluster start time per night. Where we still start clusters from ADF, we use an instance pool so nodes come from warm VMs.

#### Q13. How did you size your cluster?

I sized from the workload, not by guessing. The silver sales MERGE and the gold fact build are shuffle-heavy joins, so I picked memory-optimized workers, Standard_E8ds_v5 with 8 cores and 64 GB each, plus local SSD for shuffle spill. The driver is a Standard_D8ds_v5. Our driver does little work, but I didn't want it too small because of broadcast joins and query planning on big tables.

The job cluster autoscales between 2 and 10 workers. To set the max, I looked at the Spark UI for the heaviest stage. It shuffled about 300 GB, which at around 128 MB per partition is about 2,400 tasks. With 80 cores that's about 30 waves of tasks, which finished in our time budget. More nodes gave diminishing returns, because the job was then limited by MERGE commit and file writing.

I also checked the cluster metrics. CPU was around 70 to 80 percent and there was no heavy spill, which told me the size was right. The small ingestion jobs use a separate tiny cluster, one to two workers, so we don't pay for big nodes to read small tables. Job clusters terminate when the job ends. All-purpose clusters auto-terminate after 30 minutes idle.

#### Q14. What is Photon, and did you enable it?

Photon is Databricks' native vectorized query engine, written in C++. It replaces parts of the JVM-based Spark execution engine for SQL and DataFrame operations: scans, filters, joins, aggregations and Delta writes. It processes data in columnar batches, which uses the CPU much more efficiently.

We enabled it on the gold job and on the SQL warehouse for Power BI, and tested it on silver. The gold fact build, which is mostly joins and aggregations, went from about 48 minutes to 26 minutes. Photon has a higher DBU rate, but the run was nearly twice as fast, so total cost went down.

On the ingestion job it made almost no difference, because that job is I/O-bound and the cost isn't worth it there. Photon doesn't speed up Python UDFs or RDD code. Those fall back to normal Spark, so check the query plan for Photon operators to confirm it's being used.

#### Q15. How did you control Databricks cost?

We cut monthly Databricks spend by about 35 percent over two quarters, with a few levers.

First, all scheduled workloads moved to job clusters from all-purpose clusters, which was the single biggest saving. Second, cluster policies. Developers can only create clusters from approved node types, with a max of 4 workers and auto-termination forced to 30 minutes or less. Every cluster must carry cost-center tags, which we use for chargeback reports. Third, spot instances for workers with fallback to on-demand, while the driver stays on-demand so a spot eviction can't kill the job. Our nightly jobs tolerate losing a worker because Spark just retries those tasks.

Fourth, right-sizing from the Spark UI. Some jobs were on 10 workers but only used 3. Fifth, instance pools to reduce start-up time, which is billed VM time too. And finally, the data work itself: OPTIMIZE, partition pruning and avoiding full-table MERGEs reduced runtime, and that is the biggest cost driver. We review the system billing tables in a monthly dashboard to catch any job whose cost suddenly grows.

#### Q16. How does Databricks access ADLS? Why are mounts discouraged?

We use Unity Catalog. There's an Access Connector for Azure Databricks with a managed identity that has Storage Blob Data Contributor on the storage account. In Unity Catalog that's registered as a storage credential, and on top of it we created external locations for the landing container. Bronze, silver and gold are managed catalogs on their own storage.

Engineers never handle keys or service principal secrets. Access is controlled with grants: for example, the ingestion service principal can read files from the landing external location, and analysts get SELECT only on gold.

The older project I supported used mount points with a service principal. Mounts are discouraged because a mount is visible to every user in the workspace with the same credential behind it, so there's no per-user access control. There's also no audit of who read what, and the secret has to be rotated and re-mounted. Unity Catalog gives fine-grained permissions, lineage and audit logs, and works across workspaces. We migrated those mounts to external locations as part of our Unity Catalog adoption.


### PySpark

#### Q17. Transformations vs actions; narrow vs wide transformations.

Transformations like select, filter, withColumn and join are lazy. They only build the logical plan. Actions like count, write, collect or display trigger execution, and that's when Catalyst optimizes the whole plan, which is why filters get pushed down to the source.

Narrow transformations, such as filter, select and withColumn, work on each partition independently with no data movement. Wide transformations, such as groupBy, join, distinct, orderBy and window functions, need a shuffle, because rows with the same key have to end up in the same partition. Every shuffle creates a new stage boundary in the Spark UI.

In our silver sales notebook, filtering on load date and casting columns are narrow. The window function for deduplication and the join with the product dimension are wide. Knowing that, I filter and select only the needed columns before the join, so less data is shuffled. I also learned to avoid stray actions. An early version called count for logging after every step, and each count recomputed the plan from the source, which nearly doubled the runtime. Now we take metrics from the Delta operation history after the write instead.

#### Q18. How did you remove duplicates?

Duplicates came from two places: the same record changing more than once between loads, and vendors sometimes resending a file. dropDuplicates on the business key removes duplicates, but which row it keeps isn't deterministic, so you might keep an older version. That's fine only when the rows are exact copies.

For silver I used row_number over a window partitioned by the business key and ordered by the modified timestamp descending, with ingestion time as a tie-breaker, and kept rank one. That always keeps the latest version, which is what MERGE needs. Delta MERGE actually fails if multiple source rows match the same target row, so deduplicating first is required, not optional.

```python
w = Window.partitionBy("order_id", "line_no").orderBy(F.col("modified_ts").desc(), F.col("_ingest_ts").desc())
dedup = src.withColumn("rn", F.row_number().over(w)).filter("rn = 1").drop("rn")
```

For exact duplicate rows inside a file, a plain dropDuplicates is fine and cheaper. Then the MERGE makes the load idempotent against what's already in the table.

#### Q19. How did you implement SCD Type 2?

Customer and product dimensions are SCD2 because the business wanted sales reported by the customer's segment and region at the time of sale. Each row has a surrogate key, the business key, effective_from, effective_to, an is_current flag and a hash of the tracked columns, so change detection is one comparison instead of comparing 20 columns.

A changed customer needs two actions: close the old row and insert a new one. A single MERGE can only act once on each matched row, so I used the staged union technique. The changed records appear twice in the source: once with the real key to expire the old row, and once with a null merge key so they fall into the insert branch.

```sql
MERGE INTO gold.dim_customer t
USING (
  SELECT s.customer_id AS merge_key, s.* FROM stg_customer s
  UNION ALL
  SELECT NULL AS merge_key, s.* FROM stg_customer s
  JOIN gold.dim_customer t ON s.customer_id = t.customer_id AND t.is_current
  WHERE s.row_hash <> t.row_hash
) src
ON t.customer_id = src.merge_key AND t.is_current
WHEN MATCHED AND t.row_hash <> src.row_hash THEN
  UPDATE SET is_current = false, effective_to = src.effective_from
WHEN NOT MATCHED THEN
  INSERT (customer_id, name, segment, region, row_hash, effective_from, effective_to, is_current)
  VALUES (src.customer_id, src.name, src.segment, src.region, src.row_hash, src.effective_from, NULL, true)
```

The fact load looks up the surrogate key where the sale date falls between effective_from and effective_to. That way history is reported correctly even after a customer moves region.

#### Q20. How do you handle schema drift and bad records?

Bronze is flexible and silver is strict. In bronze, Auto Loader uses schema inference with a schema location and schemaEvolutionMode set to addNewColumns. When the ERP added a column, the stream stopped once, picked up the new schema and continued on restart. Our job retries automatically, so nobody had to intervene. Any value that doesn't match the expected type goes into the `_rescued_data` column instead of being lost.

Silver has an explicit schema. Delta schema enforcement rejects unexpected changes, and we add new columns there deliberately through a code change. That stops a source change from silently breaking the gold model.

For vendor CSVs, which were the messiest, we read in PERMISSIVE mode with a corrupt-record column. Rows that fail parsing, or fail our checks like a negative quantity or an unknown store code, go to a quarantine table with the reason and the file name. We alert if the quarantine count passes a threshold. On a few loads we also used badRecordsPath. The principle is to never fail the whole load because of a few bad rows, and never drop bad rows silently either.

#### Q21. What is a broadcast join, and when did you use it?

In a broadcast join, Spark sends a full copy of the small table to every executor. Each partition of the big table joins locally, and the big table isn't shuffled at all. Without it, Spark does a sort-merge join, which shuffles and sorts both sides.

Spark broadcasts automatically when the smaller side's estimated size is below `spark.sql.autoBroadcastJoinThreshold`, which is 10 MB by default. With AQE, Spark can also switch to a broadcast join at runtime if a side turns out to be small after filtering.

In our gold fact build, the store dimension (420 rows) and the date dimension were broadcast automatically. The product dimension was about 180 MB, so it wasn't. I added an explicit broadcast hint, and on the sales fact join that cut that stage from about 14 minutes to under 4, because the 1.8-billion-row side no longer shuffled. I wouldn't broadcast anything over a few hundred MB, though. The table is collected to the driver first, so it can cause driver out-of-memory errors and slow the job down. For customer, at 12 million rows, we kept sort-merge.

#### Q22. repartition versus coalesce?

repartition does a full shuffle and can increase or decrease the number of partitions. You can also repartition by a column, so data is evenly distributed or grouped by key. coalesce only reduces the number of partitions, by merging existing ones without a shuffle, so it's cheaper but can give uneven partitions.

I used coalesce when writing small outputs, for example an extract file for a downstream team, where 200 tiny files would be silly. I used repartition by date before writing a large daily output, so each date was written by a balanced set of tasks instead of many tiny files.

One mistake to avoid, which I saw in an older notebook: coalesce(1) on a big DataFrame before writing. That pushes the whole upstream computation into a single task, because coalesce doesn't add a stage boundary. It took 40 minutes. Changing it to repartition(1), or better, letting Delta optimized writes handle file sizes, fixed it. On Delta tables I rarely repartition by hand now. Optimized writes and auto compaction handle file sizing.

#### Q23. Why avoid Python UDFs, and what did you use instead?

A regular Python UDF is a black box to Catalyst. Spark can't optimize through it or push filters past it, and Photon can't run it. Worse, each row is serialized from the JVM to a Python worker process and back, which is very slow at scale.

In our project, an earlier developer wrote a Python UDF to standardize phone numbers and another to map store codes. On 25 million rows that step took about 18 minutes. I rewrote the phone logic with built-in functions, regexp_replace, substring and when-otherwise. The store mapping became a broadcast join to a small lookup table instead of a Python dictionary inside a UDF. The step dropped to under 2 minutes.

If logic really can't be expressed with built-ins, I'd use a pandas UDF, which uses Apache Arrow and processes vectorized batches. It's much faster than a row-by-row UDF. A SQL UDF also works for simple reusable expressions, because it gets inlined into the plan.

#### Q24. Did you use Auto Loader or Structured Streaming?

Yes, bronze ingestion uses Auto Loader, which is the cloudFiles source in Structured Streaming. It reads the Parquet and CSV files that ADF lands in ADLS. It handles incremental file discovery for us: it keeps track of which files are processed, so even if ADF writes thousands of files we never reprocess or miss one.

The checkpoint location stores the stream's progress, the offsets and the list of ingested files (in RocksDB), so a restart continues exactly where it stopped. Each source table has its own checkpoint, and you must never share or casually delete one. Deleting a checkpoint means reprocessing everything.

We don't need real-time data, so we run it with `trigger(availableNow=True)`. It processes all new files available at that moment, in batches, then stops, and the cluster terminates. It works like a batch job but keeps streaming's exactly-once file tracking. For file discovery we started with directory listing and switched to file notification mode for the vendor folder, which had grown to hundreds of thousands of files and was slow to list.

```python
(spark.readStream.format("cloudFiles")
   .option("cloudFiles.format", "parquet")
   .option("cloudFiles.schemaLocation", schema_path)
   .load(landing_path)
   .withColumn("_ingest_ts", F.current_timestamp())
   .withColumn("_source_file", F.col("_metadata.file_path"))
 .writeStream.option("checkpointLocation", ckpt_path)
   .trigger(availableNow=True)
   .toTable("bronze.erp.sales_line"))
```


### Delta Lake

#### Q25. What does Delta give you over plain Parquet?

Delta is Parquet files plus a transaction log, the `_delta_log` folder. That log is what gives us everything else.

First, ACID transactions. A failed write leaves no partial data, and readers never see half-written results. With plain Parquet, a failed job could leave half the files behind. Second, MERGE, UPDATE and DELETE, which our silver and SCD2 logic depend on, plus deletes for GDPR requests. Third, schema enforcement and controlled evolution. Fourth, time travel. When a bad deployment wrote wrong discount values into gold, we compared with the previous version and used `RESTORE TABLE` to go back in minutes instead of reloading. Fifth, performance: file-level statistics for data skipping, OPTIMIZE, and Z-ordering or liquid clustering.

We also enabled Change Data Feed on a few silver tables so gold could read only the changed rows instead of rescanning.

#### Q26. OPTIMIZE, Z-order / liquid clustering, VACUUM: how often, and what's the risk?

OPTIMIZE compacts many small files into larger ones of about 1 GB. Z-ORDER BY rewrites the data so that rows with similar values in the chosen columns sit in the same files, which makes data skipping effective for filters on those columns. On the sales fact we Z-ordered by store_id and product_id because most Power BI queries filter on those, and the table was already partitioned by month. For newer tables we used liquid clustering with CLUSTER BY instead. It's incremental, and you can change the clustering keys without rewriting the table.

We run OPTIMIZE nightly on gold, after the load and before the Power BI refresh, and weekly on the big silver tables. VACUUM runs weekly with the default 7-day retention.

The risk with VACUUM is setting the retention too short. VACUUM deletes data files no longer referenced by the latest version, so you lose time travel beyond the retention period. A long-running query or a streaming job still reading an older version can also fail with file-not-found. Databricks blocks retention under 7 days unless you disable a safety check, and I'd never do that in production. VACUUM is also expensive on huge tables, so we schedule it off-peak.

#### Q27. What causes the small-file problem and how did you fix it?

Small files come from frequent small appends, streaming micro-batches, too many shuffle partitions at write time, and over-partitioning. Every file costs an open and a metadata read, so queries spend more time listing and opening files than reading data. The transaction log also grows.

We hit this on the bronze vendor table. Auto Loader ran several times a day and each batch wrote a few dozen small files. After a few months the table had around 400,000 files averaging about 2 MB, and a simple query took minutes just in planning.

The fix had three parts. I enabled `delta.autoOptimize.optimizeWrite`, which adds a shuffle before the write so files come out near 128 MB, and `autoCompact`, which compacts small files after a write. I ran a one-off OPTIMIZE to clean up the backlog, and scheduled regular OPTIMIZE. The file count fell to about 2,000 and that query went from 3 minutes to around 10 seconds. On new Unity Catalog managed tables we also turned on predictive optimization, which runs OPTIMIZE and VACUUM automatically.

#### Q28. How did you partition your tables? What goes wrong with over-partitioning?

Our rule: don't partition unless the table is large, roughly over a terabyte, and the partition column is low-cardinality and used in almost every filter. Each partition should hold at least about a gigabyte.

Only the sales fact, at about 1.1 TB, is partitioned, and by sale month, not by day. Partitioning by day would have made around 2,500 partitions with small files in each. Monthly partitions are a few GB each, and inside them we use Z-ordering for store and product. Most other tables aren't partitioned at all. We rely on data skipping statistics and clustering.

With over-partitioning, for example by date and store, you get hundreds of thousands of directories with tiny files. Metadata and listing overhead grows, OPTIMIZE can't help much because it only compacts within a partition, and queries that don't filter on the partition column get slower. A previous team had partitioned inventory by store and date. I migrated it to an unpartitioned table with liquid clustering on those columns, and both the load and the queries got faster.


### Spark UI and performance tuning

#### Q29. A 20-minute job now takes 2 hours. How do you debug it in the Spark UI?

First I check what changed: data volume, code deployment, cluster config, Databricks Runtime version. Our audit table tells me rows in for each run, so I can quickly see whether it's three times more data or the same data running slower.

Then the Spark UI. In the Jobs tab, I find which job takes the time. I drill into Stages and find the slow stage. There I look at the task summary metrics: min, median and max duration, shuffle read size, and spill. If the max task takes 40 minutes and the median 20 seconds, that's skew. If all tasks are slow and there's lots of spill, there's too much data per partition or not enough memory. If there are thousands of tiny tasks, it's a small-files or too-many-partitions problem.

Next the SQL / DataFrame tab, to read the physical plan. I check whether a join changed from broadcast to sort-merge, whether partition filters and file pruning actually applied (files read versus total), and whether the MERGE is scanning the whole target. The Executors tab shows GC time, failed tasks and lost executors, which point to memory pressure or spot evictions.

In one real case it was a MERGE that had stopped pruning. Someone had wrapped the date column in a function in the merge condition, so it scanned the entire 1.8-billion-row target. The plan showed all files being read. Fixing the condition brought it back to normal.

#### Q30. How do you identify data skew, and how did you fix it?

In the stage detail, the task summary shows it immediately. The median task finishes in seconds but the max takes many minutes, and the max shuffle read is several GB while the median is a few MB. Usually 199 tasks finish and the stage waits on one or two.

In our gold sales build, the join with the customer dimension was skewed. About 30 percent of sales were walk-in customers with a null customer id, and all of them hashed to the same partition. One task processed around 500 million rows.

There are a few fixes. First, AQE skew join handling, which is on by default in recent runtimes. It splits skewed partitions automatically, but only for sort-merge joins, and only when the partition passes its thresholds. Second, handle the hot key separately. For nulls, I mapped them to the "unknown customer" key, minus 1, before the join. That's also correct dimensional modelling. Third, salting for non-null hot keys: add a random salt from 0 to N to the big side, explode the small side N times, and join on key plus salt. Fourth, broadcast the smaller side if it's small enough. After handling the nulls, that stage went from 35 minutes to 6.

#### Q31. What is Adaptive Query Execution?

AQE re-optimizes the query plan during execution, using real statistics collected at each shuffle boundary, instead of relying only on estimates made before the job starts. It's on by default since Spark 3.2.

It does three main things. It coalesces shuffle partitions: if you set 2,000 shuffle partitions but a stage only produced 5 GB, it merges them into fewer, reasonably sized partitions, so you don't get thousands of tiny tasks. It switches join strategy: if one side turns out to be small after filters, it changes a sort-merge join into a broadcast hash join. And it handles skew joins by splitting oversized partitions into smaller tasks.

In practice, AQE meant I no longer had to tune shuffle partitions for every job. I set a higher starting value and let AQE coalesce. In the Spark UI's SQL tab you can see the plan marked as AdaptiveSparkPlan with isFinalPlan=true, and the AQE shuffle read nodes show how many partitions were coalesced or split.

#### Q32. What do spill (memory) and spill (disk) mean? How do you reduce them?

Spill happens when a task's data for a sort, aggregation or shuffle doesn't fit in execution memory, so Spark writes part of it to local disk and reads it back later. "Spill (memory)" is the size of that data in its in-memory form. "Spill (disk)" is the size of the same data once serialized and compressed on disk, so it's always smaller. Any spill means extra disk I/O and slower tasks.

We saw large spill, tens of GB, in the silver MERGE stage. The causes are usually too few shuffle partitions so each task gets too much data, skew so one task gets too much, or simply nodes with too little memory per core.

How I reduced it: more shuffle partitions, so each partition was around 128 to 200 MB. Fixing skew. Selecting only needed columns and filtering early, so less data was shuffled. Using memory-optimized nodes, from D-series to E-series, which doubled the memory per core. After that the spill went to almost zero and the stage was about 40 percent faster.

#### Q33. What does spark.sql.shuffle.partitions control? What value did you use?

It sets how many partitions are created after a shuffle in DataFrame and SQL operations, such as joins, groupBy and window functions. The default is 200, whatever the data size.

For 2 GB of shuffle, 200 is fine. Our gold fact build shuffles about 300 GB, which with 200 partitions means 1.5 GB per task: big spill and slow tasks. I aim for about 128 to 200 MB per partition, so about 300 GB divided by roughly 150 MB gives around 2,000. Then I make it a multiple of the total cores, 80 on the full cluster, so the waves of tasks are even. We used 2,000 for that job, set in the job's Spark config.

With AQE on, I treat it as the upper bound and let AQE coalesce down for smaller stages. On Databricks you can also set it to `auto`, which lets the optimizer choose. We used auto for the smaller jobs and kept an explicit value only for the heavy one, where we'd measured it.

#### Q34. Driver out-of-memory: common causes and fixes?

The common causes are collect, toPandas or display on a large DataFrame, which pulls all the data to the driver. Broadcasting a table that's too big, since it's collected on the driver first. Very large query plans, for example a loop that adds hundreds of withColumn calls or unions DataFrames repeatedly, so the plan grows huge. And listing or tracking a huge number of files or partitions.

We hit it once in a reconciliation notebook. A developer used toPandas on a 40-million-row DataFrame to compare counts in pandas. The fix was to do the comparison in Spark and only collect the small aggregated result.

Another time a job built a DataFrame in a loop over 300 columns with withColumn. The plan grew so large that planning alone took minutes and the driver ran out of memory. I replaced it with a single select using a list comprehension.

General fixes: never collect big data, and write it to a table instead. Lower the broadcast threshold or remove forced broadcast hints. Break very long lineage with a checkpoint or an intermediate write. Raise spark.driver.maxResultSize only if the result really needs to be bigger. Increase the driver size only as the last step, after fixing the code.

#### Q35. Tell me about a real performance problem you fixed, with numbers.

The silver sales MERGE was the biggest one. When I joined, that single step took about 2 hours 10 minutes, and it was the main reason the pipeline missed its 6 AM SLA about four times a month.

In the Spark UI I found three problems. First, the MERGE condition was only on order id and line number, so Delta had to scan all 1.8 billion target rows to find matches, even though 98 percent of daily changes were in the last 60 days. Second, the target had about 350,000 small files. Third, the join stage was skewed and spilled about 80 GB.

I fixed them in order. I added a date range predicate to the MERGE condition (target sale date within the min and max of the incoming batch), so file pruning kicked in and it read about 4 percent of the files. I compacted the table and enabled optimized writes. I Z-ordered on order date and order id. I raised shuffle partitions to 2,000 and moved to E-series nodes to remove the spill.

The MERGE went from 2 hours 10 minutes to 28 minutes. Together with the job cluster consolidation and Photon on gold, the full pipeline went from about five and a half hours to three hours fifteen. We haven't missed the SLA since, and the nightly compute cost dropped about 30 percent.


### Scenarios

#### Q36. The pipeline failed halfway through the silver load. How do you make the rerun idempotent?

We designed every step so that running it twice gives the same result as running it once.

At the table level, silver writes use MERGE on the business key, never a blind append. If the job failed after half the tables, rerunning simply merges the same rows again, and the matched rows are updated to the same values. Where we load whole slices, like a daily snapshot, we use `replaceWhere` on the load date, which atomically overwrites just that day. Delta transactions mean a single table write either commits fully or not at all, so there's never a half-written table.

At the pipeline level, the watermark in the control table only moves forward after the downstream step succeeds. A failed run therefore reprocesses the same window. Auto Loader's checkpoint guarantees bronze doesn't ingest the same file twice. Every row carries a batch id and load timestamp, so if we ever need to back out a bad batch, we can delete by batch id or use time travel.

In practice, when silver failed one night because a node went down, on-call just reran the job from the failed task in Databricks Workflows. There was no manual cleanup.

#### Q37. A source file arrived late, or twice. What does your pipeline do?

**Twice:** Auto Loader tracks file paths in its checkpoint, so the same file at the same path isn't ingested again. A vendor sometimes resent the same data under a new file name. That data gets into bronze, but in silver the deduplication on business key plus the MERGE means it only updates rows to identical values. No duplicates reach silver or gold. We also store a file hash in an audit table and alert when the same content arrives twice, so we can tell the vendor.

**Late:** our logic works on the business date inside the data, not on arrival time. A file for Monday that arrives on Wednesday is still loaded into Monday's sales, and the gold aggregates for the affected dates are recomputed. Gold rebuilds the last 7 days of aggregates every night for exactly this reason. Anything older triggers a targeted reprocessing of those dates.

For late-arriving dimensions, like a sale for a new product before the product record arrives, the fact gets the unknown member key, minus 1, so the sale isn't lost. A daily job re-points those facts once the product shows up. We also have a freshness check: if an expected vendor file hasn't arrived by 3 AM, the support channel is alerted before the SLA is at risk.

#### Q38. Gold doesn't match the source. How do you investigate?

First I make the question precise: which measure, which date range, which filter, and the source query they're comparing with. Half the time the difference is definitions, for example gross versus net sales, or returns included or excluded.

Then I reconcile layer by layer, starting at the source. Our audit table already has row counts and amount totals for each table and load date at source, bronze, silver and gold, so I can see at which layer the numbers split. If source and bronze match but silver doesn't, it's a dedupe or filter issue. If silver and gold differ, it's usually a join.

The most common root causes I've seen: inner joins to a dimension dropping facts with missing keys (the reason we switched to unknown-member keys), a time-zone difference between UTC timestamps and the IST business day, duplicates fanning out in a join, SCD2 rows overlapping and doubling a fact, and late data not yet loaded.

A real one: Finance reported gold revenue 0.8 percent lower than the ERP. Tracing a single day, I found orders placed between midnight and 5:30 AM IST were being assigned to the previous day, because we derived the date from the UTC timestamp. We fixed the conversion, reprocessed the history, and added a daily automated reconciliation against the source totals so it can't drift silently again.

#### Q39. How do you monitor data quality?

We built a lightweight, config-driven data quality framework in PySpark, similar in idea to Great Expectations or DLT expectations. Rules live in a table: table name, column, rule type, threshold, and severity, warn or fail.

The checks run as part of silver and gold. Completeness: not-null on keys and required columns. Uniqueness on business keys. Validity: ranges such as quantity and price, and allowed values like store codes. Referential integrity: facts whose dimension key is unknown, as a percentage. Volume: today's row count compared with the 7-day average, alerting if it's more than 30 percent off. Freshness: the max business date versus expected.

A failing "fail" rule stops the load before bad data reaches gold. "Warn" rules let the data through but log it. Bad rows go to a quarantine table with the reason. All results go to a DQ results table, and a small Power BI dashboard shows trends. Alerts go to Teams through the same Logic App as pipeline failures.

That volume check caught a real issue. A source system change meant one region's stores stopped sending data. Row counts dropped 18 percent, we got the alert at 3 AM, and we told the business before they saw wrong reports at 9.


#### Q40. The source team added two columns and renamed one without telling you. How does your ADF pipeline handle schema drift?

See [section 5](#5-schema-drift-in-adf). The spoken answer is at the end of that section.

---

## 4. Schema drift: general approach (bronze → silver → Delta)

**Schema drift** means the source structure changes without warning: a column is **added**, **removed** or **renamed**, a column's **type changes** (int → string), or nested JSON fields change.

**Approach:** be lenient in bronze, strict in silver, and stable in gold. Detect and alert on every change.

### 4.1 Bronze: Auto Loader keeps everything

```python
(spark.readStream.format("cloudFiles")
   .option("cloudFiles.format", "json")
   .option("cloudFiles.schemaLocation", schema_path)        # tracks schema versions
   .option("cloudFiles.schemaEvolutionMode", "addNewColumns")
   .option("cloudFiles.schemaHints", "amount DECIMAL(18,2), order_ts TIMESTAMP")
   .load(landing_path)
 .writeStream
   .option("checkpointLocation", ckpt_path)
   .option("mergeSchema", "true")                            # let the Delta table add the column
   .trigger(availableNow=True)
   .toTable("bronze.erp.orders"))
```

`schemaEvolutionMode` options:

| Mode | Behaviour |
|---|---|
| `addNewColumns` (default) | When a new column appears, the stream stops once with `UnknownFieldException`, then restarts with the new schema. Set **job retries** so this happens automatically. |
| `rescue` | The schema never changes; unexpected columns go to `_rescued_data`. |
| `failOnNewColumns` | Fails until someone updates the schema. Use for strict sources. |
| `none` | New columns are ignored. |

**`_rescued_data`** catches values with the wrong type, columns that differ only in letter case, and unknown fields, so nothing is lost silently.

### 4.2 Delta table behaviour

- **Schema enforcement** is on by default: a write with an unexpected column or type fails.
- **Add a column:** `.option("mergeSchema","true")`. For MERGE, use `MERGE WITH SCHEMA EVOLUTION INTO ...` (newer runtimes) or `spark.databricks.delta.schema.autoMerge.enabled=true`.
- **Widen a type** (int → bigint, float → double): **type widening** (`delta.enableTypeWidening`), with no table rewrite.
- **Rename or drop a column:** enable column mapping (`delta.columnMapping.mode = 'name'`). After that, `ALTER TABLE ... RENAME COLUMN` and `DROP COLUMN` change only metadata.
- **Incompatible change** (string → int): there's no automatic fix. Use a controlled `overwriteSchema`.

### 4.3 Silver: enforce a contract

```python
expected = {"order_id":"bigint","store_id":"int","amount":"decimal(18,2)","order_ts":"timestamp"}

def conform(df):
    cols = {c.lower(): c for c in df.columns}
    return df.select([
        (F.expr(f"try_cast(`{cols[c]}` AS {t})") if c in cols else F.lit(None).cast(t)).alias(c)
        for c, t in expected.items()
    ])
```

Rows where a cast fails (the value is not null but the cast result is null) go to a **quarantine** table. New columns reach silver and gold only through a reviewed code change.

### 4.4 Detect and alert

```python
def schema_diff(df, expected):
    inc = {f.name.lower(): f.dataType.simpleString() for f in df.schema.fields}
    exp = {k.lower(): v for k, v in expected.items()}
    return {"added":   sorted(inc.keys() - exp.keys()),
            "removed": sorted(exp.keys() - inc.keys()),
            "changed": sorted(c for c in inc.keys() & exp.keys() if inc[c] != exp[c])}
```

Write the result to an audit table and alert Teams whenever any list is non-empty.
- **Removed column:** it turns null downstream, which is usually a source bug.
- **Renamed column:** shows up as one *added* plus one *removed*. Map it in the config table.
- **Changed type:** widen the column type or quarantine the rows.

Over the long term, agree a **data contract** with the source team.

### 4.5 Interview answer (about 1 minute)

> "We handle schema drift layer by layer. Bronze is tolerant. Auto Loader runs with a schema location and `addNewColumns`, with schema hints for important types, so a new source column is added automatically. The job retries, so the one-time restart needs no manual work. Values that don't fit the schema go to `_rescued_data` instead of being dropped. Silver is strict: we select an explicit column contract with `try_cast`, quarantine rows that fail, and new columns only reach silver and gold through a reviewed code change. For renames and type widening we use Delta column mapping and type widening, so we don't rewrite the table. A schema-diff check compares every load with the expected schema stored in our control table, logs the differences and alerts Teams. That's how we caught the ERP team renaming `cust_no` to `customer_id`: it showed up as one added and one removed column, we mapped it in config the same morning, and gold never broke."

---

## 5. Schema drift in ADF

Pattern: **land the data as-is → detect what changed → apply safe changes automatically → stop and alert on breaking changes.**

### 5.1 Copy activity

**a) Keep the generic datasets schema-less.** Don't import a schema in parameterized datasets. A fixed dataset schema can drop new columns or cause failures.

**b) Default mapping into file sinks.** With no explicit mapping, the Copy activity maps columns **by name, case-sensitive**. A Parquet/CSV sink in ADLS takes the source schema, so new columns land automatically. This is why landing raw files first and letting Databricks evolve the Delta schema is the most drift-friendly design.

**c) Dynamic mapping from the control table.** Store the mapping JSON in the control table and set Mapping → *Add dynamic content* → `@json(item().ColumnMapping)`:

```json
{
  "type": "TabularTranslator",
  "mappings": [
    { "source": { "name": "cust_no" },  "sink": { "name": "customer_id" } },
    { "source": { "name": "ord_amt" },  "sink": { "name": "amount" } }
  ],
  "typeConversion": true,
  "typeConversionSettings": { "allowDataTruncation": false }
}
```

A source rename becomes a one-row config change, with no pipeline redeployment.

**d) Fault tolerance.** Copy activity → Settings → Fault tolerance → **Skip incompatible rows**, with logging to ADLS. Rows with values that can't be converted are skipped and logged instead of failing the copy. Alert on the count of skipped rows.

**e) SQL sink.** **Auto create table** only creates a table that doesn't exist yet; it never adds columns to an existing table. To handle additive drift, call a stored procedure before the copy that runs `ALTER TABLE ... ADD`.

### 5.2 Detection step

```
Get Metadata (field list: structure, columnCount)    ← or Lookup on INFORMATION_SCHEMA.COLUMNS
        ↓
Stored Procedure: usp_CheckSchemaDrift(@Table, @IncomingSchema = @string(activity('GetSchema').output.structure))
        ↓   logs added / removed / type-changed columns to an audit table, returns DriftType
If Condition  @equals(activity('CheckDrift').output.firstRow.DriftType, 'BREAKING')
   ├─ True  → Web activity → Logic App → Teams/email alert → Fail activity
   └─ False → (ADDITIVE: auto ALTER TABLE ADD / update mapping) → Copy activity
```

```sql
-- @IncomingSchema = '[{"name":"order_id","type":"Int64"}, ...]'
SELECT i.name, i.type, e.ColumnName, e.DataType
FROM OPENJSON(@IncomingSchema) WITH (name sysname '$.name', type varchar(50) '$.type') i
FULL OUTER JOIN ctl.ExpectedColumns e
  ON e.TableName = @Table AND e.ColumnName = i.name
WHERE i.name IS NULL OR e.ColumnName IS NULL OR i.type <> e.DataType;
```

| Change | Classification | Action |
|---|---|---|
| New column | Additive | Add automatically, log it |
| Missing column | Breaking (often a rename) | Alert, fail that table |
| Type widening (int → bigint) | Safe | Apply |
| Other type change | Breaking | Alert |

For SQL sources, a **Lookup on `INFORMATION_SCHEMA.COLUMNS`** gives more reliable type information than Get Metadata.

### 5.3 Mapping data flows

| Setting | Where | What it does |
|---|---|---|
| **Allow schema drift** | Source | Columns not in the projection still flow through. |
| **Infer drifted column types** | Source | Gives drifted columns real types (otherwise they're strings). |
| **Validate schema** | Source | Fails if the source doesn't match the projection (strict sources). |
| **Allow schema drift** | Sink | Writes the new columns; combine with **Auto mapping**. |
| **Merge schema** | Delta sink | Lets the target Delta table add new columns. |

To work with drifted columns:
- `byName('cust_no')` in a Derived Column refers to a column by name.
- **Column patterns**, e.g. `type == 'string'` → `trim($$)`, apply a rule to every matching column.
- **Rule-based mapping** in a Select transformation, e.g. `name like 'addr_%'`.
- **Map drifted**, in data preview, turns drifted columns into named columns.

### 5.4 Interview answer

> "In ADF we kept the generic datasets schema-less, so the Copy activity maps columns by name and the Parquet landing files take whatever schema the source sends. Where we needed explicit mapping, for example into SQL or for renamed columns, the mapping JSON lives in our control table and the Copy activity reads it with dynamic content (`@json(item().ColumnMapping)`), so a rename is a config change, not a redeployment. Before each copy, a Lookup on INFORMATION_SCHEMA feeds a stored procedure that compares the source schema with our expected columns and logs the differences. Additive changes are applied automatically with ALTER TABLE ADD. Breaking changes, like a dropped column or a narrowing type change, go down an If Condition path that alerts Teams through a Logic App and fails only that table. Type mismatches at row level are handled with 'skip incompatible rows' and logged to ADLS. In data flows we turn on Allow schema drift and Infer drifted column types, and use rule-based mapping. That's how we caught `cust_no` being renamed to `customer_id`: the drift check flagged one column added and one removed, we updated the mapping row, and we reran the same morning."

---

## 6. Silver and gold layer code, line by line

| Layer | Purpose | Main operations | Example table |
|---|---|---|---|
| **Bronze** | Raw copy of the source plus audit columns | Auto Loader, append only | `bronze.erp.sales_line` |
| **Silver** | Clean, correct, one row per business key | Cast types, standardise, data quality checks, dedupe, **MERGE** | `silver.sales.sales_line` |
| **Gold** | Business-ready star schema for Power BI | Join dimensions, surrogate keys, SCD2 as-of lookup, measures, aggregates | `gold.sales.fact_sales`, `agg_daily_store_sales` |

*"Silver answers: is this data correct? Gold answers: is this data useful to the business?"*

### 6.1 SILVER notebook: `nb_silver_sales_line`

#### Cell 1: Imports and parameters
```python
from pyspark.sql import functions as F
from pyspark.sql.window import Window
from delta.tables import DeltaTable
import json

dbutils.widgets.text("load_date", "")
dbutils.widgets.text("batch_id", "")
load_date = dbutils.widgets.get("load_date")
batch_id  = dbutils.widgets.get("batch_id")
```
- `functions as F`: Spark's built-in column functions. We use these instead of Python UDFs so Catalyst and Photon can optimise them.
- `Window`: needed for `row_number()` when deduplicating.
- `DeltaTable`: the Python API for `MERGE` and table history.
- `json`: used to send a result back to ADF.
- `dbutils.widgets.text(...)`: creates the parameters that ADF fills through **Base parameters** in the Notebook activity. The empty defaults let you run the notebook by hand.
- `dbutils.widgets.get(...)`: reads the values ADF passed (`load_date`, `batch_id` = the ADF run id).

#### Cell 2: Read only today's bronze data
```python
bronze = (spark.table("bronze.erp.sales_line")
               .filter(F.col("_ingest_date") == load_date))
```
- `spark.table(...)`: reads the bronze Delta table through Unity Catalog (`catalog.schema.table`).
- `.filter(_ingest_date == load_date)`: an **incremental read**. Delta's file statistics skip all the older files, so we never rescan 1.8B rows.

#### Cell 3: Clean and conform
```python
clean = (bronze.select(
            F.col("ORDER_ID").cast("bigint").alias("order_id"),
            F.col("LINE_NO").cast("int").alias("line_no"),
            F.col("STORE_CD").cast("int").alias("store_id"),
            F.upper(F.trim(F.col("SKU"))).alias("product_code"),
            F.col("CUST_NO").cast("bigint").alias("customer_id"),
            F.col("QTY").cast("int").alias("quantity"),
            F.col("UNIT_PRICE").cast("decimal(18,2)").alias("unit_price"),
            F.coalesce(F.col("DISC_AMT").cast("decimal(18,2)"), F.lit(0)).alias("discount_amount"),
            F.from_utc_timestamp(F.col("ORDER_TS"), "Asia/Kolkata").alias("order_ts_ist"),
            F.col("MODIFIED_TS").cast("timestamp").alias("modified_ts"),
            F.col("_ingest_ts"),
            F.col("_source_file"))
         .withColumn("sale_date", F.to_date("order_ts_ist"))
         .withColumn("net_amount",
                     F.col("quantity") * F.col("unit_price") - F.col("discount_amount"))
         .withColumn("_batch_id", F.lit(batch_id)))
```
- `select(...)`: picks **only the needed columns**. This is the silver schema contract, so source changes don't leak in, and there's less data to shuffle.
- `.cast(...)`: fixed, correct types. A value that can't be cast becomes null, and the data quality check catches it.
- `.alias(...)`: renames uppercase ERP codes to clear snake_case business names.
- `F.upper(F.trim("SKU"))`: standardises codes, because `" ab123"` and `"AB123"` would otherwise break the product join.
- `decimal(18,2)` for money: **never float for currency**.
- `F.coalesce(DISC_AMT, 0)`: a missing discount means 0. Otherwise `net_amount` becomes null.
- `from_utc_timestamp(..., "Asia/Kolkata")`: the source stores UTC. Without this, orders between 00:00 and 05:30 IST fell on the previous day (the 0.8% revenue mismatch).
- `modified_ts`: decides which version of a row is the latest.
- `_ingest_ts`, `_source_file`: audit columns, so any row can be traced back to its file.
- `sale_date`: the business date from the **IST** timestamp. Used for partitioning and MERGE pruning.
- `net_amount`: the measure is defined once in silver, so every report uses the same formula.
- `_batch_id`: tags each row with its ADF run, so a bad batch can be deleted by id.

#### Cell 4: Data quality checks and quarantine
```python
dq_reason = (F.when(F.col("order_id").isNull() | F.col("line_no").isNull(), "missing key")
              .when(F.col("store_id").isNull(), "missing store")
              .when(F.col("unit_price").isNull() | (F.col("unit_price") < 0), "invalid price")
              .when(F.col("quantity") == 0, "zero quantity"))

checked = clean.withColumn("_dq_reason", dq_reason)

(checked.filter(F.col("_dq_reason").isNotNull())
        .write.mode("append")
        .saveAsTable("silver.quarantine.sales_line"))

valid = checked.filter(F.col("_dq_reason").isNull()).drop("_dq_reason")
```
- `F.when(...).when(...)`: the first rule that fails gives the reason. A row that passes every rule gets **null**, meaning valid.
- Rules: keys are required for MERGE. Negative **quantity** is allowed (a return); zero quantity is junk. A negative price is invalid.
- Bad rows are appended to a **quarantine** table with the reason. We don't fail the load, and we don't drop rows silently. We alert above a threshold.
- `valid`: only clean rows continue, and the helper column is dropped.

#### Cell 5: Deduplicate and keep the latest version
```python
w = (Window.partitionBy("order_id", "line_no")
           .orderBy(F.col("modified_ts").desc(), F.col("_ingest_ts").desc()))

latest = (valid.withColumn("rn", F.row_number().over(w))
               .filter(F.col("rn") == 1)
               .drop("rn"))
```
- `partitionBy(order_id, line_no)`: groups all versions of the same business key.
- `orderBy(modified_ts desc, _ingest_ts desc)`: newest first, with `_ingest_ts` as a tie-breaker.
- `row_number()` then `rn == 1`: keeps only the latest version.
- **Why not `dropDuplicates`?** Which row it keeps isn't deterministic. Delta `MERGE` also **fails** if two source rows match one target row, so this step is required.

#### Cell 6: MERGE into silver, limited to the affected dates
```python
min_d, max_d = latest.agg(F.min("sale_date"), F.max("sale_date")).first()

if min_d is None:
    dbutils.notebook.exit(json.dumps({"status": "NO_DATA"}))

target = DeltaTable.forName(spark, "silver.sales.sales_line")

(target.alias("t")
   .merge(latest.alias("s"),
          f"""t.order_id = s.order_id
              AND t.line_no = s.line_no
              AND t.sale_date BETWEEN '{min_d}' AND '{max_d}'""")
   .whenMatchedUpdateAll(condition="s.modified_ts > t.modified_ts")
   .whenNotMatchedInsertAll()
   .execute())
```
- `agg(min, max).first()`: a small action to get the date range of today's changes.
- `if min_d is None`: no data, so exit cleanly. ADF reads `NO_DATA` and can alert.
- `DeltaTable.forName(...)`: a handle on the target table.
- Business key match on `order_id` + `line_no`.
- **`t.sale_date BETWEEN min and max`**: the key performance line. It lets Delta **prune files**. This took the MERGE from **2h10m to 28 min**. Trade-off: it assumes `sale_date` never changes for an order.
- `whenMatchedUpdateAll(s.modified_ts > t.modified_ts)`: update only if the incoming row is newer, so an old replayed file can't overwrite newer data. This makes the step **idempotent**.
- `whenNotMatchedInsertAll()`: inserts new lines.
- `.execute()`: one **ACID transaction**. It commits fully or not at all.

#### Cell 7: Return metrics to ADF
```python
m = target.history(1).select("operationMetrics").first()[0]

dbutils.notebook.exit(json.dumps({
    "status": "OK",
    "rows_inserted": int(m["numTargetRowsInserted"]),
    "rows_updated":  int(m["numTargetRowsUpdated"])
}))
```
- `history(1)`: the latest commit, which is our MERGE. `operationMetrics` gives the counts for free, with no extra `count()` actions.
- `dbutils.notebook.exit(json)`: ADF reads it as `@activity('nb_silver_sales').output.runOutput` and logs it to the audit table.

### 6.2 GOLD notebook: `nb_gold_fact_sales`

#### Cell 1: Parameters and the rebuild window
```python
from pyspark.sql import functions as F
dbutils.widgets.text("load_date", "")
load_date  = dbutils.widgets.get("load_date")
start_date = spark.sql(f"SELECT date_sub(DATE'{load_date}', 7)").first()[0]

sales = spark.table("silver.sales.sales_line").filter(F.col("sale_date") >= F.lit(start_date))
```
- `start_date = load_date − 7`: every night we **rebuild the last 7 days**, so late files are picked up automatically.
- The filter reads only those 7 days from silver, with file pruning.

#### Cell 2: Reusable SCD2 as-of lookup
```python
def asof_lookup(fact, dim_table, fact_bk, dim_bk, key_col, broadcast=False):
    d = (spark.table(dim_table)
              .select(F.col(dim_bk).alias("_bk"), key_col, "effective_from", "effective_to"))
    if broadcast:
        d = F.broadcast(d)
    cond = ((fact[fact_bk] == d["_bk"]) &
            (fact["sale_date"] >= d["effective_from"]) &
            (d["effective_to"].isNull() | (fact["sale_date"] < d["effective_to"])))
    return (fact.join(d, cond, "left")
                .withColumn(key_col, F.coalesce(F.col(key_col), F.lit(-1)))
                .drop("_bk", "effective_from", "effective_to"))
```
- **Purpose:** find the dimension version that was **valid on the sale date**. January sales keep the customer's January region even after they move.
- `select(...)`: only the join columns, so less shuffle.
- `F.broadcast(d)`: optional. It copies a small dimension to every executor, so the fact table isn't shuffled.
- The condition: business key match, `sale_date >= effective_from`, and `effective_to IS NULL` (current) or `sale_date < effective_to`.
- `"left"` join: **never lose a sale**. An inner join silently drops unmatched facts, the most common cause of gold not matching the source.
- `coalesce(key, -1)`: **unknown member**. The sale still counts, and a daily job repoints it when the dimension row arrives (late-arriving dimension).

#### Cell 3: Build the fact table
```python
walkin = (sales.filter(F.col("customer_id").isNull())
               .withColumn("customer_key", F.lit(-1)))
known  = asof_lookup(sales.filter(F.col("customer_id").isNotNull()),
                     "gold.dim.dim_customer", "customer_id", "customer_id", "customer_key")
sales_c = known.unionByName(walkin)

sales_cp = asof_lookup(sales_c, "gold.dim.dim_product",
                       "product_code", "product_code", "product_key", broadcast=True)

store = F.broadcast(spark.table("gold.dim.dim_store").select("store_id", "store_key"))

fact = (sales_cp.join(store, "store_id", "left")
          .withColumn("store_key", F.coalesce("store_key", F.lit(-1)))
          .withColumn("date_key",  F.date_format("sale_date", "yyyyMMdd").cast("int"))
          .withColumn("sale_month", F.trunc("sale_date", "month"))
          .withColumn("gross_amount", F.col("quantity") * F.col("unit_price"))
          .select("date_key", "store_key", "product_key", "customer_key",
                  "order_id", "line_no", "sale_date", "sale_month",
                  "quantity", "unit_price", "gross_amount",
                  "discount_amount", "net_amount", "_batch_id"))
```
- `walkin`: about **30% of sales have no customer**. Joined, all null keys land in **one partition** (the skew story). So they skip the join and get `-1` directly.
- `known`: only rows with a customer go through the SCD2 join, which is now evenly distributed.
- `unionByName`: recombines the two sets by column **name**, not position.
- Product lookup with `broadcast=True`: about 180 MB, above the 10 MB automatic threshold. Broadcasting it explicitly cut the join from **14 min to under 4**.
- `store`: 420 rows, always broadcast. Joining on the column name avoids a duplicate `store_id` column.
- `date_key = yyyyMMdd int`: computed directly, with **no join to the date dimension**.
- `sale_month`: the partition column. Monthly, not daily, to avoid small files.
- `gross_amount`: the measure before discount, since Finance wanted both gross and net.
- `.select(...)`: the final star schema (surrogate keys, degenerate dimensions `order_id`/`line_no`, measures, audit column).

#### Cell 4: Write with replaceWhere (idempotent)
```python
(fact.write.format("delta")
     .mode("overwrite")
     .option("replaceWhere", f"sale_date >= '{start_date}'")
     .saveAsTable("gold.sales.fact_sales"))
```
- `overwrite` with **`replaceWhere`**: atomically replaces **only the last 7 days**, without touching history.
- **Not append:** a rerun would duplicate rows. With replaceWhere, running twice gives the same result, so it's **idempotent**.
- It's a single Delta transaction, so Power BI never sees a half-written table.

#### Cell 5: Aggregate table for Power BI
```python
fact_recent = spark.table("gold.sales.fact_sales").filter(F.col("sale_date") >= F.lit(start_date))

agg = (fact_recent.groupBy("date_key", "store_key")
                  .agg(F.sum("net_amount").alias("net_sales"),
                       F.sum("quantity").alias("units_sold"),
                       F.countDistinct("order_id").alias("order_count")))

(agg.write.format("delta").mode("overwrite")
    .option("replaceWhere", f"date_key >= {start_date.strftime('%Y%m%d')}")
    .saveAsTable("gold.sales.agg_daily_store_sales"))
```
- **Read back from the table**, not the `fact` DataFrame. Spark is lazy, so reusing `fact` would recompute every join.
- `groupBy(date_key, store_key)`: about 420 × 7 rows instead of millions.
- KPIs are `sum` and `countDistinct`. Power BI reads this small table, so reports open in seconds.
- `replaceWhere` on `date_key`: the same idempotent 7-day refresh.

#### Cell 6: Maintenance
```python
spark.sql(f"""
  OPTIMIZE gold.sales.fact_sales
  WHERE sale_month >= trunc(DATE'{start_date}', 'MM')
  ZORDER BY (store_key, product_key)
""")
```
- `OPTIMIZE`: compacts small files into files of about 1 GB.
- `WHERE sale_month >= ...`: only the recent partitions (the WHERE clause must use partition columns).
- `ZORDER BY (store_key, product_key)`: the most common Power BI filters, so queries skip most files.

---

## 7. Execution order and one-line summaries

```
ADF (01:00) → Copy to landing → Databricks Workflows job (one shared job cluster):
   bronze (Auto Loader) → silver_sales_line → silver dims (SCD2 MERGE)
   → gold dims → gold fact_sales → agg_daily_store_sales → OPTIMIZE
→ ADF logs runOutput to audit table → Power BI refresh (06:30)
```

**Silver vs gold in one line:**

> "Silver makes the data **correct**: right types, IST dates, standardised codes, quarantined bad rows, deduplicated, and merged by business key with date pruning. Gold makes it **useful**: a star schema with SCD2 as-of surrogate keys, unknown members so no sale is lost, broadcast joins, a 7-day idempotent rebuild for late data, and a daily aggregate so Power BI is fast."

---

## 8. Practice tools

| Tool | Link | What it does |
|---|---|---|
| **Pipeline Interview Room** | https://claude.ai/artifact/LeaPXNQ827UzaVuP3LTAGx | Asks questions aloud, records your spoken answer, scores it out of 10, gives a model answer and asks a follow-up. |
| **Pipeline Interview Answers** | https://claude.ai/artifact/7mk9b2bB1h2Mp3mu72WAFP | All model answers as continuous audio (interviewer voice + candidate voice), with speed, sections and a 5-second "think" pause. |

Both pages are private to your account. Voice input works in Chrome, Edge or the Claude desktop app.
