
# Sistema de Órdenes de Venta con Docker Compose

## 1. Descripción del proyecto

Este proyecto implementa un sistema de gestión de órdenes de venta mediante una arquitectura de tres contenedores Docker.

El sistema está compuesto por:

- **SQL Server 2022:** almacenamiento de los datos.
- **Flask:** API REST para consultar y administrar información.
- **Django:** interfaz web para visualizar las órdenes.

Los servicios se ejecutan mediante Docker Compose, con configuración de recursos, redes, persistencia y comprobaciones de salud.

## 2. Objetivo general

Desarrollar e implementar una aplicación distribuida utilizando Docker Compose para integrar una base de datos SQL Server, una API REST con Flask y una aplicación web con Django.

## 3. Objetivos específicos

- Crear una arquitectura de tres contenedores.
- Configurar la comunicación entre los servicios.
- Implementar una base de datos de órdenes de venta.
- Desarrollar una API REST con Flask.
- Construir una interfaz web con Django.
- Establecer límites de recursos para los contenedores.
- Configurar comprobaciones de salud.
- Implementar persistencia mediante volúmenes.
- Publicar el código fuente en GitHub.
- Facilitar una instalación reproducible desde un repositorio remoto.

## 4. Tecnologías utilizadas

| Tecnología | Función |
|---|---|
| Docker | Ejecución de contenedores |
| Docker Compose | Orquestación de servicios |
| SQL Server 2022 | Base de datos relacional |
| Python | Lenguaje de programación |
| Flask | API REST |
| Django | Interfaz web |
| Git | Control de versiones |
| GitHub | Repositorio remoto |
| Docker Hub | Publicación de imágenes |
| PowerShell | Automatización de instalación |

## 5. Arquitectura del sistema

La aplicación utiliza tres servicios:

```text
                   USUARIO
                      |
                      v
              +---------------+
              | DJANGO WEB    |
              | Puerto 8000   |
              +---------------+
                      |
                      v
              +---------------+
              | FLASK API     |
              | Puerto 5000   |
              +---------------+
                      |
                      v
              +---------------+
              | SQL SERVER    |
              | Puerto 1433   |
              +---------------+
                      |
                      v
              VOLUMEN PERSISTENTE
```

La comunicación entre contenedores se realiza mediante la red definida en Docker Compose.

## 6. Estructura del proyecto

```text
ordenes-docker/
|
|-- api/
|   |-- Dockerfile
|   |-- requirements.txt
|   |-- ...
|
|-- web/
|   |-- Dockerfile
|   |-- requirements.txt
|   |-- ...
|
|-- db/
|   |-- init.sql
|
|-- compose.yaml
|-- .env.example
|-- README.md
```

## 7. Requisitos previos

Para ejecutar el proyecto se necesita:

- Windows 10 o Windows 11.
- Docker Desktop instalado.
- Docker Desktop iniciado.
- Git instalado.
- PowerShell.
- Conexión a Internet durante la descarga y construcción inicial.

Se recomienda disponer de al menos 8 GB de memoria RAM.

Verificar Docker:

```powershell
docker --version
```

Verificar Docker Compose:

```powershell
docker compose version
```

Verificar Git:

```powershell
git --version
```

## 8. Instalación automatizada desde GitHub

Esta sección permite descargar y ejecutar el proyecto sin editar manualmente el archivo `.env`.

Los comandos están preparados para PowerShell.

### 8.1. Descargar el repositorio

Abrir PowerShell y ejecutar:

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

Este comando genera:

- Una contraseña para SQL Server.
- Una clave secreta para Django.
- El archivo `.env` necesario para Docker Compose.

No es necesario editar el archivo manualmente.

### 8.3. Validar la configuración

```powershell
docker compose config --quiet
```

Si no aparecen errores, la configuración es válida.

### 8.4. Resolver conflictos de contenedores anteriores

Si anteriormente se ejecutó otra copia del proyecto, podrían existir contenedores con los mismos nombres.

Para comprobarlos:

```powershell
docker ps -a --filter "name=ordenes-"
```

Si se trata de contenedores de pruebas anteriores que ya no se necesitan, se pueden eliminar mediante:

```powershell
$contenedores = @("ordenes-db", "ordenes-api", "ordenes-web")
foreach ($nombre in $contenedores) {
    $existe = docker ps -aq --filter "name=^${nombre}$"
    if ($existe) {
        docker rm -f $nombre
    }
}
```

Este procedimiento elimina los contenedores indicados, pero conserva los volúmenes Docker.

**Advertencia:** los comandos anteriores detienen y eliminan cualquier contenedor que tenga exactamente esos nombres, incluso si pertenece a otro proyecto. Deben ejecutarse únicamente cuando esos contenedores ya no sean necesarios.

### 8.5. Iniciar SQL Server

```powershell
docker compose up -d db
```

### 8.6. Esperar a que SQL Server esté saludable

```powershell
while ((docker inspect ordenes-db --format '{{.State.Health.Status}}') -eq 'starting') { Start-Sleep -Seconds 5 }
docker compose ps
```

El servicio debe mostrar:

```text
ordenes-db   Up (healthy)
```

Si aparece `unhealthy`, revisar los registros:

```powershell
docker logs ordenes-db --tail 50
```

### 8.7. Crear la base de datos y cargar los datos iniciales

Cuando SQL Server esté saludable, ejecutar:

```powershell
Get-Content .\db\init.sql -Raw | docker exec -i ordenes-db /opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P ((Get-Content .\.env | Where-Object { $_ -match '^MSSQL_SA_PASSWORD=' } | Select-Object -First 1) -replace '^MSSQL_SA_PASSWORD=', '') -C -b
```

Este comando ejecuta el script `db/init.sql` utilizando la contraseña generada automáticamente.

### 8.8. Construir e iniciar todos los servicios

```powershell
docker compose up -d --build
```

### 8.9. Verificar el estado de los contenedores

```powershell
docker compose ps
```

Se espera encontrar los servicios:

```text
ordenes-db
ordenes-api
ordenes-web
```

Los tres deben estar ejecutándose correctamente.

### 8.10. Abrir la aplicación

```powershell
Start-Process http://localhost:8000
```

La aplicación web de Django debe abrirse en el navegador.

## 9. Direcciones de acceso

| Servicio | Dirección |
|---|---|
| Django | http://localhost:8000 |
| Flask | http://localhost:5000 |
| SQL Server | localhost:1433 |

Los servicios se comunican internamente a través de la red Docker.

## 10. Base de datos

La base de datos utiliza Microsoft SQL Server 2022.

Su nombre es:

```text
OrdenesDB
```

El archivo de inicialización se encuentra en:

```text
db/init.sql
```

El script contiene la estructura necesaria para almacenar órdenes de venta y sus detalles.

La información se conserva mediante un volumen Docker, incluso cuando se eliminan los contenedores sin eliminar sus volúmenes.

## 11. Datos iniciales

La base de datos incluye información de prueba.

En las pruebas realizadas con el script SQL se obtuvieron:

| Indicador | Resultado |
|---|---:|
| Órdenes registradas | 6 |
| Detalles registrados | 12 |
| Monto total | L 130,800.00 |

Los datos permiten comprobar el funcionamiento de la base de datos, la API y la aplicación web.

## 12. API REST con Flask

Flask proporciona la capa de acceso a los datos.

Su función principal es recibir solicitudes HTTP, consultar SQL Server y devolver respuestas que pueden ser utilizadas por Django.

Dirección base:

```text
http://localhost:5000
```

Para consultar los registros del contenedor:

```powershell
docker compose logs api --tail 50
```

Para comprobar su estado:

```powershell
docker compose ps api
```

Las rutas disponibles dependen de la implementación incluida en la carpeta `api`.

## 13. Aplicación web con Django

Django proporciona la interfaz visual del sistema.

La aplicación permite consultar la información de órdenes de venta a través de la API Flask.

Dirección:

```text
http://localhost:8000
```

Abrir desde PowerShell:

```powershell
Start-Process http://localhost:8000
```

Consultar registros:

```powershell
docker compose logs web --tail 50
```

## 14. Docker Compose

El archivo principal de orquestación es:

```text
compose.yaml
```

Docker Compose permite:

- Definir los tres servicios.
- Construir las imágenes de Flask y Django.
- Configurar puertos.
- Establecer variables de entorno.
- Crear una red para la comunicación.
- Administrar la persistencia de SQL Server.
- Aplicar límites de recursos.
- Comprobar el estado de salud de los servicios.

Para revisar la configuración:

```powershell
docker compose config
```

Para validar sin mostrar toda la configuración:

```powershell
docker compose config --quiet
```

Para consultar los servicios:

```powershell
docker compose ps
```

## 15. Pruebas de funcionamiento

### 15.1. Verificar los contenedores

```powershell
docker compose ps
```

### 15.2. Consultar la salud de SQL Server

```powershell
docker inspect ordenes-db --format '{{.State.Health.Status}}'
```

Resultado esperado:

```text
healthy
```

### 15.3. Consultar la salud de Flask

```powershell
docker inspect ordenes-api --format '{{.State.Health.Status}}'
```

### 15.4. Consultar la salud de Django

```powershell
docker inspect ordenes-web --format '{{.State.Health.Status}}'
```

Si los servicios tienen comprobaciones de salud configuradas, el resultado esperado es:

```text
healthy
```

### 15.5. Verificar los recursos

```powershell
docker stats --no-stream
```

Este comando permite consultar:

- Consumo de CPU.
- Consumo de memoria.
- Tráfico de red.
- Actividad de entrada y salida.

### 15.6. Revisar los registros

SQL Server:

```powershell
docker compose logs db --tail 50
```

Flask:

```powershell
docker compose logs api --tail 50
```

Django:

```powershell
docker compose logs web --tail 50
```

### 15.7. Verificar la interfaz web

```powershell
Start-Process http://localhost:8000
```

### 15.8. Verificar la persistencia

Detener los servicios:

```powershell
docker compose down
```

Iniciarlos nuevamente:

```powershell
docker compose up -d
```

Comprobar el estado:

```powershell
docker compose ps
```

El volumen de SQL Server conserva los datos mientras no se elimine explícitamente.

## 16. Evidencias recomendadas

Para documentar el funcionamiento del proyecto se recomienda incluir capturas de:

1. Los tres contenedores ejecutándose.
2. El resultado de `docker compose ps`.
3. Los estados de salud de los servicios.
4. La interfaz Django funcionando.
5. Las respuestas de la API Flask.
6. Las tablas y registros de SQL Server.
7. El consumo de recursos mediante `docker stats`.
8. El repositorio publicado en GitHub.
9. Las imágenes publicadas en Docker Hub.

## 17. Imágenes en Docker Hub

Las imágenes publicadas del proyecto son:

**API Flask:**

https://hub.docker.com/r/ashurrov/ordenes-api

**Aplicación Django:**

https://hub.docker.com/r/ashurrov/ordenes-web

Para consultar las imágenes locales:

```powershell
docker images
```

Para descargar las imágenes publicadas:

```powershell
docker pull ashurrov/ordenes-api:v1.0
docker pull ashurrov/ordenes-web:v1.0
```

Las imágenes también pueden construirse localmente desde el código fuente:

```powershell
docker compose build
```

## 18. Repositorio de GitHub

El código fuente del proyecto está disponible en:

https://github.com/raaraudalesg-cell/ordenes-docker

Para descargarlo:

```powershell
git clone https://github.com/raaraudalesg-cell/ordenes-docker.git
```

Para comprobar el estado del repositorio local:

```powershell
git status
```

Para consultar los últimos cambios:

```powershell
git log --oneline -5
```

## 19. Comandos útiles

### Iniciar los servicios

```powershell
docker compose up -d
```

### Construir y ejecutar

```powershell
docker compose up -d --build
```

### Consultar el estado

```powershell
docker compose ps
```

### Consultar todos los registros

```powershell
docker compose logs --tail 100
```

### Reiniciar los servicios

```powershell
docker compose restart
```

### Detener y eliminar los contenedores del proyecto

```powershell
docker compose down
```

### Consultar los volúmenes

```powershell
docker volume ls
```

### Consultar las redes

```powershell
docker network ls
```

### Consultar el consumo de recursos

```powershell
docker stats --no-stream
```

**Nota:** no se recomienda ejecutar `docker compose down -v` durante las pruebas de persistencia, ya que la opción `-v` elimina los volúmenes asociados al proyecto.

## 20. Solución de problemas

### Error: nombre de contenedor en uso

Si aparece un mensaje similar a:

```text
Conflict. The container name "/ordenes-db" is already in use
```

Significa que ya existe un contenedor con ese nombre.

Identificarlo:

```powershell
docker ps -a --filter "name=ordenes-db"
```

Si se confirma que es un contenedor anterior que ya no se necesita:

```powershell
docker rm -f ordenes-db
```

Luego iniciar nuevamente:

```powershell
docker compose up -d db
```

Este procedimiento no elimina el volumen de SQL Server.

### Error: SQL Server todavía está iniciando

Comprobar:

```powershell
docker compose ps
```

Esperar:

```powershell
while ((docker inspect ordenes-db --format '{{.State.Health.Status}}') -eq 'starting') { Start-Sleep -Seconds 5 }
```

### Error: contraseña incorrecta de SQL Server

Si aparece:

```text
Login failed for user 'sa'
```

Comprobar que el archivo `.env` corresponda al contenedor SQL Server del proyecto actual.

Una contraseña nueva en `.env` no cambia automáticamente la contraseña de una base de datos SQL Server previamente inicializada.

### Error: puerto ocupado

Comprobar los contenedores activos:

```powershell
docker ps
```

Verificar que los puertos `1433`, `5000` y `8000` no estén ocupados por otros servicios.

### Error: Docker Desktop no está iniciado

Comprobar:

```powershell
docker info
```

Si Docker no responde, iniciar Docker Desktop y volver a ejecutar el comando.

## 21. Conclusiones

El proyecto demuestra cómo Docker Compose permite implementar una arquitectura distribuida formada por tres servicios independientes.

SQL Server proporciona persistencia de datos, Flask implementa la API REST y Django ofrece la interfaz web.

La configuración permite administrar los contenedores desde un único archivo, comprobar su estado y supervisar el consumo de recursos.

La publicación del código en GitHub y de las imágenes en Docker Hub facilita la distribución y reproducción del proyecto.

## 22. Referencias

- Docker: https://docs.docker.com/
- Docker Compose: https://docs.docker.com/compose/
- SQL Server: https://learn.microsoft.com/sql/
- Flask: https://flask.palletsprojects.com/
- Django: https://docs.djangoproject.com/
- GitHub: https://github.com/
- Docker Hub: https://hub.docker.com/
