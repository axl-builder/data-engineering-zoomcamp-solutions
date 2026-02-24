# Module 5 Homework: Data Platforms with Bruin

[](https://github.com/DataTalksClub/data-engineering-zoomcamp/blob/main/cohorts/2026/05-data-platforms/homework.md#module-5-homework-data-platforms-with-bruin)

In this homework, we'll use Bruin to build a complete data pipeline, from ingestion to reporting.

## Setup

[](https://github.com/DataTalksClub/data-engineering-zoomcamp/blob/main/cohorts/2026/05-data-platforms/homework.md#setup)

1. Install Bruin CLI: `curl -LsSf https://getbruin.com/install/cli | sh`
2. Initialize the zoomcamp template: `bruin init zoomcamp my-pipeline`
3. Configure your `.bruin.yml` with a DuckDB connection
4. Follow the tutorial in the [main module README](https://github.com/DataTalksClub/data-engineering-zoomcamp/blob/main/05-data-platforms)

After completing the setup, you should have a working NYC taxi data pipeline.

---

### Question 1. Bruin Pipeline Structure

[](https://github.com/DataTalksClub/data-engineering-zoomcamp/blob/main/cohorts/2026/05-data-platforms/homework.md#question-1-bruin-pipeline-structure)

In a Bruin project, what are the required files/directories?

- `bruin.yml` and `assets/`  ✔
- `.bruin.yml` and `pipeline.yml` (assets can be anywhere)
- `.bruin.yml` and `pipeline/` with `pipeline.yml` and `assets/` 
- `pipeline.yml` and `assets/` only


#### Justification:
The `.bruin.yml` file defines the core project configuration and database connections, while `pipeline.yml` handles the pipeline structure. Bruin's design philosophy allows for high flexibility regarding where your data assets are physically stored within the project. While `pipeline.yml` can exist for specific grouping, the absolute bare minimum for a functional Bruin environment is the **root configuration file** (`.bruin.yml`) and the **directory containing the logic** (`assets/`)

---

### Question 2. Materialization Strategies

[](https://github.com/DataTalksClub/data-engineering-zoomcamp/blob/main/cohorts/2026/05-data-platforms/homework.md#question-2-materialization-strategies)

You're building a pipeline that processes NYC taxi data organized by month based on `pickup_datetime`. Which incremental strategy is best for processing a specific interval period by deleting and inserting data for that time period?

- `append` - always add new rows 
- `replace` - truncate and rebuild entirely 
- `time_interval` - incremental based on a time column ✔
- `view` - create a virtual table only 

#### Justification:
It allows the pipeline to "replace" specific windows of time by deleting existing records for that period and inserting new ones, preventing duplicates without the cost of a full table rebuild.

---

### Question 3. Pipeline Variables

[](https://github.com/DataTalksClub/data-engineering-zoomcamp/blob/main/cohorts/2026/05-data-platforms/homework.md#question-3-pipeline-variables)

You have the following variable defined in `pipeline.yml`:

```yaml
variables:
  taxi_types:
    type: array
    items:
      type: string
    default: ["yellow", "green"]
```

How do you override this when running the pipeline to only process yellow taxis?

- `bruin run --taxi-types yellow`
- `bruin run --var taxi_types=yellow`
- `bruin run --var 'taxi_types=["yellow"]'`✔
- `bruin run --set taxi_types=["yellow"]` 

#### Justification:
Bruin uses the `--var` flag to override defined variables. Since the variable is defined as an array in the YAML configuration, the override must be passed as a valid JSON-formatted string representing an array.

---

### Question 4. Running with Dependencies

[](https://github.com/DataTalksClub/data-engineering-zoomcamp/blob/main/cohorts/2026/05-data-platforms/homework.md#question-4-running-with-dependencies)

You've modified the `ingestion/trips.py` asset and want to run it plus all downstream assets. Which command should you use?

- `bruin run ingestion.trips --all`
- `bruin run ingestion/trips.py --downstream` 
- `bruin run pipeline/trips.py --recursive`
- `bruin run --select ingestion.trips+ ` ✔

#### Justification:
Following the convention of modern tools like dbt, the `+` operator at the end of an asset name tells the runner to include that specific asset and all of its downstream dependencies.

---

### Question 5. Quality Checks

[](https://github.com/DataTalksClub/data-engineering-zoomcamp/blob/main/cohorts/2026/05-data-platforms/homework.md#question-5-quality-checks)

You want to ensure the `pickup_datetime` column in your trips table never has NULL values. Which quality check should you add to your asset definition?

- `name: unique`
- `name: not_null`  ✔
- `name: positive`
- `name: accepted_values, value: [not_null]`

#### Justification:
**Justification:** Bruin uses declarative data quality checks. The `not_null` check is a built-in validation that ensures critical columns (like `pickup_datetime`) do not contain empty values, maintaining data integrity.

---

### Question 6. Lineage and Dependencies

[](https://github.com/DataTalksClub/data-engineering-zoomcamp/blob/main/cohorts/2026/05-data-platforms/homework.md#question-6-lineage-and-dependencies)

After building your pipeline, you want to visualize the dependency graph between assets. Which Bruin command should you use?

- `bruin graph`
- `bruin dependencies`
- `bruin lineage` ✔
- `bruin show`

#### Justification:
The `lineage` command is specifically designed to visualize the dependency graph and the flow of data between different assets in the pipeline, making it essential for impact analysis.

---

### Question 7. First-Time Run

[](https://github.com/DataTalksClub/data-engineering-zoomcamp/blob/main/cohorts/2026/05-data-platforms/homework.md#question-7-first-time-run)

You're running a Bruin pipeline for the first time on a new DuckDB database. What flag should you use to ensure tables are created from scratch?

- `--create`
- `--init`
- `--full-refresh ✔`
- `--truncate`

#### Justification:
**Justification:** On a first run or after a schema change, the `--full-refresh` flag forces Bruin to drop existing structures and recreate the tables from scratch, ignoring any incremental logic that might rely on pre-existing data.