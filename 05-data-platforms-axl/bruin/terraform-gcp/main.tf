# Habilita la API de BigQuery automáticamente
resource "google_project_service" "bigquery_api" {
  project = "de-bruin-488403"
  service = "bigquery.googleapis.com"

  disable_on_destroy = false
}

provider "google" {
  project     = "de-bruin-488403"
  region      = "us-central1"
  credentials = file("/home/axl/keys/gcp-sa.json") # Apunta a tu llave
}

# Definimos el dataset para los datos crudos (Ingesta)
resource "google_bigquery_dataset" "ingestion" {
  dataset_id                  = "ingestion"
  friendly_name               = "Ingestion Layer"
  description                 = "Datos crudos traídos de APIs o Seeds"
  location                    = "US" # Ajusta a EU si prefieres, pero Bruin sugiere US
  delete_contents_on_destroy = true # Útil para desarrollo: si borras el proyecto, borra las tablas
  
  depends_on = [google_project_service.bigquery_api]
}

# Definimos el dataset para la transformación (Staging)
resource "google_bigquery_dataset" "staging" {
  dataset_id                  = "staging"
  friendly_name               = "Staging Layer"
  description                 = "Tablas intermedias limpias"
  location                    = "US"
  delete_contents_on_destroy = true

  depends_on = [google_project_service.bigquery_api]
}

# Definimos el dataset para los reportes finales (Analítica)
resource "google_bigquery_dataset" "reports" {
  dataset_id                  = "reports"
  friendly_name               = "Reporting Layer"
  description                 = "Tablas listas para dashboards o consumo final"
  location                    = "US"
  delete_contents_on_destroy = true

  depends_on = [google_project_service.bigquery_api]
}