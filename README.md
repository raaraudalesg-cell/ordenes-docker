
# RAUL | Sistema de Órdenes de Venta

### Arquitectura de tres contenedores con Docker Compose

**Asignatura:** Arquitectura de Computadoras  
**Evaluación:** Examen práctico del segundo parcial  
**Valor:** 15 puntos  
**Fecha de entrega:** 17 de noviembre de 2026

**Repositorio oficial:**  
https://github.com/raaraudalesg-cell/ordenes-docker

---

## 1. Integrantes

| Nombre completo | Número de cuenta |
|---|---|
| RAUL ANDRES RAUDALES GARCIA | 202510010696 |

## 2. Descripción

Se desarrolló un sistema web para administrar órdenes de venta y sus respectivos productos, utilizando una arquitectura distribuida de tres contenedores Docker.

El sistema permite crear, consultar, actualizar y eliminar órdenes y detalles de productos mediante una interfaz web desarrollada en Django.

La comunicación entre los servicios se realiza a través de una API REST implementada en Flask, mientras que la información se almacena en Microsoft SQL Server 2022.

El proyecto utiliza Docker Compose para administrar los contenedores, las redes, los volúmenes, las variables de entorno, las dependencias y los límites de recursos.

## 3. Objetivos

### Objetivo general

Diseñar e implementar una aplicación distribuida utilizando Docker Compose y tres contenedores independientes para presentación, servicios y almacenamiento.

### Objetivos específicos

- Construir imágenes Docker propias para Flask y Django.
- Implementar una base de datos SQL Server con relaciones PK y FK.
- Desarrollar una API REST con operaciones CRUD.
- Crear una interfaz web para administrar órdenes y productos.
- Implementar persistencia mediante volúmenes Docker.
- Configurar redes, healthchecks y límites de CPU y memoria.
- Documentar y publicar el proyecto en GitHub y Docker Hub.

## 4. Tecnologías utilizadas

| Tecnología | Función |
|---|---|
| Docker | Contenedorización |
| Docker Compose | Orquestación |
| SQL Server 2022 | Base de datos |
| Python Flask | API REST |
| Python Django | Interfaz web |
| Gunicorn | Servidor de aplicaciones |
| pymssql | Conexión Flask-SQL Server |
| requests | Comunicación Django-Flask |
| HTML, CSS y JavaScript | Presentación |
| Git y GitHub | Control de versiones |

## 5. Arquitectura

El proyecto utiliza tres servicios:

- `db`: almacenamiento de información en SQL Server.
- `api`: procesamiento de solicitudes REST con Flask.
- `web`: interfaz de usuario con Django.

### Diagrama

```text
                       USUARIO
                          |
                          v
                    NAVEGADOR WEB
                          |
                      Puerto 8000
                          |
                          v
               +-----------------------+
               |      ordenes-web      |
               |        DJANGO         |
               |        512 MB         |
               |         1 CPU         |
               +-----------------------+
                          |
                     http://api:5000
                          |
                          v
               +-----------------------+
               |      ordenes-api      |
               |      PYTHON FLASK     |
               |        512 MB         |
               |         1 CPU         |
               +-----------------------+
                          |
                        db:1433
                          |
                          v
               +-----------------------+
               |       ordenes-db      |
               |    SQL SERVER 2022    |
               |         2 GB          |
               |        2 CPU          |
               +-----------------------+
                          |
                          v
               +-----------------------+
               |    sqlserver_data     |
               |   VOLUMEN PERSISTENTE |
               +-----------------------+

                RED: ordenes_network
                    DRIVER: bridge
```

Django consume exclusivamente la API REST. Flask es el único servicio que accede directamente a SQL Server.

## 6. Estructura del proyecto

```text
ordenes-docker/
|
|-- api/
|   |-- app.py
|   |-- Dockerfile
|   |-- requirements.txt
|   |-- .dockerignore
|
|-- db/
|   |-- init.sql
|
|-- web/
|   |-- config/
|   |-- ordenes/
|   |   |-- templates/
|   |       |-- ordenes/
|   |           |-- base.html
|   |           |-- lista.html
|   |           |-- detalle.html
|   |           |-- formulario_orden.html
|   |           |-- formulario_detalle.html
|   |-- manage.py
|   |-- Dockerfile
|   |-- requirements.txt
|   |-- .dockerignore
|
|-- evidencias/
|-- compose.yaml
|-- .env.example
|-- .gitignore
|-- README.md
```

## 7. Requisitos previos

Para ejecutar el sistema se necesita:

- Docker Desktop con Docker Compose.
- Git.
- Navegador web.
- Recursos suficientes para ejecutar SQL Server y los servicios Python.
- Puertos 1433, 5000 y 8000 disponibles.

No es necesario instalar SQL Server, Flask o Django directamente en Windows.

## 8. Instalación y ejecución

### 8.1. Clonar el repositorio

```powershell
git clone https://github.com/raaraudalesg-cell/ordenes-docker.git
cd ordenes-docker
```

### 8.2. Crear el archivo de configuración

```powershell
Copy-Item .env.example .env
```

Editar `.env` y configurar las variables:

```dotenv
MSSQL_SA_PASSWORD=REEMPLAZAR_CON_CONTRASENA_SEGURA
DJANGO_SECRET_KEY=REEMPLAZAR_CON_CLAVE_ALEATORIA
```

La contraseña de SQL Server debe cumplir los requisitos de complejidad del motor.

La clave de Django debe ser un valor aleatorio suficientemente largo.

Para generar una clave de Django desde PowerShell:

```powershell
[guid]::NewGuid().ToString("N") + [guid]::NewGuid().ToString("N")
```

Copiar el resultado y utilizarlo como valor de `DJANGO_SECRET_KEY`.

El archivo `.env` contiene información privada y no debe subirse al repositorio.

### 8.3. Validar Docker Compose

```powershell
docker compose config --quiet
```

Si no aparecen errores, la configuración es válida.

### 8.4. Iniciar SQL Server

```powershell
docker compose up -d db
```

Comprobar su estado:

```powershell
docker compose ps
```

Esperar hasta que `ordenes-db` aparezca como `healthy`.

### 8.5. Inicializar la base de datos

En una instalación nueva, ejecutar el archivo `db/init.sql` para crear `OrdenesDB`, sus tablas y los datos de prueba.

Desde PowerShell:

```powershell
Get-Content .\db\init.sql -Raw | docker exec -i ordenes-db /opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P ((Get-Content .\.env | Where-Object { $_ -match '^MSSQL_SA_PASSWORD=' } | Select-Object -First 1) -replace '^MSSQL_SA_PASSWORD=', '') -C -b
```

La inicialización debe realizarse una sola vez para una base nueva, salvo que el script esté preparado para ejecutarse repetidamente.

En una instalación limpia se cargan:

- 6 órdenes iniciales.
- 12 detalles de productos.
- Un monto total de L 130,800.00.

### 8.6. Construir e iniciar todos los servicios

```powershell
docker compose up -d --build
```

### 8.7. Verificar los contenedores

```powershell
docker compose ps
```

Los tres servicios deben aparecer activos y saludables:

- `ordenes-db`
- `ordenes-api`
- `ordenes-web`

## 9. Direcciones de acceso

| Servicio | Dirección |
|---|---|
| Django | http://localhost:8000 |
| Flask API | http://localhost:5000/api/ordenes |
| Healthcheck API | http://localhost:5000/health |
| SQL Server | localhost:1433 |

## 10. Base de datos

Se utiliza Microsoft SQL Server 2022 con la base de datos `OrdenesDB`.

### Tabla ordenes

| Campo | Descripción |
|---|---|
| id | Clave primaria autoincremental |
| cliente | Nombre del cliente |
| fecha | Fecha de la orden |
| estado | Pendiente, Pagada o Anulada |
| total | Total de la venta |

### Tabla orden_detalle

| Campo | Descripción |
|---|---|
| id | Clave primaria autoincremental |
| orden_id | Clave foránea |
| producto | Nombre del producto |
| cantidad | Unidades |
| precio_unitario | Precio en lempiras |
| subtotal | Importe del producto |

Una orden puede tener múltiples detalles.

La base de datos incluye registros iniciales para comprobar el funcionamiento del sistema.

## 11. Productos y referencia de precios

Los productos tecnológicos utilizados como referencia para los datos de ejemplo se basan en el catálogo de PC Builds Honduras.

**Fuente:** https://pcbuildshonduras.com/

Los valores del sistema están expresados en lempiras hondureños (HNL).

Los precios almacenados son datos de prueba académicos. No se garantiza que coincidan con los precios vigentes del proveedor.

Los importes pueden cambiar según disponibilidad, promociones y actualizaciones del catálogo.

## 12. API REST Flask

La API permite administrar órdenes y detalles mediante solicitudes HTTP y respuestas JSON.

| Método | Endpoint | Operación |
|---|---|---|
| GET | /api/ordenes | Listar órdenes |
| GET | /api/ordenes/{id} | Consultar una orden |
| POST | /api/ordenes | Crear orden |
| PUT | /api/ordenes/{id} | Actualizar orden |
| DELETE | /api/ordenes/{id} | Eliminar orden |
| GET | /api/ordenes/{id}/detalles | Listar detalles |
| POST | /api/ordenes/{id}/detalles | Agregar detalle |
| PUT | /api/detalles/{id} | Actualizar detalle |
| DELETE | /api/detalles/{id} | Eliminar detalle |
| GET | /health | Comprobar disponibilidad |

La API contempla respuestas HTTP como 200, 201, 400 y 404.

### Cálculo de totales

El subtotal de cada detalle se calcula mediante:

`subtotal = cantidad * precio_unitario`

El total de la orden es:

`total = suma de subtotales`

Cuando se agrega, modifica o elimina un producto, el total se recalcula automáticamente.

## 13. Frontend Django

La interfaz RAUL permite:

- Listar órdenes.
- Registrar clientes y órdenes.
- Consultar información de una orden.
- Editar órdenes.
- Eliminar órdenes.
- Agregar productos.
- Modificar cantidades y precios.
- Eliminar detalles.
- Visualizar los totales calculados.
- Mostrar mensajes de error o confirmación.

La aplicación presenta un diseño oscuro de estilo retro con efectos de neón.

Django utiliza la variable `API_URL` para comunicarse con Flask mediante el nombre del servicio Docker.

## 14. Docker Compose y recursos

| Servicio | Puerto | RAM máxima | CPU máxima |
|---|---|---|---|
| SQL Server | 1433 | 2 GB | 2 |
| Flask | 5000 | 512 MB | 1 |
| Django | 8000 | 512 MB | 1 |

### Healthchecks

- SQL Server verifica la respuesta del motor de base de datos.
- Flask comprueba `/health`.
- Django comprueba que el frontend responda por HTTP.

### Dependencias

- Flask espera a que SQL Server esté saludable.
- Django espera a que Flask esté saludable.

### Persistencia

SQL Server utiliza el volumen `sqlserver_data`, montado en `/var/opt/mssql`.

Los datos se conservan al detener y eliminar los contenedores sin eliminar el volumen.

## 15. Pruebas de funcionamiento

### Estado de los contenedores

```powershell
docker compose ps
```

### Estado de la API

```powershell
Invoke-RestMethod http://localhost:5000/health
```

El resultado esperado es:

```text
database   status
--------   ------
connected  healthy
```

### Consulta de órdenes

```powershell
Invoke-RestMethod http://localhost:5000/api/ordenes
```

### Respuesta HTTP de Django

```powershell
(Invoke-WebRequest http://localhost:8000 -UseBasicParsing).StatusCode
```

La respuesta esperada es `200`.

### Consumo de recursos

```powershell
docker stats --no-stream
```

### Comprobar límites de CPU

```powershell
docker inspect ordenes-db --format '{{.HostConfig.NanoCpus}}'
docker inspect ordenes-api --format '{{.HostConfig.NanoCpus}}'
docker inspect ordenes-web --format '{{.HostConfig.NanoCpus}}'
```

### Prueba de persistencia

Registrar una orden de prueba y comprobar que aparece en la interfaz.

Después ejecutar:

```powershell
docker compose down
docker compose up -d
```

Esperar a que los tres contenedores estén saludables.

Abrir http://localhost:8000 y comprobar que la orden continúa registrada.

No ejecutar `docker compose down -v`, porque esa opción elimina los volúmenes del proyecto.

### Pruebas CRUD

Se deben comprobar las operaciones de creación, consulta, edición y eliminación de órdenes y detalles desde el navegador.

También se deben comprobar las respuestas JSON de la API mediante PowerShell, curl, Postman o Thunder Client.

### Prueba de instalación limpia realizada

Se comprobó el funcionamiento del proyecto utilizando un nombre independiente de Docker Compose:

```powershell
docker compose -p ordenes-prueba up -d db
```

Se inicializó una base de datos nueva con 6 órdenes y 12 detalles.

Posteriormente se construyeron y ejecutaron los tres servicios:

```powershell
docker compose -p ordenes-prueba up -d --build
```

Los tres contenedores alcanzaron el estado `healthy`.

La API respondió correctamente y Django devolvió HTTP `200`.

### Prueba de persistencia realizada

Se detuvieron y eliminaron los contenedores de prueba sin eliminar el volumen:

```powershell
docker compose -p ordenes-prueba down
```

Se iniciaron nuevamente:

```powershell
docker compose -p ordenes-prueba up -d
```

Después del reinicio, la API recuperó las mismas 6 órdenes iniciales, confirmando que la información permaneció almacenada en el volumen Docker.

El volumen original `ordenes-docker_sqlserver_data` se mantuvo independiente del volumen de prueba `ordenes-prueba_sqlserver_data`.

## 16. Evidencias

Las capturas del funcionamiento se almacenan en la carpeta `evidencias/`.

| Archivo | Evidencia |
|---|---|
| 01-contenedores-healthy.png | Tres servicios saludables |
| 02-docker-stats.png | Límites y consumo de recursos |
| 03-api-health.png | Endpoint de salud |
| 04-api-crud.png | Pruebas REST |
| 05-listado-ordenes.png | Listado de órdenes |
| 06-crear-orden.png | Creación de orden |
| 07-detalles-orden.png | Detalles de una orden |
| 08-agregar-producto.png | Registro de producto |
| 09-editar-producto.png | Actualización de producto |
| 10-eliminar-orden.png | Eliminación |
| 11-persistencia-antes.png | Datos antes de detener Compose |
| 12-persistencia-despues.png | Datos después de iniciar Compose |

Las capturas deben corresponder a ejecuciones reales del proyecto.

## 17. Docker Hub

Las imágenes propias de Flask y Django fueron construidas utilizando sus respectivos Dockerfile y publicadas en Docker Hub.

### Imágenes publicadas

| Servicio | Imagen | Etiqueta |
|---|---|---|
| Flask API | `ashurrov/ordenes-api` | `v1.0` |
| Django Web | `ashurrov/ordenes-web` | `v1.0` |
| SQL Server | `mcr.microsoft.com/mssql/server` | `2022-latest` |

### Enlaces oficiales

**Flask API:**

https://hub.docker.com/r/ashurrov/ordenes-api

**Django Web:**

https://hub.docker.com/r/ashurrov/ordenes-web

### Descargar las imágenes

```powershell
docker pull ashurrov/ordenes-api:v1.0
docker pull ashurrov/ordenes-web:v1.0
```

### Construcción local

```powershell
docker compose build
```

### Etiquetar las imágenes

```powershell
docker tag ordenes-api:v1.0 ashurrov/ordenes-api:v1.0
docker tag ordenes-web:v1.0 ashurrov/ordenes-web:v1.0
```

### Publicar en Docker Hub

```powershell
docker login -u ashurrov
docker push ashurrov/ordenes-api:v1.0
docker push ashurrov/ordenes-web:v1.0
```

### Resultado de la publicación

La imagen de Flask API fue publicada correctamente con la etiqueta `v1.0`.

La imagen de Django Web fue publicada correctamente con la etiqueta `v1.0`.

Ambas imágenes están disponibles en los repositorios de Docker Hub indicados anteriormente.

SQL Server utiliza la imagen oficial de Microsoft y no requiere una publicación adicional.

La instalación documentada en la sección 8 utiliza Docker Compose para construir las imágenes desde el código fuente del repositorio.

## 18. GitHub

**Repositorio público:**

https://github.com/raaraudalesg-cell/ordenes-docker

El repositorio contiene el código fuente, la configuración Docker, el script SQL y la documentación.

Las credenciales privadas deben permanecer fuera del repositorio.

El archivo `.env.example` incluye valores de ejemplo que deben reemplazarse antes de iniciar la aplicación.

El archivo `.env` no debe publicarse en GitHub.

## 19. Comandos de administración

### Iniciar

```powershell
docker compose up -d
```

### Reconstruir

```powershell
docker compose up -d --build
```

### Consultar estado

```powershell
docker compose ps
```

### Consultar registros

```powershell
docker compose logs --tail 50
```

### Reiniciar

```powershell
docker compose restart
```

### Detener sin eliminar datos

```powershell
docker compose down
```

## 20. Conclusiones

El proyecto RAUL demuestra la implementación de una arquitectura distribuida mediante tres contenedores Docker independientes.

La separación entre Django, Flask y SQL Server facilita la organización del sistema y permite que cada servicio tenga una responsabilidad específica.

Docker Compose permite administrar las dependencias, redes, recursos y ejecución de la aplicación desde un único archivo.

La persistencia de SQL Server permite conservar la información, mientras que los healthchecks facilitan la comprobación de disponibilidad.

El sistema implementa las operaciones CRUD necesarias para administrar órdenes de venta y sus detalles.

Durante las pruebas se verificó que la aplicación puede instalarse desde cero, inicializar la base de datos, iniciar sus tres contenedores y responder correctamente a las solicitudes HTTP.

También se comprobó que los registros de SQL Server permanecen disponibles después de detener y recrear los contenedores sin eliminar el volumen.

Las imágenes propias de Flask y Django fueron publicadas en Docker Hub con la versión `v1.0`.

## 21. Referencias

- Docker: https://docs.docker.com/
- Docker Compose: https://docs.docker.com/compose/
- Microsoft SQL Server: https://learn.microsoft.com/sql/
- Flask: https://flask.palletsprojects.com/
- Django: https://docs.djangoproject.com/
- PC Builds Honduras: https://pcbuildshonduras.com/

---

**Proyecto académico — Arquitectura de Computadoras — Segundo Parcial — 2026**
