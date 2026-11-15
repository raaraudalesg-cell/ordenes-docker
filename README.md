
# RAUL | Sistema de Órdenes de Venta

## Arquitectura de tres contenedores con Docker Compose

**Asignatura:** Arquitectura de Computadoras  
**Evaluación:** Examen práctico del segundo parcial  
**Valor:** 15 puntos  
**Fecha de entrega:** 17 de noviembre de 2026

**Repositorio:** https://github.com/raaraudalesg-cell/ordenes-docker

---

## 1. Integrantes

| Nombre completo | Número de cuenta |
|---|---|
| RAUL ANDRES RAUDALES GARCIA | 202510010696 |

## 2. Descripción del proyecto

RAUL es un sistema web de administración de órdenes de venta desarrollado mediante una arquitectura de tres contenedores Docker.

La aplicación permite registrar clientes, crear órdenes, agregar productos, consultar información, modificar registros y eliminar órdenes o detalles.

Los servicios se distribuyen de la siguiente manera:

- **Django:** interfaz web.
- **Flask:** API REST y lógica de negocio.
- **SQL Server 2022:** almacenamiento de información.

Docker Compose permite administrar los servicios, redes, volúmenes, variables de entorno, dependencias, límites de recursos y verificaciones de salud.

## 3. Objetivos

### Objetivo general

Implementar una aplicación distribuida mediante Docker Compose, utilizando tres contenedores independientes para presentación, procesamiento y almacenamiento.

### Objetivos específicos

- Crear imágenes Docker para Django y Flask.
- Implementar una base de datos relacional en SQL Server.
- Desarrollar operaciones CRUD mediante una API REST.
- Crear una interfaz web para administrar órdenes.
- Implementar persistencia mediante volúmenes.
- Configurar healthchecks y límites de recursos.
- Publicar el código en GitHub.
- Publicar las imágenes propias en Docker Hub.
- Comprobar la instalación desde una clonación limpia.

## 4. Tecnologías utilizadas

| Tecnología | Función |
|---|---|
| Docker | Contenedorización |
| Docker Compose | Administración de servicios |
| SQL Server 2022 | Base de datos |
| Python | Lenguaje de programación |
| Flask | API REST |
| Django | Interfaz web |
| Gunicorn | Servidor de aplicaciones |
| pymssql | Conexión con SQL Server |
| requests | Comunicación entre Django y Flask |
| HTML y CSS | Presentación |
| Git | Control de versiones |
| GitHub | Repositorio del proyecto |
| Docker Hub | Publicación de imágenes |

## 5. Arquitectura del sistema

La aplicación utiliza tres servicios conectados mediante una red Docker.

```text
                  USUARIO
                     |
                     v
               NAVEGADOR WEB
                     |
                 Puerto 8000
                     |
                     v
           +-------------------+
           |    ordenes-web    |
           |      DJANGO       |
           |      512 MB       |
           |       1 CPU       |
           +-------------------+
                     |
                api:5000
                     |
                     v
           +-------------------+
           |    ordenes-api    |
           |       FLASK       |
           |      512 MB       |
           |       1 CPU       |
           +-------------------+
                     |
                  db:1433
                     |
                     v
           +-------------------+
           |     ordenes-db    |
           |    SQL SERVER     |
           |       2 GB        |
           |       2 CPU       |
           +-------------------+
                     |
                     v
           +-------------------+
           |  sqlserver_data   |
           | VOLUMEN PERSISTENTE|
           +-------------------+

             ordenes_network
```

Django se comunica con Flask mediante HTTP.

Flask es el único servicio que accede directamente a SQL Server.

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

Para ejecutar el proyecto se necesita:

- Windows con PowerShell.
- Docker Desktop instalado y funcionando.
- Docker Compose disponible.
- Git instalado.
- Conexión a Internet para descargar imágenes.
- Puertos 1433, 5000 y 8000 disponibles.

No es necesario instalar SQL Server, Flask o Django directamente en Windows.

**Importante:** los comandos de instalación están preparados para PowerShell. Deben ejecutarse en el orden indicado.

## 8. Instalación completa desde GitHub

Esta sección permite descargar y ejecutar el proyecto sin modificar manualmente ningún archivo de configuración.

Los comandos se pueden copiar y pegar directamente en PowerShell.

### 8.1. Clonar el repositorio

```powershell
cd $HOME\Downloads
git clone https://github.com/raaraudalesg-cell/ordenes-docker.git
cd ordenes-docker
```

### 8.2. Generar automáticamente las variables de entorno

Ejecutar:

```powershell
$clave="Raul!"+[guid]::NewGuid().ToString("N")+"9A"; $django=[guid]::NewGuid().ToString("N")+[guid]::NewGuid().ToString("N"); @("MSSQL_SA_PASSWORD=$clave","DJANGO_SECRET_KEY=$django") | Set-Content -Path .env -Encoding ascii
```

Este comando genera automáticamente:

- Una contraseña segura para SQL Server.
- Una clave secreta para Django.
- El archivo `.env` con ambas variables.

No es necesario abrir el archivo ni escribir contraseñas manualmente.

El archivo `.env` no debe subirse a GitHub.

### 8.3. Validar Docker Compose

```powershell
docker compose config --quiet
```

Si no aparecen errores ni advertencias, la configuración es válida.

### 8.4. Iniciar SQL Server

```powershell
docker compose up -d db
```

### 8.5. Esperar automáticamente a que SQL Server esté saludable

```powershell
while ((docker inspect ordenes-db --format '{{.State.Health.Status}}') -ne 'healthy') { Start-Sleep -Seconds 5 }
```

Este comando espera hasta que SQL Server termine de iniciar.

Cuando finalice, continuar con el siguiente paso.

Si el contenedor no alcanza el estado saludable, consultar los registros con:

```powershell
docker logs ordenes-db --tail 40
```

### 8.6. Crear la base de datos y cargar los registros iniciales

```powershell
Get-Content .\db\init.sql -Raw | docker exec -i ordenes-db /opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P ((Get-Content .\.env | Where-Object { $_ -match '^MSSQL_SA_PASSWORD=' } | Select-Object -First 1) -replace '^MSSQL_SA_PASSWORD=', '') -C -b
```

Este comando ejecuta el archivo `db/init.sql` y prepara la base de datos `OrdenesDB`.

En una instalación nueva se cargan:

- 6 órdenes.
- 12 detalles.
- L 130,800.00 en registros de venta.

El comando de inicialización está destinado a una base de datos nueva y no debe ejecutarse repetidamente sobre una base ya inicializada sin revisar previamente el script.

### 8.7. Construir e iniciar Flask y Django

```powershell
docker compose up -d --build
```

Docker Compose construirá las imágenes de Flask y Django y levantará los servicios.

### 8.8. Verificar los tres contenedores

```powershell
docker compose ps
```

El resultado esperado es:

```text
ordenes-db    Up (healthy)
ordenes-api   Up (healthy)
ordenes-web   Up (healthy)
```

### 8.9. Abrir la aplicación

Desde PowerShell:

```powershell
Start-Process http://localhost:8000
```

La interfaz RAUL debe abrirse en el navegador.

## 9. Direcciones de acceso

| Servicio | Dirección |
|---|---|
| Django | http://localhost:8000 |
| Flask API | http://localhost:5000/api/ordenes |
| Salud de la API | http://localhost:5000/health |
| SQL Server | localhost:1433 |

## 10. Base de datos

Se utiliza Microsoft SQL Server 2022 con la base de datos `OrdenesDB`.

### Tabla ordenes

| Campo | Descripción |
|---|---|
| id | Clave primaria |
| cliente | Nombre del cliente |
| fecha | Fecha de registro |
| estado | Estado de la orden |
| total | Total de la venta |

### Tabla orden_detalle

| Campo | Descripción |
|---|---|
| id | Clave primaria |
| orden_id | Clave foránea |
| producto | Nombre del producto |
| cantidad | Cantidad solicitada |
| precio_unitario | Precio unitario |
| subtotal | Importe del detalle |

Una orden puede tener varios detalles.

Los estados utilizados son:

- Pendiente.
- Pagada.
- Anulada.

## 11. Datos de prueba

La base de datos inicial contiene seis órdenes y doce detalles.

| ID | Cliente | Estado | Total |
|---|---|---|---|
| 1 | GUSTAVO ADOLFO SIU MARQUEZ | Pendiente | L 16,600.00 |
| 2 | JOSE ALFREDO MEJIA GRANADOS | Pagada | L 17,400.00 |
| 3 | NELSON JAVIER GUERRA NOLASCO | Pendiente | L 27,500.00 |
| 4 | RAUL ANDRES RAUDALES GARCIA | Pagada | L 22,900.00 |
| 5 | RUT NOHEMY SANCHEZ GARCIA | Pendiente | L 15,300.00 |
| 6 | STANLEY LEMUEL GOFF STERBROOCK | Anulada | L 31,100.00 |

**Total general: L 130,800.00**

Los productos utilizados como referencia incluyen laptops y teclados.

**Referencia comercial:** https://pcbuildshonduras.com/

Los precios almacenados son datos de prueba académicos y no representan necesariamente precios vigentes.

## 12. API REST Flask

La API administra las órdenes y sus detalles mediante solicitudes HTTP.

| Método | Endpoint | Operación |
|---|---|---|
| GET | /api/ordenes | Listar órdenes |
| GET | /api/ordenes/{id} | Consultar orden |
| POST | /api/ordenes | Crear orden |
| PUT | /api/ordenes/{id} | Actualizar orden |
| DELETE | /api/ordenes/{id} | Eliminar orden |
| GET | /api/ordenes/{id}/detalles | Listar detalles |
| POST | /api/ordenes/{id}/detalles | Agregar detalle |
| PUT | /api/detalles/{id} | Actualizar detalle |
| DELETE | /api/detalles/{id} | Eliminar detalle |
| GET | /health | Verificar salud |

### Cálculo de totales

El subtotal se calcula mediante:

`subtotal = cantidad * precio_unitario`

El total de una orden corresponde a la suma de sus subtotales.

## 13. Frontend Django

La interfaz web permite:

- Consultar órdenes.
- Registrar nuevas órdenes.
- Modificar información.
- Eliminar órdenes.
- Consultar detalles.
- Agregar productos.
- Modificar cantidades y precios.
- Eliminar productos.
- Visualizar totales.

Django consume la API Flask mediante la red interna de Docker.

La aplicación presenta un diseño oscuro de estilo retro con efectos de neón.

## 14. Docker Compose y límites de recursos

| Servicio | Puerto | Memoria | CPU |
|---|---|---|---|
| SQL Server | 1433 | 2 GB | 2 |
| Flask | 5000 | 512 MB | 1 |
| Django | 8000 | 512 MB | 1 |

### Red

Los tres servicios utilizan la red `ordenes_network`.

### Persistencia

SQL Server utiliza el volumen `sqlserver_data`, montado en `/var/opt/mssql`.

### Healthchecks

Cada servicio dispone de una comprobación de salud para verificar su disponibilidad.

### Dependencias

Flask depende de SQL Server.

Django depende de Flask.

## 15. Pruebas de funcionamiento

### 15.1. Verificar contenedores

```powershell
docker compose ps
```

### 15.2. Verificar la API

```powershell
Invoke-RestMethod http://localhost:5000/health
```

Resultado esperado:

```text
database   status
--------   ------
connected  healthy
```

### 15.3. Consultar órdenes

```powershell
Invoke-RestMethod http://localhost:5000/api/ordenes
```

### 15.4. Comprobar Django

```powershell
(Invoke-WebRequest http://localhost:8000 -UseBasicParsing).StatusCode
```

Resultado esperado:

```text
200
```

### 15.5. Consultar recursos

```powershell
docker stats --no-stream
```

### 15.6. Comprobar límites de CPU

```powershell
docker inspect ordenes-db --format '{{.HostConfig.NanoCpus}}'
docker inspect ordenes-api --format '{{.HostConfig.NanoCpus}}'
docker inspect ordenes-web --format '{{.HostConfig.NanoCpus}}'
```

### 15.7. Comprobar persistencia

Crear una orden desde la interfaz.

Después ejecutar:

```powershell
docker compose down
docker compose up -d
```

Comprobar nuevamente las órdenes:

```powershell
Invoke-RestMethod http://localhost:5000/api/ordenes
```

La orden creada debe permanecer registrada.

**No utilizar `docker compose down -v` si se desea conservar la información.**

### 15.8. Prueba de instalación desde GitHub

Se realizó una prueba utilizando una clonación independiente del repositorio.

La instalación permitió:

- Descargar el proyecto desde GitHub.
- Generar automáticamente el archivo `.env`.
- Validar Docker Compose.
- Iniciar SQL Server.
- Crear `OrdenesDB`.
- Insertar seis órdenes.
- Insertar doce detalles.
- Comprobar un total de L 130,800.00.

La prueba confirmó que la base de datos puede inicializarse desde una copia nueva del repositorio.

## 16. Evidencias

Las capturas del proyecto pueden almacenarse en `evidencias/`.

| Archivo sugerido | Evidencia |
|---|---|
| 01-contenedores-healthy.png | Contenedores saludables |
| 02-docker-stats.png | Consumo de recursos |
| 03-api-health.png | Salud de la API |
| 04-api-crud.png | Operaciones REST |
| 05-listado-ordenes.png | Listado de órdenes |
| 06-crear-orden.png | Registro de orden |
| 07-detalles-orden.png | Detalles |
| 08-agregar-producto.png | Agregar producto |
| 09-editar-producto.png | Editar producto |
| 10-eliminar-orden.png | Eliminar orden |
| 11-persistencia-antes.png | Datos antes del reinicio |
| 12-persistencia-despues.png | Datos después del reinicio |

Las capturas deben obtenerse de ejecuciones reales.

## 17. Docker Hub

Las imágenes propias de Flask y Django fueron publicadas en Docker Hub.

### Imágenes publicadas

| Servicio | Imagen | Versión |
|---|---|---|
| Flask API | ashurrov/ordenes-api | v1.0 |
| Django Web | ashurrov/ordenes-web | v1.0 |
| SQL Server | mcr.microsoft.com/mssql/server | 2022-latest |

### Enlaces

**Flask API:**  
https://hub.docker.com/r/ashurrov/ordenes-api

**Django Web:**  
https://hub.docker.com/r/ashurrov/ordenes-web

### Descargar las imágenes

```powershell
docker pull ashurrov/ordenes-api:v1.0
docker pull ashurrov/ordenes-web:v1.0
```

### Publicación de imágenes

```powershell
docker login -u ashurrov
docker tag ordenes-api:v1.0 ashurrov/ordenes-api:v1.0
docker tag ordenes-web:v1.0 ashurrov/ordenes-web:v1.0
docker push ashurrov/ordenes-api:v1.0
docker push ashurrov/ordenes-web:v1.0
```

Las dos imágenes se publicaron correctamente con la etiqueta `v1.0`.

SQL Server utiliza la imagen oficial de Microsoft.

La instalación principal del proyecto construye las imágenes de Flask y Django desde sus Dockerfile.

## 18. GitHub

**Repositorio oficial:**

https://github.com/raaraudalesg-cell/ordenes-docker

El repositorio contiene el código fuente, Docker Compose, el script SQL y la documentación.

El archivo `.env.example` incluye valores de referencia.

El archivo `.env` se genera automáticamente durante la instalación y no debe publicarse.

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

### Consultar recursos

```powershell
docker stats --no-stream
```

### Reiniciar

```powershell
docker compose restart
```

### Detener sin borrar datos

```powershell
docker compose down
```

## 20. Conclusiones

El sistema RAUL demuestra la implementación de una arquitectura distribuida mediante tres contenedores Docker.

La separación entre Django, Flask y SQL Server permite organizar las responsabilidades de presentación, procesamiento y almacenamiento.

Docker Compose facilita la configuración de redes, volúmenes, dependencias y límites de recursos.

La persistencia de SQL Server permite conservar los registros después de detener y recrear los contenedores.

La API REST implementa las operaciones necesarias para administrar órdenes y productos.

Se verificó que la base de datos puede inicializarse correctamente desde una clonación nueva del repositorio.

Las imágenes de Flask y Django fueron publicadas en Docker Hub con la etiqueta `v1.0`.

La instalación documentada permite generar automáticamente las credenciales necesarias desde PowerShell sin editar manualmente archivos de configuración.

## 21. Referencias

- Docker: https://docs.docker.com/
- Docker Compose: https://docs.docker.com/compose/
- SQL Server: https://learn.microsoft.com/sql/
- Flask: https://flask.palletsprojects.com/
- Django: https://docs.djangoproject.com/
- PC Builds Honduras: https://pcbuildshonduras.com/

---

**Proyecto académico — Arquitectura de Computadoras — Segundo Parcial — 2026**
