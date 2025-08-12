# Introducción a Docker
## Fundamentos y Aplicaciones

---

## Tabla de Contenidos

1. [Fundamentos de Contenedorización](#1-fundamentos-de-contenedorización)
2. [Arquitectura Docker](#2-arquitectura-docker)
3. [Trabajando con Imágenes Docker](#3-trabajando-con-imágenes-docker)
4. [Gestión de Contenedores](#4-gestión-de-contenedores)
5. [Almacenamiento y Volúmenes](#5-almacenamiento-y-volúmenes)
6. [Networking en Docker](#6-networking-en-docker)
7. [Docker Compose](#7-docker-compose)
8. [Casos de Uso y Patrones](#8-casos-de-uso-y-patrones)
9. [Seguridad en Docker](#9-seguridad-en-docker)
10. [Troubleshooting y Debugging](#10-troubleshooting-y-debugging)

---

## 1. Fundamentos de Contenedorización

### 1.1 Evolución de las Arquitecturas

La evolución tecnológica en el desarrollo de software ha transitado por diferentes paradigmas arquitectónicos:

**Aplicaciones Monolíticas**: Una única unidad desplegable que contiene toda la funcionalidad. Ventajas: simplicidad inicial, fácil testing. Desventajas: escalabilidad limitada, tecnología única, despliegues riesgosos.

**Arquitectura de Microservicios**: Descomposición de la aplicación en servicios pequeños e independientes. Cada servicio se ejecuta en su propio proceso y se comunica mediante APIs bien definidas.

**La Necesidad de Contenedorización**: Los microservicios introdujeron nuevos desafíos:
- Gestión de dependencias complejas
- Inconsistencias entre entornos (desarrollo, testing, producción)
- Escalabilidad granular
- Despliegues independientes

### 1.2 Virtualización vs Contenedorización

**Virtualización Tradicional**:
```
Hardware Físico
└── Hypervisor
    ├── VM1 (SO Completo + App)
    ├── VM2 (SO Completo + App)
    └── VM3 (SO Completo + App)
```

**Contenedorización**:
```
Hardware Físico
└── Sistema Operativo Host
    └── Container Runtime
        ├── Container 1 (App + Libs)
        ├── Container 2 (App + Libs)
        └── Container 3 (App + Libs)
```

**Comparación Técnica**:

| Aspecto | Virtualización | Contenedorización |
|---------|----------------|-------------------|
| Overhead | Alto (SO completo) | Bajo (proceso aislado) |
| Tiempo de inicio | Minutos | Segundos |
| Densidad | Baja (GB por VM) | Alta (MB por contenedor) |
| Aislamiento | Completo | Proceso/namespace |
| Portabilidad | Media | Muy alta |

### 1.3 Conceptos Fundamentales

**Imagen Docker**: Template inmutable que contiene el código de la aplicación, runtime, bibliotecas del sistema, herramientas del sistema y configuraciones necesarias para ejecutar una aplicación.

**Contenedor**: Instancia ejecutable de una imagen. Es un proceso aislado que se ejecuta en el kernel del host pero con su propio filesystem, networking y espacio de procesos.

**Registry**: Servicio de almacenamiento y distribución de imágenes Docker. Docker Hub es el registry público más conocido.

**Dockerfile**: Archivo de texto que contiene instrucciones para construir una imagen Docker de forma automatizada.

### 1.4 Ventajas y Desventajas

**Ventajas**:

- **Portabilidad**: "Write once, run anywhere"
- **Eficiencia**: Menor overhead que VMs
- **Escalabilidad**: Escalado horizontal rápido
- **Consistencia**: Mismo entorno en desarrollo y producción
- **Aislamiento**: Dependencias encapsuladas
- **DevOps**: Facilita CI/CD

**Desventajas**:

- **Complejidad**: Curva de aprendizaje inicial
- **Seguridad**: Superficie de ataque compartida del kernel
- **Persistencia**: Manejo de datos stateful más complejo
- **Networking**: Configuración de red puede ser compleja
- **Debugging**: Más difícil debuggear aplicaciones distribuidas

---

## 2. Arquitectura Docker

### 2.1 Arquitectura Cliente-Servidor

Docker utiliza una arquitectura cliente-servidor con los siguientes componentes:

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Docker CLI    │◄──►│   Docker Daemon  │◄──►│   Docker Registry│
│   (Cliente)     │    │   (dockerd)      │    │   (Docker Hub)   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌──────────────────┐
                       │   Contenedores   │
                       │   e Imágenes     │
                       └──────────────────┘
```

### 2.2 Componentes del Ecosistema

**Docker Engine**: El runtime de contenedores que incluye:

- **dockerd**: Daemon que gestiona contenedores, imágenes, redes y volúmenes
- **containerd**: Runtime de contenedores de bajo nivel
- **runc**: Runtime OCI que efectivamente ejecuta contenedores

**Docker CLI**: Interfaz de línea de comandos que comunica con el daemon vía REST API.

**Docker API**: REST API que permite interactuar programáticamente con Docker.

### 2.3 Namespaces y Control Groups

**Namespaces**: Proporcionan aislamiento de procesos. Docker utiliza:

- **PID namespace**: Aislamiento de procesos
- **Network namespace**: Aislamiento de red (interfaces, rutas, puertos)
- **Mount namespace**: Aislamiento del filesystem
- **UTS namespace**: Aislamiento de hostname
- **User namespace**: Mapeo de usuarios
- **IPC namespace**: Aislamiento de comunicación entre procesos

**Control Groups (cgroups)**: Limitan y monitorizan el uso de recursos:
- CPU
- Memoria
- I/O de disco
- Red

**Ejemplo práctico**:
```bash
# Verificar namespaces de un contenedor
docker run -d --name test nginx
docker inspect test | grep -i pid
sudo ls -la /proc/$(docker inspect test --format '{{.State.Pid}}')/ns/
```

### 2.4 Union File Systems

Docker utiliza sistemas de archivos por capas que permiten:

- **Copy-on-Write (CoW)**: Solo se escriben las diferencias
- **Layering**: Imágenes construidas por capas incrementales
- **Sharing**: Capas compartidas entre imágenes

**Drivers de Storage comunes**:

- **overlay2**: Recomendado para la mayoría de distribuciones Linux
- **aufs**: Legacy, aún usado en algunas distribuciones
- **devicemapper**: Para sistemas con limitaciones de filesystem

---

## 3. Trabajando con Imágenes Docker

### 3.1 Anatomía de una Imagen Docker

Una imagen Docker es una colección de capas de solo lectura. Cada instrucción en un Dockerfile crea una nueva capa:

```dockerfile
FROM ubuntu:20.04          # Capa base
RUN apt-get update         # Capa 1
RUN apt-get install -y nginx  # Capa 2
COPY . /app               # Capa 3
CMD ["nginx", "-g", "daemon off;"]  # Metadata
```

### 3.2 Gestión de Imágenes

**Comandos fundamentales**:

```bash
# Listar imágenes locales
docker images
docker image ls

# Descargar imagen sin ejecutar
docker pull ubuntu:20.04

# Eliminar imágenes
docker rmi image_name
docker image rm image_name

# Información detallada de imagen
docker inspect ubuntu:20.04

# Historial de capas
docker history ubuntu:20.04

# Buscar imágenes en Docker Hub
docker search nginx
```

### 3.3 Docker Hub y Registries

**Docker Hub**: Registry público por defecto. Formato: `namespace/repository:tag`

**Registries privados**: Para organizaciones que requieren control total:

- Harbor
- AWS ECR
- Google Container Registry
- Azure Container Registry

**Comandos de registry**:
```bash
# Login en registry
docker login

# Tag para registry específico
docker tag local-image:latest myregistry.com/myimage:v1.0

# Push a registry
docker push myregistry.com/myimage:v1.0

# Pull desde registry específico
docker pull myregistry.com/myimage:v1.0
```

### 3.4 Construcción con Dockerfile

**Estructura básica de Dockerfile**:

```dockerfile
# Comentario
FROM base_image:tag
LABEL maintainer="engineer@company.com"
LABEL version="1.0"

# Variables de entorno
ENV NODE_ENV=production
ENV PORT=3000

# Directorio de trabajo
WORKDIR /app

# Instalación de dependencias del sistema
RUN apt-get update && \
    apt-get install -y curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copia de archivos
COPY package*.json ./
RUN npm install --only=production

COPY . .

# Exposición de puerto
EXPOSE 3000

# Usuario no privilegiado
USER node

# Comando por defecto
CMD ["npm", "start"]
```

**Instrucciones principales**:

- **FROM**: Imagen base
- **RUN**: Ejecuta comandos durante la construcción
- **COPY/ADD**: Copia archivos del contexto al contenedor
- **WORKDIR**: Establece directorio de trabajo
- **ENV**: Variables de entorno
- **EXPOSE**: Documenta puertos expuestos
- **USER**: Usuario para ejecutar comandos
- **CMD/ENTRYPOINT**: Comando por defecto

### 3.5 Mejores Prácticas para Dockerfiles

**Optimización de capas**:
```dockerfile
# ❌ Múltiples capas RUN
RUN apt-get update
RUN apt-get install -y curl
RUN apt-get clean

# ✅ Single RUN con limpieza
RUN apt-get update && \
    apt-get install -y curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
```

**Aprovechamiento de caché**:
```dockerfile
# ✅ Copiar dependencias primero
COPY package*.json ./
RUN npm install

# Después copiar código fuente
COPY . .
```

**Imágenes mínimas**:
```dockerfile
# Usar imágenes base pequeñas
FROM node:16-alpine

# O multi-stage builds
FROM node:16 AS builder
COPY . .
RUN npm run build

FROM node:16-alpine
COPY --from=builder /app/dist /app
```

### 3.6 Multi-stage Builds

Técnica para crear imágenes optimizadas separando la construcción de la ejecución:

```dockerfile
# Stage 1: Build
FROM node:16 AS builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# Stage 2: Production
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

**Ventajas**:

- Imágenes finales más pequeñas
- No incluye herramientas de desarrollo
- Mejor seguridad
- Separación clara de responsabilidades

---

## 4. Gestión de Contenedores

### 4.1 Ciclo de Vida de Contenedores

```
Created → Running → Paused → Stopped → Deleted
    ↑         ↓         ↑         ↓
    └─────────┴─────────┴─────────┘
```

**Estados del contenedor**:

- **Created**: Contenedor creado pero no iniciado
- **Running**: Contenedor ejecutándose
- **Paused**: Contenedor pausado (proceso suspendido)
- **Restarting**: Contenedor reiniciándose
- **Exited**: Contenedor detenido
- **Dead**: Contenedor que no pudo detenerse correctamente

### 4.2 Comandos Fundamentales

**Gestión básica**:
```bash
# Ejecutar contenedor
docker run [opciones] imagen [comando]

# Ejemplos específicos
docker run -d --name webserver -p 80:80 nginx
docker run -it ubuntu:20.04 /bin/bash
docker run --rm alpine echo "Hello World"

# Listar contenedores
docker ps                    # Solo ejecutándose
docker ps -a                # Todos los contenedores
docker ps -f status=running  # Filtrar por estado

# Controlar contenedores
docker start container_name
docker stop container_name
docker restart container_name
docker pause container_name
docker unpause container_name

# Eliminar contenedores
docker rm container_name
docker rm -f container_name  # Forzar eliminación
docker container prune      # Eliminar contenedores detenidos
```

**Opciones importantes de `docker run`**:

- `-d, --detach`: Ejecutar en background
- `-it`: Interactivo con TTY
- `--name`: Nombre del contenedor
- `-p, --publish`: Mapeo de puertos
- `-v, --volume`: Montaje de volúmenes
- `--env, -e`: Variables de entorno
- `--rm`: Eliminar automáticamente al salir
- `--restart`: Política de reinicio

### 4.3 Interacción con Contenedores

**Ejecutar comandos en contenedores**:

```bash
# Ejecutar comando en contenedor existente
docker exec -it container_name /bin/bash
docker exec container_name ls -la /app

# Verificar procesos
docker top container_name

# Estadísticas de recursos
docker stats container_name

# Logs del contenedor
docker logs container_name
docker logs -f --tail 100 container_name
```

**Inspección y debugging**:
```bash
# Información completa del contenedor
docker inspect container_name

# Cambios en el filesystem
docker diff container_name

# Copia de archivos
docker cp container_name:/path/file ./local_file
docker cp ./local_file container_name:/path/
```

### 4.4 Mapeo de Puertos

**Tipos de mapeo**:
```bash
# Puerto específico
docker run -p 8080:80 nginx

# Puerto aleatorio del host
docker run -P nginx

# IP específica
docker run -p 127.0.0.1:8080:80 nginx

# Protocolo específico
docker run -p 8080:80/tcp nginx
```

**Verificación de puertos**:
```bash
# Ver puertos mapeados
docker port container_name

# Inspeccionar configuración de red
docker inspect container_name | grep -i port
```

### 4.5 Variables de Entorno

**Configuración de aplicaciones**:
```bash
# Variable simple
docker run -e NODE_ENV=production app:latest

# Múltiples variables
docker run -e NODE_ENV=production -e PORT=3000 app:latest

# Desde archivo
docker run --env-file .env app:latest

# Ver variables de un contenedor
docker exec container_name env
```

**Archivo .env**:
```env
NODE_ENV=production
DATABASE_URL=postgresql://user:pass@db:5432/mydb
REDIS_URL=redis://redis:6379
API_KEY=secret123
```

---

## 5. Almacenamiento y Volúmenes

### 5.1 Fundamentos de Persistencia

**Problema**: Los contenedores son efímeros. Los datos se pierden al eliminar el contenedor.

**Solución**: Sistema de almacenamiento persistente que permite:
- Persistir datos más allá del ciclo de vida del contenedor
- Compartir datos entre contenedores
- Backup y restore de datos
- Performance optimizada

### 5.2 Tipos de Almacenamiento

**Bind Mounts**: Mapeo directo de directorio/archivo del host al contenedor.

```bash
# Sintaxis
docker run -v /host/path:/container/path image

# Ejemplos
docker run -v /home/user/data:/app/data nginx
docker run -v $(pwd):/app node:16 npm start

# Solo lectura
docker run -v /host/path:/container/path:ro nginx
```

**Ventajas**: Acceso directo desde el host, simple para desarrollo.
**Desventajas**: Dependiente del filesystem del host, problemas de permisos.

**Volumes**: Gestionados completamente por Docker.

```bash
# Crear volumen
docker volume create my_volume

# Listar volúmenes
docker volume ls

# Inspeccionar volumen
docker volume inspect my_volume

# Usar volumen
docker run -v my_volume:/app/data nginx

# Eliminar volumen
docker volume rm my_volume
docker volume prune  # Eliminar volúmenes no utilizados
```

**Ventajas**: Gestionados por Docker, mejor performance, funciona en todos los sistemas.
**Desventajas**: Menos accesibles desde el host.

**tmpfs Mounts**: Almacenamiento en memoria RAM.

```bash
# Usar tmpfs
docker run --tmpfs /app/temp nginx

# Con opciones específicas
docker run --tmpfs /app/temp:rw,noexec,nosuid,size=1g nginx
```

**Casos de uso**: Datos temporales, cache, información sensible.

### 5.3 Gestión Práctica de Volúmenes

**Comandos de gestión**:
```bash
# Crear volumen con driver específico
docker volume create --driver local \
  --opt type=nfs \
  --opt o=addr=192.168.1.100,rw \
  --opt device=:/path/to/dir \
  nfs_volume

# Backup de volumen
docker run --rm -v my_volume:/data -v $(pwd):/backup \
  alpine tar czf /backup/backup.tar.gz -C /data .

# Restore de volumen
docker run --rm -v my_volume:/data -v $(pwd):/backup \
  alpine tar xzf /backup/backup.tar.gz -C /data
```

**Compartir volúmenes entre contenedores**:
```bash
# Contenedor que crea datos
docker run -d --name producer -v shared_data:/app/output producer:latest

# Contenedor que consume datos
docker run -d --name consumer -v shared_data:/app/input consumer:latest
```

### 5.4 Patrones de Backup y Restore

**Backup automatizado**:
```bash
#!/bin/bash
# backup_script.sh
VOLUME_NAME=$1
BACKUP_NAME="backup_$(date +%Y%m%d_%H%M%S).tar.gz"

docker run --rm \
  -v $VOLUME_NAME:/data:ro \
  -v $(pwd):/backup \
  alpine tar czf /backup/$BACKUP_NAME -C /data .

echo "Backup created: $BACKUP_NAME"
```

**Data containers pattern** (legacy pero útil para entender):
```bash
# Crear contenedor solo para datos
docker create -v /data --name datastore alpine

# Usar desde otros contenedores
docker run --volumes-from datastore app:latest
```

### 5.5 Storage Drivers y Performance

**Drivers comunes**:
- **local**: Almacenamiento local del host
- **nfs**: Network File System
- **cifs**: Common Internet File System
- **rexray**: Para cloud storage

**Consideraciones de performance**:
```bash
# Verificar driver usado
docker system info | grep -i storage

# Configurar opciones de performance
docker volume create --driver local \
  --opt type=ext4 \
  --opt device=/dev/sdb1 \
  fast_volume
```

### 5.6 Ejercicios Prácticos

**Laboratorio 1: Persistencia básica**
```bash
# 1. Crear volumen
docker volume create lab_data

# 2. Escribir datos
docker run --rm -v lab_data:/data alpine \
  sh -c "echo 'Hello from container' > /data/message.txt"

# 3. Verificar persistencia
docker run --rm -v lab_data:/data alpine cat /data/message.txt

# 4. Usar con aplicación web
docker run -d --name web -p 8080:80 -v lab_data:/usr/share/nginx/html nginx
```

**Laboratorio 2: Desarrollo con bind mounts**
```bash
# Directorio de proyecto
mkdir my-app && cd my-app
echo "<h1>Hello Docker</h1>" > index.html

# Desarrollo con auto-reload
docker run -d --name dev-server \
  -p 8080:80 \
  -v $(pwd):/usr/share/nginx/html:ro \
  nginx

# Editar index.html y ver cambios inmediatos
```

---

## 6. Networking en Docker

### 6.1 Fundamentos de Networking

Docker proporciona aislamiento de red mediante namespaces de red. Cada contenedor tiene:

- Su propia interfaz de red
- Tabla de rutas independiente
- Stack TCP/IP completo
- Configuración de iptables aislada

### 6.2 Tipos de Redes

**Bridge Network (default)**:
```bash
# Red bridge por defecto
docker run -d --name web nginx

# Verificar configuración
docker network ls
docker network inspect bridge
```

**Características**:

- Red privada interna
- NAT para comunicación externa
- Comunicación por IP entre contenedores
- Puerto mapping necesario para acceso externo

**Host Network**:
```bash
# Usar red del host directamente
docker run --network host nginx
```

**Características**:

- Sin aislamiento de red
- Performance máxima
- Conflictos potenciales de puertos
- Útil para aplicaciones de alto rendimiento

**None Network**:
```bash
# Sin conectividad de red
docker run --network none alpine
```

**Características**:

- Máximo aislamiento
- Solo interfaz loopback
- Útil para procesamiento de datos seguros

### 6.3 Custom Networks

**Crear redes personalizadas**:
```bash
# Red bridge personalizada
docker network create my_network

# Con configuración específica
docker network create --driver bridge \
  --subnet=172.20.0.0/16 \
  --ip-range=172.20.240.0/20 \
  custom_network

# Red overlay (para swarm)
docker network create --driver overlay overlay_network
```

**Ventajas de redes personalizadas**:

- Resolución DNS automática por nombre de contenedor
- Mejor aislamiento
- Control granular de conectividad
- Configuración de red avanzada

### 6.4 Comunicación entre Contenedores

**En red personalizada**:

```bash
# Crear red
docker network create app_network

# Ejecutar contenedores en la red
docker run -d --name database --network app_network postgres
docker run -d --name webapp --network app_network \
  -e DATABASE_HOST=database webapp:latest

# Verificar conectividad
docker exec webapp ping database
```

**Múltiples redes**:
```bash
# Conectar contenedor a múltiples redes
docker network create frontend
docker network create backend

docker run -d --name app --network frontend webapp:latest
docker network connect backend app

# Verificar conexiones
docker inspect app | grep -i network
```

### 6.5 Configuración Avanzada

**Port mapping avanzado**:

```bash
# Múltiples puertos
docker run -p 80:80 -p 443:443 nginx

# Rango de puertos
docker run -p 8000-8010:8000-8010 app:latest

# IP específica
docker run -p 192.168.1.100:80:80 nginx
```

**Variables de red**:

```bash
# Configurar DNS
docker run --dns 8.8.8.8 --dns 8.8.4.4 alpine

# Hostname personalizado
docker run --hostname myserver nginx

# Archivo hosts personalizado
docker run --add-host mydb:192.168.1.100 app:latest
```

### 6.6 Troubleshooting de Conectividad

**Herramientas de diagnóstico**:

```bash
# Inspeccionar configuración de red
docker network inspect bridge

# Verificar puertos
docker port container_name
netstat -tlnp | grep docker

# Logs de conectividad
docker logs container_name

# Ejecutar herramientas de red
docker exec container_name netstat -rn
docker exec container_name nslookup google.com
docker exec container_name tcpdump -i eth0
```

**Problemas comunes**:

1. **Contenedores no se conectan**: Verificar que estén en la misma red
2. **DNS no resuelve**: Usar redes personalizadas
3. **Puerto no accesible**: Verificar port mapping y firewall
4. **Performance de red**: Considerar usar host network

**Ejemplo de aplicación multi-tier**:

```bash
# Red para la aplicación
docker network create tiered_app

# Base de datos (solo backend)
docker run -d --name db \
  --network tiered_app \
  -e POSTGRES_PASSWORD=secret \
  postgres

# API backend
docker run -d --name api \
  --network tiered_app \
  -e DATABASE_URL=postgresql://postgres:secret@db/myapp \
  api:latest

# Frontend web
docker run -d --name web \
  --network tiered_app \
  -p 80:80 \
  -e API_URL=http://api:3000 \
  frontend:latest
```

---

## 7. Docker Compose

### 7.1 Introducción a Docker Compose

Docker Compose es una herramienta para definir y ejecutar aplicaciones Docker multi-contenedor. Utiliza archivos YAML para configurar servicios, redes y volúmenes.

**Ventajas**:

- Definición declarativa de la infraestructura
- Gestión simplificada de aplicaciones complejas
- Reproducibilidad de entornos
- Integración con CI/CD
- Escalado horizontal sencillo

### 7.2 Sintaxis YAML para Compose

**Estructura básica**:

```yaml
version: '3.8'

services:
  service_name:
    # Configuración del servicio
    
networks:
  # Definición de redes personalizadas
  
volumes:
  # Definición de volúmenes
```

**Versiones de esquema**:

- **3.8**: Última versión estable (recomendada)
- **3.7, 3.6**: Versiones anteriores compatibles
- **2.x**: Legacy, no recomendado para nuevos proyectos

### 7.3 Definición de Servicios

**Ejemplo completo de aplicación web**:

```yaml
version: '3.8'

services:
  # Base de datos
  database:
    image: postgres:13
    environment:
      POSTGRES_DB: myapp
      POSTGRES_USER: appuser
      POSTGRES_PASSWORD: secret123
    volumes:
      - db_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql:ro
    networks:
      - backend
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U appuser -d myapp"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Cache Redis
  cache:
    image: redis:6-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    networks:
      - backend
    restart: unless-stopped

  # API Backend
  api:
    build:
      context: ./backend
      dockerfile: Dockerfile
      args:
        NODE_ENV: production
    environment:
      - DATABASE_URL=postgresql://appuser:secret123@database:5432/myapp
      - REDIS_URL=redis://cache:6379
      - JWT_SECRET=${JWT_SECRET}
    depends_on:
      database:
        condition: service_healthy
      cache:
        condition: service_started
    networks:
      - backend
      - frontend
    restart: unless-stopped
    deploy:
      replicas: 2
      resources:
        limits:
          memory: 512M
        reservations:
          memory: 256M

  # Frontend Web
  web:
    build:
      context: ./frontend
      dockerfile: Dockerfile
      target: production
    environment:
      - API_BASE_URL=http://api:3000
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - api
    networks:
      - frontend
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ssl_certs:/etc/ssl/certs
    restart: unless-stopped

  # Worker para tareas asíncronas
  worker:
    build:
      context: ./backend
      dockerfile: Dockerfile
    environment:
      - DATABASE_URL=postgresql://appuser:secret123@database:5432/myapp
      - REDIS_URL=redis://cache:6379
    command: ["npm", "run", "worker"]
    depends_on:
      - database
      - cache
    networks:
      - backend
    restart: unless-stopped
    deploy:
      replicas: 3

networks:
  frontend:
    driver: bridge
  backend:
    driver: bridge
    internal: true  # Sin acceso a internet

volumes:
  db_data:
    driver: local
  redis_data:
    driver: local
  ssl_certs:
    external: true  # Volumen creado externamente
```

### 7.4 Configuraciones Avanzadas

**Build contexts y argumentos**:

```yaml
services:
  app:
    build:
      context: .
      dockerfile: Dockerfile.prod
      args:
        - BUILD_VERSION=${BUILD_VERSION:-latest}
        - ENVIRONMENT=production
      target: production
      cache_from:
        - app:latest
      labels:
        - "com.example.version=${BUILD_VERSION}"
```

**Profiles para diferentes entornos**:

```yaml
services:
  app:
    image: myapp:latest
    # Configuración base
    
  debug:
    extends: app
    profiles: ["debug"]
    environment:
      - DEBUG=true
    ports:
      - "9229:9229"  # Puerto de debugging
      
  monitoring:
    image: prometheus:latest
    profiles: ["monitoring"]
    ports:
      - "9090:9090"
```

**Configuración con secretos**:

```yaml
services:
  app:
    image: myapp:latest
    secrets:
      - db_password
      - api_key
    environment:
      - DB_PASSWORD_FILE=/run/secrets/db_password

secrets:
  db_password:
    file: ./secrets/db_password.txt
  api_key:
    external: true
```

### 7.5 Variables de Entorno y Archivos .env

**Archivo .env**:

```env
# Database configuration
POSTGRES_DB=myapp
POSTGRES_USER=appuser
POSTGRES_PASSWORD=secret123

# Application configuration
NODE_ENV=production
API_PORT=3000
JWT_SECRET=your-super-secret-jwt-key

# Build arguments
BUILD_VERSION=1.2.3
```

**Uso en docker-compose.yml**:

```yaml
version: '3.8'

services:
  database:
    image: postgres:13
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    
  app:
    build:
      args:
        BUILD_VERSION: ${BUILD_VERSION}
    environment:
      - NODE_ENV=${NODE_ENV}
      - DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@database:5432/${POSTGRES_DB}
    ports:
      - "${API_PORT}:3000"
```

**Variables con valores por defecto**:

```yaml
environment:
  - NODE_ENV=${NODE_ENV:-development}
  - PORT=${PORT:-3000}
  - WORKERS=${WORKERS:-1}
```

### 7.6 Comandos de Docker Compose

**Gestión de servicios**:

```bash
# Iniciar todos los servicios
docker-compose up

# Iniciar en background
docker-compose up -d

# Iniciar servicios específicos
docker-compose up database cache

# Construir imágenes antes de iniciar
docker-compose up --build

# Forzar recreación de contenedores
docker-compose up --force-recreate

# Detener servicios
docker-compose down

# Detener y eliminar volúmenes
docker-compose down -v

# Detener y eliminar imágenes
docker-compose down --rmi all
```

**Gestión de builds**:
```bash
# Construir todas las imágenes
docker-compose build

# Construir sin cache
docker-compose build --no-cache

# Construir servicio específico
docker-compose build api

# Pull de imágenes
docker-compose pull
```

**Operaciones en servicios**:
```bash
# Listar servicios
docker-compose ps

# Logs de todos los servicios
docker-compose logs

# Logs de servicio específico
docker-compose logs api

# Seguir logs en tiempo real
docker-compose logs -f

# Ejecutar comando en servicio
docker-compose exec api bash
docker-compose exec database psql -U appuser myapp

# Escalar servicios
docker-compose up --scale worker=3

# Reiniciar servicios
docker-compose restart api
```

**Gestión de configuración**:
```bash
# Validar archivo compose
docker-compose config

# Ver configuración renderizada
docker-compose config --services

# Usar archivo compose específico
docker-compose -f docker-compose.prod.yml up

# Combinar múltiples archivos
docker-compose -f docker-compose.yml -f docker-compose.override.yml up
```

### 7.7 Patrones de Uso Avanzados

**Override files para diferentes entornos**:

**docker-compose.yml** (base):
```yaml
version: '3.8'
services:
  app:
    build: .
    environment:
      - NODE_ENV=production
```

**docker-compose.override.yml** (desarrollo local):
```yaml
version: '3.8'
services:
  app:
    environment:
      - NODE_ENV=development
      - DEBUG=true
    volumes:
      - .:/app
    ports:
      - "3000:3000"
```

**docker-compose.prod.yml** (producción):
```yaml
version: '3.8'
services:
  app:
    image: myregistry.com/myapp:${VERSION}
    deploy:
      replicas: 3
      resources:
        limits:
          memory: 512M
```

**Healthchecks y dependencias**:
```yaml
services:
  database:
    image: postgres:13
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 30s

  app:
    build: .
    depends_on:
      database:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

**Ejemplo completo: Stack MEAN**:
```yaml
version: '3.8'

services:
  # MongoDB
  mongodb:
    image: mongo:5
    environment:
      MONGO_INITDB_ROOT_USERNAME: admin
      MONGO_INITDB_ROOT_PASSWORD: password123
      MONGO_INITDB_DATABASE: meanapp
    volumes:
      - mongodb_data:/data/db
      - ./mongo-init.js:/docker-entrypoint-initdb.d/mongo-init.js:ro
    networks:
      - backend
    restart: unless-stopped

  # Express.js API
  api:
    build:
      context: ./backend
      dockerfile: Dockerfile
    environment:
      - NODE_ENV=production
      - MONGODB_URI=mongodb://admin:password123@mongodb:27017/meanapp?authSource=admin
      - JWT_SECRET=${JWT_SECRET}
      - PORT=3000
    depends_on:
      - mongodb
    networks:
      - backend
      - frontend
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Angular Frontend
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
      args:
        - API_URL=http://api:3000
    ports:
      - "80:80"
    depends_on:
      api:
        condition: service_healthy
    networks:
      - frontend
    restart: unless-stopped

  # Nginx Reverse Proxy
  nginx:
    image: nginx:alpine
    ports:
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/ssl:ro
    depends_on:
      - frontend
      - api
    networks:
      - frontend
    restart: unless-stopped

networks:
  frontend:
    driver: bridge
  backend:
    driver: bridge
    internal: true

volumes:
  mongodb_data:
    driver: local

secrets:
  jwt_secret:
    file: ./secrets/jwt.txt
```

---

## 8. Casos de Uso y Patrones

### 8.1 Desarrollo Local con Docker

**Ventajas del desarrollo con Docker**:
- Entorno consistente para todo el equipo
- Fácil onboarding de nuevos desarrolladores
- Aislamiento de dependencias
- Proximidad al entorno de producción

**Setup de desarrollo típico**:
```yaml
# docker-compose.dev.yml
version: '3.8'

services:
  app:
    build:
      context: .
      target: development
    volumes:
      - .:/app
      - /app/node_modules  # Anonymous volume para node_modules
    ports:
      - "3000:3000"
      - "9229:9229"  # Debug port
    environment:
      - NODE_ENV=development
      - DEBUG=app:*
    command: npm run dev

  database:
    image: postgres:13
    environment:
      POSTGRES_DB: myapp_dev
      POSTGRES_USER: dev
      POSTGRES_PASSWORD: dev123
    ports:
      - "5432:5432"
    volumes:
      - dev_db_data:/var/lib/postgresql/data

  redis:
    image: redis:6-alpine
    ports:
      - "6379:6379"

volumes:
  dev_db_data:
```

**Dockerfile multi-stage para desarrollo**:
```dockerfile
FROM node:16 AS base
WORKDIR /app
COPY package*.json ./

FROM base AS development
RUN npm install
COPY . .
EXPOSE 3000 9229
CMD ["npm", "run", "dev"]

FROM base AS production
RUN npm ci --only=production
COPY . .
USER node
EXPOSE 3000
CMD ["npm", "start"]
```

### 8.2 CI/CD con Docker

**Pipeline de CI/CD**:
```yaml
# .github/workflows/ci-cd.yml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Build test image
        run: docker build --target test -t myapp:test .
      
      - name: Run tests
        run: |
          docker-compose -f docker-compose.test.yml up --abort-on-container-exit
          docker-compose -f docker-compose.test.yml down
      
      - name: Run security scan
        run: |
          docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
            aquasec/trivy:latest image myapp:test

  build-and-deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
      - uses: actions/checkout@v2
      
      - name: Build production image
        run: |
          docker build --target production -t myapp:${{ github.sha }} .
          docker tag myapp:${{ github.sha }} myapp:latest
      
      - name: Push to registry
        run: |
          echo ${{ secrets.DOCKER_PASSWORD }} | docker login -u ${{ secrets.DOCKER_USERNAME }} --password-stdin
          docker push myapp:${{ github.sha }}
          docker push myapp:latest
      
      - name: Deploy to production
        run: |
          # Deployment script usando docker-compose o Kubernetes
```

**docker-compose.test.yml**:
```yaml
version: '3.8'

services:
  app:
    build:
      target: test
    environment:
      - NODE_ENV=test
      - DATABASE_URL=postgresql://test:test@testdb:5432/testdb
    depends_on:
      - testdb
    command: npm test

  testdb:
    image: postgres:13
    environment:
      POSTGRES_DB: testdb
      POSTGRES_USER: test
      POSTGRES_PASSWORD: test
    tmpfs:
      - /var/lib/postgresql/data  # Base de datos en memoria para tests
```

### 8.3 Arquitectura de Microservicios

**Principios de diseño**:
- Un servicio por contenedor
- Comunicación vía APIs REST/GraphQL
- Base de datos por servicio
- Service discovery
- Circuit breakers y retry logic

**Ejemplo de arquitectura**:
```yaml
version: '3.8'

services:
  # API Gateway
  gateway:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./gateway/nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - user-service
      - product-service
      - order-service
    networks:
      - frontend

  # User Service
  user-service:
    build: ./services/user
    environment:
      - DATABASE_URL=postgresql://users:password@user-db:5432/users
      - JWT_SECRET=${JWT_SECRET}
    depends_on:
      - user-db
    networks:
      - frontend
      - user-backend
    deploy:
      replicas: 2

  user-db:
    image: postgres:13
    environment:
      POSTGRES_DB: users
      POSTGRES_USER: users
      POSTGRES_PASSWORD: password
    volumes:
      - user_db_data:/var/lib/postgresql/data
    networks:
      - user-backend

  # Product Service
  product-service:
    build: ./services/product
    environment:
      - MONGODB_URI=mongodb://product-db:27017/products
    depends_on:
      - product-db
    networks:
      - frontend
      - product-backend
    deploy:
      replicas: 3

  product-db:
    image: mongo:5
    volumes:
      - product_db_data:/data/db
    networks:
      - product-backend

  # Order Service
  order-service:
    build: ./services/order
    environment:
      - DATABASE_URL=postgresql://orders:password@order-db:5432/orders
      - USER_SERVICE_URL=http://user-service:3000
      - PRODUCT_SERVICE_URL=http://product-service:3000
      - RABBITMQ_URL=amqp://rabbitmq:5672
    depends_on:
      - order-db
      - rabbitmq
    networks:
      - frontend
      - order-backend
      - messaging

  order-db:
    image: postgres:13
    environment:
      POSTGRES_DB: orders
      POSTGRES_USER: orders
      POSTGRES_PASSWORD: password
    volumes:
      - order_db_data:/var/lib/postgresql/data
    networks:
      - order-backend

  # Message Broker
  rabbitmq:
    image: rabbitmq:3-management
    environment:
      RABBITMQ_DEFAULT_USER: admin
      RABBITMQ_DEFAULT_PASS: password
    ports:
      - "15672:15672"  # Management UI
    networks:
      - messaging

  # Event Processor
  event-processor:
    build: ./services/events
    environment:
      - RABBITMQ_URL=amqp://rabbitmq:5672
    depends_on:
      - rabbitmq
    networks:
      - messaging
    deploy:
      replicas: 2

networks:
  frontend:
  user-backend:
    internal: true
  product-backend:
    internal: true
  order-backend:
    internal: true
  messaging:
    internal: true

volumes:
  user_db_data:
  product_db_data:
  order_db_data:
```

### 8.4 Aplicaciones Web Completas

**Stack LAMP con Docker**:
```yaml
version: '3.8'

services:
  # Apache + PHP
  web:
    build:
      context: ./docker/apache-php
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./src:/var/www/html
      - ./docker/apache-php/vhosts:/etc/apache2/sites-enabled
      - ./docker/apache-php/ssl:/etc/ssl
    environment:
      - MYSQL_HOST=mysql
      - MYSQL_DATABASE=myapp
      - MYSQL_USER=appuser
      - MYSQL_PASSWORD=secret123
    depends_on:
      mysql:
        condition: service_healthy
    networks:
      - lamp-network

  # MySQL
  mysql:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: rootpassword
      MYSQL_DATABASE: myapp
      MYSQL_USER: appuser
      MYSQL_PASSWORD: secret123
    volumes:
      - mysql_data:/var/lib/mysql
      - ./database/init:/docker-entrypoint-initdb.d
    networks:
      - lamp-network
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 10s
      timeout: 5s
      retries: 3

  # phpMyAdmin
  phpmyadmin:
    image: phpmyadmin:latest
    environment:
      PMA_HOST: mysql
      PMA_USER: root
      PMA_PASSWORD: rootpassword
    ports:
      - "8080:80"
    depends_on:
      - mysql
    networks:
      - lamp-network

networks:
  lamp-network:
    driver: bridge

volumes:
  mysql_data:
```

**Dockerfile para Apache + PHP**:
```dockerfile
FROM php:8.1-apache

# Instalar extensiones PHP necesarias
RUN docker-php-ext-install mysqli pdo pdo_mysql

# Habilitar mod_rewrite
RUN a2enmod rewrite ssl

# Instalar Composer
COPY --from=composer:latest /usr/bin/composer /usr/bin/composer

# Configurar PHP
COPY php.ini /usr/local/etc/php/

# Configurar Apache
COPY apache.conf /etc/apache2/apache2.conf

WORKDIR /var/www/html

EXPOSE 80 443
```

---

## 9. Seguridad en Docker

### 9.1 Principios de Seguridad

**Modelo de seguridad en capas**:
1. **Host Security**: Sistema operativo seguro
2. **Docker Daemon Security**: Configuración segura del daemon
3. **Image Security**: Imágenes base seguras y actualizadas
4. **Container Security**: Configuración segura de contenedores
5. **Network Security**: Aislamiento y control de red
6. **Runtime Security**: Monitoreo y detección de amenazas

**Principio de menor privilegio**: Los contenedores deben ejecutarse con los mínimos privilegios necesarios.

### 9.2 Usuarios No Privilegiados

**Problemática**: Los contenedores ejecutándose como root pueden comprometer el host.

**Solución: Usuario no privilegiado en Dockerfile**:
```dockerfile
FROM node:16-alpine

# Crear usuario no privilegiado
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nextjs -u 1001

# Configurar directorio de trabajo
WORKDIR /app

# Copiar archivos como root
COPY package*.json ./
RUN npm ci --only=production

# Cambiar ownership de archivos
COPY --chown=nextjs:nodejs . .

# Cambiar a usuario no privilegiado
USER nextjs

EXPOSE 3000
CMD ["npm", "start"]
```

**Configuración en docker-compose.yml**:
```yaml
services:
  app:
    build: .
    user: "1001:1001"  # UID:GID
    read_only: true     # Filesystem de solo lectura
    tmpfs:
      - /tmp
      - /var/cache
    cap_drop:
      - ALL
    cap_add:
      - NET_BIND_SERVICE  # Solo si necesita bindear puertos < 1024
    security_opt:
      - no-new-privileges:true
```

### 9.3 Escaneo de Vulnerabilidades

**Herramientas de escaneo**:

**Trivy** (recomendado):
```bash
# Escanear imagen
trivy image nginx:latest

# Escanear vulnerabilidades críticas y altas
trivy image --severity HIGH,CRITICAL myapp:latest

# Generar reporte JSON
trivy image --format json --output result.json myapp:latest

# Escanear filesystem
trivy fs ./project-directory
```

**Clair**:
```bash
# Con docker-compose
docker-compose -f clair-compose.yml up -d
clairctl analyze myapp:latest
```

**Snyk**:
```bash
# Escanear Dockerfile
snyk test --docker myapp:latest --file=Dockerfile

# Integración en CI/CD
snyk monitor --docker myapp:latest
```

### 9.4 Secrets Management

**❌ Malas prácticas**:
```dockerfile
# NO hacer esto
ENV API_KEY=secret123
RUN echo "password=secret" > /app/config
```

**✅ Buenas prácticas**:

**Docker Secrets (Swarm)**:
```yaml
version: '3.8'

services:
  app:
    image: myapp:latest
    secrets:
      - db_password
      - api_key
    environment:
      - DB_PASSWORD_FILE=/run/secrets/db_password

secrets:
  db_password:
    file: ./secrets/db_password.txt
  api_key:
    external: true
```

**Variables de entorno en runtime**:
```bash
# Usar archivos de secrets
docker run -v /host/secrets:/secrets:ro \
  -e DB_PASSWORD_FILE=/secrets/db_password \
  myapp:latest
```

**HashiCorp Vault integration**:
```yaml
services:
  app:
    image: myapp:latest
    environment:
      - VAULT_ADDR=http://vault:8200
      - VAULT_TOKEN_FILE=/vault/token
    volumes:
      - vault_token:/vault:ro
```

### 9.5 Configuración Segura

**Docker daemon seguro**:
```json
{
  "icc": false,
  "userland-proxy": false,
  "no-new-privileges": true,
  "seccomp-profile": "/path/to/seccomp.json",
  "apparmor-profile": "docker-default"
}
```

**Restricciones de recursos**:
```yaml
services:
  app:
    image: myapp:latest
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: '0.5'
        reservations:
          memory: 256M
    ulimits:
      nofile: 65536
      nproc: 16384
```

**Network security**:
```yaml
networks:
  frontend:
    driver: bridge
    driver_opts:
      com.docker.network.bridge.enable_icc: "false"
  backend:
    driver: bridge
    internal: true  # Sin acceso a internet
```

### 9.6 Auditoría y Compliance

**Docker Bench Security**:
```bash
# Ejecutar auditoría de seguridad
docker run --rm --net host --pid host --userns host --cap-add audit_control \
  -e DOCKER_CONTENT_TRUST=$DOCKER_CONTENT_TRUST \
  -v /var/lib:/var/lib:ro \
  -v /var/run/docker.sock:/var/run/docker.sock:ro \
  -v /usr/lib/systemd:/usr/lib/systemd:ro \
  -v /etc:/etc:ro \
  --label docker_bench_security \
  docker/docker-bench-security
```

**Content Trust**:
```bash
# Habilitar Docker Content Trust
export DOCKER_CONTENT_TRUST=1

# Solo imágenes firmadas serán ejecutadas
docker pull nginx:latest
```

---

## 10. Troubleshooting y Debugging

### 10.1 Logs y Monitoreo

**Gestión de logs**:
```bash
# Ver logs de contenedor
docker logs container_name

# Seguir logs en tiempo real
docker logs -f container_name

# Logs con timestamp
docker logs -t container_name

# Últimas N líneas
docker logs --tail 50 container_name

# Logs desde una fecha específica
docker logs --since "2023-01-01T00:00:00" container_name

# Logs hasta una fecha específica
docker logs --until "2023-01-01T12:00:00" container_name
```

**Configuración de logging drivers**:
```yaml
services:
  app:
    image: myapp:latest
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

**Logging drivers disponibles**:
- **json-file**: Por defecto, logs en archivos JSON
- **syslog**: Envío a syslog del host
- **journald**: Integración con systemd journal
- **gelf**: Graylog Extended Log Format
- **fluentd**: Para Fluentd logging
- **awslogs**: AWS CloudWatch Logs

**Stack de monitoreo completo**:
```yaml
version: '3.8'

services:
  # Aplicación principal
  app:
    image: myapp:latest
    logging:
      driver: "fluentd"
      options:
        fluentd-address: "fluentd:24224"
        tag: "app.logs"

  # Fluentd para agregación de logs
  fluentd:
    build: ./fluentd
    volumes:
      - ./fluentd/conf:/fluentd/etc
    depends_on:
      - elasticsearch

  # Elasticsearch para almacenamiento
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:7.14.0
    environment:
      - discovery.type=single-node
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
    volumes:
      - es_data:/usr/share/elasticsearch/data

  # Kibana para visualización
  kibana:
    image: docker.elastic.co/kibana/kibana:7.14.0
    ports:
      - "5601:5601"
    environment:
      ELASTICSEARCH_HOSTS: http://elasticsearch:9200
    depends_on:
      - elasticsearch

  # Prometheus para métricas
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus

  # Grafana para dashboards
  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana
    depends_on:
      - prometheus

volumes:
  es_data:
  prometheus_data:
  grafana_data:
```

### 10.2 Debugging de Contenedores

**Inspección de contenedores**:
```bash
# Información completa del contenedor
docker inspect container_name

# Estado específico
docker inspect --format='{{.State.Status}}' container_name

# Variables de entorno
docker inspect --format='{{range .Config.Env}}{{println .}}{{end}}' container_name

# Configuración de red
docker inspect --format='{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' container_name
```

**Acceso interactivo**:
```bash
# Ejecutar bash en contenedor existente
docker exec -it container_name /bin/bash

# Si bash no está disponible
docker exec -it container_name /bin/sh

# Ejecutar como root
docker exec -it --user root container_name /bin/bash

# Ejecutar con variables específicas
docker exec -it -e DEBUG=true container_name /bin/bash
```

**Debugging de imágenes**:
```bash
# Ejecutar imagen con shell override
docker run -it --entrypoint /bin/bash myapp:latest

# Ejecutar sin CMD definido
docker run -it myapp:latest /bin/sh

# Ejecutar con filesystem de solo lectura
docker run --read-only -it myapp:latest
```

### 10.3 Problemas Comunes y Soluciones

**Problema: Contenedor se detiene inmediatamente**
```bash
# Verificar logs
docker logs container_name

# Verificar exit code
docker ps -a

# Ejecutar interactivamente para debugging
docker run -it image_name /bin/bash
```

**Problema: No se puede conectar al contenedor**
```bash
# Verificar puertos mapeados
docker port container_name

# Verificar procesos escuchando
docker exec container_name netstat -tlnp

# Verificar conectividad de red
docker exec container_name ping google.com
```

**Problema: Problemas de permisos**
```bash
# Verificar usuario del proceso
docker exec container_name ps aux

# Verificar ownership de archivos
docker exec container_name ls -la /app

# Ejecutar como usuario específico
docker exec -it --user 1000:1000 container_name /bin/bash
```

**Problema: Alto uso de memoria/CPU**
```bash
# Estadísticas en tiempo real
docker stats container_name

# Límites configurados
docker inspect container_name | grep -i memory

# Procesos dentro del contenedor
docker exec container_name top
```

### 10.4 Herramientas de Debugging Avanzadas

**cAdvisor para monitoreo**:
```yaml
services:
  cadvisor:
    image: gcr.io/cadvisor/cadvisor:latest
    ports:
      - "8080:8080"
    volumes:
      - /:/rootfs:ro
      - /var/run:/var/run:ro
      - /sys:/sys:ro
      - /var/lib/docker/:/var/lib/docker:ro
    privileged: true
```

**Portainer para gestión visual**:
```yaml
services:
  portainer:
    image: portainer/portainer-ce:latest
    ports:
      - "9000:9000"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - portainer_data:/data
```

**Debugging de red**:
```bash
# Crear contenedor para debugging de red
docker run -it --rm --net container:target_container nicolaka/netshoot

# Capturar tráfico de red
docker exec container_name tcpdump -i eth0

# Verificar rutas
docker exec container_name ip route show

# DNS lookup
docker exec container_name nslookup google.com
```

**Performance profiling**:
```bash
# Analizar uso de disco
docker exec container_name du -sh /*

# Verificar file descriptors abiertos
docker exec container_name lsof

# Memory mapping
docker exec container_name cat /proc/meminfo

# Procesos y threads
docker exec container_name ps -eLf
```

### 10.5 Optimización de Performance

**Optimización de imágenes**:
```dockerfile
# Multi-stage build para reducir tamaño
FROM node:16 AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

FROM node:16-alpine
RUN addgroup -g 1001 -S nodejs && adduser -S nextjs -u 1001
COPY --from=builder --chown=nextjs:nodejs /app/node_modules ./node_modules
COPY --chown=nextjs:nodejs . .
USER nextjs
```

**Optimización de contenedores**:
```yaml
services:
  app:
    image: myapp:latest
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: '1.0'
        reservations:
          memory: 256M
          cpus: '0.5'
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

**Cache de builds**:
```bash
# Usar BuildKit para mejor caching
export DOCKER_BUILDKIT=1

# Build con cache específico
docker build --cache-from myapp:latest -t myapp:new .

# Registry cache
docker build --cache-from myregistry.com/myapp:cache -t myapp:new .
```

---

## Conclusiones

### Resumen de Conceptos Clave

Docker ha revolucionado el desarrollo y despliegue de aplicaciones mediante la contenedorización, proporcionando:

**Beneficios Fundamentales**:
- **Portabilidad**: Aplicaciones que ejecutan consistentemente en cualquier entorno
- **Eficiencia**: Menor overhead comparado con virtualización tradicional
- **Escalabilidad**: Facilitación del escalado horizontal y microservicios
- **DevOps**: Integración seamless en pipelines CI/CD
- **Aislamiento**: Encapsulación de dependencias y configuraciones

### Arquitectura y Componentes

La arquitectura cliente-servidor de Docker, basada en:
- **Namespaces** para aislamiento de procesos
- **Control Groups** para limitación de recursos
- **Union File Systems** para eficiencia de almacenamiento
- **Container Runtime** para ejecución de contenedores

### Mejores Prácticas Aprendidas

**Seguridad**:
- Ejecutar contenedores con usuarios no privilegiados
- Escanear vulnerabilidades regularmente
- Gestionar secrets de forma segura
- Aplicar principio de menor privilegio

**Performance**:
- Usar multi-stage builds para imágenes optimizadas
- Implementar healthchecks apropiados
- Configurar límites de recursos
- Optimizar layers en Dockerfiles

**Operaciones**:
- Implementar logging y monitoreo centralizados
- Usar Docker Compose para orquestación local
- Planificar estrategias de backup para volúmenes
- Configurar redes personalizadas para mejor aislamiento

### Casos de Uso Industriales

Docker se ha establecido como estándar en:

**Desarrollo Local**: Entornos consistentes para equipos de desarrollo
**CI/CD**: Pipelines automatizados y confiables
**Microservicios**: Arquitecturas distribuidas y escalables
**Cloud Computing**: Base para orchestrators como Kubernetes

### Evolución y Futuro

La contenedorización ha evolucionado hacia:
- **Kubernetes**: Orquestación a gran escala
- **Serverless**: Functions as a Service
- **Edge Computing**: Contenedores en el borde de la red
- **WebAssembly**: Nueva frontera de la contenedización

### Recomendaciones para Estudiantes de Ingeniería

**Fundamentos Sólidos**:
1. Dominar conceptos de sistemas operativos (procesos, memoria, I/O)
2. Entender networking y protocolos de comunicación
3. Conocer principios de arquitectura de software
4. Practicar con herramientas de línea de comandos

**Práctica Progresiva**:
1. Comenzar con contenedores simples
2. Avanzar a aplicaciones multi-contenedor
3. Experimentar con diferentes stacks tecnológicos
4. Implementar pipelines CI/CD completos

**Recursos Continuos**:
- Documentación oficial de Docker
- Comunidades de práctica (Docker Community, Stack Overflow)
- Proyectos open source para contribuir
- Certificaciones profesionales (Docker Certified Associate)

### Consideraciones Finales

Docker representa un cambio paradigmático en cómo desarrollamos, distribuimos y ejecutamos aplicaciones. Para ingenieros, dominar esta tecnología es esencial en el ecosistema de desarrollo moderno.

La contenedorización no es solo una herramienta técnica, sino una metodología que habilita:
- Mejores prácticas de desarrollo
- Colaboración efectiva en equipos
- Despliegues más confiables
- Arquitecturas más resilientes

El futuro del desarrollo de software está intrínsecamente ligado a tecnologías de contenedorización, y Docker continúa siendo la puerta de entrada fundamental para entender este ecosistema.

---

## Referencias y Recursos Adicionales

### Documentación Oficial
- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Docker Hub](https://hub.docker.com/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)

### Herramientas y Utilidades
- [Trivy - Vulnerability Scanner](https://github.com/aquasecurity/trivy)
- [Hadolint - Dockerfile Linter](https://github.com/hadolint/hadolint)
- [Dive - Image Layer Explorer](https://github.com/wagoodman/dive)
- [Docker Bench Security](https://github.com/docker/docker-bench-security)

### Recursos de Aprendizaje
- [Play with Docker](https://labs.play-with-docker.com/)
- [Docker Training](https://training.docker.com/)
- [Katacoda Docker Scenarios](https://katacoda.com/docker)

### Libros Recomendados
- "Docker: Up & Running" by Karl Matthias
- "Docker in Action" by Jeff Nickoloff
- "Docker Deep Dive" by Nigel Poulton

### Comunidades
- [Docker Community Slack](https://dockercommunity.slack.com/)
- [Docker Subreddit](https://reddit.com/r/docker)
- [Docker Community Forums](https://forums.docker.com/)

---

*Este documento ha sido desarrollado como material educativo para estudiantes de Ingeniería en Informática. Su objetivo es proporcionar una comprensión integral de Docker desde fundamentos teóricos hasta implementaciones prácticas en entornos profesionales.*

**Autor**: Gabriel Quintero - Computación II  
**Versión**: 1.0  
**Fecha**: 2025  
**Licencia**: Uso Educativo