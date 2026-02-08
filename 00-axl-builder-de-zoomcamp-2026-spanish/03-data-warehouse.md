## Data Warehouse
#### OLAP VS OLTP (Online Analytical Processing vs Online Transactional Processing)
###### OLTP (Online Transactional Processing)
El procesamiento de transacciones en línea es el sistema que soporta las operaciones del día a día de una empresa. Su objetivo principal es la velocidad y la integridad al registrar datos individuales.
###### OLAP (Online Analytical Processing)
El procesamiento analítico en línea se utiliza para la consulta y el análisis de grandes volúmenes de datos. No se usa para "escribir" ventas nuevas, sino para analizar los datos que ya ocurrieron.

| **Característica**      | [[OLTP (Online Transactional Processing)]] | [[OLAP (Online Analytical Processing)]]               |     |
| ----------------------- | ------------------------------------------ | ----------------------------------------------------- | --- |
| **Objetivo**            | Ejecutar tareas administrativas.           | Apoyar la toma de decisiones.                         |     |
| **Operaciones**         | Consultas simples: INSERT, UPDATE, DELETE. | Consultas complejas: SELECT con muchos filtros.       |     |
| **Tiempo de respuesta** | Milisegundos (Instantáneo).                | Segundos, minutos o incluso horas.                    |     |
| **Datos**               | Solo datos actuales y detallados.          | Históricos, masivos y resumidos.                      |     |
| **Usuarios**            | Personal operativo (cajeros, clientes).    | Analistas, científicos de datos, ejecutivos.          |     |
| **Backup**              | Crítico para la continuidad del negocio.   | El backup es el data warehouse cargado desde el OLTP. |     |

|                     | OLTP                                                                                                  | OLAP                                                                                                  |
| ------------------- | ----------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| Purpose             | Control and run essential business operations in real time                                            | Plan, solve problems, support decisions, discover hidden insights                                     |
| Data updates        | Short, fast updates initiated by user                                                                 | Data periodically refreshed with scheduled, long-running batch jobs                                   |
| Database design     | Normalized databases for efficiency                                                                   | Denormalized databases for analysis                                                                   |
| Space requirements  | Generally small if historical data is archived                                                        | Generally large due to aggregating large datasets                                                     |
| Backup and recovery | Regular backups required to ensure business continuity and meet legal and governance requirements<br> | Regular backups required to ensure business continuity and meet legal and governance requirements<br> |
| Productivity        | Increases productivity of end users<br>                                                               | Increases productivity of business managers, data analysts, and executives<br>                        |
| Data view<br>       | Lists day-to-day business transactions<br>                                                            | Multi-dimensional view of enterprise data<br>                                                         |
| User examples<br>   | Customer-facing personnel, clerks, online shoppers<br>                                                | Knowledge workers such as data analysts, business analysts, and executives<br>                        |
#### Que es es data Warehouse

El [[Data Warehouse]] un sistema diseñado para el análisis de datos al cual se dirigen los mismos provenientes de distintas fuentes heterogéneas, para convertirlos en información estratégica
- Es una solución *OLAP* 
- Es utilizado para reporte y análisis de datos.

## [[BigQuery]]
Durante esta sección se utilizo un script aportado por el curso. El cual es en lenguaje SQL dedicado a GCP.
Entre las consultas queries que se hacen están:
- Consultar una tabla pública disponible
- Crear una tabla externa que haga referencia a una ruta de GCS (Google Cloud Storage)
- Verificar los datos de viajes de taxis amarillos (Yellow trip data)
- Crear una tabla no particionada a partir de una tabla externa
- Crear una tabla particionada a partir de una tabla externa
- Impacto de la partición
- Examinar las particiones
- Crear una tabla particionada y con clúster (Clustering)

A continuacion. Las dos versiones del codigo. la aportada por el curso. y la que cuenta con los datos actualizados del proyecto propio.

Datode configuracion: 
En el video del curso antes de comenzar con la demostracion configura lo siguiente.
En 'More...' > Query settings > Cache preference (desactivar "Use cached results")
>(This attempts to use results from a previous run of this query, as long as the referenced tables are unmodified. If cached results are returned, you will not be billed for any usage. Results are cached for approximately 24 hours.
Caching cannot be enabled when a destination table is selected. [Learn more](https://cloud.google.com/bigquery/docs/cached-results)))
### Anatomía de la referencia en BigQuery
En BigQuery, la jerarquía siempre es **Proyecto -> Dataset -> Tabla**. Se escribe así: 
`` `ID_PROYECTO.NOMBRE_DATASET.NOMBRE_TABLA` ``

1. **`NOMBRE_DE_TU_PROYECTO` (ID del Proyecto):** Es el contenedor de Google Cloud donde se factura y organiza todo. Lo ves en tu terminal con `gcloud config get-value project`.
    
2. **`nytaxi` (Dataset):** Es una agrupación lógica de tablas. **No se crea solo**. Si no lo has creado, el comando fallará.
    
    - **¿Dónde lo buscas?** En la terminal corre: `bq ls`.
        
    - **¿Cómo lo creas?** Si no aparece, créalo desde la CLI:        
        ```
        bq mk --location=US nytaxi
        ```
        
3. **`external_yellow_tripdata` (Nombre de la Tabla):** Este nombre lo inventas tú en este momento. Es como se llamará el "acceso directo" a tus archivos dentro de BigQuery.



[big_query.sql](https://github.com/DataTalksClub/data-engineering-zoomcamp/blob/main/03-data-warehouse/big_query.sql "big_query.sql")
```sql
-- Query public available table
SELECT station_id, name FROM
    bigquery-public-data.new_york_citibike.citibike_stations
LIMIT 100;


-- Creating external table referring to gcs path
CREATE OR REPLACE EXTERNAL TABLE `taxi-rides-ny.nytaxi.external_yellow_tripdata`
OPTIONS (
  format = 'CSV',
  uris = ['gs://nyc-tl-data/trip data/yellow_tripdata_2019-*.csv', 'gs://nyc-tl-data/trip data/yellow_tripdata_2020-*.csv']
);

-- Check yellow trip data
SELECT * FROM taxi-rides-ny.nytaxi.external_yellow_tripdata limit 10;

-- Create a non partitioned table from external table
CREATE OR REPLACE TABLE taxi-rides-ny.nytaxi.yellow_tripdata_non_partitioned AS
SELECT * FROM taxi-rides-ny.nytaxi.external_yellow_tripdata;


-- Create a partitioned table from external table
CREATE OR REPLACE TABLE taxi-rides-ny.nytaxi.yellow_tripdata_partitioned
PARTITION BY
  DATE(tpep_pickup_datetime) AS
SELECT * FROM taxi-rides-ny.nytaxi.external_yellow_tripdata;

-- Impact of partition
-- Scanning 1.6GB of data
SELECT DISTINCT(VendorID)
FROM taxi-rides-ny.nytaxi.yellow_tripdata_non_partitioned
WHERE DATE(tpep_pickup_datetime) BETWEEN '2019-06-01' AND '2019-06-30';

-- Scanning ~106 MB of DATA
SELECT DISTINCT(VendorID)
FROM taxi-rides-ny.nytaxi.yellow_tripdata_partitioned
WHERE DATE(tpep_pickup_datetime) BETWEEN '2019-06-01' AND '2019-06-30';

-- Let's look into the partitions
SELECT table_name, partition_id, total_rows
FROM `nytaxi.INFORMATION_SCHEMA.PARTITIONS`
WHERE table_name = 'yellow_tripdata_partitioned'
ORDER BY total_rows DESC;

-- Creating a partition and cluster table
CREATE OR REPLACE TABLE taxi-rides-ny.nytaxi.yellow_tripdata_partitioned_clustered
PARTITION BY DATE(tpep_pickup_datetime)
CLUSTER BY VendorID AS
SELECT * FROM taxi-rides-ny.nytaxi.external_yellow_tripdata;

-- Query scans 1.1 GB
SELECT count(*) as trips
FROM taxi-rides-ny.nytaxi.yellow_tripdata_partitioned
WHERE DATE(tpep_pickup_datetime) BETWEEN '2019-06-01' AND '2020-12-31'
  AND VendorID=1;

-- Query scans 864.5 MB
SELECT count(*) as trips
FROM taxi-rides-ny.nytaxi.yellow_tripdata_partitioned_clustered
WHERE DATE(tpep_pickup_datetime) BETWEEN '2019-06-01' AND '2020-12-31'
  AND VendorID=1;
```
![[big_query.sql]]

```SQL
-- Query public available table

SELECT station_id, name FROM

    bigquery-public-data.new_york_citibike.citibike_stations

LIMIT 100;

  
  

-- Creating external table referring to gcs path

CREATE OR REPLACE EXTERNAL TABLE `NOMBRE_DE_TU_PROYECTO.zoomcamp.external_yellow_tripdata`

OPTIONS (

  format = 'CSV',

  uris = ["gs://NOMBRE_DE_TU_BUCKET/yellow_tripdata_2019-*.csv", "gs://NOMBRE_DE_TU_BUCKET/yellow_tripdata_2020-*.csv"]

);

  

-- Check yellow trip data

SELECT * FROM NOMBRE_DE_TU_PROYECTO.zoomcamp.external_yellow_tripdata limit 10;

  

-- Create a non partitioned table from external table

CREATE OR REPLACE TABLE NOMBRE_DE_TU_PROYECTO.zoomcamp.yellow_tripdata_non_partitioned AS

SELECT * FROM NOMBRE_DE_TU_PROYECTO.zoomcamp.external_yellow_tripdata;

  
  

-- Create a partitioned table from external table

CREATE OR REPLACE TABLE NOMBRE_DE_TU_PROYECTO.zoomcamp.yellow_tripdata_partitioned

PARTITION BY

  DATE(tpep_pickup_datetime) AS

SELECT * FROM NOMBRE_DE_TU_PROYECTO.zoomcamp.external_yellow_tripdata;

  

-- Impact of partition

-- Scanning 1.6GB of data

SELECT DISTINCT(VendorID)

FROM NOMBRE_DE_TU_PROYECTO.zoomcamp.yellow_tripdata_non_partitioned

WHERE DATE(tpep_pickup_datetime) BETWEEN '2019-06-01' AND '2019-06-30';

  

-- Scanning ~106 MB of DATA

SELECT DISTINCT(VendorID)

FROM NOMBRE_DE_TU_PROYECTO.zoomcamp.yellow_tripdata_partitioned

WHERE DATE(tpep_pickup_datetime) BETWEEN '2019-06-01' AND '2019-06-30';

  

-- Let's look into the partitions

SELECT table_name, partition_id, total_rows

FROM `zoomcamp.INFORMATION_SCHEMA.PARTITIONS`

WHERE table_name = 'yellow_tripdata_partitioned'

ORDER BY total_rows DESC;

  

-- Creating a partition and cluster table

CREATE OR REPLACE TABLE NOMBRE_DE_TU_PROYECTO.zoomcamp.yellow_tripdata_partitioned_clustered

PARTITION BY DATE(tpep_pickup_datetime)

CLUSTER BY VendorID AS

SELECT * FROM NOMBRE_DE_TU_PROYECTO.zoomcamp.external_yellow_tripdata;

  

-- Query scans 1.1 GB

SELECT count(*) as trips

FROM NOMBRE_DE_TU_PROYECTO.zoomcamp.yellow_tripdata_partitioned

WHERE DATE(tpep_pickup_datetime) BETWEEN '2019-06-01' AND '2020-12-31'

  AND VendorID=1;

  

-- Query scans 864.5 MB

SELECT count(*) as trips

FROM NOMBRE_DE_TU_PROYECTO.zoomcamp.yellow_tripdata_partitioned_clustered

WHERE DATE(tpep_pickup_datetime) BETWEEN '2019-06-01' AND '2020-12-31'

  AND VendorID=1;
```


##### Comandos de utilidad para gcloud:

Para verificar tus recursos sin entrar a la consola web, usa estos comandos de "inspección":
### 1. Verificar el Dataset en BigQuery

Para ver si el dataset `nytaxi` ya existe en tu proyecto actual:

```
bq ls
```

_Si lo ves en la lista, el contenedor está listo._

### 2. Verificar Tablas dentro del Dataset

Si el dataset existe, mira si ya hay tablas (internas o externas) creadas:

```
bq ls nytaxi
```

### 3. Verificar el Bucket en Cloud Storage (GCS)

Para ver qué buckets tienes creados:

```
gsutil ls
```

Y para ver si dentro de esos buckets ya tienes los archivos `.csv` o `.parquet` que necesitas para la tabla externa:

```
# Cambia 'tu-nombre-de-bucket' por el que aparezca en el comando anterior
gsutil ls -r gs://tu-nombre-de-bucket/
```



## Particionamiento y Clustering
El **particionamiento** y el **clustering** son estrategias en BigQuery diseñadas para optimizar el rendimiento de las consultas y reducir costos al organizar cómo se almacenan los datos. Mientras que el particionamiento divide la tabla en segmentos basados en una columna, el clustering ordena los datos internamente según los valores de varias columnas.

A continuación, presento un resumen detallado de sus características y cuándo utilizar cada uno:
#### 1. Particionamiento (Partitioning)

Esta técnica divide los datos en unidades lógicas basadas generalmente en tiempo o rangos.

• **Tipos de partición:** Se puede particionar por tiempo (diario, horario, mensual o anual) o por un rango de números enteros. El particionamiento **diario** es el predeterminado y el más común.

• **Limitaciones:** BigQuery impone un límite de **4,000 particiones** por tabla. Si se usa particionamiento horario en grandes volúmenes de datos, se debe considerar una estrategia de expiración para no exceder este límite.

• **Ventajas clave:** Permite conocer los **costos de la consulta de antemano** y facilita la gestión de datos, como eliminar o mover particiones específicas.

• **Uso:** Generalmente se aplica sobre una **sola columna** para filtrar o agregar datos.

#### 2. Clustering

El clustering organiza los datos en bloques basados en el contenido de hasta cuatro columnas específicas.

• **Orden de las columnas:** El orden en que se especifican las columnas es crítico, ya que determina la **jerarquía de clasificación** de los datos (por ejemplo, si se agrupa por A, B y C, los datos se ordenan primero por A, luego por B y finalmente por C).

• **Tipos de datos permitidos:** Se puede aplicar a columnas de tipo fecha, booleano, geografía, entero, numérico, cadena de texto (string) y fecha-hora.

• **Granularidad:** Es ideal cuando se necesita una granularidad que el particionamiento no puede ofrecer o cuando una columna tiene **alta cardinalidad** (muchos valores únicos).

#### 3. Comparativa: ¿Cuál elegir?

|Característica|Particionamiento|Clustering|
|---|---|---|
|**Costo**|Se conoce de antemano antes de ejecutar la consulta.|Los beneficios de costo son desconocidos hasta la ejecución.|
|**Gestión**|Permite gestión a nivel de partición (borrar/mover).|No permite gestión granular de bloques.|
|**Columnas**|Se limita a una sola columna.|Permite usar hasta 4 columnas para filtrar/agrupar.|
|**Eficiencia**|Ideal para filtros basados en tiempo o rangos simples.|Ideal para filtros complejos y alta cardinalidad.|

Recomendaciones de Uso

• **Evite ambos en tablas pequeñas:** Si el tamaño de los datos es **menor a 1 GB**, no se recomienda usar ninguna de las dos técnicas, ya que el costo de mantenimiento de metadatos puede superar los beneficios de rendimiento.

• **Prefiera el Clustering cuando:** El particionamiento resulte en particiones muy pequeñas (menos de 1 GB cada una) o cuando exceda el límite de 4,000 particiones.

• **Mantenimiento Automático:** BigQuery realiza un **re-clustering automático** en segundo plano sin costo adicional para el usuario, manteniendo el rendimiento a medida que se agregan nuevos datos.


## BigQuery Buenas Practicas

Las mejores prácticas en BigQuery se dividen principalmente en dos categorías fundamentales: la **reducción de costos** y la **mejora del rendimiento** de las consultas.

Aquí tienes un resumen detallado de los puntos clave:

#### 1. Reducción de Costos

Dado que BigQuery cobra por la cantidad de datos procesados, estas estrategias son vitales:

• **Evitar el** **SELECT *****:** Al ser un almacenamiento columnar, es mejor especificar los nombres de las columnas necesarias para no leer datos innecesarios.

• **Previsualizar el costo:** Siempre se debe revisar el precio estimado de la consulta (ubicado en la esquina superior derecha) antes de ejecutarla.

• **Particionamiento y Clustering:** Estas técnicas ayudan significativamente a limitar los datos que BigQuery necesita escanear.

• **Materializar resultados:** Si utilizas una CTE (Expresión de Tabla Común) en múltiples etapas, es preferible materializar esos resultados en lugar de recalculallos.

• **Precaución con "Streaming Inserts":** Su uso puede aumentar drásticamente los costos si no se manejan con cuidado.

#### 2. Mejora del Rendimiento (Query Performance)

Para que tus consultas sean más rápidas y eficientes, sigue estas recomendaciones:

• **Filtros inteligentes:** Siempre aplica filtros sobre las columnas que han sido **particionadas o clústerizadas**.

• **Desnormalización:** Se recomienda desnormalizar los datos utilizando **columnas anidadas (nested) o repetidas** en lugar de estructuras relacionales complejas.

• **Optimización de Joins:**

    ◦ Reduce los datos antes de realizar un join.

    ◦ Coloca la **tabla más grande primero**, seguida de las tablas más pequeñas. Esto permite que las tablas pequeñas se distribuyan (broadcast) a todos los nodos de manera eficiente.

• **Funciones de agregación:** Utiliza funcsiones de aproximación (como `HyperLogLog++`) en lugar de funciones exactas cuando sea posible.

• **Uso de** **ORDER BY****:** Esta sentencia debe ser siempre la **última parte** de tu consulta para maximizar el rendimiento.

#### 3. Otras Consideraciones Técnicas

• **Evitar funciones externas:** Reduce el uso de JavaScript y funciones definidas por el usuario (UDFs).

• **Fuentes externas:** No abuses del acceso a fuentes de datos externas (como Google Cloud Storage), ya que puede ser más costoso y lento.

• **Caché:** BigQuery almacena en caché los resultados de las consultas, lo cual ayuda tanto en costo como en velocidad para consultas repetitivas.