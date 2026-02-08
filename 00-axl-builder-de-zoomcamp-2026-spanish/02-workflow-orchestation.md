## 02-workflow-orchestration

 *02-workflow-orchestration*/

###### Course Structure:
2.1 - Introducción a la orquestación de los workflow (flujos de trabajo)
2.2 - Getting Started With Kestra
2.3 - Hands-On Coding Project: Build ETL Data Pipelines with Kestra
2.4 - ELT Pipelines in Kestra: Google Cloud Platform
2.5 - Using AI for Data Engineering in Kestra
2.6 - Bonus

###### Recursos (scripts para Kestra utilizados):
https://github.com/DataTalksClub/data-engineering-zoomcamp/tree/main/02-workflow-orchestration/flows

## 2.1 Introducción a la orquestación de los workflow (flujos de trabajo)
Una buena analogia es la de la orquesta musical, la cual es guiada por un conductor de orquesta. Salvo que en este caso cambiaríamos los instrumentos musicales por herramientas de software y al director por una herramienta de orquestación como [[Kestra]].

Un orquestador de workflow cuenta generalmente con las siguientes características:
- Llevan adelante flujos de trabajo con pasos pre-definidos.
- Monitorea y registra errores.
- Lleva adelante automáticamente los flujos de trabajo basados en planificaciones y eventos.

Es interesante la comparación entre automatización  y orquestación
Mientras la primera trata de no tener que ejecutar manualmente multiples pasos de una o varias tareas. La orquestación directamente maneja, ejecuta y organiza en un sistema consistente todas las tareas, con escalabilidad infinita en el caso de Kestra, ya sean estas automatizadas o no.

![[Automation vs orchestration.png]]

Resources:
- Quickstart Guide
- What is an Orchestrator?

 Quickstart Guide

Para correr Kestra con solo un comando en la terminal:
```bash
docker run --pull=always -it -p 8080:8080 --user=root \
  --name kestra --restart=always \
  -v kestra_data:/app/storage \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v /tmp:/tmp \
  kestra/kestra:latest server local
```
Es bueno para pruebas rapidas, pero si se quiere trabajar con base de datos que deje todo registrado, mantener puertos, configuraciones, etc. Lo mejor es con docker composer.
#### Ejecutar el primer flujo de trabajo Kestra en Docker
Vamos al GitHub de Kestra y copiamos el Código del Docker composer para correrlo en nuestra terminal (o terminal de vs code en el video)
https://github.com/kestra-io/kestra/blob/develop/docker-compose.yml

Aplicamos el siguiente script en un archivo docker-compose.yalm

```yaml
volumes:
  postgres-data:
    driver: local
  kestra-data:
    driver: local

services:
  postgres:
    image: postgres:18
    volumes:
      - postgres-data:/var/lib/postgresql
    environment:
      POSTGRES_DB: kestra
      POSTGRES_USER: kestra
      POSTGRES_PASSWORD: k3str4
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -d $${POSTGRES_DB} -U $${POSTGRES_USER}"]
      interval: 30s
      timeout: 10s
      retries: 10

  kestra:
    image: kestra/kestra:latest
    pull_policy: always
    # Kestra, by default, has a termination grace period of 5m. We need to wait a little more to be sure no active tasks are running.
    stop_grace_period: 6m
    # Note that this setup with a root user is intended for development purpose.
    # Our base image runs without root, but the Docker Compose implementation needs root to access the Docker socket
    user: "root"
    command: server standalone
    volumes:
      - kestra-data:/app/storage
      - /var/run/docker.sock:/var/run/docker.sock
      - /tmp/kestra-wd:/tmp/kestra-wd
    environment:
      KESTRA_CONFIGURATION: |
        datasources:
          postgres:
            url: jdbc:postgresql://postgres:5432/kestra
            driverClassName: org.postgresql.Driver
            username: kestra
            password: k3str4
        kestra:
          # server:
          #   basic-auth:
          #     username: admin@kestra.io # it must be a valid email address
          #     password: Admin1234! # it must be at least 8 characters long with uppercase letter and a number
          repository:
            type: postgres
          storage:
            type: local
            local:
              base-path: "/app/storage"
          queue:
            type: postgres
          tasks:
            tmp-dir:
              path: /tmp/kestra-wd/tmp
          url: http://localhost:8080/
    ports:
      - "8080:8080"
      - "8081:8081"
    depends_on:
      postgres:
        condition: service_started
```

Para correr Kestra con solo un comando en la terminal:
```bash
docker compose up
```

Una vez que nos conectamos a localhost:8080 hacemos un script de prueba

```yaml
id: partridge_169922
namespace: company.team

tasks:
  - id: python_script
    type: io.kestra.plugin.scripts.python.Script
    beforeCommands:
      - pip install requests kestra
    script: |
      import requests
      from kestra import Kestra

      r = requests.get('https://api.github.com/repos/kestra-io/kestra')
      gh_stars = r.json()['stargazers_count']
      Kestra.outputs({'gh_stars': gh_stars})
      
  - id: python_output
    type: io.kestra.plugin.core.log.Log
    message: "Number of stars: {{ outputs.python_script.vars.gh_stars}}"
```
se puede aprovechar el autocompletado con ctrl + espacio para los types por ejemplo.
Aca tenemos un script en la tarea con id "python_script" en el cual se conecta a la api de GitHub y se le hace una solicitud de cantidad de estrellas.
Con Kestra. outputs tenemos la posibilidad de retener el valr resultante, que de otra manera quedaria unicamente en los logs. Asignando la variable en una estructura de datos de clave valor.
Luego en Python_output. invocamos esa variable retenida de la tarea anterior. Retomando el pipeline.

## 2.2 Arrancando con Kestra
### 2.2.1 - Instalando Kestra

Como instalar Kestra
Conceptos relacionados a Kestra necesario para construir flujos de trabajo
Ejecutar un script de python en un workflow de Kestra

El siguiente script es un docker compose, que aparte de contar con la instalación de Kestra cuenta ya con una base de datos postgres, y el cliente pgAdmin del modulo 01.
Es una modificación del script de docker compose visto mas arriba si no me equivoco
```yaml
volumes:
  ny_taxi_postgres_data:
    driver: local
  kestra_postgres_data:
    driver: local
  kestra_data:
    driver: local

services:
  pgdatabase:
    image: postgres:18
    environment:
      POSTGRES_USER: root
      POSTGRES_PASSWORD: root
      POSTGRES_DB: ny_taxi
    ports:
      - "5432:5432"
    volumes:
      - ny_taxi_postgres_data:/var/lib/postgresql
    depends_on:
      kestra:
        condition: service_started

  pgadmin:
    image: dpage/pgadmin4
    environment:
      - PGADMIN_DEFAULT_EMAIL=TU_EMAIL
      - PGADMIN_DEFAULT_PASSWORD=root
    ports:
      - "8085:80"
    depends_on:
      pgdatabase:
        condition: service_started

  kestra_postgres:
    image: postgres:18
    volumes:
      - kestra_postgres_data:/var/lib/postgresql
    environment:
      POSTGRES_DB: kestra
      POSTGRES_USER: kestra
      POSTGRES_PASSWORD: k3str4
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -d $${POSTGRES_DB} -U $${POSTGRES_USER}"]
      interval: 30s
      timeout: 10s
      retries: 10

  kestra:
    image: kestra/kestra:v1.1
    pull_policy: always
    # Note that this setup with a root user is intended for development purpose.
    # Our base image runs without root, but the Docker Compose implementation needs root to access the Docker socket
    # To run Kestra in a rootless mode in production, see: https://kestra.io/docs/installation/podman-compose
    user: "root"
    command: server standalone
    volumes:
      - kestra_data:/app/storage
      - /var/run/docker.sock:/var/run/docker.sock
      - /tmp/kestra-wd:/tmp/kestra-wd
    environment:
      KESTRA_CONFIGURATION: |
        datasources:
          postgres:
            url: jdbc:postgresql://kestra_postgres:5432/kestra
            driverClassName: org.postgresql.Driver
            username: kestra
            password: k3str4
        kestra:
          server:
            basicAuth:
              username: "admin@kestra.io" # it must be a valid email address
              password: Admin1234!
          repository:
            type: postgres
          storage:
            type: local
            local:
              basePath: "/app/storage"
          queue:
            type: postgres
          tasks:
            tmpDir:
              path: /tmp/kestra-wd/tmp
          url: http://localhost:8080/
    ports:
      - "8080:8080"
      - "8081:8081"
    depends_on:
      kestra_postgres:
        condition: service_started
    
```

Ojo, si tarda en activarse el puerto de Kestra
```yaml
  depends_on:
      kestra_postgres:
        condition: service_started
        
```
Esto, colisiona con el check health de:
```yaml
  kestra_postgres:
    image: postgres:18
    volumes:
      - kestra_postgres_data:/var/lib/postgresql
    environment:
      POSTGRES_DB: kestra
      POSTGRES_USER: kestra
      POSTGRES_PASSWORD: k3str4
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -d $${POSTGRES_DB} -U $${POSTGRES_USER}"]
      interval: 30s
      timeout: 10s
      retries: 10
```

---
### Post-Mortem: El Misterio del 404 y el Cold Start en Kestra

### 📝 Contexto

Al levantar un stack de orquestación (Kestra + Postgres) mediante Docker Compose en un entorno WSL2, los servicios parecían estar activos (`Up`), pero la interfaz web y la API no respondían inicialmente o devolvían errores 404.

#### 🔍 Diagnóstico Técnico (El "Por Qué")

1. **Cold Start (Arranque en Frío):** Un contenedor `Up` solo significa que el proceso principal ha iniciado, no que la aplicación esté lista. Kestra es una app Java que requiere tiempo para cargar el contexto de Spring Boot.
    
2. **Database Migrations (Flyway):** En el primer arranque, Kestra detectó una base de datos vacía y ejecutó **43 migraciones de esquema**. Hasta que la última tabla no se crea, el servidor web no abre los puertos de comunicación.
    
3. **Race Condition (Condición de Carrera):** El servicio `kestra` intentó conectar a `kestra_postgres` mientras esta última aún estaba inicializando su motor (Estado: `health: starting`).
    
4. **WSL2 Bridge Delay:** En entornos Windows con WSL2, el mapeo de red entre el host y el kernel de Linux puede tener una latencia extra mientras se estabilizan las tablas de ruteo de Docker.
    
#### 🛠️ Comandos de Verificación (Cheat Sheet para la Terminal)

|**Objetivo**|**Comando CLI**|
|---|---|
|**Ver salud real**|`docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Health}}"`|
|**Ver progreso interno**|`docker logs -f <nombre_contenedor>`|
|**Testear API (Auth)**|`curl -i -u user:pass http://localhost:8080/api/v1/flows`|
|**Healthcheck rápido**|`curl -i http://localhost:8081/health`|

#### 💡 Lecciones Aprendidas (Key Takeaways)

- **No confíes en `docker ps`:** Un contenedor puede estar "Up" pero estar "muerto" por dentro si la aplicación falló al conectar a la DB.
    
- **Logs sobre UI:** Siempre revisa los logs antes de refrescar el navegador. Los logs de Flyway confirmaron que el sistema estaba trabajando, no colapsado.
    
- **Healthchecks son Ley:** Configurar `condition: service_healthy` en el `docker-compose` evita que los servicios dependientes arranquen antes de tiempo.
---

### 2.2.2 Conceptos de Kestra

##### Conceptos Core de Kestra (Arquitectura de Flujos)
###### Flow (flujo): 
Es precisamente el blueprint, el script que contiene las distintas tareas (tasks), con la lógica de orquestación que uno defina de punta a punta. Se define en YAML.
###### Tasks (tareas):
Es cada una de las tareas individuales que componen el flow. Como Kestra esta basado en plugins, cada tarea suele invoca un plugin individual.
###### Inputs (entradas):
Son los parametros dinamicos que pueden aplicarse al inicio y que seran utilizados por el flow.
###### Outputs (salidas): 
Es el mecanismo que permite el traspaso de información entre tareas.
###### Triggers (disparadores):
Es el mecanismo de automatización. Que se activa ya se con un evento externo (ej. llegada de archivo a S3), una programación temporal especifica (cron), o una llamada via API (webhooks)
###### Control y Estado del Sistema
Execution (ejecución):
Es una instancia viva del flow. Una analogia útil es que seria como el proceso en la memoria de un código en ejecución. Tienen ID único, estado (success, failed, running) y logs detallados.
###### Variables:
Están en formato de claves pares valor. Tenes variables de sistema como {{ execution.startDate }} y las que quieres definir vos.
###### Plugin Defaults:
Importante. Permite establecer valores por defecto para cada plugin.
Por ejemplo, permite definir usuario, contraseña y cualquier otro valor similar necesario para conectarse a una base de datos Postgres.
###### Concurrency (concurrencia):
Es el control del trafico. Se encarga de manejar cuantos flujos suceden paralelamente.

Dato de color:
	A la derecha dependiendo donde hagamos click en el flow, si tenemos activada la pestaña de documentation podemos ver descripción, ejemplos, etc. de el tipo de elemento en el que estemos parado (task, output, log, etc.)

### 2.2.3 Orquestar código de Python

Kestra nos permite correr código de python de un archivo dedicado, pero también se puede correrlo directamente en el flujo de Kestra.
Lo que hace este código es conectarse con una api de GitHub para recuperar un dato en particular, en este caso seria la cantidad de descargas que tiene esa imagen Docker de Kestra.
Se asigna previamente a una variable un par de clave/valor.
Después se utiliza la biblioteca de python, "Kestra". Y particularmente la función Kestra.outputs para cargar esa variable con la clave/valor asignada en outputs.
[02_python.yaml](https://github.com/DataTalksClub/data-engineering-zoomcamp/blob/main/02-workflow-orchestration/flows/02_python.yaml "02_python.yaml")
```yaml
id: 02_python
namespace: zoomcamp

description: This flow will install the pip package in a Docker container, and use kestra's Python library to generate outputs (number of downloads of the Kestra Docker image) and metrics (duration of the script).

tasks:
  - id: collect_stats
    type: io.kestra.plugin.scripts.python.Script
    taskRunner:
      type: io.kestra.plugin.scripts.runner.docker.Docker
    containerImage: python:slim
    dependencies:
      - requests
      - kestra
    script: |
      from kestra import Kestra
      import requests
      def get_docker_image_downloads(image_name: str = "kestra/kestra"):
          """Queries the Docker Hub API to get the number of downloads for a specific Docker image."""
          url = f"https://hub.docker.com/v2/repositories/{image_name}/"
          response = requests.get(url)
          data = response.json()
          downloads = data.get('pull_count', 'Not available')
          return downloads
      downloads = get_docker_image_downloads()
      outputs = {
          'downloads': downloads
      }
      Kestra.outputs(outputs)
```

Puntos interesantes:
- Kestra puede correr archivos con código python dedicado, pero también directamente correr el script en su script YAML.
- En type encontramos muchísimas herramientas, vemos que la de este caso se dedica a correr scripts de python
- En task Runner notamos que se define que todo corra en un contendor docker.
- En dependencies se instala previamente a correr el script, todas las bibliotecas de python que se necesitaran
- En el script notamos que se inicia con un " | " :  YAML trata de ser eficiente con el espacio, y toma los saltos de linea muy distinto a como lo toma python por ejemplo. El cual es un lenguaje en el que los espacios tienen una relevancia mayor. Entonces con el símbolo "pipe", se le dice a Kestra: _"Todo lo que viene debajo de esta línea, respétalo exactamente como está escrito, manteniendo los saltos de línea y la sangría"_.
- Asunto outputs, fundamental
*IMPORTANTE - OUTPUTS*
Los outputs en Kestra funcionan con un método de Almacenamiento / Referencia
Por ejemplo cuando ejecutamos en un script de python Kestra.outputs({'Downloads': downloads}), Kestra toma ese diccionario y lo almacena en su servidor. (En este caso es una variable que almacena).
De esa manera Kestra guarda en su base de datos interna los datos, asociado directamente a esa ejecución y al ID de esa tarea.
La manera de llamar esas referencias de vuelta es con una sintaxis especial denominada JinJa:
`{{outputs.collect_stats.vars.downloads}}`

3 conceptos también interesantes:
- Desacoplamiento (la razón arquitectónica): es de mayor utilidad que cada tarea sea independiente. De esta manera las tareas que recopilan información, datos, valores, etc. No tienen porque utilizarla instantemente ni saber para que se la utilizara.
- Trazabilidad y auditaría: Si fallara el flujo podes fijarte en los outputs de Kestra a ver que valor devolvió.
- Tipos de Outputs (valores vs archivos): Los outputs pueden ser de dons tipos de salidas *variables (JSON)* o *Internal Storage (URI)*. En el primer caso son datos pequeños números, textos cortos o booleanos. En el segundo caso son por ejemplo archivos .csv que pesan 1gb, y en ese caso se sube a un almacenamiento (GCP, S3, disco local, etc.) y el output es en realidad un enlace (URI) y para que la siguiente tarea que lo convoque lo descargue.
Para tener acceso a estos outputs. En *Executions* seleccionamos el flow ejecutado, vamos a la pestaña outputs para ver los valores recuperados de los procesos ejecutados. Tasks > Outputs (y seleccionamos lo que estamos buscando)

## 2.3 Manos a la obra, proyecto de código: Construir data pipelines con Kestra

Vamos a construir pipelines ETL (Extract, Transform, Load):
1. Extraeremos datos de archivos CSV
2. Cargaremos esos datos en Postgres o Google Cloud (GCS + BigQuery)
3. Exploraremos como programar (scheduling) y recuperar (backfilling) workflows

### 2.3.1 Arrancando con los pipelines
Este flujo introductorio se añade solo para demostrar una canalización de datos (data pipeline) simple que extrae datos a través de una API REST HTTP, los transforma en Python y luego los consulta utilizando DuckDB. Para esta etapa, se crea una nueva base de datos Postgres independiente para los ejercicios.

[03_getting_started_data_pipeline.yaml](https://github.com/DataTalksClub/data-engineering-zoomcamp/blob/main/02-workflow-orchestration/flows/03_getting_started_data_pipeline.yaml "03_getting_started_data_pipeline.yaml")
```yaml
id: 03_getting_started_data_pipeline
namespace: zoomcamp

inputs:
  - id: columns_to_keep
    type: ARRAY
    itemType: STRING
    defaults:
      - brand
      - price

tasks:
  - id: extract
    type: io.kestra.plugin.core.http.Download
    uri: https://dummyjson.com/products

  - id: transform
    type: io.kestra.plugin.scripts.python.Script
    containerImage: python:3.11-alpine
    inputFiles:
      data.json: "{{outputs.extract.uri}}"
    outputFiles:
      - "*.json"
    env:
      COLUMNS_TO_KEEP: "{{inputs.columns_to_keep}}"
    script: |
      import json
      import os

      columns_to_keep_str = os.getenv("COLUMNS_TO_KEEP")
      columns_to_keep = json.loads(columns_to_keep_str)

      with open("data.json", "r") as file:
          data = json.load(file)

      filtered_data = [
          {column: product.get(column, "N/A") for column in columns_to_keep}
          for product in data["products"]
      ]

      with open("products.json", "w") as file:
          json.dump(filtered_data, file, indent=4)

  - id: query
    type: io.kestra.plugin.jdbc.duckdb.Queries
    inputFiles:
      products.json: "{{outputs.transform.outputFiles['products.json']}}"
    sql: |
      INSTALL json;
      LOAD json;
      SELECT brand, round(avg(price), 2) as avg_price
      FROM read_json_auto('{{workingDir}}/products.json')
      GROUP BY brand
      ORDER BY avg_price DESC;
    fetchType: STORE
```
Puntos interesantes:
- Aparecen los *inputs*. Podemos ingresar datos que utilizaremos en el workflow. En este caso un *ARRAY* de strings. con el id de columns_to_keep que nos indica que sea utilizado para definir columnas a mantener a la hora de la transformacion.
- id: extract. Aca vemos que se descarga el archivo json, en formato crudo. Y es almacenado con salida *URI*
- id: transform. Se utiliza python corriendo en un contenedor docker, (imagen python 3.11 alpine),  y extraemos del almacenamiento URI con la sintaxis JinJa {{outputs.extract.uri}}. Se define que como output files se tome todo lo que sea formato JSON (`*.json`) . Se cargarn variables de entorno con "env". y finalmente se ejecuta el script que transforma los datos y le da el formato que buscamos.
- id: query. Se utiliza duckdb para hacer una consulta en particular a los datos trasnformados. Se guarda como fetchtype: STORE?
-  ¿Consultar un JSON en lugar de una base de datos?
**DuckDB** (el plugin que usa la última tarea) no es una base de datos tradicional como MySQL o PostgreSQL que requiere un servidor corriendo 24/7. Es una base de datos **OLAP in-process**.
**¿Qué significa esto?** Que DuckDB tiene la capacidad de tratar archivos (JSON, CSV, Parquet) como si fueran tablas temporales en memoria.
**¿Por qué lo hacemos así?** Porque es mucho más rápido y barato. No tienes que "subir" los datos a una base de datos, crear esquemas y luego borrarlos. Simplemente le dices: _"Oye, lee este JSON y hazle un SELECT como si fuera una tabla"_.
-   `fetchType: STORE`
Aquí es donde la terminología de Kestra puede ser confusa al principio. Tienes razón en que los outputs suelen ser variables o URIs (enlaces a archivos).
`fetchType: STORE` es una instrucción específica para los plugins de bases de datos (JDBC) que hace lo siguiente:
**Normalmente (`fetchType: FETCH`):** Kestra intentaría traer todos los resultados de la consulta SQL (las filas y columnas) y meterlos en una **variable** de salida. Si la consulta devuelve 1 millón de filas, el flujo colapsaría porque una "variable" no puede ser tan grande.
**Con `STORE`:** Kestra dice: _"No me des los datos en una variable. Toma el resultado de la consulta, conviértelo en un archivo binario (normalmente .ion o .arrow) y guárdalo en el **Internal Storage**"_.
**Entonces, el output final sigue siendo una URI**, pero una que apunta a un archivo que contiene los resultados de tu SQL.

### 2.3.2 DB local: Cargando datos de taxis en Postgres
Ahora si, al estar levantando con Docker Compose  tambien Postgres. Aprovechamos para cargar ahi los datos.
Extraeremos los datos CSV, se crearan tabblas, y se cargaran los datos en tablas mensuales, para finalmente unirlas (Merge) los datos en una tabla final.

[04_postgres_taxi.yaml](https://github.com/DataTalksClub/data-engineering-zoomcamp/blob/main/02-workflow-orchestration/flows/04_postgres_taxi.yaml "04_postgres_taxi.yaml")
```yaml
id: 04_postgres_taxi
namespace: zoomcamp
description: |
  The CSV Data used in the course: https://github.com/DataTalksClub/nyc-tlc-data/releases

inputs:
  - id: taxi
    type: SELECT
    displayName: Select taxi type
    values: [yellow, green]
    defaults: yellow

  - id: year
    type: SELECT
    displayName: Select year
    values: ["2019", "2020"]
    defaults: "2019"

  - id: month
    type: SELECT
    displayName: Select month
    values: ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"]
    defaults: "01"

variables:
  file: "{{inputs.taxi}}_tripdata_{{inputs.year}}-{{inputs.month}}.csv"
  staging_table: "public.{{inputs.taxi}}_tripdata_staging"
  table: "public.{{inputs.taxi}}_tripdata"
  data: "{{outputs.extract.outputFiles[inputs.taxi ~ '_tripdata_' ~ inputs.year ~ '-' ~ inputs.month ~ '.csv']}}"

tasks:
  - id: set_label
    type: io.kestra.plugin.core.execution.Labels
    labels:
      file: "{{render(vars.file)}}"
      taxi: "{{inputs.taxi}}"

  - id: extract
    type: io.kestra.plugin.scripts.shell.Commands
    outputFiles:
      - "*.csv"
    taskRunner:
      type: io.kestra.plugin.core.runner.Process
    commands:
      - wget -qO- https://github.com/DataTalksClub/nyc-tlc-data/releases/download/{{inputs.taxi}}/{{render(vars.file)}}.gz | gunzip > {{render(vars.file)}}

  - id: if_yellow_taxi
    type: io.kestra.plugin.core.flow.If
    condition: "{{inputs.taxi == 'yellow'}}"
    then:
      - id: yellow_create_table
        type: io.kestra.plugin.jdbc.postgresql.Queries
        sql: |
          CREATE TABLE IF NOT EXISTS {{render(vars.table)}} (
              unique_row_id          text,
              filename               text,
              VendorID               text,
              tpep_pickup_datetime   timestamp,
              tpep_dropoff_datetime  timestamp,
              passenger_count        integer,
              trip_distance          double precision,
              RatecodeID             text,
              store_and_fwd_flag     text,
              PULocationID           text,
              DOLocationID           text,
              payment_type           integer,
              fare_amount            double precision,
              extra                  double precision,
              mta_tax                double precision,
              tip_amount             double precision,
              tolls_amount           double precision,
              improvement_surcharge  double precision,
              total_amount           double precision,
              congestion_surcharge   double precision
          );

      - id: yellow_create_staging_table
        type: io.kestra.plugin.jdbc.postgresql.Queries
        sql: |
          CREATE TABLE IF NOT EXISTS {{render(vars.staging_table)}} (
              unique_row_id          text,
              filename               text,
              VendorID               text,
              tpep_pickup_datetime   timestamp,
              tpep_dropoff_datetime  timestamp,
              passenger_count        integer,
              trip_distance          double precision,
              RatecodeID             text,
              store_and_fwd_flag     text,
              PULocationID           text,
              DOLocationID           text,
              payment_type           integer,
              fare_amount            double precision,
              extra                  double precision,
              mta_tax                double precision,
              tip_amount             double precision,
              tolls_amount           double precision,
              improvement_surcharge  double precision,
              total_amount           double precision,
              congestion_surcharge   double precision
          );

      - id: yellow_truncate_staging_table
        type: io.kestra.plugin.jdbc.postgresql.Queries
        sql: |
          TRUNCATE TABLE {{render(vars.staging_table)}};

      - id: yellow_copy_in_to_staging_table
        type: io.kestra.plugin.jdbc.postgresql.CopyIn
        format: CSV
        from: "{{render(vars.data)}}"
        table: "{{render(vars.staging_table)}}"
        header: true
        columns: [VendorID,tpep_pickup_datetime,tpep_dropoff_datetime,passenger_count,trip_distance,RatecodeID,store_and_fwd_flag,PULocationID,DOLocationID,payment_type,fare_amount,extra,mta_tax,tip_amount,tolls_amount,improvement_surcharge,total_amount,congestion_surcharge]

      - id: yellow_add_unique_id_and_filename
        type: io.kestra.plugin.jdbc.postgresql.Queries
        sql: |
          UPDATE {{render(vars.staging_table)}}
          SET 
            unique_row_id = md5(
              COALESCE(CAST(VendorID AS text), '') ||
              COALESCE(CAST(tpep_pickup_datetime AS text), '') || 
              COALESCE(CAST(tpep_dropoff_datetime AS text), '') || 
              COALESCE(PULocationID, '') || 
              COALESCE(DOLocationID, '') || 
              COALESCE(CAST(fare_amount AS text), '') || 
              COALESCE(CAST(trip_distance AS text), '')      
            ),
            filename = '{{render(vars.file)}}';

      - id: yellow_merge_data
        type: io.kestra.plugin.jdbc.postgresql.Queries
        sql: |
          MERGE INTO {{render(vars.table)}} AS T
          USING {{render(vars.staging_table)}} AS S
          ON T.unique_row_id = S.unique_row_id
          WHEN NOT MATCHED THEN
            INSERT (
              unique_row_id, filename, VendorID, tpep_pickup_datetime, tpep_dropoff_datetime,
              passenger_count, trip_distance, RatecodeID, store_and_fwd_flag, PULocationID,
              DOLocationID, payment_type, fare_amount, extra, mta_tax, tip_amount, tolls_amount,
              improvement_surcharge, total_amount, congestion_surcharge
            )
            VALUES (
              S.unique_row_id, S.filename, S.VendorID, S.tpep_pickup_datetime, S.tpep_dropoff_datetime,
              S.passenger_count, S.trip_distance, S.RatecodeID, S.store_and_fwd_flag, S.PULocationID,
              S.DOLocationID, S.payment_type, S.fare_amount, S.extra, S.mta_tax, S.tip_amount, S.tolls_amount,
              S.improvement_surcharge, S.total_amount, S.congestion_surcharge
            );

  - id: if_green_taxi
    type: io.kestra.plugin.core.flow.If
    condition: "{{inputs.taxi == 'green'}}"
    then:
      - id: green_create_table
        type: io.kestra.plugin.jdbc.postgresql.Queries
        sql: |
          CREATE TABLE IF NOT EXISTS {{render(vars.table)}} (
              unique_row_id          text,
              filename               text,
              VendorID               text,
              lpep_pickup_datetime   timestamp,
              lpep_dropoff_datetime  timestamp,
              store_and_fwd_flag     text,
              RatecodeID             text,
              PULocationID           text,
              DOLocationID           text,
              passenger_count        integer,
              trip_distance          double precision,
              fare_amount            double precision,
              extra                  double precision,
              mta_tax                double precision,
              tip_amount             double precision,
              tolls_amount           double precision,
              ehail_fee              double precision,
              improvement_surcharge  double precision,
              total_amount           double precision,
              payment_type           integer,
              trip_type              integer,
              congestion_surcharge   double precision
          );

      - id: green_create_staging_table
        type: io.kestra.plugin.jdbc.postgresql.Queries
        sql: |
          CREATE TABLE IF NOT EXISTS {{render(vars.staging_table)}} (
              unique_row_id          text,
              filename               text,
              VendorID               text,
              lpep_pickup_datetime   timestamp,
              lpep_dropoff_datetime  timestamp,
              store_and_fwd_flag     text,
              RatecodeID             text,
              PULocationID           text,
              DOLocationID           text,
              passenger_count        integer,
              trip_distance          double precision,
              fare_amount            double precision,
              extra                  double precision,
              mta_tax                double precision,
              tip_amount             double precision,
              tolls_amount           double precision,
              ehail_fee              double precision,
              improvement_surcharge  double precision,
              total_amount           double precision,
              payment_type           integer,
              trip_type              integer,
              congestion_surcharge   double precision
          );

      - id: green_truncate_staging_table
        type: io.kestra.plugin.jdbc.postgresql.Queries
        sql: |
          TRUNCATE TABLE {{render(vars.staging_table)}};

      - id: green_copy_in_to_staging_table
        type: io.kestra.plugin.jdbc.postgresql.CopyIn
        format: CSV
        from: "{{render(vars.data)}}"
        table: "{{render(vars.staging_table)}}"
        header: true
        columns: [VendorID,lpep_pickup_datetime,lpep_dropoff_datetime,store_and_fwd_flag,RatecodeID,PULocationID,DOLocationID,passenger_count,trip_distance,fare_amount,extra,mta_tax,tip_amount,tolls_amount,ehail_fee,improvement_surcharge,total_amount,payment_type,trip_type,congestion_surcharge]

      - id: green_add_unique_id_and_filename
        type: io.kestra.plugin.jdbc.postgresql.Queries
        sql: |
          UPDATE {{render(vars.staging_table)}}
          SET 
            unique_row_id = md5(
              COALESCE(CAST(VendorID AS text), '') ||
              COALESCE(CAST(lpep_pickup_datetime AS text), '') || 
              COALESCE(CAST(lpep_dropoff_datetime AS text), '') || 
              COALESCE(PULocationID, '') || 
              COALESCE(DOLocationID, '') || 
              COALESCE(CAST(fare_amount AS text), '') || 
              COALESCE(CAST(trip_distance AS text), '')      
            ),
            filename = '{{render(vars.file)}}';

      - id: green_merge_data
        type: io.kestra.plugin.jdbc.postgresql.Queries
        sql: |
          MERGE INTO {{render(vars.table)}} AS T
          USING {{render(vars.staging_table)}} AS S
          ON T.unique_row_id = S.unique_row_id
          WHEN NOT MATCHED THEN
            INSERT (
              unique_row_id, filename, VendorID, lpep_pickup_datetime, lpep_dropoff_datetime,
              store_and_fwd_flag, RatecodeID, PULocationID, DOLocationID, passenger_count,
              trip_distance, fare_amount, extra, mta_tax, tip_amount, tolls_amount, ehail_fee,
              improvement_surcharge, total_amount, payment_type, trip_type, congestion_surcharge
            )
            VALUES (
              S.unique_row_id, S.filename, S.VendorID, S.lpep_pickup_datetime, S.lpep_dropoff_datetime,
              S.store_and_fwd_flag, S.RatecodeID, S.PULocationID, S.DOLocationID, S.passenger_count,
              S.trip_distance, S.fare_amount, S.extra, S.mta_tax, S.tip_amount, S.tolls_amount, S.ehail_fee,
              S.improvement_surcharge, S.total_amount, S.payment_type, S.trip_type, S.congestion_surcharge
            );
  
  - id: purge_files
    type: io.kestra.plugin.core.storage.PurgeCurrentExecutionFiles
    description: This will remove output files. If you'd like to explore Kestra outputs, disable it.

pluginDefaults:
  - type: io.kestra.plugin.jdbc.postgresql
    values:
      url: jdbc:postgresql://pgdatabase:5432/ny_taxi
      username: root
      password: root
```

Puntos interesantes:
- En este casos en los input podemos definir datos que son los que determinaran de donde se decargaran los archivos, como se transformaran y en que tablas se descargaran. Esto lo definimos seleccionando tipo de color del taxi, el año, y el mes.
- Variables: Aqui vemos el primer uso que se le da a los inputs. Ya que con los mismos se contruyen las siguientes variables:
1. file, o archivo. Se define con un string cual sera el archivo a descargar o con el que se trabajará. file: "{{inputs.taxi}}_tripdata_{{inputs.year}}-{{inputs.month}}.csv"
2. staging_table. 
3. table
4. data. 

- id: set_label. Genera una etiqueta. En este caso con el "file" y el color del taxi. Para saber cual proceso se ejecuto.
- id: extract. utiliza los comandos de la terminal (Shell), con wget para descargar el archivo csv.gz desde el github de datatalkclub y lo descompime en un gunzip. en tiempo real
- Vemos una logica condicional, ya que dependiendo del tipo de taxi se activa un bloque u otro. Bloque `if_yellow_taxi` con la condicion `condition: "{{inputs.taxi == 'yellow'}}"` (y análogamente para `green`):
- **`yellow_create_table`**: Crea la tabla final donde vivirán los datos permanentemente si no existe
- **`yellow_create_staging_table`**: Crea una tabla temporal (staging). Es una copia exacta de la estructura pero sirve para "limpiar" los datos antes del paso final.
- **`yellow_truncate_staging_table`**: Se asegura de que la tabla de staging esté vacía (borra lo que haya quedado de ejecuciones anteriores).
- **`yellow_copy_in_to_staging_table`**: Esta es la tarea más rápida. En lugar de insertar fila por fila, usa el comando `COPY` de PostgreSQL para "volcar" todo el archivo CSV directamente en la tabla de staging.
- **`yellow_add_unique_id_and_filename`**: **Paso de limpieza.** Crea un ID único (`md5`) usando varias columnas (hora, lugar, costo). Esto sirve para evitar duplicados si corres el script dos veces. También anota de qué archivo vino el dato.
- **`yellow_merge_data`**: Es el gran final. Compara la tabla de staging con la tabla final. Si un registro nuevo no existe (basado en el ID único), lo inserta. Esto garantiza que tus datos sean consistentes y no se repitan.

- Limpieza de la Casa: **`purge_files`**: Una vez que los datos ya están seguros dentro de PostgreSQL, ya no necesitamos los archivos `.csv` pesados ocupando espacio en el almacenamiento de Kestra. Esta tarea borra los archivos temporales de la ejecución actual.

- **`pluginDefaults`**: Al final del script verás que no se repite la contraseña y el usuario en cada tarea. Se define una vez abajo para que todas las tareas de PostgreSQL la hereden. Eso es **código limpio**.

 - **Idempotencia**: Gracias al paso de `unique_row_id` y el `MERGE`, puedes correr este script 100 veces y no tendrás datos duplicados. Es una característica vital en Big Data.

IMPORTANTE:
Como sabemos en este caso nos conectamos con pdadmin a la base de dato postgres. Todo esto levantado con el docker compose, donde ya se configuraron los datos de usuario para ingresar a ambos.
Sin embargo en este otros script de Kestra vemos en plugin defaults:
```yaml
pluginDefaults:
  - type: io.kestra.plugin.jdbc.postgresql
    values:
      url: jdbc:postgresql://pgdatabase:5432/ny_taxi
      username: root
      password: root
```
Es importante para conectarse al servidor estos datos. Ya que usaremos en Register > Server > Connections (pestaña)
Host name/address : `pgdatabase`
Port: 5432 (definido con Docker Compose)
Username: `root`
Password: `root`

### 2.3.3 DB local: programando y rellenando (Scheduling and Backfills)

Ahora podemos programar el mismo flujo mostrado anteriormente para que se ejecute diariamente a las 9 AM UTC. También demostraremos cómo realizar un **backfill** de la canalización de datos para que se ejecute con datos históricos.

Nota: debido al gran tamaño del conjunto de datos, realizaremos el **backfill** únicamente para los datos de los taxis verdes correspondientes al año 2019.

[05_postgres_taxi_scheduled.yaml](https://github.com/DataTalksClub/data-engineering-zoomcamp/blob/main/02-workflow-orchestration/flows/05_postgres_taxi_scheduled.yaml "05_postgres_taxi_scheduled.yaml")
```yaml
id: 05_postgres_taxi_scheduled
namespace: zoomcamp
description: |
  Best to add a label `backfill:true` from the UI to track executions created via a backfill.
  CSV data used here comes from: https://github.com/DataTalksClub/nyc-tlc-data/releases

concurrency:
  limit: 1

inputs:
  - id: taxi
    type: SELECT
    displayName: Select taxi type
    values: [yellow, green]
    defaults: yellow

variables:
  file: "{{inputs.taxi}}_tripdata_{{trigger.date | date('yyyy-MM')}}.csv"
  staging_table: "public.{{inputs.taxi}}_tripdata_staging"
  table: "public.{{inputs.taxi}}_tripdata"
  data: "{{outputs.extract.outputFiles[inputs.taxi ~ '_tripdata_' ~ (trigger.date | date('yyyy-MM')) ~ '.csv']}}"

tasks:
  - id: set_label
    type: io.kestra.plugin.core.execution.Labels
    labels:
      file: "{{render(vars.file)}}"
      taxi: "{{inputs.taxi}}"

  - id: extract
    type: io.kestra.plugin.scripts.shell.Commands
    outputFiles:
      - "*.csv"
    taskRunner:
      type: io.kestra.plugin.core.runner.Process
    commands:
      - wget -qO- https://github.com/DataTalksClub/nyc-tlc-data/releases/download/{{inputs.taxi}}/{{render(vars.file)}}.gz | gunzip > {{render(vars.file)}}

  - id: if_yellow_taxi
    type: io.kestra.plugin.core.flow.If
    condition: "{{inputs.taxi == 'yellow'}}"
    then:
      - id: yellow_create_table
        type: io.kestra.plugin.jdbc.postgresql.Queries
        sql: |
          CREATE TABLE IF NOT EXISTS {{render(vars.table)}} (
              unique_row_id          text,
              filename               text,
              VendorID               text,
              tpep_pickup_datetime   timestamp,
              tpep_dropoff_datetime  timestamp,
              passenger_count        integer,
              trip_distance          double precision,
              RatecodeID             text,
              store_and_fwd_flag     text,
              PULocationID           text,
              DOLocationID           text,
              payment_type           integer,
              fare_amount            double precision,
              extra                  double precision,
              mta_tax                double precision,
              tip_amount             double precision,
              tolls_amount           double precision,
              improvement_surcharge  double precision,
              total_amount           double precision,
              congestion_surcharge   double precision
          );

      - id: yellow_create_staging_table
        type: io.kestra.plugin.jdbc.postgresql.Queries
        sql: |
          CREATE TABLE IF NOT EXISTS {{render(vars.staging_table)}} (
              unique_row_id          text,
              filename               text,
              VendorID               text,
              tpep_pickup_datetime   timestamp,
              tpep_dropoff_datetime  timestamp,
              passenger_count        integer,
              trip_distance          double precision,
              RatecodeID             text,
              store_and_fwd_flag     text,
              PULocationID           text,
              DOLocationID           text,
              payment_type           integer,
              fare_amount            double precision,
              extra                  double precision,
              mta_tax                double precision,
              tip_amount             double precision,
              tolls_amount           double precision,
              improvement_surcharge  double precision,
              total_amount           double precision,
              congestion_surcharge   double precision
          );

      - id: yellow_truncate_staging_table
        type: io.kestra.plugin.jdbc.postgresql.Queries
        sql: |
          TRUNCATE TABLE {{render(vars.staging_table)}};

      - id: yellow_copy_in_to_staging_table
        type: io.kestra.plugin.jdbc.postgresql.CopyIn
        format: CSV
        from: "{{render(vars.data)}}"
        table: "{{render(vars.staging_table)}}"
        header: true
        columns: [VendorID,tpep_pickup_datetime,tpep_dropoff_datetime,passenger_count,trip_distance,RatecodeID,store_and_fwd_flag,PULocationID,DOLocationID,payment_type,fare_amount,extra,mta_tax,tip_amount,tolls_amount,improvement_surcharge,total_amount,congestion_surcharge]

      - id: yellow_add_unique_id_and_filename
        type: io.kestra.plugin.jdbc.postgresql.Queries
        sql: |
          UPDATE {{render(vars.staging_table)}}
          SET 
            unique_row_id = md5(
              COALESCE(CAST(VendorID AS text), '') ||
              COALESCE(CAST(tpep_pickup_datetime AS text), '') || 
              COALESCE(CAST(tpep_dropoff_datetime AS text), '') || 
              COALESCE(PULocationID, '') || 
              COALESCE(DOLocationID, '') || 
              COALESCE(CAST(fare_amount AS text), '') || 
              COALESCE(CAST(trip_distance AS text), '')      
            ),
            filename = '{{render(vars.file)}}';

      - id: yellow_merge_data
        type: io.kestra.plugin.jdbc.postgresql.Queries
        sql: |
          MERGE INTO {{render(vars.table)}} AS T
          USING {{render(vars.staging_table)}} AS S
          ON T.unique_row_id = S.unique_row_id
          WHEN NOT MATCHED THEN
            INSERT (
              unique_row_id, filename, VendorID, tpep_pickup_datetime, tpep_dropoff_datetime,
              passenger_count, trip_distance, RatecodeID, store_and_fwd_flag, PULocationID,
              DOLocationID, payment_type, fare_amount, extra, mta_tax, tip_amount, tolls_amount,
              improvement_surcharge, total_amount, congestion_surcharge
            )
            VALUES (
              S.unique_row_id, S.filename, S.VendorID, S.tpep_pickup_datetime, S.tpep_dropoff_datetime,
              S.passenger_count, S.trip_distance, S.RatecodeID, S.store_and_fwd_flag, S.PULocationID,
              S.DOLocationID, S.payment_type, S.fare_amount, S.extra, S.mta_tax, S.tip_amount, S.tolls_amount,
              S.improvement_surcharge, S.total_amount, S.congestion_surcharge
            );

  - id: if_green_taxi
    type: io.kestra.plugin.core.flow.If
    condition: "{{inputs.taxi == 'green'}}"
    then:
      - id: green_create_table
        type: io.kestra.plugin.jdbc.postgresql.Queries
        sql: |
          CREATE TABLE IF NOT EXISTS {{render(vars.table)}} (
              unique_row_id          text,
              filename               text,
              VendorID               text,
              lpep_pickup_datetime   timestamp,
              lpep_dropoff_datetime  timestamp,
              store_and_fwd_flag     text,
              RatecodeID             text,
              PULocationID           text,
              DOLocationID           text,
              passenger_count        integer,
              trip_distance          double precision,
              fare_amount            double precision,
              extra                  double precision,
              mta_tax                double precision,
              tip_amount             double precision,
              tolls_amount           double precision,
              ehail_fee              double precision,
              improvement_surcharge  double precision,
              total_amount           double precision,
              payment_type           integer,
              trip_type              integer,
              congestion_surcharge   double precision
          );

      - id: green_create_staging_table
        type: io.kestra.plugin.jdbc.postgresql.Queries
        sql: |
          CREATE TABLE IF NOT EXISTS {{render(vars.staging_table)}} (
              unique_row_id          text,
              filename               text,
              VendorID               text,
              lpep_pickup_datetime   timestamp,
              lpep_dropoff_datetime  timestamp,
              store_and_fwd_flag     text,
              RatecodeID             text,
              PULocationID           text,
              DOLocationID           text,
              passenger_count        integer,
              trip_distance          double precision,
              fare_amount            double precision,
              extra                  double precision,
              mta_tax                double precision,
              tip_amount             double precision,
              tolls_amount           double precision,
              ehail_fee              double precision,
              improvement_surcharge  double precision,
              total_amount           double precision,
              payment_type           integer,
              trip_type              integer,
              congestion_surcharge   double precision
          );

      - id: green_truncate_staging_table
        type: io.kestra.plugin.jdbc.postgresql.Queries
        sql: |
          TRUNCATE TABLE {{render(vars.staging_table)}};

      - id: green_copy_in_to_staging_table
        type: io.kestra.plugin.jdbc.postgresql.CopyIn
        format: CSV
        from: "{{render(vars.data)}}"
        table: "{{render(vars.staging_table)}}"
        header: true
        columns: [VendorID,lpep_pickup_datetime,lpep_dropoff_datetime,store_and_fwd_flag,RatecodeID,PULocationID,DOLocationID,passenger_count,trip_distance,fare_amount,extra,mta_tax,tip_amount,tolls_amount,ehail_fee,improvement_surcharge,total_amount,payment_type,trip_type,congestion_surcharge]

      - id: green_add_unique_id_and_filename
        type: io.kestra.plugin.jdbc.postgresql.Queries
        sql: |
          UPDATE {{render(vars.staging_table)}}
          SET 
            unique_row_id = md5(
              COALESCE(CAST(VendorID AS text), '') ||
              COALESCE(CAST(lpep_pickup_datetime AS text), '') || 
              COALESCE(CAST(lpep_dropoff_datetime AS text), '') || 
              COALESCE(PULocationID, '') || 
              COALESCE(DOLocationID, '') || 
              COALESCE(CAST(fare_amount AS text), '') || 
              COALESCE(CAST(trip_distance AS text), '')      
            ),
            filename = '{{render(vars.file)}}';

      - id: green_merge_data
        type: io.kestra.plugin.jdbc.postgresql.Queries
        sql: |
          MERGE INTO {{render(vars.table)}} AS T
          USING {{render(vars.staging_table)}} AS S
          ON T.unique_row_id = S.unique_row_id
          WHEN NOT MATCHED THEN
            INSERT (
              unique_row_id, filename, VendorID, lpep_pickup_datetime, lpep_dropoff_datetime,
              store_and_fwd_flag, RatecodeID, PULocationID, DOLocationID, passenger_count,
              trip_distance, fare_amount, extra, mta_tax, tip_amount, tolls_amount, ehail_fee,
              improvement_surcharge, total_amount, payment_type, trip_type, congestion_surcharge
            )
            VALUES (
              S.unique_row_id, S.filename, S.VendorID, S.lpep_pickup_datetime, S.lpep_dropoff_datetime,
              S.store_and_fwd_flag, S.RatecodeID, S.PULocationID, S.DOLocationID, S.passenger_count,
              S.trip_distance, S.fare_amount, S.extra, S.mta_tax, S.tip_amount, S.tolls_amount, S.ehail_fee,
              S.improvement_surcharge, S.total_amount, S.payment_type, S.trip_type, S.congestion_surcharge
            );
  
  - id: purge_files
    type: io.kestra.plugin.core.storage.PurgeCurrentExecutionFiles
    description: To avoid cluttering your storage, we will remove the downloaded files

pluginDefaults:
  - type: io.kestra.plugin.jdbc.postgresql
    values:
      url: jdbc:postgresql://pgdatabase:5432/ny_taxi
      username: root
      password: root

triggers:
  - id: green_schedule
    type: io.kestra.plugin.core.trigger.Schedule
    cron: "0 9 1 * *"
    inputs:
      taxi: green

  - id: yellow_schedule
    type: io.kestra.plugin.core.trigger.Schedule
    cron: "0 10 1 * *"
    inputs:
      taxi: yellow
```

Puntos interesantes:
- La Gran Novedad: `triggers` y `backfill`
- El script cuenta con dos despertadores programados usando formato *cron*:
1. - **`green_schedule`**: Se ejecuta el día 1 de cada mes a las 09:00 AM (`0 9 1 * *`).
2. **`yellow_schedule`**: Se ejecuta el día 1 de cada mes a las 10:00 AM (`0 10 1 * *`).

- El concepto de triggers.date. En las variables ya no usamos input.year o input.month como en el caso anterior.
  ahora usamos {{trigger.date | date('yyyy-MM')}}
- esto es de vital importancia por dos razones:
1. **En ejecuciones programadas:** Kestra sabe automáticamente en qué fecha está y descarga el archivo correspondiente a ese mes.
2. **En Backfills:** Si te das cuenta de que te faltan los datos de todo el año 2024, puedes usar la función de **Backfill** de Kestra. Le dices: "Ejecuta este flujo para cada mes entre enero y diciembre de 2024". Kestra simulará que el tiempo pasó y el script usará la `trigger.date` correcta para cada ejecución.
BACKFILLS Y TRIGGER VAN DE LA MANO.

- ### `concurrency: limit: 1`
Este ID es vital. Le dice a Kestra: _"No importa cuántas ejecuciones haya pendientes, solo corre UNA a la vez"_. Como estamos escribiendo en una base de datos PostgreSQL, si intentamos meter 10 meses al mismo tiempo, las tablas de **staging** podrían chocar y causar errores. Esto pone orden en la fila.

- ### `variables: data`
Aquí la lógica de selección de archivos se vuelve un poco más compleja: `{{outputs.extract.outputFiles[inputs.taxi ~ '_tripdata_' ~ (trigger.date | date('yyyy-MM')) ~ '.csv']}}` Usa el símbolo `~` para concatenar (pegar) textos y construir el nombre exacto del archivo basándose en la fecha del trigger.

- Las Tareas (`extract`, `if_yellow`, `merge`, etc.)
Son idénticas al script anterior, pero con una diferencia filosófica: están diseñadas para ser **idempotentes**.
- Como el `MERGE` ya está programado, si el backfill intenta meter datos que ya existían, no pasará nada malo. El sistema simplemente dirá "esto ya lo tengo" y seguirá adelante.
##### ¿Por qué este script es el estándar de la industria?
Imagina que eres el ingeniero de datos de una empresa de taxis. Con el script anterior, tendrías que despertarte cada día 1 de mes para cargar los datos. Con **este script**:
1. Te vas de vacaciones.
2. El día 1 a las 9 AM, Kestra se despierta solo.
3. Busca la fecha actual.
4. Descarga, limpia, hace el staging y el merge en PostgreSQL.
5. Borra los archivos temporales para no gastar dinero en disco.
6. Te deja un log de que todo salió bien.
> **Consejo de clase:** La nota que ves en la descripción sobre `backfill:true` es una convención de etiqueta. Ayuda a que, cuando revises el panel de control, puedas filtrar rápidamente cuáles fueron ejecuciones "de rutina" y cuáles fueron cargas de datos históricos.

*ERROR SET_LABEL*
El error ocurre porque estás intentando darle al botón "Execute" manualmente. Al hacerlo, la variable {{trigger.date}} no existe, y como vars.file depende de esa fecha, todo el sistema de etiquetas (Labels) colapsa. Es decir que hay scripts como este que están diseñados para correr con trigger o backfill 

## 2.4 Pipelines ELT en Kestra: Google Cloud Platform
Ahora que has aprendido a construir canalizaciones **ETL** localmente usando **Postgres**, estamos listos para pasar a la **nube**. En esta sección, cargaremos los mismos datos de los taxis amarillos (_Yellow Taxi_) y verdes (_Green Taxi_) a **Google Cloud Platform (GCP)** utilizando:
- **Google Cloud Storage (GCS)** como lago de datos (_data lake_)
- **BigQuery** como almacén de datos (_data warehouse_)

### 2.4.1 - ETL vs ELT
En la sección 2.3, creamos una canalización **ETL** dentro de Kestra:
- **Extract (Extraer):** Primero, extraemos el conjunto de datos desde GitHub.
- **Transform (Transformar):** Luego, lo transformamos con Python.
- **Load (Cargar):** Finalmente, lo cargamos en nuestra base de datos Postgres.

Aunque esto es un estándar en la industria, a veces tiene sentido cambiar el orden cuando se trabaja en la **nube**. Si trabajas con conjuntos de datos grandes, como los de los taxis amarillos, puede haber beneficios al extraer y cargar directamente en un almacén de datos, para luego realizar las transformaciones allí mismo. Al trabajar con **BigQuery**, utilizaremos **ELT**:

- **Extract (Extraer):** Primero, extraemos el conjunto de datos desde GitHub.
- **Load (Cargar):** Luego, cargamos este conjunto de datos (en este caso, un archivo CSV) en un lago de datos (**Google Cloud Storage**).
- **Transform (Transformar):** Finalmente, podemos crear una tabla dentro de nuestro almacén de datos (**BigQuery**) que utilice los datos de nuestro lago de datos para realizar las transformaciones.
La razón de cargar en el almacén de datos antes de transformar es que podemos aprovechar los **beneficios de rendimiento** de la nube para procesar grandes volúmenes de datos. Lo que podría tardar mucho tiempo en una máquina local, puede tomar una fracción de ese tiempo en la nube.

### 2.4.2 Setup de Google Cloud Platform (GCP)

Antes de cargar los datos necesitamos hacer le set up de google cloud platform

Lo que se hasta ahora con este script es cargar en Kestra, en *KV Store* estos valores que se necesitaran para el script que le sigue.
Primero. Ajustar el siguiente script para incluir el *service account*, *GCP project ID*, *BigQuery dataset* and *GCS bucket name* (junto con su locacion) como KV Store Values:
- GCP_PROJECT_ID
- GCP_LOCATION
- GCP_BUCKET_NAME
- GCP_DATASET.
[06_gcp_kv.yaml](https://github.com/DataTalksClub/data-engineering-zoomcamp/blob/main/02-workflow-orchestration/flows/06_gcp_kv.yaml "06_gcp_kv.yaml")
```yaml
id: 06_gcp_kv
namespace: zoomcamp

tasks:
  - id: gcp_project_id
    type: io.kestra.plugin.core.kv.Set
    key: GCP_PROJECT_ID
    kvType: STRING
    value: kestra-sandbox # TODO replace with your project id

  - id: gcp_location
    type: io.kestra.plugin.core.kv.Set
    key: GCP_LOCATION
    kvType: STRING
    value: TU_REGION

  - id: gcp_bucket_name
    type: io.kestra.plugin.core.kv.Set
    key: GCP_BUCKET_NAME
    kvType: STRING
    value: your-name-kestra # TODO make sure it's globally unique!

  - id: gcp_dataset
    type: io.kestra.plugin.core.kv.Set
    key: GCP_DATASET
    kvType: STRING
    value: zoomcamp
```

EJEMPLO DE PRUEBA (IMPORTANTE, SOLUCION SIN SECRETS):![[company.team.swallow_904373.yaml]]
```yaml
id: 06_gcp_kv

namespace: zoomcamp

  

tasks:

  - id: set_gcp_creds

    type: io.kestra.plugin.core.kv.Set

    key: GCP_CREDS

    kvType: STRING

    value: |

      {

        "type": "service_account",

        "project_id": "TU_PROYECTO_ID",

        "private_key_id": "TU_LLAVE_PRIVADA_AQUI",

        "private_key": "-----BEGIN PRIVATE KEY-----\TU_LLAVE_PRIVADA_AQUI\n-----END PRIVATE KEY-----\n",

        "client_email": "xxxxxxxxxxxx",

        "client_id": "107538322334698760437",

        "auth_uri": "https://accounts.google.com/o/oauth2/auth",

        "token_uri": "https://oauth2.googleapis.com/token",

        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",

        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/for-kestra%40NOMBRE_DE_TU_PROYECTO.iam.gserviceaccount.com",

        "universe_domain": "googleapis.com"

      }

  

  - id: gcp_project_id

    type: io.kestra.plugin.core.kv.Set

    key: GCP_PROJECT_ID

    kvType: STRING

    value: NOMBRE_DE_TU_PROYECTO # TODO replace with your project id

  

  - id: gcp_location

    type: io.kestra.plugin.core.kv.Set

    key: GCP_LOCATION

    kvType: STRING

    value: TU_REGION

  

  - id: gcp_bucket_name

    type: io.kestra.plugin.core.kv.Set

    key: GCP_BUCKET_NAME

    kvType: STRING

    value: NOMBRE_DE_TU_BUCKET # TODO make sure it's globally unique!

  

  - id: gcp_dataset

    type: io.kestra.plugin.core.kv.Set

    key: GCP_DATASET

    kvType: STRING

    value: zoomcamp
```
Puntos interesantes:
- set_gcp_creds: El actor que aparece. Abajo de esta seccion voy a proceder a explicar un poco porque se tuvo que hacer de esta manera. Pero de momento importante saber que se hace esto para cargar en Kestra la clave del service acount que uno descarga cuando esta configurando google platform. Es un archivo .JSON. Despues desde la izquierda en el panel de kestra, uno puede revisar que se haya cargado correctamente el key.
- id: gcp_project_id: Aca tenemos que logicmente colocarl en value el id del proyecto en que queremos trabajar de google platform
- id: gcp_location: Definir locacion (En lo posible un data center cercano)
- id: gcp_bucket_name: Definir nombre del bucket. Que sea globalmente único. Puede ser uno existente
- id: gcp_dataset: Elegiremos "Zoomcamp" como nombre

*IMPORTANTE Maneras de resolver cuestión Key:*
En el curso explican que hay una manera mas segura denominada secrets. Pero es para la version paga de Kestra.
Tambien se puede cargar los valores del .JSON en el archivo YAML pero del Docker-compose. Sin embargo este no funciona siempre bien, como aclaran en la pagina oficial. Lo que nos deja con el método que utilizamos mas arriba. Sin embargo es IMPORTANTE recordar que esto no es seguro. Ya que estamos haciendo hard-coding en el script y dejándolo en Kestra. Si alguien accediera a nuestro Kestra obtendría nuestra clave de acceso fácilmente.

Y ahora si Creamos el bucket, el dataset y establecemos los valores que definimos en el script anterior como las credenciales , id, locación, nombres, etc. Default.
[07_gcp_setup.yaml](https://github.com/DataTalksClub/data-engineering-zoomcamp/blob/main/02-workflow-orchestration/flows/07_gcp_setup.yaml "07_gcp_setup.yaml")
```yaml
id: 07_gcp_setup
namespace: zoomcamp

tasks:
  - id: create_gcs_bucket
    type: io.kestra.plugin.gcp.gcs.CreateBucket
    ifExists: SKIP
    storageClass: REGIONAL
    name: "{{kv('GCP_BUCKET_NAME')}}" # make sure it's globally unique!

  - id: create_bq_dataset
    type: io.kestra.plugin.gcp.bigquery.CreateDataset
    name: "{{kv('GCP_DATASET')}}"
    ifExists: SKIP

pluginDefaults:
  - type: io.kestra.plugin.gcp
    values:
      serviceAccount: "{{kv('GCP_CREDS')}}"
      projectId: "{{kv('GCP_PROJECT_ID')}}"
      location: "{{kv('GCP_LOCATION')}}"
      bucket: "{{kv('GCP_BUCKET_NAME')}}"
```
Puntos interesantes:
- El Concepto de "Infraestructura como Código" (IaC): En lugar de entrar a la consola de Google Cloud y hacer clics para crear cosas, usamos este script. Esto asegura que si mañana quieres crear todo de nuevo en otro proyecto, solo tienes que correr este flujo.
- id: create_gcs_bucket. 
	1. **¿Qué hace?** Crea un "Bucket" en **Google Cloud Storage (GCS)**.
	2. **¿Qué es un Bucket?** Es el **Data Lake** que mencionábamos antes. Es básicamente una carpeta infinita en la nube donde guardaremos los archivos CSV crudos.
	3. **`ifExists: SKIP`**: Esto es muy importante para la **idempotencia**. Si el bucket ya existe, el script no hace nada y no da error.
	4. **`storageClass: REGIONAL`**: Define cómo se guardan los datos (optimizado para acceso frecuente en una región específica).
- id: create_bq_dataset.
	1.  **Qué hace?** Crea un "Dataset" en **BigQuery**.
	2. **¿Qué es BigQuery?** Es el **Data Warehouse** de Google. Es como un PostgreSQL pero que puede procesar Petabytes de datos en segundos. El Dataset es el contenedor (como una base de datos) donde luego crearemos las tablas de los taxis.
- El uso de `kv()` (Key-Value Store)
	Fíjate que en lugar de escribir tu nombre de proyecto o tus credenciales directamente (lo cual sería peligroso y poco profesional), el script usa `{{kv('...')}}`.
	1. **¿Qué es?** Es el "Almacén de Secretos" de Kestra.
	2. **¿Por qué se usa?** Para no exponer información sensible. Tú guardas tus credenciales en la configuración de Kestra una sola vez, y el script las "llama" por su nombre de etiqueta. Así, puedes compartir tu código sin compartir tus contraseñas.
- `pluginDefaults`: La limpieza del código
	Como ambas tareas son de Google Cloud (`io.kestra.plugin.gcp`), en lugar de repetir el ID del proyecto, la ubicación y las credenciales en cada tarea, las definimos una sola vez al final.
	3. **`serviceAccount`**: Es la "llave" (un archivo JSON) que le da permiso a Kestra para actuar en tu nombre en Google Cloud.
	4. **`projectId`**: El identificador único de tu cuenta de Google Cloud.


### 2.4.3 Workflow de GCP: Cargando los datos de taxis en BigQuery

Ahora que Google cloud ya tiene todo preparado. Procedemos con el proceso ELT.

```yaml
id: 08_gcp_taxi
namespace: zoomcamp
description: |
  The CSV Data used in the course: https://github.com/DataTalksClub/nyc-tlc-data/releases

inputs:
  - id: taxi
    type: SELECT
    displayName: Select taxi type
    values: [yellow, green]
    defaults: green

  - id: year
    type: SELECT
    displayName: Select year
    values: ["2019", "2020"]
    defaults: "2019"
    allowCustomValue: true # allows you to type 2021 from the UI for the homework 🤗

  - id: month
    type: SELECT
    displayName: Select month
    values: ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"]
    defaults: "01"

variables:
  file: "{{inputs.taxi}}_tripdata_{{inputs.year}}-{{inputs.month}}.csv"
  gcs_file: "gs://{{kv('GCP_BUCKET_NAME')}}/{{vars.file}}"
  table: "{{kv('GCP_DATASET')}}.{{inputs.taxi}}_tripdata_{{inputs.year}}_{{inputs.month}}"
  data: "{{outputs.extract.outputFiles[inputs.taxi ~ '_tripdata_' ~ inputs.year ~ '-' ~ inputs.month ~ '.csv']}}"

tasks:
  - id: set_label
    type: io.kestra.plugin.core.execution.Labels
    labels:
      file: "{{render(vars.file)}}"
      taxi: "{{inputs.taxi}}"

  - id: extract
    type: io.kestra.plugin.scripts.shell.Commands
    outputFiles:
      - "*.csv"
    taskRunner:
      type: io.kestra.plugin.core.runner.Process
    commands:
      - wget -qO- https://github.com/DataTalksClub/nyc-tlc-data/releases/download/{{inputs.taxi}}/{{render(vars.file)}}.gz | gunzip > {{render(vars.file)}}

  - id: upload_to_gcs
    type: io.kestra.plugin.gcp.gcs.Upload
    from: "{{render(vars.data)}}"
    to: "{{render(vars.gcs_file)}}"

  - id: if_yellow_taxi
    type: io.kestra.plugin.core.flow.If
    condition: "{{inputs.taxi == 'yellow'}}"
    then:
      - id: bq_yellow_tripdata
        type: io.kestra.plugin.gcp.bigquery.Query
        sql: |
          CREATE TABLE IF NOT EXISTS `{{kv('GCP_PROJECT_ID')}}.{{kv('GCP_DATASET')}}.yellow_tripdata`
          (
              unique_row_id BYTES OPTIONS (description = 'A unique identifier for the trip, generated by hashing key trip attributes.'),
              filename STRING OPTIONS (description = 'The source filename from which the trip data was loaded.'),      
              VendorID STRING OPTIONS (description = 'A code indicating the LPEP provider that provided the record. 1= Creative Mobile Technologies, LLC; 2= VeriFone Inc.'),
              tpep_pickup_datetime TIMESTAMP OPTIONS (description = 'The date and time when the meter was engaged'),
              tpep_dropoff_datetime TIMESTAMP OPTIONS (description = 'The date and time when the meter was disengaged'),
              passenger_count INTEGER OPTIONS (description = 'The number of passengers in the vehicle. This is a driver-entered value.'),
              trip_distance NUMERIC OPTIONS (description = 'The elapsed trip distance in miles reported by the taximeter.'),
              RatecodeID STRING OPTIONS (description = 'The final rate code in effect at the end of the trip. 1= Standard rate 2=JFK 3=Newark 4=Nassau or Westchester 5=Negotiated fare 6=Group ride'),
              store_and_fwd_flag STRING OPTIONS (description = 'This flag indicates whether the trip record was held in vehicle memory before sending to the vendor, aka "store and forward," because the vehicle did not have a connection to the server. TRUE = store and forward trip, FALSE = not a store and forward trip'),
              PULocationID STRING OPTIONS (description = 'TLC Taxi Zone in which the taximeter was engaged'),
              DOLocationID STRING OPTIONS (description = 'TLC Taxi Zone in which the taximeter was disengaged'),
              payment_type INTEGER OPTIONS (description = 'A numeric code signifying how the passenger paid for the trip. 1= Credit card 2= Cash 3= No charge 4= Dispute 5= Unknown 6= Voided trip'),
              fare_amount NUMERIC OPTIONS (description = 'The time-and-distance fare calculated by the meter'),
              extra NUMERIC OPTIONS (description = 'Miscellaneous extras and surcharges. Currently, this only includes the $0.50 and $1 rush hour and overnight charges'),
              mta_tax NUMERIC OPTIONS (description = '$0.50 MTA tax that is automatically triggered based on the metered rate in use'),
              tip_amount NUMERIC OPTIONS (description = 'Tip amount. This field is automatically populated for credit card tips. Cash tips are not included.'),
              tolls_amount NUMERIC OPTIONS (description = 'Total amount of all tolls paid in trip.'),
              improvement_surcharge NUMERIC OPTIONS (description = '$0.30 improvement surcharge assessed on hailed trips at the flag drop. The improvement surcharge began being levied in 2015.'),
              total_amount NUMERIC OPTIONS (description = 'The total amount charged to passengers. Does not include cash tips.'),
              congestion_surcharge NUMERIC OPTIONS (description = 'Congestion surcharge applied to trips in congested zones')
          )
          PARTITION BY DATE(tpep_pickup_datetime);

      - id: bq_yellow_table_ext
        type: io.kestra.plugin.gcp.bigquery.Query
        sql: |
          CREATE OR REPLACE EXTERNAL TABLE `{{kv('GCP_PROJECT_ID')}}.{{render(vars.table)}}_ext`
          (
              VendorID STRING OPTIONS (description = 'A code indicating the LPEP provider that provided the record. 1= Creative Mobile Technologies, LLC; 2= VeriFone Inc.'),
              tpep_pickup_datetime TIMESTAMP OPTIONS (description = 'The date and time when the meter was engaged'),
              tpep_dropoff_datetime TIMESTAMP OPTIONS (description = 'The date and time when the meter was disengaged'),
              passenger_count INTEGER OPTIONS (description = 'The number of passengers in the vehicle. This is a driver-entered value.'),
              trip_distance NUMERIC OPTIONS (description = 'The elapsed trip distance in miles reported by the taximeter.'),
              RatecodeID STRING OPTIONS (description = 'The final rate code in effect at the end of the trip. 1= Standard rate 2=JFK 3=Newark 4=Nassau or Westchester 5=Negotiated fare 6=Group ride'),
              store_and_fwd_flag STRING OPTIONS (description = 'This flag indicates whether the trip record was held in vehicle memory before sending to the vendor, aka "store and forward," because the vehicle did not have a connection to the server. TRUE = store and forward trip, FALSE = not a store and forward trip'),
              PULocationID STRING OPTIONS (description = 'TLC Taxi Zone in which the taximeter was engaged'),
              DOLocationID STRING OPTIONS (description = 'TLC Taxi Zone in which the taximeter was disengaged'),
              payment_type INTEGER OPTIONS (description = 'A numeric code signifying how the passenger paid for the trip. 1= Credit card 2= Cash 3= No charge 4= Dispute 5= Unknown 6= Voided trip'),
              fare_amount NUMERIC OPTIONS (description = 'The time-and-distance fare calculated by the meter'),
              extra NUMERIC OPTIONS (description = 'Miscellaneous extras and surcharges. Currently, this only includes the $0.50 and $1 rush hour and overnight charges'),
              mta_tax NUMERIC OPTIONS (description = '$0.50 MTA tax that is automatically triggered based on the metered rate in use'),
              tip_amount NUMERIC OPTIONS (description = 'Tip amount. This field is automatically populated for credit card tips. Cash tips are not included.'),
              tolls_amount NUMERIC OPTIONS (description = 'Total amount of all tolls paid in trip.'),
              improvement_surcharge NUMERIC OPTIONS (description = '$0.30 improvement surcharge assessed on hailed trips at the flag drop. The improvement surcharge began being levied in 2015.'),
              total_amount NUMERIC OPTIONS (description = 'The total amount charged to passengers. Does not include cash tips.'),
              congestion_surcharge NUMERIC OPTIONS (description = 'Congestion surcharge applied to trips in congested zones')
          )
          OPTIONS (
              format = 'CSV',
              uris = ['{{render(vars.gcs_file)}}'],
              skip_leading_rows = 1,
              ignore_unknown_values = TRUE
          );

      - id: bq_yellow_table_tmp
        type: io.kestra.plugin.gcp.bigquery.Query
        sql: |
          CREATE OR REPLACE TABLE `{{kv('GCP_PROJECT_ID')}}.{{render(vars.table)}}`
          AS
          SELECT
            MD5(CONCAT(
              COALESCE(CAST(VendorID AS STRING), ""),
              COALESCE(CAST(tpep_pickup_datetime AS STRING), ""),
              COALESCE(CAST(tpep_dropoff_datetime AS STRING), ""),
              COALESCE(CAST(PULocationID AS STRING), ""),
              COALESCE(CAST(DOLocationID AS STRING), "")
            )) AS unique_row_id,
            "{{render(vars.file)}}" AS filename,
            *
          FROM `{{kv('GCP_PROJECT_ID')}}.{{render(vars.table)}}_ext`;

      - id: bq_yellow_merge
        type: io.kestra.plugin.gcp.bigquery.Query
        sql: |
          MERGE INTO `{{kv('GCP_PROJECT_ID')}}.{{kv('GCP_DATASET')}}.yellow_tripdata` T
          USING `{{kv('GCP_PROJECT_ID')}}.{{render(vars.table)}}` S
          ON T.unique_row_id = S.unique_row_id
          WHEN NOT MATCHED THEN
            INSERT (unique_row_id, filename, VendorID, tpep_pickup_datetime, tpep_dropoff_datetime, passenger_count, trip_distance, RatecodeID, store_and_fwd_flag, PULocationID, DOLocationID, payment_type, fare_amount, extra, mta_tax, tip_amount, tolls_amount, improvement_surcharge, total_amount, congestion_surcharge)
            VALUES (S.unique_row_id, S.filename, S.VendorID, S.tpep_pickup_datetime, S.tpep_dropoff_datetime, S.passenger_count, S.trip_distance, S.RatecodeID, S.store_and_fwd_flag, S.PULocationID, S.DOLocationID, S.payment_type, S.fare_amount, S.extra, S.mta_tax, S.tip_amount, S.tolls_amount, S.improvement_surcharge, S.total_amount, S.congestion_surcharge);

  - id: if_green_taxi
    type: io.kestra.plugin.core.flow.If
    condition: "{{inputs.taxi == 'green'}}"
    then:
      - id: bq_green_tripdata
        type: io.kestra.plugin.gcp.bigquery.Query
        sql: |
          CREATE TABLE IF NOT EXISTS `{{kv('GCP_PROJECT_ID')}}.{{kv('GCP_DATASET')}}.green_tripdata`
          (
              unique_row_id BYTES OPTIONS (description = 'A unique identifier for the trip, generated by hashing key trip attributes.'),
              filename STRING OPTIONS (description = 'The source filename from which the trip data was loaded.'),      
              VendorID STRING OPTIONS (description = 'A code indicating the LPEP provider that provided the record. 1= Creative Mobile Technologies, LLC; 2= VeriFone Inc.'),
              lpep_pickup_datetime TIMESTAMP OPTIONS (description = 'The date and time when the meter was engaged'),
              lpep_dropoff_datetime TIMESTAMP OPTIONS (description = 'The date and time when the meter was disengaged'),
              store_and_fwd_flag STRING OPTIONS (description = 'This flag indicates whether the trip record was held in vehicle memory before sending to the vendor, aka "store and forward," because the vehicle did not have a connection to the server. Y= store and forward trip N= not a store and forward trip'),
              RatecodeID STRING OPTIONS (description = 'The final rate code in effect at the end of the trip. 1= Standard rate 2=JFK 3=Newark 4=Nassau or Westchester 5=Negotiated fare 6=Group ride'),
              PULocationID STRING OPTIONS (description = 'TLC Taxi Zone in which the taximeter was engaged'),
              DOLocationID STRING OPTIONS (description = 'TLC Taxi Zone in which the taximeter was disengaged'),
              passenger_count INT64 OPTIONS (description = 'The number of passengers in the vehicle. This is a driver-entered value.'),
              trip_distance NUMERIC OPTIONS (description = 'The elapsed trip distance in miles reported by the taximeter.'),
              fare_amount NUMERIC OPTIONS (description = 'The time-and-distance fare calculated by the meter'),
              extra NUMERIC OPTIONS (description = 'Miscellaneous extras and surcharges. Currently, this only includes the $0.50 and $1 rush hour and overnight charges'),
              mta_tax NUMERIC OPTIONS (description = '$0.50 MTA tax that is automatically triggered based on the metered rate in use'),
              tip_amount NUMERIC OPTIONS (description = 'Tip amount. This field is automatically populated for credit card tips. Cash tips are not included.'),
              tolls_amount NUMERIC OPTIONS (description = 'Total amount of all tolls paid in trip.'),
              ehail_fee NUMERIC,
              improvement_surcharge NUMERIC OPTIONS (description = '$0.30 improvement surcharge assessed on hailed trips at the flag drop. The improvement surcharge began being levied in 2015.'),
              total_amount NUMERIC OPTIONS (description = 'The total amount charged to passengers. Does not include cash tips.'),
              payment_type INTEGER OPTIONS (description = 'A numeric code signifying how the passenger paid for the trip. 1= Credit card 2= Cash 3= No charge 4= Dispute 5= Unknown 6= Voided trip'),
              trip_type STRING OPTIONS (description = 'A code indicating whether the trip was a street-hail or a dispatch that is automatically assigned based on the metered rate in use but can be altered by the driver. 1= Street-hail 2= Dispatch'),
              congestion_surcharge NUMERIC OPTIONS (description = 'Congestion surcharge applied to trips in congested zones')
          )
          PARTITION BY DATE(lpep_pickup_datetime);

      - id: bq_green_table_ext
        type: io.kestra.plugin.gcp.bigquery.Query
        sql: |
          CREATE OR REPLACE EXTERNAL TABLE `{{kv('GCP_PROJECT_ID')}}.{{render(vars.table)}}_ext`
          (
              VendorID STRING OPTIONS (description = 'A code indicating the LPEP provider that provided the record. 1= Creative Mobile Technologies, LLC; 2= VeriFone Inc.'),
              lpep_pickup_datetime TIMESTAMP OPTIONS (description = 'The date and time when the meter was engaged'),
              lpep_dropoff_datetime TIMESTAMP OPTIONS (description = 'The date and time when the meter was disengaged'),
              store_and_fwd_flag STRING OPTIONS (description = 'This flag indicates whether the trip record was held in vehicle memory before sending to the vendor, aka "store and forward," because the vehicle did not have a connection to the server. Y= store and forward trip N= not a store and forward trip'),
              RatecodeID STRING OPTIONS (description = 'The final rate code in effect at the end of the trip. 1= Standard rate 2=JFK 3=Newark 4=Nassau or Westchester 5=Negotiated fare 6=Group ride'),
              PULocationID STRING OPTIONS (description = 'TLC Taxi Zone in which the taximeter was engaged'),
              DOLocationID STRING OPTIONS (description = 'TLC Taxi Zone in which the taximeter was disengaged'),
              passenger_count INT64 OPTIONS (description = 'The number of passengers in the vehicle. This is a driver-entered value.'),
              trip_distance NUMERIC OPTIONS (description = 'The elapsed trip distance in miles reported by the taximeter.'),
              fare_amount NUMERIC OPTIONS (description = 'The time-and-distance fare calculated by the meter'),
              extra NUMERIC OPTIONS (description = 'Miscellaneous extras and surcharges. Currently, this only includes the $0.50 and $1 rush hour and overnight charges'),
              mta_tax NUMERIC OPTIONS (description = '$0.50 MTA tax that is automatically triggered based on the metered rate in use'),
              tip_amount NUMERIC OPTIONS (description = 'Tip amount. This field is automatically populated for credit card tips. Cash tips are not included.'),
              tolls_amount NUMERIC OPTIONS (description = 'Total amount of all tolls paid in trip.'),
              ehail_fee NUMERIC,
              improvement_surcharge NUMERIC OPTIONS (description = '$0.30 improvement surcharge assessed on hailed trips at the flag drop. The improvement surcharge began being levied in 2015.'),
              total_amount NUMERIC OPTIONS (description = 'The total amount charged to passengers. Does not include cash tips.'),
              payment_type INTEGER OPTIONS (description = 'A numeric code signifying how the passenger paid for the trip. 1= Credit card 2= Cash 3= No charge 4= Dispute 5= Unknown 6= Voided trip'),
              trip_type STRING OPTIONS (description = 'A code indicating whether the trip was a street-hail or a dispatch that is automatically assigned based on the metered rate in use but can be altered by the driver. 1= Street-hail 2= Dispatch'),
              congestion_surcharge NUMERIC OPTIONS (description = 'Congestion surcharge applied to trips in congested zones')
          )
          OPTIONS (
              format = 'CSV',
              uris = ['{{render(vars.gcs_file)}}'],
              skip_leading_rows = 1,
              ignore_unknown_values = TRUE
          );

      - id: bq_green_table_tmp
        type: io.kestra.plugin.gcp.bigquery.Query
        sql: |
          CREATE OR REPLACE TABLE `{{kv('GCP_PROJECT_ID')}}.{{render(vars.table)}}`
          AS
          SELECT
            MD5(CONCAT(
              COALESCE(CAST(VendorID AS STRING), ""),
              COALESCE(CAST(lpep_pickup_datetime AS STRING), ""),
              COALESCE(CAST(lpep_dropoff_datetime AS STRING), ""),
              COALESCE(CAST(PULocationID AS STRING), ""),
              COALESCE(CAST(DOLocationID AS STRING), "")
            )) AS unique_row_id,
            "{{render(vars.file)}}" AS filename,
            *
          FROM `{{kv('GCP_PROJECT_ID')}}.{{render(vars.table)}}_ext`;

      - id: bq_green_merge
        type: io.kestra.plugin.gcp.bigquery.Query
        sql: |
          MERGE INTO `{{kv('GCP_PROJECT_ID')}}.{{kv('GCP_DATASET')}}.green_tripdata` T
          USING `{{kv('GCP_PROJECT_ID')}}.{{render(vars.table)}}` S
          ON T.unique_row_id = S.unique_row_id
          WHEN NOT MATCHED THEN
            INSERT (unique_row_id, filename, VendorID, lpep_pickup_datetime, lpep_dropoff_datetime, store_and_fwd_flag, RatecodeID, PULocationID, DOLocationID, passenger_count, trip_distance, fare_amount, extra, mta_tax, tip_amount, tolls_amount, ehail_fee, improvement_surcharge, total_amount, payment_type, trip_type, congestion_surcharge)
            VALUES (S.unique_row_id, S.filename, S.VendorID, S.lpep_pickup_datetime, S.lpep_dropoff_datetime, S.store_and_fwd_flag, S.RatecodeID, S.PULocationID, S.DOLocationID, S.passenger_count, S.trip_distance, S.fare_amount, S.extra, S.mta_tax, S.tip_amount, S.tolls_amount, S.ehail_fee, S.improvement_surcharge, S.total_amount, S.payment_type, S.trip_type, S.congestion_surcharge);

  - id: purge_files
    type: io.kestra.plugin.core.storage.PurgeCurrentExecutionFiles
    description: If you'd like to explore Kestra outputs, disable it.
    disabled: false

pluginDefaults:
  - type: io.kestra.plugin.gcp
    values:
      serviceAccount: "{{kv('GCP_CREDS')}}"
      projectId: "{{kv('GCP_PROJECT_ID')}}"
      location: "{{kv('GCP_LOCATION')}}"
      bucket: "{{kv('GCP_BUCKET_NAME')}}"
```
Puntos interesantes:
Extracción y Carga al Data Lake
- **`extract`**: Igual que antes, descarga el CSV de GitHub.
- **`upload_to_gcs`**: Aquí está el cambio clave. En lugar de pasar el archivo directamente a la base de datos, lo subimos a **Google Cloud Storage**.
	 **¿Por qué?** Porque tener una copia del dato crudo en la nube es más seguro, más barato y permite que otras herramientas también lo usen
El poder de las Tablas Externas (`EXTERNAL TABLE`)
Aquí BigQuery demuestra por qué es especial.
- **`bq_yellow_table_ext`**: Crea una **Tabla Externa**.
- **¿Qué es esto?** Es una tabla que vive en BigQuery, pero **no tiene datos adentro**. Cuando tú le haces una consulta, BigQuery va corriendo al archivo CSV en GCS, lo lee en el aire y te da el resultado. Es una forma increíble de ver qué hay en el "Data Lake" sin pagar por almacenamiento duplicado.
Transformación Incremental (Staging y Merge)
El flujo sigue la lógica de "capas" (Medallion Architecture):
1. **Capa Bronze (`_ext`)**: La tabla externa que apunta al CSV crudo.
2. **Capa Silver (`bq_yellow_table_tmp`)**: Crea una tabla temporal (staging). Aquí es donde se hace la **Transformación**:
    - Usa `MD5(CONCAT(...))` para crear el ID único.
    - Asigna el nombre del archivo.
    - Convierte tipos de datos.
3. **Capa Gold (`yellow_tripdata`)**: Es la tabla final, **particionada por fecha** (`PARTITION BY DATE`).
    - **`bq_yellow_merge`**: Compara la tabla temporal con la final e inserta solo los viajes nuevos.
Optimizaciones de Big Data
Este script incluye dos conceptos de nivel Senior:
- **Particionamiento:** `PARTITION BY DATE(tpep_pickup_datetime)`. Esto hace que, si consultas los datos de un día específico, BigQuery solo lea esa "carpetita" de datos y no los 100GB de toda la tabla. **¡Ahorras mucho dinero!**
- **Comentarios en el Esquema:** Verás que cada columna tiene una `description`. En empresas grandes, esto es obligatorio para que los analistas sepan qué significa cada campo (ej. `RatecodeID`).

Una vez ejecutado este script podemos ver dentro del Google Cloud Plaform nuestro Data set en big query y datos en el Bucket del Google cloud storage


### 2.4.4 GCP Workflow: Programar y realizar el Backfill del conjunto de datos completo (Schedule and Backfill Full Dataset)

Ahora podemos programar el mismo flujo mostrado anteriormente para que se ejecute diariamente a las 9 AM UTC para el conjunto de datos verde y a las 10 AM UTC para el conjunto de datos amarillo. Puedes realizar el **backfill** de datos históricos directamente desde la interfaz de usuario de **[Kestra](https://kestra.io/blogs/2022-02-22-leroy-merlin-usage-kestra?ref=ssp.sh)**. 

Dado que ahora procesamos los datos en un entorno de nube con almacenamiento y cómputo infinitamente escalables, podemos realizar el **backfill** de todo el conjunto de datos, tanto de los taxis amarillos como de los verdes, sin riesgo de quedarnos sin recursos en nuestra máquina local.

[09_gcp_taxi_scheduled.yaml](https://github.com/DataTalksClub/data-engineering-zoomcamp/blob/main/02-workflow-orchestration/flows/09_gcp_taxi_scheduled.yaml "09_gcp_taxi_scheduled.yaml")
```yaml

id: 09_gcp_taxi_scheduled
namespace: zoomcamp
description: |
  Best to add a label `backfill:true` from the UI to track executions created via a backfill.
  CSV data used here comes from: https://github.com/DataTalksClub/nyc-tlc-data/releases

inputs:
  - id: taxi
    type: SELECT
    displayName: Select taxi type
    values: [yellow, green]
    defaults: green

variables:
  file: "{{inputs.taxi}}_tripdata_{{trigger.date | date('yyyy-MM')}}.csv"
  gcs_file: "gs://{{kv('GCP_BUCKET_NAME')}}/{{vars.file}}"
  table: "{{kv('GCP_DATASET')}}.{{inputs.taxi}}_tripdata_{{trigger.date | date('yyyy_MM')}}"
  data: "{{outputs.extract.outputFiles[inputs.taxi ~ '_tripdata_' ~ (trigger.date | date('yyyy-MM')) ~ '.csv']}}"

tasks:
  - id: set_label
    type: io.kestra.plugin.core.execution.Labels
    labels:
      file: "{{render(vars.file)}}"
      taxi: "{{inputs.taxi}}"

  - id: extract
    type: io.kestra.plugin.scripts.shell.Commands
    outputFiles:
      - "*.csv"
    taskRunner:
      type: io.kestra.plugin.core.runner.Process
    commands:
      - wget -qO- https://github.com/DataTalksClub/nyc-tlc-data/releases/download/{{inputs.taxi}}/{{render(vars.file)}}.gz | gunzip > {{render(vars.file)}}

  - id: upload_to_gcs
    type: io.kestra.plugin.gcp.gcs.Upload
    from: "{{render(vars.data)}}"
    to: "{{render(vars.gcs_file)}}"

  - id: if_yellow_taxi
    type: io.kestra.plugin.core.flow.If
    condition: "{{inputs.taxi == 'yellow'}}"
    then:
      - id: bq_yellow_tripdata
        type: io.kestra.plugin.gcp.bigquery.Query
        sql: |
          CREATE TABLE IF NOT EXISTS `{{kv('GCP_PROJECT_ID')}}.{{kv('GCP_DATASET')}}.yellow_tripdata`
          (
              unique_row_id BYTES OPTIONS (description = 'A unique identifier for the trip, generated by hashing key trip attributes.'),
              filename STRING OPTIONS (description = 'The source filename from which the trip data was loaded.'),      
              VendorID STRING OPTIONS (description = 'A code indicating the LPEP provider that provided the record. 1= Creative Mobile Technologies, LLC; 2= VeriFone Inc.'),
              tpep_pickup_datetime TIMESTAMP OPTIONS (description = 'The date and time when the meter was engaged'),
              tpep_dropoff_datetime TIMESTAMP OPTIONS (description = 'The date and time when the meter was disengaged'),
              passenger_count INTEGER OPTIONS (description = 'The number of passengers in the vehicle. This is a driver-entered value.'),
              trip_distance NUMERIC OPTIONS (description = 'The elapsed trip distance in miles reported by the taximeter.'),
              RatecodeID STRING OPTIONS (description = 'The final rate code in effect at the end of the trip. 1= Standard rate 2=JFK 3=Newark 4=Nassau or Westchester 5=Negotiated fare 6=Group ride'),
              store_and_fwd_flag STRING OPTIONS (description = 'This flag indicates whether the trip record was held in vehicle memory before sending to the vendor, aka "store and forward," because the vehicle did not have a connection to the server. TRUE = store and forward trip, FALSE = not a store and forward trip'),
              PULocationID STRING OPTIONS (description = 'TLC Taxi Zone in which the taximeter was engaged'),
              DOLocationID STRING OPTIONS (description = 'TLC Taxi Zone in which the taximeter was disengaged'),
              payment_type INTEGER OPTIONS (description = 'A numeric code signifying how the passenger paid for the trip. 1= Credit card 2= Cash 3= No charge 4= Dispute 5= Unknown 6= Voided trip'),
              fare_amount NUMERIC OPTIONS (description = 'The time-and-distance fare calculated by the meter'),
              extra NUMERIC OPTIONS (description = 'Miscellaneous extras and surcharges. Currently, this only includes the $0.50 and $1 rush hour and overnight charges'),
              mta_tax NUMERIC OPTIONS (description = '$0.50 MTA tax that is automatically triggered based on the metered rate in use'),
              tip_amount NUMERIC OPTIONS (description = 'Tip amount. This field is automatically populated for credit card tips. Cash tips are not included.'),
              tolls_amount NUMERIC OPTIONS (description = 'Total amount of all tolls paid in trip.'),
              improvement_surcharge NUMERIC OPTIONS (description = '$0.30 improvement surcharge assessed on hailed trips at the flag drop. The improvement surcharge began being levied in 2015.'),
              total_amount NUMERIC OPTIONS (description = 'The total amount charged to passengers. Does not include cash tips.'),
              congestion_surcharge NUMERIC OPTIONS (description = 'Congestion surcharge applied to trips in congested zones')
          )
          PARTITION BY DATE(tpep_pickup_datetime);

      - id: bq_yellow_table_ext
        type: io.kestra.plugin.gcp.bigquery.Query
        sql: |
          CREATE OR REPLACE EXTERNAL TABLE `{{kv('GCP_PROJECT_ID')}}.{{render(vars.table)}}_ext`
          (
              VendorID STRING OPTIONS (description = 'A code indicating the LPEP provider that provided the record. 1= Creative Mobile Technologies, LLC; 2= VeriFone Inc.'),
              tpep_pickup_datetime TIMESTAMP OPTIONS (description = 'The date and time when the meter was engaged'),
              tpep_dropoff_datetime TIMESTAMP OPTIONS (description = 'The date and time when the meter was disengaged'),
              passenger_count INTEGER OPTIONS (description = 'The number of passengers in the vehicle. This is a driver-entered value.'),
              trip_distance NUMERIC OPTIONS (description = 'The elapsed trip distance in miles reported by the taximeter.'),
              RatecodeID STRING OPTIONS (description = 'The final rate code in effect at the end of the trip. 1= Standard rate 2=JFK 3=Newark 4=Nassau or Westchester 5=Negotiated fare 6=Group ride'),
              store_and_fwd_flag STRING OPTIONS (description = 'This flag indicates whether the trip record was held in vehicle memory before sending to the vendor, aka "store and forward," because the vehicle did not have a connection to the server. TRUE = store and forward trip, FALSE = not a store and forward trip'),
              PULocationID STRING OPTIONS (description = 'TLC Taxi Zone in which the taximeter was engaged'),
              DOLocationID STRING OPTIONS (description = 'TLC Taxi Zone in which the taximeter was disengaged'),
              payment_type INTEGER OPTIONS (description = 'A numeric code signifying how the passenger paid for the trip. 1= Credit card 2= Cash 3= No charge 4= Dispute 5= Unknown 6= Voided trip'),
              fare_amount NUMERIC OPTIONS (description = 'The time-and-distance fare calculated by the meter'),
              extra NUMERIC OPTIONS (description = 'Miscellaneous extras and surcharges. Currently, this only includes the $0.50 and $1 rush hour and overnight charges'),
              mta_tax NUMERIC OPTIONS (description = '$0.50 MTA tax that is automatically triggered based on the metered rate in use'),
              tip_amount NUMERIC OPTIONS (description = 'Tip amount. This field is automatically populated for credit card tips. Cash tips are not included.'),
              tolls_amount NUMERIC OPTIONS (description = 'Total amount of all tolls paid in trip.'),
              improvement_surcharge NUMERIC OPTIONS (description = '$0.30 improvement surcharge assessed on hailed trips at the flag drop. The improvement surcharge began being levied in 2015.'),
              total_amount NUMERIC OPTIONS (description = 'The total amount charged to passengers. Does not include cash tips.'),
              congestion_surcharge NUMERIC OPTIONS (description = 'Congestion surcharge applied to trips in congested zones')
          )
          OPTIONS (
              format = 'CSV',
              uris = ['{{render(vars.gcs_file)}}'],
              skip_leading_rows = 1,
              ignore_unknown_values = TRUE
          );

      - id: bq_yellow_table_tmp
        type: io.kestra.plugin.gcp.bigquery.Query
        sql: |
          CREATE OR REPLACE TABLE `{{kv('GCP_PROJECT_ID')}}.{{render(vars.table)}}`
          AS
          SELECT
            MD5(CONCAT(
              COALESCE(CAST(VendorID AS STRING), ""),
              COALESCE(CAST(tpep_pickup_datetime AS STRING), ""),
              COALESCE(CAST(tpep_dropoff_datetime AS STRING), ""),
              COALESCE(CAST(PULocationID AS STRING), ""),
              COALESCE(CAST(DOLocationID AS STRING), "")
            )) AS unique_row_id,
            "{{render(vars.file)}}" AS filename,
            *
          FROM `{{kv('GCP_PROJECT_ID')}}.{{render(vars.table)}}_ext`;

      - id: bq_yellow_merge
        type: io.kestra.plugin.gcp.bigquery.Query
        sql: |
          MERGE INTO `{{kv('GCP_PROJECT_ID')}}.{{kv('GCP_DATASET')}}.yellow_tripdata` T
          USING `{{kv('GCP_PROJECT_ID')}}.{{render(vars.table)}}` S
          ON T.unique_row_id = S.unique_row_id
          WHEN NOT MATCHED THEN
            INSERT (unique_row_id, filename, VendorID, tpep_pickup_datetime, tpep_dropoff_datetime, passenger_count, trip_distance, RatecodeID, store_and_fwd_flag, PULocationID, DOLocationID, payment_type, fare_amount, extra, mta_tax, tip_amount, tolls_amount, improvement_surcharge, total_amount, congestion_surcharge)
            VALUES (S.unique_row_id, S.filename, S.VendorID, S.tpep_pickup_datetime, S.tpep_dropoff_datetime, S.passenger_count, S.trip_distance, S.RatecodeID, S.store_and_fwd_flag, S.PULocationID, S.DOLocationID, S.payment_type, S.fare_amount, S.extra, S.mta_tax, S.tip_amount, S.tolls_amount, S.improvement_surcharge, S.total_amount, S.congestion_surcharge);

  - id: if_green_taxi
    type: io.kestra.plugin.core.flow.If
    condition: "{{inputs.taxi == 'green'}}"
    then:
      - id: bq_green_tripdata
        type: io.kestra.plugin.gcp.bigquery.Query
        sql: |
          CREATE TABLE IF NOT EXISTS `{{kv('GCP_PROJECT_ID')}}.{{kv('GCP_DATASET')}}.green_tripdata`
          (
              unique_row_id BYTES OPTIONS (description = 'A unique identifier for the trip, generated by hashing key trip attributes.'),
              filename STRING OPTIONS (description = 'The source filename from which the trip data was loaded.'),      
              VendorID STRING OPTIONS (description = 'A code indicating the LPEP provider that provided the record. 1= Creative Mobile Technologies, LLC; 2= VeriFone Inc.'),
              lpep_pickup_datetime TIMESTAMP OPTIONS (description = 'The date and time when the meter was engaged'),
              lpep_dropoff_datetime TIMESTAMP OPTIONS (description = 'The date and time when the meter was disengaged'),
              store_and_fwd_flag STRING OPTIONS (description = 'This flag indicates whether the trip record was held in vehicle memory before sending to the vendor, aka "store and forward," because the vehicle did not have a connection to the server. Y= store and forward trip N= not a store and forward trip'),
              RatecodeID STRING OPTIONS (description = 'The final rate code in effect at the end of the trip. 1= Standard rate 2=JFK 3=Newark 4=Nassau or Westchester 5=Negotiated fare 6=Group ride'),
              PULocationID STRING OPTIONS (description = 'TLC Taxi Zone in which the taximeter was engaged'),
              DOLocationID STRING OPTIONS (description = 'TLC Taxi Zone in which the taximeter was disengaged'),
              passenger_count INT64 OPTIONS (description = 'The number of passengers in the vehicle. This is a driver-entered value.'),
              trip_distance NUMERIC OPTIONS (description = 'The elapsed trip distance in miles reported by the taximeter.'),
              fare_amount NUMERIC OPTIONS (description = 'The time-and-distance fare calculated by the meter'),
              extra NUMERIC OPTIONS (description = 'Miscellaneous extras and surcharges. Currently, this only includes the $0.50 and $1 rush hour and overnight charges'),
              mta_tax NUMERIC OPTIONS (description = '$0.50 MTA tax that is automatically triggered based on the metered rate in use'),
              tip_amount NUMERIC OPTIONS (description = 'Tip amount. This field is automatically populated for credit card tips. Cash tips are not included.'),
              tolls_amount NUMERIC OPTIONS (description = 'Total amount of all tolls paid in trip.'),
              ehail_fee NUMERIC,
              improvement_surcharge NUMERIC OPTIONS (description = '$0.30 improvement surcharge assessed on hailed trips at the flag drop. The improvement surcharge began being levied in 2015.'),
              total_amount NUMERIC OPTIONS (description = 'The total amount charged to passengers. Does not include cash tips.'),
              payment_type INTEGER OPTIONS (description = 'A numeric code signifying how the passenger paid for the trip. 1= Credit card 2= Cash 3= No charge 4= Dispute 5= Unknown 6= Voided trip'),
              trip_type STRING OPTIONS (description = 'A code indicating whether the trip was a street-hail or a dispatch that is automatically assigned based on the metered rate in use but can be altered by the driver. 1= Street-hail 2= Dispatch'),
              congestion_surcharge NUMERIC OPTIONS (description = 'Congestion surcharge applied to trips in congested zones')
          )
          PARTITION BY DATE(lpep_pickup_datetime);

      - id: bq_green_table_ext
        type: io.kestra.plugin.gcp.bigquery.Query
        sql: |
          CREATE OR REPLACE EXTERNAL TABLE `{{kv('GCP_PROJECT_ID')}}.{{render(vars.table)}}_ext`
          (
              VendorID STRING OPTIONS (description = 'A code indicating the LPEP provider that provided the record. 1= Creative Mobile Technologies, LLC; 2= VeriFone Inc.'),
              lpep_pickup_datetime TIMESTAMP OPTIONS (description = 'The date and time when the meter was engaged'),
              lpep_dropoff_datetime TIMESTAMP OPTIONS (description = 'The date and time when the meter was disengaged'),
              store_and_fwd_flag STRING OPTIONS (description = 'This flag indicates whether the trip record was held in vehicle memory before sending to the vendor, aka "store and forward," because the vehicle did not have a connection to the server. Y= store and forward trip N= not a store and forward trip'),
              RatecodeID STRING OPTIONS (description = 'The final rate code in effect at the end of the trip. 1= Standard rate 2=JFK 3=Newark 4=Nassau or Westchester 5=Negotiated fare 6=Group ride'),
              PULocationID STRING OPTIONS (description = 'TLC Taxi Zone in which the taximeter was engaged'),
              DOLocationID STRING OPTIONS (description = 'TLC Taxi Zone in which the taximeter was disengaged'),
              passenger_count INT64 OPTIONS (description = 'The number of passengers in the vehicle. This is a driver-entered value.'),
              trip_distance NUMERIC OPTIONS (description = 'The elapsed trip distance in miles reported by the taximeter.'),
              fare_amount NUMERIC OPTIONS (description = 'The time-and-distance fare calculated by the meter'),
              extra NUMERIC OPTIONS (description = 'Miscellaneous extras and surcharges. Currently, this only includes the $0.50 and $1 rush hour and overnight charges'),
              mta_tax NUMERIC OPTIONS (description = '$0.50 MTA tax that is automatically triggered based on the metered rate in use'),
              tip_amount NUMERIC OPTIONS (description = 'Tip amount. This field is automatically populated for credit card tips. Cash tips are not included.'),
              tolls_amount NUMERIC OPTIONS (description = 'Total amount of all tolls paid in trip.'),
              ehail_fee NUMERIC,
              improvement_surcharge NUMERIC OPTIONS (description = '$0.30 improvement surcharge assessed on hailed trips at the flag drop. The improvement surcharge began being levied in 2015.'),
              total_amount NUMERIC OPTIONS (description = 'The total amount charged to passengers. Does not include cash tips.'),
              payment_type INTEGER OPTIONS (description = 'A numeric code signifying how the passenger paid for the trip. 1= Credit card 2= Cash 3= No charge 4= Dispute 5= Unknown 6= Voided trip'),
              trip_type STRING OPTIONS (description = 'A code indicating whether the trip was a street-hail or a dispatch that is automatically assigned based on the metered rate in use but can be altered by the driver. 1= Street-hail 2= Dispatch'),
              congestion_surcharge NUMERIC OPTIONS (description = 'Congestion surcharge applied to trips in congested zones')
          )
          OPTIONS (
              format = 'CSV',
              uris = ['{{render(vars.gcs_file)}}'],
              skip_leading_rows = 1,
              ignore_unknown_values = TRUE
          );

      - id: bq_green_table_tmp
        type: io.kestra.plugin.gcp.bigquery.Query
        sql: |
          CREATE OR REPLACE TABLE `{{kv('GCP_PROJECT_ID')}}.{{render(vars.table)}}`
          AS
          SELECT
            MD5(CONCAT(
              COALESCE(CAST(VendorID AS STRING), ""),
              COALESCE(CAST(lpep_pickup_datetime AS STRING), ""),
              COALESCE(CAST(lpep_dropoff_datetime AS STRING), ""),
              COALESCE(CAST(PULocationID AS STRING), ""),
              COALESCE(CAST(DOLocationID AS STRING), "")
            )) AS unique_row_id,
            "{{render(vars.file)}}" AS filename,
            *
          FROM `{{kv('GCP_PROJECT_ID')}}.{{render(vars.table)}}_ext`;

      - id: bq_green_merge
        type: io.kestra.plugin.gcp.bigquery.Query
        sql: |
          MERGE INTO `{{kv('GCP_PROJECT_ID')}}.{{kv('GCP_DATASET')}}.green_tripdata` T
          USING `{{kv('GCP_PROJECT_ID')}}.{{render(vars.table)}}` S
          ON T.unique_row_id = S.unique_row_id
          WHEN NOT MATCHED THEN
            INSERT (unique_row_id, filename, VendorID, lpep_pickup_datetime, lpep_dropoff_datetime, store_and_fwd_flag, RatecodeID, PULocationID, DOLocationID, passenger_count, trip_distance, fare_amount, extra, mta_tax, tip_amount, tolls_amount, ehail_fee, improvement_surcharge, total_amount, payment_type, trip_type, congestion_surcharge)
            VALUES (S.unique_row_id, S.filename, S.VendorID, S.lpep_pickup_datetime, S.lpep_dropoff_datetime, S.store_and_fwd_flag, S.RatecodeID, S.PULocationID, S.DOLocationID, S.passenger_count, S.trip_distance, S.fare_amount, S.extra, S.mta_tax, S.tip_amount, S.tolls_amount, S.ehail_fee, S.improvement_surcharge, S.total_amount, S.payment_type, S.trip_type, S.congestion_surcharge);

  - id: purge_files
    type: io.kestra.plugin.core.storage.PurgeCurrentExecutionFiles
    description: To avoid cluttering your storage, we will remove the downloaded files

pluginDefaults:
  - type: io.kestra.plugin.gcp
    values:
      serviceAccount: "{{kv('GCP_CREDS')}}"
      projectId: "{{kv('GCP_PROJECT_ID')}}"
      location: "{{kv('GCP_LOCATION')}}"
      bucket: "{{kv('GCP_BUCKET_NAME')}}"

triggers:
  - id: green_schedule
    type: io.kestra.plugin.core.trigger.Schedule
    cron: "0 9 1 * *"
    inputs:
      taxi: green

  - id: yellow_schedule
    type: io.kestra.plugin.core.trigger.Schedule
    cron: "0 10 1 * *"
    inputs:
      taxi: yellow
```
Puntos interesantes:
La fuente de la Verdad: `trigger.date`
En el script anterior, tú elegías el año y el mes manualmente en los `inputs`. Aquí, las variables dependen del reloj de Kestra
- `file`: Construye el nombre usando `{{trigger.date | date('yyyy-MM')}}`.
- `table`: Crea una tabla temporal específica para ese mes exacto para no chocar con otras ejecuciones.
Los Triggers (El corazón de la automatización)
Al final del script aparecen los `triggers`. Esto significa que Google Cloud recibirá los datos de los taxis de NY sin que tú muevas un dedo:
- **Green Taxi:** El día 1 de cada mes a las 9:00 AM.
- **Yellow Taxi:** El día 1 de cada mes a las 10:00 AM.
Preparado para el "Backfill
Este script está diseñado para "viajar en el tiempo". Si lo activas en el panel de Kestra para los últimos 2 años
1. Kestra lanzará una ejecución por cada mes.
2. Cada ejecución tendrá su propio `trigger.date`.
3. Cada una subirá su archivo a GCS y lo integrará en la tabla maestra de BigQuery.

El Flujo de Trabajo Completo (E-L-T Cloud)
1. **Extract:** Kestra descarga el archivo histórico desde GitHub.
2. **Load (GCS):** El archivo se guarda en tu **Data Lake** (GCS). Esto es ELT: primero cargamos el dato crudo.
3. **External Table:** BigQuery crea una "ventana" para mirar ese CSV en GCS sin importarlo todavía.
4. **Transform (Staging):** BigQuery lee esa ventana, calcula el `MD5` para el ID único y crea una tabla temporal.
5. **Merge (Final):** BigQuery compara la tabla temporal con la tabla histórica definitiva. Si el viaje es nuevo, lo inserta.

#### Diferencias Clave que debes recordar para el examen (o el trabajo):

| **Característica**   | **Script 04/05 (Postgres)**       | **Script 08/09 (GCP)**                  |
| -------------------- | --------------------------------- | --------------------------------------- |
| **Destino**          | Base de datos local (Postgres)    | Almacenamiento y Warehouse Cloud.       |
| **Escalabilidad**    | Limitada por tu disco/procesador. | Casi infinita (BigQuery).               |
| **Manejo de IDs**    | MD5 sobre columnas en Postgres.   | MD5 sobre columnas en BigQuery.         |
| **Particionamiento** | Manual en el SQL.                 | Integrado en BigQuery (`PARTITION BY`). |

#### Dato de interés: MD5
##### 1. ¿Qué es MD5?
Es una función que transforma cualquier cantidad de datos (un texto, un archivo, una fila) en una **huella digital única** de longitud fija (32 caracteres hexadecimales).
##### 2. ¿Para qué sirve en tus scripts?
Su función principal es la **Deduplicación**. Como los datos de los taxis no traen un ID propio, tú fabricas uno combinando las columnas más importantes (fecha, hora, lugar) y pasándolas por MD5.
- Si los datos de entrada son idénticos $\rightarrow$ El MD5 será idéntico.
- Si cambia un solo segundo en la hora $\rightarrow$ El MD5 será totalmente distinto.
##### 3. El flujo del MD5 en el Pipeline
1. **Concatenar:** Unes los campos clave: `VendorID + Pickup_Time + Location`.
2. **Hashear:** Aplicas `MD5()` a esa unión.
3. **Merge:** Comparas ese Hash con lo que ya tienes en la base de datos.
    - **¿Existe el Hash?** Ignoras la fila (evitas duplicados).
    - **¿No existe?** Insertas la fila como nueva.
##### 4. Propiedades Críticas
- **Determinista:** Misma entrada siempre da misma salida.
- **Irreversible:** No puedes obtener los datos originales a partir del Hash.
- **Rápido:** Ideal para procesar millones de filas (como los 29 millones que cargaste) sin frenar el pipeline.

## 2.5 Usando Inteligencia Artificial para Ingeniería de datos en Kestra

Esta sección se basa en lo que aprendiste anteriormente en el Módulo 2 para mostrarte cómo la IA puede acelerar el desarrollo de flujos de trabajo.
Al finalizar esta sección, podrás:
- **Entender por qué la ingeniería de contexto es importante** al colaborar con LLMs.
- **Usar AI Copilot** para construir flujos de Kestra más rápido.
- **Utilizar Retrieval Augmented Generation (RAG)** en canalizaciones de datos.

**Requisitos previos**
- Completar las secciones anteriores del Módulo 2 (Orquestación de flujos de trabajo con Kestra).
- Kestra se ejecuta localmente.
- Cuenta de Google Cloud con acceso a la API de Gemini (hay un nivel gratuito).

### 2.5.1 Porque IA para workflows?

Como ingenieros de datos, pasamos una cantidad significativa de tiempo escribiendo código repetitivo (_boilerplate_), buscando en la documentación y estructurando canalizaciones de datos. Las herramientas de IA pueden ayudarnos a:
- **Generar flujos de trabajo más rápido:** Describe lo que quieres lograr en lenguaje natural en lugar de escribir YAML desde cero.
- **Evitar errores:** Obtén código de flujo de trabajo con sintaxis correcta y actualizada que siga las mejores prácticas.

Sin embargo, la IA es tan buena como el contexto que le proporcionamos. Esta sección te enseña cómo realizar la **ingeniería de ese contexto** para obtener flujos de datos confiables y listos para producción.

### 2.5.2 Ingeniería de contexto con ChatGPT

Comencemos viendo qué sucede cuando la IA carece del contexto adecuado.
**Experimento: ChatGPT sin contexto**  
Abre ChatGPT en una ventana de incógnito (para evitar cualquier contexto de chats existentes).
Ingresa este **prompt**:
> _Crea un flujo de Kestra que cargue datos de taxis de NYC desde un archivo CSV a BigQuery. El flujo debe extraer datos, subirlos a GCS y cargarlos en BigQuery._

**Observa los resultados:**
ChatGPT generará un flujo de Kestra, pero es probable que contenga:
- **Sintaxis de plugins obsoleta:** p. ej., tipos de tareas antiguos que han sido renombrados.
- **Nombres de propiedades incorrectos:** p. ej., propiedades que no existen en las versiones actuales.
- **Funcionalidades alucinadas:** p. ej., tareas, disparadores (_triggers_) o propiedades que nunca existieron.

**¿Por qué sucede esto?**  
Los Modelos de Lenguaje Grandes (LLMs), como los modelos GPT de OpenAI, se entrenan con datos hasta un punto específico en el tiempo (**knowledge cutoff**). No conocen automáticamente sobre:
- Actualizaciones de software y nuevos lanzamientos.
- Plugins renombrados o APIs que han cambiado.
Este es el desafío fundamental al usar IA: el modelo solo puede trabajar con la información a la que tiene acceso.

**Aprendizaje clave: El contexto lo es todo**  
**Sin el contexto adecuado:**  
❌ Los asistentes de IA genéricos alucinan código obsoleto o incorrecto.  
❌ No puedes confiar en el resultado para su uso en producción.
**Con el contexto adecuado:**  
✅ La IA genera código preciso, actual y listo para producción.  
✅ Puedes iterar más rápido dejando que la IA genere el código base (_boilerplate_) del flujo de trabajo.

### 2.5.3 AI Copilot con Kestra

El **AI Copilot de Kestra** está diseñado específicamente para generar y modificar flujos de Kestra con pleno contexto sobre los últimos plugins, la sintaxis de flujos de trabajo y las mejores prácticas.

Configuración del AI Copilot

Antes de usar AI Copilot, se debe configurar el acceso a la API de Gemini en la instancia de Kestra.

**Paso 1: Obtener la clave de API de Gemini**
1. Visitar Google AI Studio. https://aistudio.google.com/app/api-keys
2. Iniciar sesión con la cuenta de Google. 
3. Hacer clic en "Create API Key".
4. Copiar la clave generada.

> [!WARNING]  
> **Advertencia:** No subir las claves de API a Git. Utilizar siempre variables de entorno o el KV Store de Kestra.

**Paso 2: Configurar Kestra AI Copilot**
Agregar lo siguiente a la configuración de Kestra. Esto puede realizarse modificando el archivo `docker-compose.yml` de la sección 2.2:

```yaml
services:
  kestra:
    environment:
      KESTRA_CONFIGURATION: |
        kestra:
          ai:
            type: gemini
            gemini:
              model-name: gemini-2.5-flash
              api-key: ${GEMINI_API_KEY}
```

Usa el código con precaución.
Luego, reiniciar Kestra:


```bash
cd 02-workflow-orchestration/docker
export GEMINI_API_KEY="tu-clave-api-aquí" 
docker compose up -d
```

Usa el código con precaución.
Ejercicio: Comparación entre ChatGPT y AI Copilot

**Objetivo:** Aprender por qué la ingeniería de contexto es importante.

1. Abrir la interfaz de Kestra en http://localhost:8080.
2. Crear un nuevo flujo y abrir el panel del Editor de Código.
3. Hacer clic en el botón de AI Copilot (icono de destellos ✨) en la esquina superior derecha.
4. Ingresar exactamente el mismo prompt que se usó con ChatGPT:
    
    > _Crea un flujo de Kestra que cargue datos de taxis de NYC desde un archivo CSV a BigQuery. El flujo debe extraer datos, subirlos a GCS y cargarlos en BigQuery._
    
5. Comparar los resultados:
    - ✅ Copilot genera un YAML ejecutable y funcional.
    - ✅ Copilot utiliza los tipos de plugins y propiedades correctos.
    - ✅ Copilot sigue las mejores prácticas actuales de Kestra.

**Aprendizaje clave:** ¡El contexto importa! AI Copilot tiene acceso a la documentación actual de Kestra, generando flujos mucho mejor que un asistente genérico como ChatGPT.


> En el archivo `docker-compose.yml`, el orden de las líneas dentro de la sección `environment` **no afecta el funcionamiento**, siempre y cuando respetes la **indentación** (los espacios a la izquierda).
Sin embargo, para mantener una buena estructura, lo ideal es colocarlo así:1. Ubicación recomendada
Puedes ponerlo al final de la sección `KESTRA_CONFIGURATION`. No importa si es antes o después de `queue`, lo que importa es que esté bajo el nivel de `kestra:`:
```
      KESTRA_CONFIGURATION: |
        kestra:
          # ... otras configuraciones (como queue, repository, etc)
          ai:
            type: gemini
            gemini:
              model-name: gemini-2.0-flash # Asegúrate de usar un modelo válido
              api-key: ${GEMINI_API_KEY}
```

>Para verificar si se exporto correctamente la api key. usar `echo $GEMINI_API_KEY`
aunque tiene que ser en la misma ventana. Ya que recordar que al reiniciar terminal estas variables de entorno temporales se borran

*IMPORTANTE GEMINI_API_KEY*
Pasando el GEMINI_API_KEY de esa manera no funciono en mi caso.
Tuve que hacerlo dentro de Kestra, en KV Store. Y cargar ahi el valor de la API KEY. Para que el script me lo tomara.

### 2.5.4 Bonus: Retrieval Augmented Generation (RAG)

Para aprender más sobre cómo proporcionar contexto a tus prompts, esta sección de bonificación demuestra cómo utilizar **RAG**. 

**¿Qué es RAG?**  
**RAG** (Generación Aumentada por Recuperación) es una técnica que: 

1. **Recupera** información relevante de tus fuentes de datos.
2. **Aumenta** el prompt de la IA con este contexto.
3. **Genera** una respuesta fundamentada en datos reales. 

Esto resuelve el problema de las alucinaciones al garantizar que la IA tenga acceso a información precisa y actualizada al momento de la consulta. 

**Cómo funciona RAG en Kestra**

**El Proceso:**

- **Ingesta de documentos:** Carga documentación, notas de lanzamiento u otras fuentes de datos.
- **Creación de embeddings:** Convierte el texto en representaciones vectoriales usando un LLM.
- **Almacenamiento de embeddings:** Guarda los vectores en el KV Store de Kestra (o en una base de datos vectorial).
- **Consulta con contexto:** Cuando haces una pregunta, se recuperan los embeddings relevantes y se incluyen en el prompt.
- **Generación de respuesta:** El LLM tiene contexto real y proporciona respuestas precisas. 

---

**Ejercicio: Recuperación Con vs. Sin Contexto**  
**Objetivo:** Comprender cómo RAG elimina las alucinaciones al fundamentar las respuestas del LLM en datos reales. 

**Parte A: Sin RAG** 

1. Navega al flujo `10_chat_without_rag.yaml` en tu interfaz de Kestra.
2. Haz clic en **Execute**.
3. Espera a que se complete la ejecución y abre la pestaña de **Logs**.
4. Lee la salida; nota cómo la respuesta sobre las "características de Kestra 1.1" es:
    - Vaga o genérica.
    - Potencialmente incorrecta.
    - Carece de detalles específicos.
    - Basada solo en los datos de entrenamiento del modelo (que pueden estar desactualizados).

**Parte B: Con RAG**

1. Navega al flujo `11_chat_with_rag.yaml`.
2. Haz clic en **Execute**.
3. Observa la ejecución:
    - **Primera tarea:** Ingiere la documentación de lanzamiento de Kestra 1.1, crea embeddings y los almacena.
    - **Segunda tarea:** Envía el prompt al LLM con el contexto recuperado de los embeddings almacenados.
4. Abre la pestaña de **Logs**.
5. Compara esta salida con la anterior; nota cómo es:
    - ✅ Específica y detallada.
    - ✅ Precisa con características reales del lanzamiento.
    - ✅ Fundamentada en documentación real. 

**Aprendizaje clave:** RAG fundamenta las respuestas de la IA en documentación actual, eliminando alucinaciones y proporcionando respuestas precisas y conscientes del contexto. 

Scripts en cuestion:
[10_chat_without_rag.yaml](https://github.com/DataTalksClub/data-engineering-zoomcamp/blob/main/02-workflow-orchestration/flows/10_chat_without_rag.yaml "10_chat_without_rag.yaml")
```yaml
id: 10_chat_without_rag
namespace: zoomcamp

description: |
  This flow demonstrates what happens when you query an LLM WITHOUT RAG.
  The model can only rely on its training data, which may be outdated or incomplete.
  
  After running this, check out 11_chat_with_rag.yaml to see how RAG fixes these issues.

tasks:
  - id: chat_without_rag
    type: io.kestra.plugin.ai.completion.ChatCompletion
    description: Query about Kestra 1.1 features WITHOUT RAG
    provider:
      type: io.kestra.plugin.ai.provider.GoogleGemini
      modelName: gemini-2.5-flash
      apiKey: "{{ kv('GEMINI_API_KEY') }}"
    messages:
      - type: USER
        content: |
          Which features were released in Kestra 1.1? 
          Please list at least 5 major features with brief descriptions.

  - id: log_results
    type: io.kestra.plugin.core.log.Log
    message: |
      ❌ Response WITHOUT RAG (no retrieved context):
      {{ outputs.chat_without_rag.textOutput }}
      
      🤔 Did you notice that this response seems to be:
      - Incorrect
      - Vague/generic
      - Listing features that haven't been added in exactly this version but rather a long time ago
      
      👉 This is why context matters. Run `11_chat_with_rag.yaml` to see the accurate, context-grounded response.
```

[11_chat_with_rag.yaml](https://github.com/DataTalksClub/data-engineering-zoomcamp/blob/main/02-workflow-orchestration/flows/11_chat_with_rag.yaml "11_chat_with_rag.yaml")
```yaml
id: 11_chat_with_rag
namespace: zoomcamp

description: |
  This flow demonstrates RAG (Retrieval Augmented Generation) by ingesting Kestra release documentation and using it to answer questions accurately.
  
  Compare this with 10_chat_without_rag.yaml to see the difference RAG makes.

tasks:
  - id: ingest_release_notes
    type: io.kestra.plugin.ai.rag.IngestDocument
    description: Ingest Kestra 1.1 release notes to create embeddings
    provider:
      type: io.kestra.plugin.ai.provider.GoogleGemini
      modelName: gemini-embedding-001
      apiKey: "{{ kv('GEMINI_API_KEY') }}"
    embeddings:
      type: io.kestra.plugin.ai.embeddings.KestraKVStore
    drop: true
    fromExternalURLs:
      - https://raw.githubusercontent.com/kestra-io/docs/refs/heads/main/src/contents/blogs/release-1-1/index.md

  - id: chat_with_rag
    type: io.kestra.plugin.ai.rag.ChatCompletion
    description: Query about Kestra 1.1 features with RAG context
    chatProvider:
      type: io.kestra.plugin.ai.provider.GoogleGemini
      modelName: gemini-2.5-flash
      apiKey: "{{ kv('GEMINI_API_KEY') }}"
    embeddingProvider:
      type: io.kestra.plugin.ai.provider.GoogleGemini
      modelName: gemini-embedding-001
      apiKey: "{{ kv('GEMINI_API_KEY') }}"
    embeddings:
      type: io.kestra.plugin.ai.embeddings.KestraKVStore
    systemMessage: |
      You are a helpful assistant that answers questions about Kestra.
      Use the provided documentation to give accurate, specific answers.
      If you don't find the information in the context, say so.
    prompt: |
      Which features were released in Kestra 1.1? 
      Please list at least 5 major features with brief descriptions.

  - id: log_results
    type: io.kestra.plugin.core.log.Log
    message: |
      ✅ RAG Response (with retrieved context):
      {{ outputs.chat_with_rag.textOutput }}
      
      Note that this response is detailed, accurate, and grounded in the actual release documentation. Compare this with the output from 06_chat_without_rag.yaml.
```


**Mejores prácticas de RAG**

- **Mantener documentos actualizados:** Re-ingiere regularmente para asegurar información vigente.
- **Fragmentación adecuada (Chunking):** Divide documentos grandes en fragmentos significativos.
- **Probar la calidad de recuperación:** Verifica que se recuperen los documentos correctos.


## **2.6 Bonus: Despliegue en la nube (Opcional)**

Ahora que tenemos todas nuestras canalizaciones funcionando y sabemos cómo crear rápidamente nuevos flujos con el AI Copilot de Kestra, podemos desplegar Kestra en la nube para que continúe orquestando nuestras ejecuciones programadas.

En esta sección adicional, cubriremos cómo puedes desplegar Kestra en **Google Cloud** y sincronizar automáticamente tus flujos de trabajo desde un repositorio de **Git**.

**Nota:** Al subir tus flujos de trabajo a Kestra, asegúrate de que no contengan información sensible. Puedes usar [Secrets](https://go.kestra.io/de-zoomcamp/secret) y el [KV Store](https://go.kestra.io/de-zoomcamp/kv-store) para mantener los datos confidenciales fuera de la lógica de tu flujo.

**Recursos**
- [Install Kestra on Google Cloud](https://go.kestra.io/de-zoomcamp/gcp-install)
- [Moving from Development to Production](https://go.kestra.io/de-zoomcamp/dev-to-prod)
- [Using Git in Kestra](https://go.kestra.io/de-zoomcamp/git)
- [Deploy Flows with GitHub Actions](https://go.kestra.io/de-zoomcamp/deploy-github-actions)