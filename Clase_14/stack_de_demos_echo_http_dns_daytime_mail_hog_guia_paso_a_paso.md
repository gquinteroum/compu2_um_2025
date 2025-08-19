# Stack de Demos: Echo HTTP + Daytime + MailHog + Cliente DNS + Netcat — Guía paso a paso

Esta guía te permite levantar, probar y **explicar en clase** varios servicios con Docker Compose, además de usar `netcat` como cliente y servidor para experimentar con TCP/UDP:

* **Echo HTTP** (ver la petición cruda que envía el cliente)
* **Daytime** (servicio simple que devuelve la hora en texto)
* **MailHog (SMTP)** (capturar correos de prueba y verlos en una UI web)
* **Cliente DNS con `dig`** (consultar registros en servidores públicos)
* **Cliente/Servidor TCP con `nc/netcat`** (herramienta versátil de red)

Incluye **comandos de cliente** con explicación de cada herramienta.

---

## 0) Requisitos

* Docker y Docker Compose instalados.
* Clientes sugeridos:

  * `telnet` → probar **HTTP** y **Daytime** (texto en TCP).
  * `dig` (paquete `dnsutils` o `bind-tools`) → probar **DNS**.
  * `nc`/`netcat` → herramienta de red genérica (cliente y servidor).

> **¿Qué es cada cliente?**
>
> * **telnet**: abre una conexión TCP interactiva a un puerto; ideal para ver/probar protocolos en texto.
> * **dig**: realiza consultas DNS (registros A/AAAA/MX, etc.) y muestra la respuesta del servidor.
> * **nc/netcat**: es la “navaja suiza” de redes: permite conectarse a puertos (cliente), escuchar como servidor TCP/UDP, transferir archivos, depurar tráfico.

---

## 1) Levantar el stack

En el archivo `docker-compose.yml` ya están definidos los servicios. Para levantar:

```bash
docker compose up -d
```

Para ver el estado:

```bash
docker compose ps
```

Para apagar y limpiar:

```bash
docker compose down
```

---

## 2) Echo HTTP — Demostración del protocolo HTTP

**Objetivo:** mostrar cómo luce una petición HTTP cruda y qué devuelve el servidor.

**URL:** [http://localhost:8080](http://localhost:8080)

**Prueba con telnet**

```text
telnet localhost 8080
GET / HTTP/1.1
Host: localhost

```

👉 Dejá **una línea en blanco** al final.

**Prueba con netcat (cliente)**

```bash
echo -e "GET / HTTP/1.1\r\nHost: localhost\r\n\r\n" | nc localhost 8080
```

👉 Hace la misma petición en una sola línea.

---

## 3) Daytime — Hora local por TCP en texto

**Puerto:** `1313`

**Prueba con telnet**

```text
telnet localhost 1313
```

**Prueba con netcat (cliente)**

```bash
nc localhost 1313
```

👉 Con cada conexión recibirás la hora actual.

---

## 4) MailHog (SMTP) — Enviar y visualizar correos de prueba

* **SMTP:** `localhost:1025`
* **Web UI:** [http://localhost:8025](http://localhost:8025)

**Prueba SMTP con telnet**

```text
telnet localhost 1025
EHLO clase.local
MAIL FROM:<profesor@clase.local>
RCPT TO:<alumno@clase.local>
DATA
Hola con telnet!
.
QUIT
```

**Prueba SMTP con netcat (cliente)**

```bash
echo -e "EHLO clase.local\r\nMAIL FROM:<profesor@clase.local>\r\nRCPT TO:<alumno@clase.local>\r\nDATA\r\nHola con nc!\r\n.\r\nQUIT\r\n" | nc localhost 1025
```

---

## 5) Cliente DNS — Consultas con `dig`

**Ejemplos:**

```bash
# IPv4
dig @8.8.8.8 google.com A

# IPv6
dig @1.1.1.1 openai.com AAAA +short

# MX
dig @8.8.8.8 gmail.com MX +short

# NS
dig @1.1.1.1 mendoza.gov.ar NS +short

# TXT
dig @8.8.8.8 openai.com TXT +short
```

---

## 6) Netcat (nc) — Cliente y Servidor

`nc` no solo sirve como cliente. También puede actuar como servidor TCP o UDP.

### Cliente TCP simple

```bash
nc google.com 80
```

👉 Abre una conexión TCP al puerto 80 de `google.com`. Podés escribir manualmente un `GET /`.

### Servidor TCP local

```bash
nc -l -p 4444
```

👉 Abre un servidor en el puerto 4444. Cualquier cliente que se conecte podrá enviar/recibir datos.

Ejemplo: en otra terminal:

```bash
echo "Hola desde cliente" | nc localhost 4444
```

### Cliente UDP

```bash
echo "Ping UDP" | nc -u 127.0.0.1 9999
```

👉 Envía un paquete UDP al puerto 9999.

### Chat sencillo con nc

En una terminal (servidor):

```bash
nc -l -p 5000
```

En otra (cliente):

```bash
nc localhost 5000
```

👉 Ahora lo que escribas en un lado aparecerá en el otro.

---

## 7) Tips y resolución de problemas

* **Puertos ocupados**: cambiá los mapeos en el compose.
* **`telnet`/`nc` no conectan**: verificá firewall y que el contenedor esté levantado.
* **Zona horaria en Daytime**: ajustá `TZ` en el compose.
* **DNS público no responde**: probá con otro (`8.8.8.8`, `1.1.1.1`).

---

## 8) Limpieza

```bash
docker compose down
```

---

### Fin

Con este stack podés mostrar **HTTP, un TCP de texto simple, SMTP**, usar `dig` contra servidores DNS reales y experimentar con `nc/netcat` tanto como **cliente** como **servidor**. Esto ofrece ejemplos prácticos y flexibles para enseñar protocolos y redes.
