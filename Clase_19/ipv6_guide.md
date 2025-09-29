# Guía Completa de IPv6 en Python

## 1. Historia y Evolución del Protocolo de Internet

### 1.1 Los Orígenes: ARPANET y el Nacimiento de IPv4

La historia de Internet comienza en 1969 con ARPANET, una red experimental desarrollada por la Agencia de Proyectos de Investigación Avanzada de Defensa (DARPA) del Departamento de Defensa de Estados Unidos. En sus inicios, ARPANET conectaba solo cuatro nodos: UCLA, Stanford, UC Santa Barbara y la Universidad de Utah.

El protocolo original, llamado **NCP (Network Control Protocol)**, resultó insuficiente a medida que la red crecía. En 1974, Vinton Cerf y Robert Kahn publicaron un artículo histórico titulado "A Protocol for Packet Network Intercommunication", que describía el TCP (Transmission Control Protocol). Este trabajo sentó las bases para lo que eventualmente se convertiría en el conjunto de protocolos TCP/IP.

**IPv4 fue estandarizado en septiembre de 1981** a través del RFC 791, escrito por Jon Postel. En ese momento, con solo unos cientos de computadoras conectadas, nadie imaginó que las 4.3 mil millones de direcciones disponibles pudieran ser insuficientes.

### 1.2 La Crisis de Agotamiento de IPv4

A principios de los años 90, los ingenieros de red comenzaron a notar un problema preocupante: el crecimiento exponencial de Internet estaba consumiendo direcciones IPv4 a un ritmo alarmante.

**Factores que aceleraron el agotamiento:**

1. **Explosión de Internet comercial (1990s)**: La World Wide Web popularizó Internet más allá de las universidades y centros de investigación.

2. **Asignación ineficiente temprana**: En los primeros días, bloques enormes de direcciones fueron asignados a organizaciones que no las necesitaban todas. Por ejemplo, MIT recibió un bloque /8 completo (16.7 millones de direcciones), al igual que empresas como IBM, Ford y HP.

3. **Dispositivos móviles**: La llegada de smartphones, tablets y dispositivos IoT multiplicó exponencialmente el número de dispositivos que necesitaban conectividad.

4. **El problema de clase**: El sistema de clases (A, B, C) de IPv4 llevaba a un desperdicio masivo. Una empresa que necesitara 300 direcciones debía recibir un bloque clase B (65,536 direcciones), desperdiciando el 99.5% del espacio.

**Medidas temporales adoptadas:**

- **NAT (Network Address Translation)**: Permite que múltiples dispositivos compartan una única dirección IP pública. Aunque efectivo, NAT complica las comunicaciones peer-to-peer y viola el principio de extremo a extremo de Internet.

- **CIDR (Classless Inter-Domain Routing)**: Introducido en 1993, permitió una asignación más granular de direcciones, pero solo retrasó lo inevitable.

- **Recuperación de direcciones**: IANA comenzó a recuperar bloques no utilizados, pero esto tuvo un impacto limitado.

**La fecha del agotamiento:**
- IANA agotó su pool global el 3 de febrero de 2011
- Los Registros Regionales de Internet (RIRs) comenzaron a agotar sus reservas entre 2011 y 2020
- RIPE NCC (Europa) entró en su última fase de asignación en 2019

### 1.3 El Nacimiento de IPv6

El desarrollo de IPv6 comenzó en 1994, cuando el IETF (Internet Engineering Task Force) formó un grupo de trabajo específico llamado IPng (IP next generation). El objetivo era diseñar un sucesor para IPv4 que resolviera no solo el problema del agotamiento de direcciones, sino también otras limitaciones del protocolo original.

**Propuestas competidoras:**

Varias propuestas fueron presentadas al IETF:

1. **TUBA (TCP/UDP over Bigger Addresses)**: Basada en CLNP de OSI
2. **CATNIP (Common Architecture for the Internet)**: Un híbrido de múltiples protocolos
3. **SIPP (Simple Internet Protocol Plus)**: La propuesta que eventualmente ganó

SIPP, desarrollada por Steve Deering y Robert Hinden, fue seleccionada como la base para IPv6 debido a su equilibrio entre simplicidad y funcionalidad avanzada.

**Hitos importantes:**

- **1995**: Se publica el RFC 1883, la primera especificación de IPv6
- **1998**: El RFC 2460 reemplaza al RFC 1883 como la especificación estándar
- **1999**: Comienza el proyecto 6bone, una red experimental IPv6
- **2008**: IANA comienza a requerir soporte IPv6 para nuevas asignaciones de direcciones
- **2012**: Google, Facebook, Yahoo y otros gigantes tecnológicos activan IPv6 permanentemente en el "World IPv6 Launch"
- **2017**: El RFC 8200 actualiza y reemplaza al RFC 2460

### 1.4 ¿Por qué IPv6 y no IPv5?

Una pregunta común es: ¿qué pasó con IPv5? La respuesta es que IPv5 fue un protocolo experimental llamado **ST (Internet Stream Protocol)**, diseñado para transmisión de voz y video en tiempo real. Usaba el número de versión 5 en el encabezado IP, por lo que cuando llegó el momento de nombrar el sucesor de IPv4, se eligió IPv6 para evitar confusiones.

---

## 2. Arquitectura y Teoría de IPv6

### 2.1 Estructura de las Direcciones IPv6

IPv6 utiliza direcciones de **128 bits**, comparado con los 32 bits de IPv4. Esto proporciona aproximadamente **340 undecillones** de direcciones (340,282,366,920,938,463,463,374,607,431,768,211,456 para ser exactos).

#### Representación de Direcciones

Las direcciones IPv6 se escriben como **8 grupos de 4 dígitos hexadecimales**, separados por dos puntos:

```
2001:0db8:85a3:0000:0000:8a2e:0370:7334
```

**Cada grupo representa 16 bits**, y el uso de hexadecimal (base 16) hace que las direcciones sean más compactas que si se usara notación decimal.

#### Reglas de Compresión

Para facilitar la escritura y lectura, IPv6 permite dos tipos de compresión:

**1. Omisión de ceros a la izquierda:**

```
2001:0db8:0000:0042:0000:8a2e:0370:7334
2001:db8:0:42:0:8a2e:370:7334
```

**2. Compresión de grupos de ceros consecutivos (::):**

```
2001:0db8:0000:0000:0000:0000:0000:0001
2001:db8::1
```

**Reglas importantes:**

- La compresión `::` solo puede usarse **una vez** en una dirección
- Si hay múltiples series de ceros, `::` debe usarse en la más larga
- Si hay dos series de igual longitud, se usa en la primera

#### Ejemplos de Compresión


```
Dirección completa:    fe80:0000:0000:0000:0204:61ff:fe9d:f156
Comprimida:            fe80::204:61ff:fe9d:f156

Dirección completa:    2001:0db8:0000:0000:0000:0000:0000:0001
Comprimida:            2001:db8::1

Dirección completa:    0000:0000:0000:0000:0000:0000:0000:0001
Comprimida:            ::1 (loopback)

Dirección completa:    0000:0000:0000:0000:0000:0000:0000:0000
Comprimida:            :: (dirección no especificada)
```

### 2.2 Tipos de Direcciones IPv6


A diferencia de IPv4, IPv6 **no utiliza direcciones de broadcast**. En su lugar, utiliza tres tipos principales:


#### 2.2.1 Unicast

Identifica una única interfaz de red. Un paquete enviado a una dirección unicast se entrega exactamente a esa interfaz.

**Subtipos importantes:**

**a) Global Unicast Addresses (GUA):**

- Equivalente a las direcciones públicas IPv4
- Enrutables en Internet
- Prefijo: `2000::/3` (direcciones que comienzan con 2 o 3 en el primer dígito)
- Estructura:

  ```
  | 48 bits        | 16 bits    | 64 bits              |
  | Prefijo Global | Subnet ID  | Interface ID         |
  ```

**b) Link-Local Addresses:**
- Solo válidas dentro de un mismo enlace físico
- No enrutables
- Prefijo: `fe80::/10`
- Se autoconfigura automáticamente en cada interfaz
- Ejemplo: `fe80::1`
- Similar a las direcciones `169.254.x.x` de APIPA en IPv4

**c) Unique Local Addresses (ULA):**
- Equivalente a las direcciones privadas de IPv4 (10.0.0.0/8, etc.)
- No enrutables en Internet público
- Prefijo: `fc00::/7` (aunque en práctica se usa `fd00::/8`)
- Usadas para comunicación dentro de organizaciones

**d) Loopback:**
- `::1`
- Equivalente a `127.0.0.1` en IPv4
- Usada para que un host se comunique consigo mismo

**e) Dirección no especificada:**
- `::`
- Indica ausencia de dirección
- Usada por hosts durante la configuración inicial

#### 2.2.2 Multicast

Identifica múltiples interfaces. Un paquete enviado a una dirección multicast se entrega a todas las interfaces del grupo.

- Prefijo: `ff00::/8`
- Reemplaza el broadcast de IPv4
- Estructura del prefijo `ff`:

  ```
  ff [flags] [scope] : [group ID]
  ```

**Direcciones multicast importantes:**

```
ff02::1             - Todos los nodos en el enlace local
ff02::2             - Todos los routers en el enlace local
ff02::1:ff00:0/104  - Solicitud de vecino (Neighbor Solicitation)
ff05::2             - Todos los routers en el sitio
```

**Scopes (alcance):**

- `1`: Interface-local
- `2`: Link-local
- `5`: Site-local
- `8`: Organization-local
- `e`: Global

#### 2.2.3 Anycast

Una dirección anycast es asignada a múltiples interfaces (típicamente en diferentes nodos). Un paquete enviado a una dirección anycast se entrega a la interfaz **más cercana** (según la métrica de enrutamiento).

- No hay un prefijo especial
- Se toman del espacio unicast
- Útil para balanceo de carga y redundancia
- Ejemplo de uso: servidores DNS raíz

### 2.3 Estructura del Encabezado IPv6

Una de las mejoras más significativas de IPv6 es su encabezado simplificado.

#### Comparación de Encabezados

**IPv4 (20-60 bytes):**

```
Version | IHL | Type of Service | Total Length
Identification | Flags | Fragment Offset
TTL | Protocol | Header Checksum
Source Address (32 bits)
Destination Address (32 bits)
Options (variable) | Padding
```

**IPv6 (40 bytes fijos):**

```
Version | Traffic Class | Flow Label
Payload Length | Next Header | Hop Limit
Source Address (128 bits)
Destination Address (128 bits)
```

#### Campos del Encabezado IPv6

1. **Version (4 bits)**: Siempre es 6
2. **Traffic Class (8 bits)**: Similar a ToS en IPv4, usado para QoS
3. **Flow Label (20 bits)**: Identifica flujos de paquetes que requieren manejo especial
4. **Payload Length (16 bits)**: Tamaño de la carga útil en bytes
5. **Next Header (8 bits)**: Indica el tipo del siguiente encabezado (TCP, UDP, ICMPv6, o encabezado de extensión)
6. **Hop Limit (8 bits)**: Equivalente al TTL de IPv4
7. **Source/Destination Address (128 bits cada uno)**: Direcciones de origen y destino

#### Encabezados de Extensión

IPv6 introduce el concepto de **encabezados de extensión** que reemplazan el campo de opciones de IPv4. Estos encabezados se encadenan usando el campo "Next Header".

**Tipos de encabezados de extensión:**

1. **Hop-by-Hop Options**: Procesado por cada nodo en el camino
2. **Destination Options**: Procesado solo por el destino
3. **Routing**: Especifica una lista de routers por los que debe pasar el paquete
4. **Fragment**: Manejo de fragmentación (solo en el origen)
5. **Authentication Header (AH)**: IPsec
6. **Encapsulating Security Payload (ESP)**: IPsec

**Orden recomendado:**

```
IPv6 Header
Hop-by-Hop Options
Destination Options (para routers en el camino)
Routing
Fragment
Authentication
ESP
Destination Options (para el destino final)
Upper Layer (TCP/UDP/ICMPv6)
```

### 2.4 ICMPv6: El Corazón de IPv6

ICMPv6 es mucho más importante en IPv6 que ICMP en IPv4. No solo maneja errores y diagnósticos, sino que es **esencial** para el funcionamiento básico de IPv6.

#### Funciones Críticas de ICMPv6

**1. Neighbor Discovery Protocol (NDP):**

Reemplaza ARP de IPv4 y agrega funcionalidades adicionales:

- **Router Solicitation (RS)**: Hosts buscan routers
- **Router Advertisement (RA)**: Routers anuncian su presencia
- **Neighbor Solicitation (NS)**: Equivalente a ARP Request
- **Neighbor Advertisement (NA)**: Equivalente a ARP Reply
- **Redirect**: Informa de una mejor ruta

**2. Path MTU Discovery:**

Determina el tamaño máximo de paquete sin fragmentación.

**3. Mensajes de Error:**

- Destination Unreachable
- Packet Too Big
- Time Exceeded
- Parameter Problem

**4. Mensajes Informativos:**

- Echo Request/Reply (ping)
- Multicast Listener Query/Report/Done

### 2.5 Autoconfiguración de Direcciones

Una de las características más elegantes de IPv6 es su capacidad de **autoconfiguración stateless** (SLAAC - Stateless Address Autoconfiguration).

#### Proceso de Autoconfiguración

1. **Generación de dirección link-local:**

   - El host genera una dirección `fe80::/64`
   - El Interface ID se deriva de la MAC address usando EUI-64, o se genera aleatoriamente

2. **Duplicate Address Detection (DAD):**

   - El host envía un Neighbor Solicitation para verificar que la dirección no está en uso
   - Si no recibe respuesta, la dirección es única

3. **Router Discovery:**

   - El host envía un Router Solicitation (RS)
   - Los routers responden con Router Advertisement (RA)

4. **Configuración global:**

   - El RA contiene el prefijo de red
   - El host combina el prefijo con su Interface ID
   - Resultado: dirección global unicast autoconfigurada
 

#### EUI-64

El método EUI-64 convierte una dirección MAC de 48 bits en un Interface ID de 64 bits:


```
MAC: 00:1A:2B:3C:4D:5E

1. Insertar FF:FE en el medio:
   00:1A:2B:FF:FE:3C:4D:5E

2. Invertir el 7mo bit (U/L bit):
   02:1A:2B:FF:FE:3C:4D:5E

3. Interface ID:
   021A:2BFF:FE3C:4D5E

4. Dirección completa:
   2001:db8:1234:5678:021a:2bff:fe3c:4d5e
```

#### Privacy Extensions (RFC 4941)

Para proteger la privacidad, los sistemas modernos generan Interface IDs **temporales y aleatorios** en lugar de usar EUI-64, evitando que la MAC address sea rastreable.

### 2.6 Ventajas Técnicas de IPv6

1. **Espacio de direcciones prácticamente ilimitado**: 
   - Suficientes direcciones para asignar 100 direcciones por átomo en la superficie terrestre
   - Permite que cada dispositivo tenga una dirección pública única

2. **Encabezado simplificado**:
   - Procesamiento más rápido en routers
   - Tamaño fijo facilita el hardware switching
   - Eliminación del checksum del encabezado

3. **Autoconfiguración**:
   - Plug-and-play genuino
   - Reduce la necesidad de DHCP
   - Facilita la renumeración de redes

4. **Seguridad mejorada**:
   - IPsec es obligatorio en la especificación (aunque opcional en implementación)
   - SEND (Secure Neighbor Discovery) protege contra ataques

5. **Mejor soporte para movilidad**:
   - Mobile IPv6 permite que dispositivos mantengan conexiones al cambiar de red
   - Sin necesidad de triangulación como en Mobile IPv4

6. **Multicast mejorado**:
   - Eliminación de broadcast reduce el tráfico innecesario
   - Scopes bien definidos
   - Anycast incorporado

7. **Fragmentación solo en origen**:
   - Los routers no fragmentan paquetes
   - Reduce la carga en routers intermedios
   - PMTU Discovery es mandatorio

8. **Mejor QoS**:
   - Flow Label permite identificar flujos de tráfico
   - Traffic Class para priorización

### 2.7 Desafíos en la Adopción de IPv6

A pesar de sus ventajas, la transición a IPv6 ha sido lenta:

**Razones técnicas:**

- Incompatibilidad con IPv4 (no hay interoperabilidad directa)
- Necesidad de actualizar hardware y software
- Complejidad de dual-stack
- Curva de aprendizaje para administradores

**Razones económicas:**

- Costo de actualización de infraestructura
- NAT ha funcionado como "parche" efectivo
- Falta de incentivos económicos inmediatos

**Adopción actual (2025):**

- Google reporta ~40% de usuarios acceden vía IPv6
- Algunos países superan el 60% (India, Malasia, Vietnam)
- Carriers móviles lideran la adopción
- IPv6-only networks están emergiendo

### 2.8 Mecanismos de Transición

Dada la imposibilidad de una migración instantánea, existen varios mecanismos de coexistencia:

#### Dual Stack

- Hosts y routers ejecutan IPv4 e IPv6 simultáneamente
- La aplicación elige qué versión usar
- Requiere el doble de recursos

#### Tunneling

- **6to4**: Túneles automáticos sobre IPv4
- **6in4**: Túneles configurados manualmente
- **Teredo**: Túneles IPv6 sobre UDP/IPv4 (atraviesa NAT)
- **ISATAP**: Intra-Site Automatic Tunnel Addressing Protocol

#### Translation

- **NAT64**: Traduce entre IPv6 e IPv4
- **DNS64**: Resuelve nombres en el contexto de NAT64
- **464XLAT**: Combinación de mecanismos para redes móviles

---

## 3. Programación con IPv6 en Python

---

## 2. Programación con IPv6 en Python

### 2.1 Conceptos Básicos

Python soporta IPv6 a través del módulo `socket` usando la familia de direcciones `AF_INET6`:

```python
import socket

# IPv4
socket_ipv4 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# IPv6
socket_ipv6 = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
```

### 2.2 Servidor TCP con IPv6

**Ejemplo básico:**


```python
import socket

# Crear socket IPv6
server_socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)

# Configurar para reutilizar la dirección
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Enlazar a dirección y puerto
# '::1' es localhost en IPv6
# '::' escucha en todas las interfaces
server_address = ('::1', 8080)
server_socket.bind(server_address)

# Escuchar conexiones
server_socket.listen(5)
print(f"Servidor IPv6 escuchando en {server_address}")

while True:
    client_socket, client_address = server_socket.accept()
    print(f"Conexión desde: {client_address}")
    
    # Recibir datos
    data = client_socket.recv(1024)
    print(f"Recibido: {data.decode()}")
    
    # Enviar respuesta
    response = f"Servidor recibió: {data.decode()}"
    client_socket.sendall(response.encode())
    
    client_socket.close()
```

### 2.3 Cliente TCP con IPv6

```python
import socket

# Crear socket IPv6
client_socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)

# Conectar al servidor
server_address = ('::1', 8080)
client_socket.connect(server_address)

# Enviar mensaje
message = "Hola desde el cliente IPv6"
client_socket.sendall(message.encode())

# Recibir respuesta
response = client_socket.recv(1024)
print(f"Respuesta del servidor: {response.decode()}")

client_socket.close()
```

---

## 3. Usando socketserver con IPv6

El módulo `socketserver` facilita la creación de servidores, pero requiere configuración adicional para IPv6.

### 3.1 Servidor Básico con socketserver

```python
import socketserver

class MiManejador(socketserver.BaseRequestHandler):
    def handle(self):
        # Información del cliente
        print(f"Conexión de: {self.client_address}")
        
        # Recibir datos
        data = self.request.recv(1024).strip()
        print(f"Recibido: {data.decode()}")
        
        # Enviar respuesta
        respuesta = f"Echo: {data.decode().upper()}"
        self.request.sendall(respuesta.encode())

# Crear clase de servidor IPv6
class ServidorIPv6(socketserver.TCPServer):
    address_family = socket.AF_INET6

if __name__ == "__main__":
    HOST, PORT = "::1", 9999
    
    with ServidorIPv6((HOST, PORT), MiManejador) as servidor:
        print(f"Servidor IPv6 iniciado en [{HOST}]:{PORT}")
        servidor.serve_forever()
```

### 3.2 Servidor con Hilos (Threading)

```python
import socketserver
import socket
import threading

class ManejadorThreading(socketserver.BaseRequestHandler):
    def handle(self):
        thread_name = threading.current_thread().name
        print(f"[{thread_name}] Conexión de: {self.client_address}")
        
        while True:
            data = self.request.recv(1024)
            if not data:
                break
            
            print(f"[{thread_name}] Recibido: {data.decode()}")
            respuesta = f"[{thread_name}] Echo: {data.decode()}"
            self.request.sendall(respuesta.encode())
        
        print(f"[{thread_name}] Conexión cerrada")

class ServidorIPv6Threading(socketserver.ThreadingTCPServer):
    address_family = socket.AF_INET6
    allow_reuse_address = True

if __name__ == "__main__":
    HOST, PORT = "::", 9999
    
    servidor = ServidorIPv6Threading((HOST, PORT), ManejadorThreading)
    print(f"Servidor multi-hilo IPv6 en [{HOST}]:{PORT}")
    
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("\nCerrando servidor...")
        servidor.shutdown()
```

---

## 4. Soporte Dual: IPv4 e IPv6

### 4.1 Usando AF_UNSPEC

`AF_UNSPEC` permite que el sistema operativo elija automáticamente entre IPv4 e IPv6:

```python
import socket

def obtener_direcciones(host, puerto):
    """Obtiene todas las direcciones disponibles para un host"""
    direcciones = socket.getaddrinfo(
        host, 
        puerto, 
        socket.AF_UNSPEC,  # IPv4 o IPv6
        socket.SOCK_STREAM
    )
    
    for addr in direcciones:
        familia, tipo, proto, canonname, sockaddr = addr
        protocolo = "IPv4" if familia == socket.AF_INET else "IPv6"
        print(f"{protocolo}: {sockaddr}")
    
    return direcciones

# Ejemplo de uso
direcciones = obtener_direcciones("localhost", 8080)
```

### 4.2 Servidor Dual Stack

```python
import socket
import socketserver
import threading

class ManejadorUniversal(socketserver.BaseRequestHandler):
    def handle(self):
        # Detectar tipo de conexión
        if self.client_address[0].count(':') > 1:
            protocolo = "IPv6"
        else:
            protocolo = "IPv4"
        
        print(f"[{protocolo}] Conexión de: {self.client_address}")
        
        data = self.request.recv(1024).strip()
        respuesta = f"Servidor {protocolo}: {data.decode()}"
        self.request.sendall(respuesta.encode())

class ServidorIPv4(socketserver.ThreadingTCPServer):
    address_family = socket.AF_INET

class ServidorIPv6(socketserver.ThreadingTCPServer):
    address_family = socket.AF_INET6

def iniciar_servidor(familia, host, port, handler):
    """Inicia un servidor en un hilo separado"""
    if familia == socket.AF_INET:
        servidor = ServidorIPv4((host, port), handler)
        nombre = "IPv4"
    else:
        servidor = ServidorIPv6((host, port), handler)
        nombre = "IPv6"
    
    print(f"Iniciando servidor {nombre} en {host}:{port}")
    thread = threading.Thread(target=servidor.serve_forever, daemon=True)
    thread.start()
    return servidor, thread

if __name__ == "__main__":
    PORT = 9999
    servidores = []
    
    # Obtener direcciones disponibles
    direcciones = socket.getaddrinfo(
        "localhost", 
        PORT, 
        socket.AF_UNSPEC, 
        socket.SOCK_STREAM
    )
    
    # Iniciar servidor para cada familia de direcciones
    familias_iniciadas = set()
    for addr_info in direcciones:
        familia = addr_info[0]
        if familia not in familias_iniciadas:
            host = "127.0.0.1" if familia == socket.AF_INET else "::1"
            srv, thread = iniciar_servidor(
                familia, host, PORT, ManejadorUniversal
            )
            servidores.append(srv)
            familias_iniciadas.add(familia)
    
    print("\nServidores iniciados. Presiona Ctrl+C para detener.")
    
    try:
        for srv in servidores:
            srv.serve_forever()
    except KeyboardInterrupt:
        print("\nDeteniendo servidores...")
        for srv in servidores:
            srv.shutdown()
```

---

## 5. Ejercicios Prácticos

### Ejercicio 1: Echo Server Básico

**Objetivo**: Crear un servidor echo IPv6 que devuelva todo lo que recibe en mayúsculas.

**Requisitos**:
- Usar IPv6 exclusivamente
- Escuchar en el puerto 8888
- Convertir mensajes a mayúsculas antes de responder
- Mantener la conexión abierta para múltiples mensajes

**Desafío adicional**: Implementar un comando "QUIT" para cerrar la conexión.

---

### Ejercicio 2: Chat Simple

**Objetivo**: Crear un sistema de chat cliente-servidor usando IPv6.

**Requisitos del servidor**:
- Aceptar múltiples clientes simultáneamente
- Transmitir mensajes de un cliente a todos los demás
- Mostrar quién envía cada mensaje

**Requisitos del cliente**:
- Conectarse al servidor
- Permitir enviar y recibir mensajes en tiempo real

---

### Ejercicio 3: Servidor de Archivos

**Objetivo**: Implementar un servidor que permita descargar archivos usando IPv6.

**Requisitos**:
- Listar archivos disponibles en un directorio
- Permitir al cliente solicitar archivos por nombre
- Transferir archivos de forma segura
- Manejar archivos grandes en chunks

---

### Ejercicio 4: Servidor Dual Stack Inteligente

**Objetivo**: Crear un servidor que funcione con IPv4 e IPv6 y registre estadísticas.

**Requisitos**:
- Aceptar conexiones IPv4 e IPv6
- Llevar registro de:
  - Número de conexiones por protocolo
  - Tiempo promedio de respuesta
  - Datos transferidos
- Generar un reporte al finalizar

---

### Ejercicio 5: Calculadora Remota

**Objetivo**: Implementar una calculadora cliente-servidor con IPv6.

**Requisitos del servidor**:
- Recibir expresiones matemáticas
- Evaluar la expresión de forma segura
- Devolver el resultado
- Manejar errores apropiadamente

**Requisitos del cliente**:
- Interfaz simple para ingresar expresiones
- Mostrar resultados
- Manejar errores de conexión

**Ejemplo de protocolo**:
```
Cliente: "2 + 2"
Servidor: "RESULTADO: 4"

Cliente: "10 / 0"
Servidor: "ERROR: División por cero"
```

---

## 6. Mejores Prácticas

### 6.1 Manejo de Errores

```python
import socket

try:
    sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    sock.connect(('::1', 8080))
except socket.gaierror as e:
    print(f"Error de resolución de dirección: {e}")
except socket.error as e:
    print(f"Error de socket: {e}")
except Exception as e:
    print(f"Error inesperado: {e}")
finally:
    sock.close()
```

### 6.2 Timeouts

```python
import socket

sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
sock.settimeout(5.0)  # Timeout de 5 segundos

try:
    sock.connect(('::1', 8080))
    sock.sendall(b"mensaje")
    data = sock.recv(1024)
except socket.timeout:
    print("La operación excedió el tiempo límite")
finally:
    sock.close()
```

### 6.3 Cierre Limpio

```python
import socket

sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
try:
    # ... operaciones con el socket ...
    sock.shutdown(socket.SHUT_RDWR)
except socket.error:
    pass
finally:
    sock.close()
```

---

## 7. Recursos Adicionales

### Direcciones IPv6 Especiales

- `::1` - Loopback (equivalente a 127.0.0.1 en IPv4)
- `::` - Dirección no especificada / todas las interfaces
- `fe80::/10` - Link-local addresses
- `ff00::/8` - Multicast addresses
- `2001:db8::/32` - Documentación y ejemplos

### Comandos Útiles para Pruebas

**Linux/Mac:**
```bash
# Ver interfaces IPv6
ip -6 addr show

# Probar conectividad
ping6 ::1

# Netcat con IPv6
nc -6 -l 8080
```

**Windows:**
```bash
# Ver configuración IPv6
ipconfig

# Probar conectividad
ping ::1

# Telnet con IPv6
telnet ::1 8080
```

### Documentación Oficial

- Python Socket: https://docs.python.org/3/library/socket.html
- Python SocketServer: https://docs.python.org/3/library/socketserver.html
- Python ipaddress: https://docs.python.org/3/library/ipaddress.html

---

## Conclusión

IPv6 no es solo el futuro de Internet, sino ya una realidad presente. Dominar su implementación en Python te preparará para desarrollar aplicaciones de red modernas y escalables. Los conceptos aprendidos aquí son fundamentales para cualquier programador que trabaje con redes y comunicaciones.

Recuerda practicar con los ejercicios propuestos y experimentar con tus propias implementaciones. La mejor forma de aprender programación de redes es escribiendo código y resolviendo problemas reales.