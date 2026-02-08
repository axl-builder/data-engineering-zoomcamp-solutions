# 🚀 Data Engineering Zoomcamp 2026 - Apuntes y Proyectos
### Por Axl | Enfoque en Backend Automation & Cloud Infrastructure

Bienvenido a mi repositorio de notas y proyectos del **Data Engineering Zoomcamp** de [DataTalks.Club](https://datatalks.club/blog/data-engineering-zoomcamp.html). 

Este espacio está dedicado a la comunidad hispanohablante. Aquí encontrarás la documentación detallada de cada módulo, traducida y enriquecida con soluciones a errores comunes encontrados durante el curso (Post-Mortems), mejores prácticas de seguridad y optimización de costos en la nube.

---

## 🛠️ Stack Tecnológico
* **Lenguajes:** Python (gestionado con `uv`), SQL.
* **Infraestructura:** Google Cloud Platform (GCS, BigQuery, Compute Engine), Terraform.
* **Contenedores:** Docker & Docker Compose.
* **Orquestación:** Kestra.
* **IA para Data:** Gemini API & RAG (Retrieval Augmented Generation).

---

## 📂 Contenido del curso

### [Módulo 1: Contenedores e Infraestructura como Código](./modulo-1/)
* **Docker & Postgres:** Levantamiento de bases de datos locales y pipelines de ingesta.
* **Gestión con `uv`:** Uso del gestor de paquetes más moderno de Python para entornos reproducibles.
* **Terraform:** Automatización de la infraestructura en GCP (Buckets y Datasets).
* **Nota Técnica:** Solución al error de instalación en WSL (PEP 668).

### [Módulo 2: Orquestación de Flujos de Trabajo](./modulo-2/)
* **Kestra:** Diseño de flujos ETL y ELT.
* **Estrategias de Datos:** Implementación de Idempotencia (MD5) y arquitecturas de capas (Bronze/Silver/Gold).
* **IA & RAG:** Uso de AI Copilot para generar YAMLs y creación de flujos con conocimiento contextual para eliminar alucinaciones.
* **Post-Mortem:** Diagnóstico de errores 404 y "Cold Start" en sistemas Java-based sobre Docker.

### [Módulo 3: Data Warehouse (BigQuery)](./modulo-3/)
* **OLAP vs OLTP:** Diferencias fundamentales y casos de uso.
* **Optimización de Costos:** Reducción drástica de escaneo de bytes mediante **Partitioning** y **Clustering**.
* **Tablas Externas:** Consultas directas a archivos en GCS sin costos de almacenamiento duplicado.
* **Buenas Prácticas:** Diseño de esquemas desnormalizados y optimización de Joins.

---

## 🛡️ Notas de Seguridad
Todos los archivos de configuración en este repositorio utilizan **placeholders** (`TU_PROYECTO_ID`, `TU_LLAVE_PRIVADA`). Nunca compartas tus llaves JSON o APIs de Gemini en repositorios públicos.

---

## 🤝 Contribuciones
Si eres estudiante del Zoomcamp y hablas español, ¡siéntete libre de abrir un Issue o un PR si encuentras algún error o quieres aportar un tip extra! 

**¡Sigamos automatizando el mundo de los datos!** ```




