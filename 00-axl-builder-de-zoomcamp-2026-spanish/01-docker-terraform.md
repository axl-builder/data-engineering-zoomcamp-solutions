## 01-docker-terraform

 *01-docker-terraform*/docker-sql
 *01-docker-terraform*/docker-sql/01-introduction.md
##### ENTRANDO EN CALOR - PRACTICA DOCKER
En este modulo vemos los primeros pasos en [[Docker]].  
Probamos que version tenemos y que este funcionando con `docker --version` (no olvidar en windows abrir docker desktop. Que es el que permite que se utilice en WSL de alguna manera)

Se practican algunos "Basic Docker Commands", Dockerización básica, administración de containers, activación de dockers con imágenes base (ubuntu, python, etc.), Prueba con volumen (Blind Mount), asignando un repositorio con script de python. Para verificar ese funcionamiento de carpeta en línea .


 *01-docker-terraform*/docker-sql
 *01-docker-terraform*/docker-sql/02-virtual-environment.md
##### VIRTUAL ENVIRONMENTS AND DATA PIPELINES
Se nos introduce al concepto de [[Data pipelines]], y se comunica que se realizaran las siguientes tareas.
- Descargar un archivo .csv
- Transformar y limpiar esos datos con Pandas (librería de python)
- Cargar esos datos resultantes en una base de datos PostgreSQL
- Procesar la gigantesca cantidad de datos en "chunks" o "trozos"

Arrancamos con un ejemplo simple de *pipeline*.
donde importando la biblioteca de *sys* en un script de python,  se busca utilizar el comando *sysarg* para con un print simplemente mostrar los argumentos volcados desde la terminal (convirtiendo en integer el primero de los argumentos insertados, por lo tanto el sys.argv[1], ya que el sys.argv[0] siempre es el nombre del archivo con su extension). Se muestran dos prints, el primero una lista de los argumentos cargados como datos, y el segundo una hipotética declaración sobre que día se estaría corriendo este pipeline.

Agregamos *pandas*, para que el script pueda generar un pequeño *data frame*, y luego lo transforme en formato .parquet para particionar. Como podemos ver nos encontramos antes un pequeño caso de pipeline. Se toma datos como argumentos en la consola, se imprime información de utilidad de los datos procesados, se transforman y se cargan (en este caso en el mismo directorio en que se ejecuta este pequeño programa)

Sin embargo aquí aparece un asunto interesante, necesitamos para llevar adelante la tarea de manera limpia y eficiente hacerlo con *Maquinas virtuales (Virtual Machines, VMs)*.
Para esto utilizaremos *"UV"*  el cual es un gestor de paquetes de python, mas eficaz que pip, mas moderno y que curiosamente genera entornos virtuales automáticamente (también es un gestor de versiones como pyenv)

*Procedemos con un simple paso a paso para ejecutar el programa creado*, con las dependencias necesarias ya instaladas, pero lógicamente todo *dentro de la VM creada con UV*. (Y lo corremos también explicitando UV en el comando a diferencia de otros paquetes de entornos virtuales como VENV los cuales se activan y desactivan)

1. Instalamos [[UV]]: `*`
```bash
pip install uv
```

2. Ahora inicializamos el proyecto con UV:
```bash
uv init --python=3.13
```

(ESTO CREA UN ARCHIVO DENOMINADO *pyproyect.toml* CUYA FUNCION ES MANEJAR LAS DEPENDENCIAS. Y TAMBIEN SE CREA UN ARCHIVO *.python-version*)

3. Empezamos a agregar las dependencias:
```bash
uv add pandas pyarrow
```

4. Corremos el programa de python creado. CON UV
```bash
uv run python3 pipeline.py
```

`*` **IMPORTANTE.** [[PEP 668]] 
En un caso como este, si estas utilizando WSL (entorno virtual Linux desde windows). El mismo no te deja instalar UV u otras bibliotecas sin antes utilizar un entorno virtual para ello. Es un poco en este caso como el dilema del huevo y la gallina. Entonces vamos a hacer lo siguiente. Para mas información, ingresar al nodo de "PEP 668"


 *01-docker-terraform*/docker-sql
 *01-docker-terraform*/docker-sql/03-dockerizing-pipeline.md
##### DOCKERIZING THE PIPELINE
La idea es dockerizar el script simple de python (pipeline) que venimos realizando. Para esto nos introducen en el Dockerfile. El archivo que sirve como receta de cocina para generar la imagen que necesitamos dockerizar.

###### Simple Dockerfile with pip

```dockerfile
# base Docker image that we will build on
FROM python:3.13.11-slim

# set up our image by installing prerequisites; pandas in this case
RUN pip install pandas pyarrow

# set up the working directory inside the container
WORKDIR /app
# copy the script to the container. 1st name is source file, 2nd is destination
COPY pipeline.py pipeline.py

# define what to do first when the container runs
# in this example, we will just run the script
ENTRYPOINT ["python", "pipeline.py"]
```

Bueno procedemos a hacer el ""build" (crear la imagen con las instrucciones definidas en el .Dockerfile) y hacemos un run, para crear el contenedor (Docker)

Let's build the image:
```bash
docker build -t test:pandas .
```
- The image name will be `test` and its tag will be `pandas`. If the tag isn't specified it will default to `latest`.

We can now run the container and pass an argument to it, so that our pipeline will receive it:

```bash
docker run -it test:pandas some_number
```

dato interesante: en el docker file, el ENTRYPOINT es lo primero que se ejecuta. Por tanto al agregar el argumento necesario del script sucede seguido a esos argumentos del ENTRYPOINT tal como necesitamos.

*IMPORTANTE (siempre UV u otras VMs para levantar docker. + pro* 
*Es fundamental que el Dockerfile en lugar de usar pip, se utilice un entorno de maquina virtual como UV*.
###### ## Dockerfile with UV
```bash
# Start with slim Python 3.13 image
FROM python:3.13.10-slim

# Copy uv binary from official uv image (multi-stage build pattern)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/

# Set working directory
WORKDIR /app

# Add virtual environment to PATH so we can use installed packages
ENV PATH="/app/.venv/bin:$PATH"

# Copy dependency files first (better layer caching)
COPY "pyproject.toml" "uv.lock" ".python-version" ./
# Install dependencies from lock file (ensures reproducible builds)
RUN uv sync --locked

# Copy application code
COPY pipeline.py pipeline.py

# Set entry point
ENTRYPOINT ["uv", "run", "python", "pipeline.py"]
```


 *01-docker-terraform*/docker-sql
 *01-docker-terraform*/docker-sql/04-postgres-docker.md
##### RUNNING POSTGRESQL WITH DOCKER
La idea es usar una base de datos Postgres
Lo interesante es que con Docker no tenes ni que instalarlo. Simpremente hacer un Docker Run. Pero es importante cargarle como argumentos algunas variables de entorno (environment variables.)

1. Crear una carpeta de prueba si se quiere, en el curso se crea una de `ny_taxi_postgres_data`. Codigo para correr el Docker:
```bash
docker run -it --rm \
  -e POSTGRES_USER="root" \
  -e POSTGRES_PASSWORD="root" \
  -e POSTGRES_DB="ny_taxi" \
  -v ny_taxi_postgres_data:/var/lib/postgresql \
  -p 5432:5432 \
  postgres:18
```
###### Explanation of Parameters
- `-e` sets environment variables (user, password, database name)
- `-v ny_taxi_postgres_data:/var/lib/postgresql` creates a **named volume**
    - Docker manages this volume automatically
    - Data persists even after container is removed
    - Volume is stored in Docker's internal storage
- `-p 5432:5432` maps port 5432 from container to host
- `postgres:18` uses PostgreSQL version 18 (latest as of Dec 2025)

###### Alternative Approach - Bind Mount (ALTERNATIVA BIND MOUNT)
First create the directory, then map it:
```shell
mkdir ny_taxi_postgres_data

docker run -it \
  -e POSTGRES_USER="root" \
  -e POSTGRES_PASSWORD="root" \
  -e POSTGRES_DB="ny_taxi" \
  -v $(pwd)/ny_taxi_postgres_data:/var/lib/postgresql \
  -p 5432:5432 \
  postgres:18
```

Named Volume vs Bind Mount
- **Named volume** (`name:/path`): Managed by Docker, easier
- **Bind mount** (`/host/path:/container/path`): Direct mapping to host filesystem, more control

Ahora que tenemos levantada la base de datos Postgres, la idea es conectarse. Y lo vamos a hacer desde el host primero. Utilizando un entorno virtual generado por UV.

2. Install pgcli in UV, "pgcli"
```bash
uv add --dev pgcli
```
The `--dev` flag marks this as a development dependency (not needed in production). It will be added to the `[dependency-groups]` section of `pyproject.toml` instead of the main `dependencies` section.

3. Now use it to connect to Postgres:
```bash
uv run pgcli -h localhost -p 5432 -u root -d ny_taxi
```

4. Hacer la prueba de algunos comandos SQL
```SQL
-- List tables
\dt

-- Create a test table
CREATE TABLE test (id INTEGER, name VARCHAR(50));

-- Insert data
INSERT INTO test VALUES (1, 'Hello Docker');

-- Query data
SELECT * FROM test;

-- Exit
\q
```


 *01-docker-terraform*/docker-sql
 *01-docker-terraform*/docker-sql/05-data-ingestion.md
##### DATA INGESTION
Aquí aparece *Jupyter Notebook*. Una aplicación web que funciona como un cuaderno de laboratorio digital e interactivo. Su uso es muy optimo para análisis de datos, visualizar los resultados paso a paso, entre otras cosas. Uno de sus puntos mas interesante es que funciona con celdas. Entonces podes ir compartimentando el código para hacerlo funcionar individualmente por partes e ir probando cada sección. Tambien se pueden agregar aclaraciones, descripciones, imágenes, graficos, notas, etc.

1. Instalamos Jupyter Notebook en UV. y lo creamos un Jupyter Notebook en una pestaña de la terminal para acceder desde un puerto.
```bash
uv add --dev jupyter
uv run jupyter notebook
```
Cuando ejecutas un Jupyter Notebook, la propia herramienta imprime en la terminal toda la información que necesitas justo al final del proceso de arranque.

Sin embargo, a veces hay tanto texto que se pierde. Aquí te explico cómo encontrarlo y cómo controlarlo:
Dónde mirar en la terminal
Al ejecutar `uv run jupyter notebook`, busca unas líneas que se ven exactamente así al final del log:

```md
[I 12:00:00.000 NotebookApp] Jupyter Notebook 7.x.x is running at:
[I 12:00:00.000 NotebookApp] http://localhost:8888/tree?token=abcdef123456...
[I 12:00:00.000 NotebookApp]        or http://127.0.0.1:8888/tree?token=abcdef123456...
```
 **El Puerto:** Es el número después de los dos puntos (usualmente `8888`).
**El Link:** Es la URL completa que incluye el **token**. Ese token es tu "contraseña" temporal.

2. Descargamos y explotamos el Dataset (en este caso de NYC). 

> Note: The CSV data is stored as gzipped files. Pandas can read them directly.
We will use data from the [NYC TLC Trip Record Data website](https://www1.nyc.gov/site/tlc/about/tlc-trip-record-data.page).
Specifically, we will use the [Yellow taxi trip records CSV file for January 2021](https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/yellow_tripdata_2021-01.csv.gz).

En el nuevo notebook realizamos el siguiente script:
```python
import pandas as pd

# Read a sample of the data
prefix = 'https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/'
df = pd.read_csv(prefix + 'yellow_tripdata_2021-01.csv.gz', nrows=100)

# Display first rows
df.head()

# Check data types
df.dtypes

# Check data shape
df.shape
```

> Handling Data Types
We have a warning: (Note that this warning might pop up later for some users, so it's best to follow the instructions below)
	/tmp/ipykernel_25483/2933316018.py:1: DtypeWarning: Columns (6) have mixed types. Specify dtype option on import or set low_memory=False.
	
So we need to specify the types:

```python
`dtype = {
    "VendorID": "Int64",
    "passenger_count": "Int64",
    "trip_distance": "float64",
    "RatecodeID": "Int64",
    "store_and_fwd_flag": "string",
    "PULocationID": "Int64",
    "DOLocationID": "Int64",
    "payment_type": "Int64",
    "fare_amount": "float64",
    "extra": "float64",
    "mta_tax": "float64",
    "tip_amount": "float64",
    "tolls_amount": "float64",
    "improvement_surcharge": "float64",
    "total_amount": "float64",
    "congestion_surcharge": "float64"
}

parse_dates = [
    "tpep_pickup_datetime",
    "tpep_dropoff_datetime"
]

df = pd.read_csv(
    prefix + 'yellow_tripdata_2021-01.csv.gz',
    nrows=100,
    dtype=dtype,
    parse_dates=parse_dates
)`
```

3. Empezamos con la preparación para la ingesta de datos en Postgres
La idea de todo esto es la de:
- descargar el .csv, 
- leerlo en trozos o "chunks", 
- convertir las columnas datatime,
- y finalmente insertar la data en PostgreSQL usando SQLAlchemy

Por tanto, lo que sigue es...
INSTALAR *SQLAlchemy*
```bash
uv add sqlalchemy psycopg2-binary
```

CREAR Conexión a la base de datos (Create Engine)
```python
from sqlalchemy import create_engine
engine = create_engine('postgresql://root:root@localhost:5432/ny_taxi')
```

	en el create_engine que ponemos postgresql://root:root@localhost:5432/ny_taxi' puede cambiar depende el caso...  ahi tenemos implicitos el motor, usuario, contraseña, direccion del host, puerto de la db, y nombre de la db
	
Conseguir el Esquema o "Schema" de DDL. ()
```python
# Para "Ver antes de actuar" (Validación)
# Antes de subir 2 millones de filas, quieres estar seguro de que Pandas entendió bienlos tipos. Al ejecutar ese `print`, verás algo como esto en tu terminal:

print(pd.io.sql.get_schema(df, name='yellow_taxi_data', con=engine))

# EL OUTPUT DEBERIA SER EL SIGUIENTE :
"""
CREATE TABLE yellow_taxi_data (
    "VendorID" BIGINT,
    tpep_pickup_datetime TIMESTAMP WITHOUT TIME ZONE,
    tpep_dropoff_datetime TIMESTAMP WITHOUT TIME ZONE,
    passenger_count BIGINT,
    trip_distance FLOAT(53),
    "RatecodeID" BIGINT,
    store_and_fwd_flag TEXT,
    "PULocationID" BIGINT,
    "DOLocationID" BIGINT,
    payment_type BIGINT,
    fare_amount FLOAT(53),
    extra FLOAT(53),
    mta_tax FLOAT(53),
    tip_amount FLOAT(53),
    tolls_amount FLOAT(53),
    improvement_surcharge FLOAT(53),
    total_amount FLOAT(53),
    congestion_surcharge FLOAT(53)
)
"""
```

Creamos una TABLE
```bash
df.head(n=0).to_sql(name='yellow_taxi_data', con=engine, if_exists='replace')

# Crea la tabla vacía en Postgres (el `head(n=0)` significa "cero filas, solo columnas").
```

4. Ingesta de datos
*IMPORTANTE* no queremos instertar absolutamente todos los datos de una. Queremos hacerlo en trozos "chunks". Por tanto utilizaremos un iterador para ello.
```python
df_iter = pd.read_csv(
    prefix + 'yellow_tripdata_2021-01.csv.gz',
    dtype=dtype,
    parse_dates=parse_dates,
    iterator=True,
    chunksize=100000
)
```

- REVISION DE SNIPETS IMPORTANTES QUE SE UTILIZARAN EN BUCLE DE DIGESTION COMPLETO SIGUIENTE.
Iterate Over Chunks
```python
for df_chunk in df_iter:
    print(len(df_chunk))
```
Inserting Data
```python
df_chunk.to_sql(name='yellow_taxi_data', con=engine, if_exists='append')
```


*IMPORTANTE* Finalmente el *BUCLE DE DIGESTION COMPLETO* se vería así:
```python
first = True

for df_chunk in df_iter:

    if first:
        # Create table schema (no data)
        df_chunk.head(0).to_sql(
            name="yellow_taxi_data",
            con=engine,
            if_exists="replace"
        )
        first = False
        print("Table created")

    # Insert chunk
    df_chunk.to_sql(
        name="yellow_taxi_data",
        con=engine,
        if_exists="append"
    )

    print("Inserted:", len(df_chunk))
```

5. Para agregar una barra de progreso intalamos *tqdm* (con "!" si queremos desde jupyter notebook) 
```bash
uv add tqdm
```

APLICAMOS LO SIGUIENTE EN EL ITERABLE ANTERIOR
```python
from tqdm.auto import tqdm

for df_chunk in tqdm(df_iter):
    ...
```

	To see progess in terms of total chunks, you would have to add the `total` argument to `tqdm(df_iter)`. In our scenario, the pragmatic way is to hardcode a value based on the number of entries in the table.

6. Finalmente verificamos los datos.
Nos conectamos usando pgcli nuevamente:
```bash
uv run pgcli -h localhost -p 5432 -u root -d ny_taxi
```
 Archivo completo del Jupyter Notebook--->![[Untitled.ipynb]]
--
#### ALTERNATIVA .PARQUET
*IMPORTANTE* EN CASO DE ARCHIVOS PARQUET. .
A diferencia del .CSV (formato de texto plano. Pandas tiene que adivinar los tipos de datos. )  Esto es importante saberlo, ya que ademas de cambiar la sintaxis que se usa en pandas para esto, hay que tener en cuenta que argumentos como dtype=, iterator=, chuncksize=, etc. No sirven
Por ejemplo para dtype se usa import fastparquet --> df.astype(dtype)
Por ejemploo para iterator se usa import pyarrow.parquet --> pyarrow.parquet.ParquetFile(archivo) para despues en un bloque de iteracion utilizar iter_batches(batch_size=100000)
Parquet es binario, y ya llega incrustado el esquema (dtypes) en los metadatos.

Las opciones que tenemos son las siguientes:
- Conversion *luego* de la carga. (la mas común)
- Definir tipos durante la lectura ([[PyArrow]])

Llevamos adelante Conversion *luego* de la carga. (la mas común)

INSTALAMOS DEPENDENCIAS:
```bash
uv pip install pandas pyarrow fastparquet
```

FUNDAMENTAL. Archivo completo del Jupyter Notebook (Con explicaciones)--->
![[green_tripdata_parquet.ipynb]]

--

 *01-docker-terraform*/docker-sql
 *01-docker-terraform*/docker-sql/06-ingestion-script.md
##### CREATING THE DATA INGESTION SCRIPT (PYTHON)
Esta es la parte donde convertimos el Jupyter Notebook en un script de python.
```bash
# La prinera linea es para hacer la conversion jn --> py. Obviamente notebook.ipynb es un ejemplo, el nombre.ipynb puede variar...
# la segunda linea es para cambiar el nombre del archivo al que uno quiera. Ese es de ejemplo

uv run jupyter nbconvert --to=script notebook.ipynb
mv notebook.py ingest_data.py
```

	EN ESTA PARTE, TENEMOS QUE ORDENAR EL SCRIPT. YA QUE EL ORDEN QUE TRAE DESDE JUPYTER NOTEBOOK NO NOS SIRVE.


Script de INGESTION COMPLETO
```python
# PRIMERO POR SUPUESTO LOS MODULOS
import pandas as pd
from sqlalchemy import create_engine
from tqdm.auto import tqdm

# SEGUNDO ESTABLECEMOS LAS VARIABLES
dtype = {
    "VendorID": "Int64",
    "passenger_count": "Int64",
    "trip_distance": "float64",
    "RatecodeID": "Int64",
    "store_and_fwd_flag": "string",
    "PULocationID": "Int64",
    "DOLocationID": "Int64",
    "payment_type": "Int64",
    "fare_amount": "float64",
    "extra": "float64",
    "mta_tax": "float64",
    "tip_amount": "float64",
    "tolls_amount": "float64",
    "improvement_surcharge": "float64",
    "total_amount": "float64",
    "congestion_surcharge": "float64"
}

```
```python
# TERCERO. ACA ES FUNDAMENTAL TRASNFORMAR PARAMETRIZAR TODO LO POSIBLE. PARA PODER MIGRAR TODO A CADA CASO NECESARIO. Y ARMAMOS UNA FUNCION PARA MODULAR EL CODIGO.

def run():
	pg_user = 'root'
	pg_pass = 'root	
	pg_host = 'localhost'
	pg_port = 5432
	pg_db = 'ny_taxi'
	
	year = 2021
	month = 1
	
	table_name = 'yellow_taxi_data'
	
	chunksize = 100000
	
	# EN ESTE CASO PARAMETRIZAMOS MEJOR EL CASO DE PREFIX + EL LINK DE DESCARGA. PARA HACERLO 1 (UNO) SOLO. con fSTRING nos ayudamos para parametrizar datos dal archivo a descargar como año, mes con decimales, etc
	prefix = 'https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/'
	url = f'{prefix}/yellow_tripdata_{year}-{month:02d}.csv.gz'
	
	# en el engine para parametrizar usamos el fSTRING. con las llaves {}
	engine = create_engine(f'postgresql://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_db}')

	
	df_iter = pd.read_csv(
	    url,
    dtype=dtype,
    parse_dates=parse_dates,
    iterator=True,
    chunksize=chunksize
)

#Construimos la logica de loop. para construir la tabla con el script
	first = True
	
	for df_chunk in tqdm(df_iter):
	    if first:
	        # Create table schema (no data)
	        df_chunk.head(0).to_sql(
	            name=table_name,
	            con=engine,
	            if_exists="replace"
	        )
	        
	        first = False
	        print("Table created")
	
	    # Insert chunk
	    df_chunk.to_sql(
	        name=table_name,
	        con=engine,
	        if_exists="append"
	    )
	
	    print("Inserted:", len(df_chunk))
	   
if __name__ == '__main__':
	run()
```
Archivo completo ---> ![[ingest_data.py]]

```python

# HASTA ESTA PARTE ES EL SCRIPT NECESARIO PARA EL DIGEST.
#PERO NECESITAMOS INGRESAR LAS VARIABLES NECESARIAS EN LOS PARAMETROS ESDE LA TERMINAL. PODEMOS USAR POR EJEMPLO DEL MODULO CLICK DE PYTHON, RESUELTO RAPIDAMENTE CON INTELIGENCIA ARTIFICIAL. PASANDOLE LOS DATOS 

import click

@click.command()
@click.option('--pg-user', default='root', help='PostgreSQL user')
@click.option('--pg-pass', default='root', help='PostgreSQL password')
@click.option('--pg-host', default='localhost', help='PostgreSQL host')
@click.option('--pg-port', default=5432, type=int, help='PostgreSQL port')
@click.option('--pg-db', default='ny_taxi', help='PostgreSQL database name')
@click.option('--target-table', default='yellow_taxi_data', help='Target table name')
def run(pg_user, pg_pass, pg_host, pg_port, pg_db, target_table):
    # Ingestion logic here
    pass
```
Lo que genera una serie de cambios. resultando en el siguiente SCRIPT COMPLETO.
Archivo completo ---> ![[ingest_data_click 1.py]]
(Se utiliza el modulo [[Click]] de python para que no tengas que ser un "cirujano de código" cada vez que quieras cambiar algo.)

Corremos el script en la terminal finalmente. Por supuesto como venimos haciendo con UV (entorno virtual)
```python
#EJEMPLO. OJO. VARIARIA EN FUNCION DE EL CLICK RESULTANTE.
uv run python ingest_data.py \
  --pg-user=root \
  --pg-pass=root \
  --pg-host=localhost \
  --pg-port=5432 \
  --pg-db=ny_taxi \
  --target-table=yellow_taxi_trips
```


 *01-docker-terraform*/docker-sql
 *01-docker-terraform*/docker-sql/07-pgadmin.md
##### pgAdmin DATABASE MANAGEMENT TOOL
En este sub-modulo, se busca:
- Correr un contenedor Docker para el cliente pgcli (*pgAdmin*)
- Correr nuevamente el contenedor Docker realizado de la db Postgres
- CREAR una red de docker. Ya que hay que lograr que los contenedores se encuentren, y eso se logra con "virtual networks"

1. Correr Container *pgAdmin*
```bash
docker run -it \
  -e PGADMIN_DEFAULT_EMAIL="TU_EMAIL" \
  -e PGADMIN_DEFAULT_PASSWORD="root" \
  -v pgadmin_data:/var/lib/pgadmin \
  -p 8085:80 \
  dpage/pgadmin4
```
- El parámetro `-v pgadmin_data:/var/lib/pgadmin` El mapeo de volumen lo que permite es que queden la configuración de pgAdmin, para no tener que configurarlo de cero cada vez que se levanta el contenedor (server connections, preferences).
- El contenedor necesita unicamente dos variables de entorno. "TU_EMAIL" Y "root" ene este caso.
- pgAdmin es una app web, y por default utiliza el puerto 80. En el mapeo de los puertos, establecemos el 8085 para conectar con nuestro localhost.
- El nombre de la imagen es dpage/pgadmin4
- OJO ESTO NO FUNCIONA AUN PORQUE HAY QUE CREAR EL *DOCKER NETWORK* PARA CONTENEDORES DE CLIENTE Y SERVIDOR SE VEAN ENTRE SI

2. Corriendo containers Docker en la misma red (*Docker Network*)
CREAMOS UNA RED DOCKER:
```bash
docker network create pg-network
```

CORREMOS CONTAINERS EN UNA RED EN COMUN:
```bash
# Run PostgreSQL on the network
docker run -it \
  -e POSTGRES_USER="root" \
  -e POSTGRES_PASSWORD="root" \
  -e POSTGRES_DB="ny_taxi" \
  -v ny_taxi_postgres_data:/var/lib/postgresql \
  -p 5432:5432 \
  --network=pg-network \
  --name pgdatabase \
  postgres:18

# In another terminal, run pgAdmin on the same network
docker run -it \
  -e PGADMIN_DEFAULT_EMAIL="TU_EMAIL" \
  -e PGADMIN_DEFAULT_PASSWORD="root" \
  -v pgadmin_data:/var/lib/pgadmin \
  -p 8085:80 \
  --network=pg-network \
  --name pgadmin \
  dpage/pgadmin4
```
- El nombre de los contenedores pgdatabase y pgadmin les permite a los contenedores encontrarse entre si.

3. Conectarse con pgAdmin a PostgreSQL
Ahora deberia no haber problema, para conectarse de un web browser con http://localhost:8085 . Usar el mail  pasword que se corrio con el container del cliente para ingresar.

PASO A PASO INGRESO:
1. Open browser and go to `http://localhost:8085`
2. Login with email: `TU_EMAIL`, password: `root`
3. Right-click "Servers" → Register → Server
4. Configure:
    - **General tab**: Name: `Local Docker`
    - **Connection tab**:
        - Host: `pgdatabase` (the container name)
        - Port: `5432`
        - Username: `root`
        - Password: `root`
5. Save

Now you can explore the database using the pgAdmin interface!


 *01-docker-terraform*/docker-sql
 *01-docker-terraform*/docker-sql/08-dockerizing-ingestion.md
##### DOCKERIZING THE INGESTION PYTHON SCRIPT
Como bien dice el titulo, hay que hacer un container del script de digestion.

1. El archivo Dockerfile
```dockerfile
FROM python:3.13.11-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/

WORKDIR /code
ENV PATH="/code/.venv/bin:$PATH"

COPY pyproject.toml .python-version uv.lock ./
RUN uv sync --locked

COPY ingest_data_click.py .

ENTRYPOINT ["uv", "run", "python", "ingest_data_click.py"]
```
Explicación de cada linea:
- `FROM python:3.13.11-slim`: Start with slim Python 3.13 image for smaller size
- `COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/`: Copy UV binary from official UV image
- `WORKDIR /code`: Set working directory inside container
- `ENV PATH="/code/.venv/bin:$PATH"`: Add virtual environment to PATH
- `COPY pyproject.toml .python-version uv.lock ./`: Copy dependency files first (better caching)
- `RUN uv sync --locked`: Install all dependencies from lock file (ensures reproducible builds)
- `COPY ingest_data.py .`: Copy ingestion script
- `ENTRYPOINT ["uv", "run", "python", "ingest_data.py"]`: Set entry point to run the ingestion script

2. Construir ¨Build¨ la IMAGEN de Docker
```bash
docker build -t taxi_ingest:v001 .
```

3. Correr finalmente la ingestion en contenedor
```bash
docker run -it \
  --network=pg-network \
  taxi_ingest:v001 \
    --pg-user=root \
    --pg-password=root \
    --pg-host=pgdatabase \
    --pg-port=5432 \
    --pg-db=ny_taxi \
    --target-table=yellow_taxi_trips
```

- IMPORTANTE. Tenemos que asignarle el nombre de red correspondiente para que encuentre al resto de los contenedores en red. Y tiene que ser antes de el nombre (en este caso el taxi_ingest:v001)
- el host en lugar de ser localhost como venia siendo antes, logicamente tiene que tener el nombre de la db de postgres corriendo en contenedor
- El script esta preparado para reemplazar la db pre existente.


 *01-docker-terraform*/docker-sql
 *01-docker-terraform*/docker-sql/09-docker-compose.md
##### DOCKER COMPOSE (ORQUESTANDO CONTENEDORES DOCKER)
Aquí es donde aprendemos a utilizar Docker Compose. El cual es de mucha utilidad, ya que de esta manera no necesitamos manejar y ejecutar tantos scripts para levantar contenedores distintos, ya que se hacen con un solo comando siguiendo las instrucciones de un archivo `docker-compose.yaml`. Un dato interesante, es que no hace falta configurar una red en especifico en este caso, porque docker compose se encarga de que los contenedores que levanta estén conectado a una red que genera por default.

EJEMPLO `docker-compose.yaml`:
```yaml
services:
  pgdatabase:
    image: postgres:18
    environment:
      POSTGRES_USER: "root"
      POSTGRES_PASSWORD: "root"
      POSTGRES_DB: "ny_taxi"
    volumes:
      - "ny_taxi_postgres_data:/var/lib/postgresql"
    ports:
      - "5432:5432"

  pgadmin:
    image: dpage/pgadmin4
    environment:
      PGADMIN_DEFAULT_EMAIL: "TU_EMAIL"
      PGADMIN_DEFAULT_PASSWORD: "root"
    volumes:
      - "pgadmin_data:/var/lib/pgadmin"
    ports:
      - "8085:80"



volumes:
  ny_taxi_postgres_data:
  pgadmin_data:
```

INICIAR SERVICIOS CON DOCKER COMPOSE:
```bash
# Levantar servicio docker compose foreground
docker-compose up

# Levantar servicio docker compose background
docker-compose up -d

# Manera correcta de apagarlo.
docker-compose down
```

OTROS COMANDOS DE UTILIDAD:
```bash
# View logs
docker-compose logs

# Stop and remove volumes
docker-compose down -v
```

IMPORTANTE. En caso de que se quisiera correr nuevamente el script de digestion una vez levantado el docker compose. Tener en cuenta que ahora *la red, o network* que genero es propia.
Debemos de buscar el nombre generado automáticamente de esa red con:
```bash
# chequear link de red:
docker network ls

# digamos en este caso.. pipeline_default (suele ser similar al nombre del directorio en que se ejecuta)
# ahora a correr este script con el network correcto script:
docker run -it --rm\
  --network=pipeline_default \
  taxi_ingest:v001 \
    --pg-user=root \
    --pg-pass=root \
    --pg-host=pgdatabase \
    --pg-port=5432 \
    --pg-db=ny_taxi \
    --target-table=yellow_taxi_trips
```


*01-docker-terraform*/docker-sql
 *01-docker-terraform*/terraform

## GUIA DE LECTURA PARA ESTA PARTE DE LA DOCUMENTACION:
Esta parte tiene 3 grandes secciones (cada una cuenta con sub-secciones):
- *DESARROLLO TEORICO: GOOGLE CLOUD PLATFORM / TERRAFORM*: Desarrollo teorico del servicio utilizado en la nube y la herramienta de infrastructure as code para su gestion automatica. Util en caso de que se quiera refrescar los conceptos importantes (aplicado al curso)
- *ACLARACION PREVIA. funcionamiento archivos*: Explicación del funcionamiento de terraform. Sus archivos de configuración como main.tf, variables.tf, etc. Y una guía de como construirlos.
- *PROCEDIMIENTO EN EL CURSO*: La sección mas importante posiblemente, ya que es la que indica paso a paso como preparar GCP y su vinculación con terraform para llevar adelante las tareas de Data Engineering que el curso tiene preparadas para uno mas adelante en el curso.
### DESARROLLO TEORICO: GOOGLE CLOUD PLATFORM / TERRAFORM:
#### GOOGLE CLOUD PLATFORM
Esta es la sección donde se empieza a ver servicios en la nube *[[Cloud Services]]*.
Una vez instalado *Terraform*, instalado *gcloud*, y registrado la cuenta en *[[Google Cloud Platform (GCP)]]

El servicio en la nube permite básicamente a personas y empresas, tener acceso a recursos informáticos a través de internet, en lugar de precisar de gestionar hardware localmente. Entre estos recursos nos referimos a cosas como servidores, almacenamiento o software por ejemplo.
La industria suele clasificar los servicios en 3 categorías, denominadas el "Cloud stack".
*SaaS (Software as a Service)*, *PaaS (Platform as a Service)* y *IaaS (Infrastructure as a Service)*.
La clasificación sobre la cual se desarrolla este submódulo es la de *IaaS*. Y Específicamente *Cloud Data Warehousing*.
##### SERVICIOS (las cajas de herramientas):
Hay muchísimos, pero para este curso de Data Engineering nos interesan los siguientes
###### A. COMPUTO (el cerebro)
Es donde corre el código. 
*Compute Engine:* Maquinas virtuales puras VMs
*Cloud Run / Functions:* Código que corre solo cuando se necesita.
	dato: En el curso estamos utilizando de momento la maquina local para llevar adelante el computo. Mas adelante se pasara también al cloud para esto.

###### B. ALMACENAMIENTO DE OBJETOS (El deposito de archivos)
*Google cloud storage (GCS*): Es donde creamos el *Bucket*
	Función: Su función es la de guardar archivos crudos o planos de diversas indoles (CSV, JSON, PARQUET, etc.).
	No es una base de datos. Es un deposito de archivos infinito. El *Data Lake*

###### C. ANALISIS DE DATOS (La base de datos inteligente)
*BigQuery*: Donde creamos el *Dataset*
	Función: Es un almacén de datos, diseñado para procesar tablas gigantes con SQL.

##### NIVEL DE ACCESO (IAM, Identity and Access Management)
Es donde se decide quien puede hacer que, y con que.
- *Service account*: Tipo especial de cuenta que no es utilizada por humanos. Es mas bien utilizada por aplicaciones o maquinas virtuales en la nube de google para interactuar con las apis de este sistema.
- *Roles*: Son los permisos que se asignan en particular a estas Service account. Por ejemplo: Storage Admin, BigQuery Admin, etc.
- *JSON Key*: Es la credencial física que le permite a *terraform* demostrarle a *IAM* que tiene permiso de entrar al proyecto y generar recursos.

#### TERRAFORM
*Terraform* es una herramienta de Infrastructure As Code (IAC) de código abierto, la cual se la utiliza para definir, aprovisionar y gestionar recursos de infraestructura para distintos servicios de en la nube, ya sean estos los de Google Cloud Platform, AWS cloud services  o Azure. Es el Standard para automatizar los distintos servicios en la  nube.

*Características importantes:* Enfoque declarativo / Lenguaje HCL / Estado (archivo recursos vinc.) / Agnóstico a la nube (funciona con todas)
###### Flujo de Trabajo Estándar (Workflow) 
El ciclo de vida típico para gestionar recursos con Terraform consta de cuatro etapas principales: 
1. **Write (Escribir):** Defines la infraestructura en archivos `.tf`.
2. **Init (Inicializar):** Preparas el directorio de trabajo y descargas los "plugins" (providers) necesarios para interactuar con la nube elegida.
3. **Plan (Planificar):** Generas una previsualización de los cambios que Terraform realizará para que coincidan con tu código.
4. **Apply (Aplicar):** Ejecutas los cambios definitivos en el proveedor de nube. 
###### Beneficios Principales
- **Automatización y Velocidad:** Elimina la necesidad de configurar recursos manualmente a través de consolas web, reduciendo errores humanos.
- **Consistencia:** Permite replicar entornos exactos (desarrollo, pruebas, producción) de manera idéntica.
- **Versionado:** Al ser código, la infraestructura puede guardarse en repositorios como **GitHub**, permitiendo auditorías, revisiones de cambios y reversión a versiones anteriores.

### ACLARACION PREVIA. funcionamiento archivos

Una manera es directamente descargar del repositorio del curso unos archivos que voy a dejar aca abajo como base para ir construyendo los `main.tf` y `variables.tf`.
Pero es importante entender que estos se construyen de la manera especificada mas abajo.

Para trabajar con Terraform como un profesional del nicho de Data Engineering, no se trata de memorizar código, sino de saber navegar la **documentación oficial** y entender el ciclo de vida de los archivos que gestionan el "estado" de tu infraestructura.
Aquí tienes la guía técnica paso a paso.

##### 1. Cómo buscar fragmentos de código: El flujo oficial
El lugar donde vive todo el conocimiento es el **Terraform Registry**. No busques en blogs aleatorios; ve directo a la fuente.
#### Paso a paso técnico:
1. **Identificar el Provider**: Primero necesitas saber con qué nube vas a hablar. En nuestro caso es el **Google Provider**.
2. **Navegar a la Documentación**: Ve a [registry.terraform.io](https://registry.terraform.io/) y busca "Google". Entra en el provider oficial de HashiCorp.    
3. **Uso del Índice (Resources)**: En el menú de la izquierda, verás una lista enorme. Los nombres siguen una convención: `google_<servicio>_<recurso>`.
    - Si buscas un Bucket: Busca `google_storage_bucket`.
    - Si buscas BigQuery: Busca `google_bigquery_dataset`.
        
4. **Copiar el "Argument Reference"**: Cada página de recurso tiene un ejemplo de uso (Example Usage). Copias ese bloque a tu `main.tf`.    
5. **Parametrizar**: Sustituyes los valores fijos por variables (ej. cambias `"mi-bucket-123"` por `var.gcs_bucket_name`).


##### 2. Definición de los Archivos Críticos
En Terraform, cada archivo tiene una responsabilidad única. Separarlos es lo que permite que tu infraestructura sea escalable.
###### A. `variables.tf` (Definición de Entradas)
Es el archivo de **configuración**. Aquí declaras qué datos necesita tu código para funcionar, pero **no** necesariamente les asignas un valor final si quieres que sean dinámicos.
- **Término correcto:** _Input Variables_.
- **Función:** Define el esquema (nombre, tipo de dato y descripción). Permite que el mismo `main.tf` sirva para crear un entorno de "Desarrollo" o de "Producción" solo cambiando los valores de las variables.
###### B. `terraform.tfstate` (La Verdad de la Infraestructura)
Es un archivo JSON generado automáticamente después de un `apply`. Es el documento más importante de tu proyecto.
- **Término correcto:** _State File_.
- **Función:** Mapea tus recursos definidos en el código con los IDs reales que Google Cloud asignó.
- **Gestión:** **NUNCA se edita a mano**. Si lo borras, Terraform "olvida" que ya construyó cosas y tratará de crearlas de nuevo, causando colisiones de nombres.
###### C. `terraform.tfstate.backup`
Es la versión anterior al último cambio exitoso.
- **Función:** Si un `apply` falla o corrompe el estado, este archivo te permite recuperar la versión inmediata anterior del mapa de infraestructura.
###### D. `.terraform/` (Carpeta de Binarios)
Es una carpeta oculta que se crea al ejecutar `terraform init`.
- **Función:** Contiene los archivos ejecutables (plugins) de los providers. Terraform no sabe hablar con Google por sí solo; necesita descargar el "traductor" (provider) y guardarlo aquí.


##### 3. Cómo se gestionan: El Ciclo de Vida (Comandos)
Para que estos archivos interactúen correctamente, sigues este orden lógico:
1. **`terraform init`**: Prepara el entorno. Descarga los plugins en la carpeta `.terraform/`.
2. **`terraform plan`**: Es un "dry run" (simulación). Lee tus `.tf`, consulta el `.tfstate` y le pregunta a la API de Google: "¿Qué falta?". Genera un plan de acción.
3. **`terraform apply`**: Ejecuta los cambios. Al finalizar, actualiza el `terraform.tfstate` con los nuevos datos recibidos de la nube.
4. **`terraform destroy`**: Usa el `.tfstate` para encontrar cada recurso en Google Cloud y borrarlos todos en el orden correcto.

##### Resumen para tus apuntes:
- **`main.tf`**: El "Qué" (Los recursos).![[main.tf]]
- **`variables.tf`**: El "Con qué" (Los parámetros).![[variables.tf]]
- **`terraform.tfstate`**: El "Cómo está" (El mapa real).![[terraform.tfstate]]
- **`.gitignore`**: Debe incluir `.terraform/`, `*.tfstate`, `*.tfstate.backup` y cualquier archivo `.json` de credenciales para evitar fugas de seguridad.


### PROCEDIMIENTO EN EL CURSO:
##### Paso 1: Crear el Proyecto en Google Cloud (Manual)
Terraform puede crear muchas cosas, pero **el Proyecto de GCP es el contenedor principal** y, por lo general, se crea manualmente una sola vez (o vía CLI) para tener un ID donde trabajar.
1. Ve a la [GCP Console](https://console.cloud.google.com/).
2. Crea un proyecto nuevo (ejemplo: `NOMBRE_DE_TU_PROYECTO`).
3. **Anotá el ID del proyecto**. Lo vas a necesitar para el código.

#####  Paso 2: Crear la Service Account (La "Llave")
Como no queremos que Terraform use tu cuenta personal (por seguridad y automatización), creamos un "usuario robot".
1. En el buscador de GCP, poné **"IAM & Admin"** -> **"Service Accounts"**.
2. Dale un nombre (ej. `terraform-runner`).
3. **Asignale Roles**: Para este curso, dale `Viewer`, `Storage Admin` y `BigQuery Admin` (o `Editor` para simplificar ahora).
4. **Generá la Key**: Entrá a la cuenta creada -> pestaña **"Keys"** -> **"Add Key"** -> **"Create new key"** -> **JSON**.
5. Ese archivo es el que moviste a `~/.google/credentials/google_credentials.json`.

##### Paso 3: Habilitar las APIs (El permiso de obra)
Google Cloud tiene todo apagado por defecto. Si Terraform intenta crear un Bucket y la API de Storage está apagada, va a fallar.
Ejecutá estos comandos en tu terminal (usando el `gcloud` SDK que ya tenés instalado):

```bash
#Reemplaza con tu ID de proyecto
gcloud services enable compute.googleapis.com storage-api.googleapis.com bigquery.googleapis.com --project="TU_PROJECT_ID"
```

##### Paso 4: Vincular la terminal con la Llave
Aquí es donde entra el `export` que hicimos antes. Le avisamos a la terminal qué llave usar para los siguientes comandos.

```bash
export GOOGLE_APPLICATION_CREDENTIALS="/home/axl/.google/credentials/google_credentials.json"
```

##### Paso 4 ALTERNATIVA: Vincular la terminal con la Llave.
Si mas adelante un error que te tiró Terraform fue: `open /home/axl/.google/credentials/google_credentials.json: no such file or directory`
**¿Por qué pasa esto?** Vos le dijiste al sistema con el `export` que la llave está ahí, pero Terraform fue a buscarla y la puerta estaba cerrada (el archivo no existe en esa ruta exacta).

**Acción Correcta:** Verificá la ruta real de tu archivo. Ejecutá este comando:
```bash
ls -l /home/axl/.google/credentials/google_credentials.json
```
- **Si te dice "No such file":** Moviste el archivo mal o el nombre es distinto.
- **Si el archivo está en tu carpeta actual**, hacé esto:
```bash
export GOOGLE_APPLICATION_CREDENTIALS="$(pwd)/nombre-real-de-tu-archivo.json"
```

**Verificá que la variable se guardó**:
```bash
echo $GOOGLE_APPLICATION_CREDENTIALS
```
- (Debe imprimir la ruta completa al archivo).

- Ahora si. **Lanza el plan**: (paso 7)

##### Paso 5: Preparar el código (`variables.tf`)
Ahora volvemos a tu carpeta donde tenés los archivos `.tf`. Abrí `variables.tf` y asegúrate de que el `default` del proyecto sea el correcto:

```
variable "project" {
  description = "Project ID"
  default     = "NOMBRE_DE_TU_PROYECTO" # <--- TU ID REAL AQUÍ
}
```

##### Paso 6: El "Limpiado" de `main.tf` (opcional, quizás no hace falta)
Aquí es donde te trabaste. Como ya hiciste el **Paso 4** (el export), no hace falta que el código mencione el archivo JSON.
**Editá tu `main.tf`** para que el bloque del provider sea simple:

```
provider "google" {
  project = var.project
  region  = var.region
  # SIN la línea de credentials: file(...)
}
```

##### Paso 7: La Verificación Final (El Plan)
Ahora, con el código limpio y la variable de entorno configurada, ejecutá:

```bash
terraform plan
```

**¿Qué deberías ver?** Si todo está bien, Terraform te mostrará una lista con un signo **`+`** verde.
- `+ google_bigquery_dataset.demo_dataset`
- `+ google_storage_bucket.demo-bucket`
Y al final dirá: `Plan: 2 to add, 0 to change, 0 to destroy.`

	### Checkpoint Técnico (Crítico para Backend): Si el `terraform plan` te tira un error ahora, lo más probable es que sea por **región** o **nombre de bucket**.

##### Paso 8: La Construcción (`apply`)
Ahora es el momento de poner los ladrillos. Ejecuta:

```bash
terraform apply
```
**Atención:**
1. Te va a mostrar el mismo plan que acabas de ver.
2. Al final, te va a preguntar: `Enter a value:`.
3. Tenés que escribir **`yes`** y darle a `Enter`.
##### Checkpoint Post-Construcción
Una vez que termine (debería tardar unos 10-20 segundos), verás un mensaje en verde: `Apply complete! Resources: 2 added, 0 changed, 0 destroyed.`
Para verificarlo como un verdadero **Backend Automation Developer** (sin entrar a la web), tirá estos comandos de la CLI de Google:

```bash
# Para ver el bucket:
gcloud storage buckets list

# Para ver el dataset de BigQuery:
bq ls --project_id NOMBRE_DE_TU_PROYECTO
```
