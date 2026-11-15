
## 17. Docker Hub

Las imágenes Docker de Flask y Django fueron construidas y publicadas en Docker Hub.

### Imágenes publicadas

| Servicio | Imagen | Versión |
|---|---|---|
| Flask API | `ashurrov/ordenes-api` | `v1.0` |
| Django Web | `ashurrov/ordenes-web` | `v1.0` |
| SQL Server | `mcr.microsoft.com/mssql/server` | `2022-latest` |

### Enlaces de Docker Hub

**Flask API:**

https://hub.docker.com/r/ashurrov/ordenes-api

**Django Web:**

https://hub.docker.com/r/ashurrov/ordenes-web

### Descargar las imágenes

```powershell
docker pull ashurrov/ordenes-api:v1.0
docker pull ashurrov/ordenes-web:v1.0
```

### Construcción de imágenes locales

```powershell
docker compose build
```

### Publicación en Docker Hub

```powershell
docker login -u ashurrov
docker tag ordenes-api:v1.0 ashurrov/ordenes-api:v1.0
docker tag ordenes-web:v1.0 ashurrov/ordenes-web:v1.0
docker push ashurrov/ordenes-api:v1.0
docker push ashurrov/ordenes-web:v1.0
```

### Verificación

Las dos imágenes fueron publicadas correctamente en Docker Hub con la etiqueta `v1.0`.

SQL Server utiliza la imagen oficial de Microsoft, por lo que no es necesario publicarla nuevamente.
