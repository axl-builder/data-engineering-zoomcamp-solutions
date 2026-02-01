### Quiz Questions

[](https://github.com/DataTalksClub/data-engineering-zoomcamp/blob/main/cohorts/2026/02-workflow-orchestration/homework.md#quiz-questions)

Complete the quiz shown below. It's a set of 6 multiple-choice questions to test your understanding of workflow orchestration, Kestra, and ETL pipelines.

1. Within the execution for `Yellow` Taxi data for the year `2020` and month `12`: what is the uncompressed file size (i.e. the output file `yellow_tripdata_2020-12.csv` of the `extract` task)? 

- 128.3 MiB
- 134.5 MiB ✓
- 364.7 MiB
- 692.6 MiB


2. What is the rendered value of the variable `file` when the inputs `taxi` is set to `green`, `year` is set to `2020`, and `month` is set to `04` during execution?

- `{{inputs.taxi}}_tripdata_{{inputs.year}}-{{inputs.month}}.csv`
- `green_tripdata_2020-04.csv` ✓
- `green_tripdata_04_2020.csv` 
- `green_tripdata_2020.csv`


3. How many rows are there for the `Yellow` Taxi data for all CSV files in the year 2020?

- 13,537.299
- 24,648,499 ✓
- 18,324,219
- 29,430,127

###### Justification:
```sql
SELECT count(*) FROM `de-zoomcamp-axl-2025.zoomcamp.yellow_tripdata` WHERE filename LIKE 'yellow_tripdata_2020%';
```

4. How many rows are there for the `Green` Taxi data for all CSV files in the year 2020?

- 5,327,301
- 936,199
- 1,734,051 ✓
- 1,342,034

###### Justification:
```sql
SELECT count(*) FROM `de-zoomcamp-axl-2025.zoomcamp.green_tripdata` WHERE filename LIKE 'green_tripdata_2020%';
```

5. How many rows are there for the `Yellow` Taxi data for the March 2021 CSV file?

- 1,428,092
- 706,911
- 1,925,152 ✓
- 2,561,031

###### Justification:
```sql
SELECT count(*) FROM `de-zoomcamp-axl-2025.zoomcamp.yellow_tripdata` WHERE filename LIKE 'yellow_tripdata_2021_03%';
```

6. How would you configure the time zone to New York in a Schedule trigger?

- Add a `timezone` property set to `EST` in the `Schedule` trigger configuration 
- Add a `timezone` property set to `America/New_York` in the `Schedule` trigger configuration ✓
- Add a `timezone` property set to `UTC-5` in the `Schedule` trigger configuration
- Add a `location` property set to `New_York` in the `Schedule` trigger configuration 

###### Justification:
```yaml
triggers:
  - id: daily_schedule
    type: io.kestra.plugin.core.trigger.Schedule
    cron: "0 9 1 * *"
    timezone: "America/New_York" #Response
    inputs:
      taxi: yellow
```


The reason `America/New_York` is the correct answer is based on how data orchestrators and operating systems handle time. In technical environments, there are two ways to define time: using a fixed offset or using a Time Zone (TZ) database identifier.

If you use a value like `UTC-5` or the abbreviation `EST`, you are providing a static value that never changes. The issue is that New York, like many other regions, adjusts its local clock twice a year due to Daylight Saving Time (DST).

- During the winter, New York is on `EST` (UTC-5).
- During the summer, New York shifts to `EDT` (UTC-4).

If you schedule a task to run at 09:00 using a fixed `UTC-5` offset, your process will start running at 10:00 local New York time once the summer shift occurs. This causes synchronization issues with local business hours or financial markets.

By using `America/New_York`, Kestra references the IANA (Internet Assigned Numbers Authority) database. This database contains the specific rules and historical changes for various regions. Kestra’s engine automatically detects when the DST transition happens and adjusts the execution time so it consistently runs at 09:00 local time, regardless of whether the current offset is 4 or 5 hours relative to UTC.

In professional data engineering, using the `Continent/City` format is the standard practice to ensure pipelines remain synchronized with local time throughout the entire year.

For your homework justification: This format is the only one that provides automatic adjustments for Daylight Saving Time (DST), whereas fixed offsets or static codes do not.

Español:
La razón por la que `America/New_York` es la respuesta correcta se debe a cómo los sistemas operativos y los orquestadores de datos gestionan el tiempo. En programación, existen dos formas de definir una hora: mediante un desplazamiento fijo (offset) o mediante un identificador de base de datos de zonas horarias (TZ database).

Si usas un valor como `UTC-5` o la sigla `EST`, le estás indicando al sistema un valor estático que no cambia nunca. El problema es que Nueva York, al igual que muchas otras ciudades, cambia su reloj dos veces al año debido al horario de verano.

- En invierno, Nueva York está en `EST` (UTC-5).
- En verano, Nueva York pasa a `EDT` (UTC-4).

Si configuras un proceso para que corra a las 09:00 con un offset fijo de `UTC-5`, cuando llegue el verano y la ciudad cambie su hora local, tu proceso se ejecutará a las 10:00 hora de Nueva York. Esto rompería cualquier sincronización que dependa del horario comercial o bancario de la ciudad.

Al usar `America/New_York`, Kestra consulta la base de datos IANA. Esta base de datos contiene el historial y las reglas de cambios de hora de cada región. Así, el motor de Kestra detecta automáticamente cuándo ocurre el cambio de horario de verano y ajusta la ejecución para que siempre sea a las 09:00 hora local, independientemente de si en ese momento la diferencia es de 4 o 5 horas respecto a UTC.

En resumen, para cualquier flujo de datos profesional que deba respetar el tiempo de una ubicación geográfica específica, siempre se debe usar el formato `Continente/Ciudad` para evitar desfases estacionales.

