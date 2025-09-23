# El Módulo Socketserver y sus Variantes de Red
## Computación II - Universidad de Mendoza

---

## Objetivos de la Clase

Al finalizar esta clase, los estudiantes serán capaces de:
- Comprender la arquitectura del módulo `socketserver` de Python
- Implementar servidores TCP y UDP usando las clases base del módulo
- Utilizar los mixins para crear servidores concurrentes
- Desarrollar handlers personalizados para diferentes protocolos
- Aplicar patrones de diseño en la programación de servidores de red

---

## 1. Base Teórica: El Módulo Socketserver

### ¿Qué es socketserver?

El módulo `socketserver` de Python proporciona un framework para crear servidores de red de manera simplificada. Ofrece una abstracción de alto nivel sobre los sockets tradicionales, permitiendo a los desarrolladores concentrarse en la lógica de negocio en lugar de los detalles de bajo nivel de la comunicación de red.

### Ventajas del módulo socketserver:

- **Abstracción de complejidad**: Maneja automáticamente la creación y gestión de sockets
- **Arquitectura extensible**: Sistema de clases que permite personalización
- **Soporte múltiple**: Compatible con TCP, UDP, Unix sockets
- **Concurrencia integrada**: Mixins para threading y forking
- **Patrones establecidos**: Implementa patrones probados de servidor

---

## 2. Arquitectura del Módulo

### 2.1 Jerarquía de Clases Base

```
BaseServer
├── TCPServer
│   └── UnixStreamServer
└── UDPServer
    └── UnixDatagramServer
```

### 2.2 Esquema de Herencia Completo

```
                BaseServer
                     |
        +------------+------------+
        |                         |
    TCPServer                UDPServer
        |                         |
UnixStreamServer        UnixDatagramServer
```

### 2.3 Mixins para Concurrencia

```
ThreadingMixIn      ForkingMixIn
       |                 |
ThreadingTCPServer  ForkingTCPServer
ThreadingUDPServer  ForkingUDPServer
```

---

## 3. Clases Base Fundamentales

### 3.1 BaseServer

Es la clase base abstracta que define la interfaz común para todos los servidores:

```python
import socketserver

class BaseServer:
    """Clase base abstracta para servidores de red"""
    
    # Métodos principales:
    # - serve_forever()     # Bucle principal del servidor
    # - shutdown()          # Detiene el servidor
    # - handle_request()    # Maneja una sola petición
    # - server_bind()       # Vincula el socket a una dirección
    # - server_activate()   # Activa el servidor para aceptar conexiones
```

### 3.2 TCPServer

Implementa un servidor TCP básico:

```python
class TCPServer(BaseServer):
    """Servidor TCP que maneja conexiones confiables"""
    
    address_family = socket.AF_INET    # Familia de direcciones IPv4
    socket_type = socket.SOCK_STREAM   # Socket TCP
    allow_reuse_address = False        # Reutilización de direcciones
    request_queue_size = 5             # Tamaño de cola de conexiones
```

### 3.3 UDPServer

Implementa un servidor UDP básico:

```python
class UDPServer(BaseServer):
    """Servidor UDP que maneja datagramas"""
    
    address_family = socket.AF_INET    # Familia de direcciones IPv4
    socket_type = socket.SOCK_DGRAM    # Socket UDP
    max_packet_size = 8192             # Tamaño máximo del paquete
```

---

## 4. Ejemplos Prácticos Comentados

### 4.1 Servidor TCP Básico

```python
#!/usr/bin/env python3
import socketserver
import threading

class EchoTCPHandler(socketserver.BaseRequestHandler):
    """
    Handler que implementa un servidor echo TCP.
    Recibe datos del cliente y los devuelve en mayúsculas.
    """
    
    def handle(self):
        """
        Método principal que maneja cada conexión TCP.
        self.request es el socket TCP conectado al cliente.
        """
        print(f"Conexión establecida con: {self.client_address}")
        
        # Bucle para manejar múltiples mensajes del mismo cliente
        while True:
            try:
                # Recibir datos (máximo 1024 bytes)
                data = self.request.recv(1024)
                
                if not data:
                    # Cliente cerró la conexión
                    print(f"Cliente {self.client_address} desconectado")
                    break
                    
                # Procesar los datos recibidos
                message = data.decode('utf-8').strip()
                print(f"Recibido de {self.client_address}: {message}")
                
                # Enviar respuesta en mayúsculas
                response = message.upper().encode('utf-8')
                self.request.sendall(response)
                
            except ConnectionResetError:
                print(f"Conexión perdida con {self.client_address}")
                break
            except Exception as e:
                print(f"Error manejando cliente {self.client_address}: {e}")
                break

if __name__ == "__main__":
    HOST, PORT = "localhost", 9999
    
    # Crear servidor TCP
    with socketserver.TCPServer((HOST, PORT), EchoTCPHandler) as server:
        print(f"Servidor TCP iniciado en {HOST}:{PORT}")
        print("Presiona Ctrl+C para detener el servidor")
        
        try:
            # Iniciar bucle principal del servidor
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nServidor detenido por el usuario")
```

### 4.2 Servidor UDP Básico

```python
#!/usr/bin/env python3
import socketserver
import time

class TimeUDPHandler(socketserver.BaseRequestHandler):
    """
    Handler UDP que responde con la hora actual.
    En UDP, self.request es una tupla (data, socket).
    """
    
    def handle(self):
        """
        Maneja cada datagrama UDP recibido.
        """
        # Extraer datos y socket de la tupla
        data, socket = self.request
        
        # Decodificar el mensaje del cliente
        message = data.decode('utf-8').strip()
        print(f"UDP de {self.client_address}: {message}")
        
        # Preparar respuesta con la hora actual
        current_time = time.strftime("%Y-%m-%d %H:%M:%S")
        response = f"Hora del servidor: {current_time}"
        
        # Enviar respuesta al cliente específico
        socket.sendto(response.encode('utf-8'), self.client_address)

class CustomUDPServer(socketserver.UDPServer):
    """
    Servidor UDP personalizado con configuraciones específicas.
    """
    
    def __init__(self, server_address, RequestHandlerClass):
        # Permitir reutilización de direcciones
        self.allow_reuse_address = True
        super().__init__(server_address, RequestHandlerClass)
        
    def server_bind(self):
        """Override para mostrar información de binding"""
        super().server_bind()
        print(f"Servidor UDP vinculado a {self.server_address}")

if __name__ == "__main__":
    HOST, PORT = "0.0.0.0", 8888  # Escuchar en todas las interfaces
    
    # Crear servidor UDP personalizado
    with CustomUDPServer((HOST, PORT), TimeUDPHandler) as server:
        print(f"Servidor UDP de tiempo iniciado en puerto {PORT}")
        print("Envía cualquier mensaje para obtener la hora")
        print("Usar: echo 'hora' | nc -u localhost 8888")
        
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nServidor UDP detenido")
```

### 4.3 Servidor TCP Concurrente con Threading

```python
#!/usr/bin/env python3
import socketserver
import threading
import time
import json

class ChatHandler(socketserver.BaseRequestHandler):
    """
    Handler para un sistema de chat simple usando TCP concurrente.
    Cada cliente es manejado en un hilo separado.
    """
    
    # Variable de clase para almacenar clientes conectados
    clients = {}
    clients_lock = threading.Lock()
    
    def setup(self):
        """Se ejecuta antes de handle() - inicialización"""
        self.username = None
        print(f"Nueva conexión desde {self.client_address}")
    
    def handle(self):
        """Maneja la comunicación con un cliente específico"""
        try:
            # Solicitar nombre de usuario
            self.request.sendall(b"Ingresa tu nombre de usuario: ")
            username_data = self.request.recv(1024)
            self.username = username_data.decode('utf-8').strip()
            
            # Registrar cliente
            with self.clients_lock:
                self.clients[self.username] = self.request
            
            # Notificar a otros clientes
            self.broadcast_message(f"{self.username} se unió al chat", exclude_self=True)
            self.request.sendall(b"Bienvenido al chat! Escribe 'quit' para salir.\n")
            
            # Bucle principal de chat
            while True:
                data = self.request.recv(1024)
                if not data:
                    break
                    
                message = data.decode('utf-8').strip()
                
                if message.lower() == 'quit':
                    break
                elif message.startswith('/list'):
                    self.send_user_list()
                elif message.startswith('/whisper'):
                    self.handle_whisper(message)
                else:
                    # Mensaje público
                    full_message = f"[{self.username}]: {message}"
                    self.broadcast_message(full_message)
                    
        except Exception as e:
            print(f"Error en handler para {self.username}: {e}")
        
    def finish(self):
        """Se ejecuta después de handle() - limpieza"""
        if self.username:
            # Remover cliente de la lista
            with self.clients_lock:
                self.clients.pop(self.username, None)
            
            # Notificar salida
            self.broadcast_message(f"{self.username} abandonó el chat", exclude_self=True)
            print(f"{self.username} desconectado")
    
    def broadcast_message(self, message, exclude_self=False):
        """Envía un mensaje a todos los clientes conectados"""
        with self.clients_lock:
            dead_clients = []
            
            for username, client_socket in self.clients.items():
                if exclude_self and username == self.username:
                    continue
                    
                try:
                    client_socket.sendall(f"{message}\n".encode('utf-8'))
                except:
                    # Cliente desconectado, marcar para eliminación
                    dead_clients.append(username)
            
            # Limpiar clientes desconectados
            for username in dead_clients:
                self.clients.pop(username, None)
    
    def send_user_list(self):
        """Envía la lista de usuarios conectados"""
        with self.clients_lock:
            users = list(self.clients.keys())
            user_list = f"Usuarios conectados: {', '.join(users)}\n"
            self.request.sendall(user_list.encode('utf-8'))
    
    def handle_whisper(self, message):
        """Maneja mensajes privados"""
        try:
            # Formato: /whisper username mensaje
            parts = message.split(' ', 2)
            if len(parts) < 3:
                self.request.sendall(b"Uso: /whisper <usuario> <mensaje>\n")
                return
                
            target_user = parts[1]
            whisper_message = parts[2]
            
            with self.clients_lock:
                if target_user in self.clients:
                    target_socket = self.clients[target_user]
                    private_msg = f"[PRIVADO de {self.username}]: {whisper_message}\n"
                    target_socket.sendall(private_msg.encode('utf-8'))
                    self.request.sendall(b"Mensaje privado enviado.\n")
                else:
                    self.request.sendall(f"Usuario '{target_user}' no encontrado.\n".encode('utf-8'))
                    
        except Exception as e:
            self.request.sendall(f"Error enviando mensaje privado: {e}\n".encode('utf-8'))

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    """
    Servidor TCP que crea un hilo para cada conexión.
    Hereda de ThreadingMixIn para funcionalidad concurrente.
    """
    
    # Permitir reutilización rápida de la dirección
    allow_reuse_address = True
    
    # Los hilos daemon se terminan automáticamente al cerrar el servidor
    daemon_threads = True

if __name__ == "__main__":
    HOST, PORT = "localhost", 7777
    
    # Crear servidor concurrente
    server = ThreadedTCPServer((HOST, PORT), ChatHandler)
    
    print(f"Servidor de chat iniciado en {HOST}:{PORT}")
    print(f"Máximo de hilos concurrentes: {threading.active_count()}")
    print("Conecta múltiples clientes con: telnet localhost 7777")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print(f"\nCerrando servidor... Hilos activos: {threading.active_count()}")
        server.shutdown()
        server.server_close()
```

### 4.4 Servidor HTTP Básico Personalizado

```python
#!/usr/bin/env python3
import socketserver
import datetime
import os
import urllib.parse

class SimpleHTTPHandler(socketserver.BaseRequestHandler):
    """
    Handler que implementa un servidor HTTP básico.
    Demuestra el manejo de protocolos de aplicación sobre TCP.
    """
    
    def handle(self):
        """Maneja una petición HTTP completa"""
        try:
            # Recibir la petición HTTP
            request_data = self.request.recv(4096).decode('utf-8')
            
            if not request_data:
                return
                
            # Parsear la primera línea (método, path, versión)
            lines = request_data.split('\r\n')
            request_line = lines[0]
            method, path, version = request_line.split(' ')
            
            print(f"Petición: {method} {path} desde {self.client_address}")
            
            # Decodificar URL
            path = urllib.parse.unquote(path)
            
            # Routear la petición
            if method == 'GET':
                if path == '/':
                    self.serve_homepage()
                elif path == '/time':
                    self.serve_time()
                elif path == '/info':
                    self.serve_server_info()
                elif path.startswith('/echo/'):
                    message = path[6:]  # Extraer mensaje después de /echo/
                    self.serve_echo(message)
                else:
                    self.serve_404()
            else:
                self.serve_method_not_allowed()
                
        except Exception as e:
            print(f"Error procesando petición: {e}")
            self.serve_500()
    
    def send_response(self, status_code, content_type, body):
        """Envía una respuesta HTTP completa"""
        status_messages = {
            200: "OK",
            404: "Not Found", 
            405: "Method Not Allowed",
            500: "Internal Server Error"
        }
        
        status_text = status_messages.get(status_code, "Unknown")
        
        # Construir respuesta HTTP
        response = f"HTTP/1.1 {status_code} {status_text}\r\n"
        response += f"Content-Type: {content_type}\r\n"
        response += f"Content-Length: {len(body.encode('utf-8'))}\r\n"
        response += f"Date: {datetime.datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')}\r\n"
        response += f"Server: SimpleHTTPServer/1.0\r\n"
        response += "\r\n"
        response += body
        
        self.request.sendall(response.encode('utf-8'))
    
    def serve_homepage(self):
        """Página principal"""
        html = """
        <!DOCTYPE html>
        <html>
        <head><title>Servidor Simple</title></head>
        <body>
            <h1>Bienvenido al Servidor Simple</h1>
            <ul>
                <li><a href="/time">Hora del servidor</a></li>
                <li><a href="/info">Información del servidor</a></li>
                <li><a href="/echo/Hola%20Mundo">Echo: Hola Mundo</a></li>
            </ul>
        </body>
        </html>
        """
        self.send_response(200, "text/html", html)
    
    def serve_time(self):
        """Responde con la hora actual"""
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        json_response = f'{{"timestamp": "{current_time}"}}'
        self.send_response(200, "application/json", json_response)
    
    def serve_server_info(self):
        """Información del servidor"""
        info = {
            "servidor": "SimpleHTTPServer/1.0",
            "python_version": os.sys.version,
            "pid": os.getpid(),
            "cliente": str(self.client_address)
        }
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head><title>Info del Servidor</title></head>
        <body>
            <h2>Información del Servidor</h2>
            <pre>{info}</pre>
        </body>
        </html>
        """
        self.send_response(200, "text/html", html)
    
    def serve_echo(self, message):
        """Servicio echo"""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head><title>Echo</title></head>
        <body>
            <h2>Echo Service</h2>
            <p>Tu mensaje: <strong>{message}</strong></p>
            <p>Longitud: {len(message)} caracteres</p>
        </body>
        </html>
        """
        self.send_response(200, "text/html", html)
    
    def serve_404(self):
        """Página no encontrada"""
        html = """
        <!DOCTYPE html>
        <html>
        <head><title>404 - No Encontrado</title></head>
        <body>
            <h1>404 - Página No Encontrada</h1>
            <p>La página solicitada no existe.</p>
        </body>
        </html>
        """
        self.send_response(404, "text/html", html)
    
    def serve_method_not_allowed(self):
        """Método no permitido"""
        self.send_response(405, "text/plain", "Método no permitido")
    
    def serve_500(self):
        """Error interno del servidor"""
        self.send_response(500, "text/plain", "Error interno del servidor")

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080
    
    with socketserver.TCPServer((HOST, PORT), SimpleHTTPHandler) as server:
        print(f"Servidor HTTP iniciado en http://{HOST}:{PORT}")
        print("Rutas disponibles:")
        print("  /        - Página principal")
        print("  /time    - Hora del servidor")
        print("  /info    - Información del servidor")
        print("  /echo/X  - Echo del mensaje X")
        
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nServidor HTTP detenido")
```

---

## 5. Patrones Avanzados y Mixins

### 5.1 Comparación de Modelos de Concurrencia

```python
#!/usr/bin/env python3
import socketserver
import threading
import os
import time

class BenchmarkHandler(socketserver.BaseRequestHandler):
    """Handler que simula trabajo computacional para benchmarks"""
    
    def handle(self):
        # Identificar el tipo de servidor y modelo de concurrencia
        server_type = type(self.server).__name__
        thread_id = threading.current_thread().name
        process_id = os.getpid()
        
        # Simular trabajo computacional
        start_time = time.time()
        result = sum(i*i for i in range(10000))  # Trabajo CPU-intensivo
        end_time = time.time()
        
        # Preparar respuesta con métricas
        response = f"""
Servidor: {server_type}
Hilo/Proceso: {thread_id} (PID: {process_id})
Cliente: {self.client_address}
Tiempo de procesamiento: {end_time - start_time:.4f}s
Resultado: {result}
Hilos activos: {threading.active_count()}
"""
        
        self.request.sendall(response.encode('utf-8'))

# Servidor secuencial (una conexión a la vez)
class SequentialServer(socketserver.TCPServer):
    """Servidor que maneja conexiones secuencialmente"""
    allow_reuse_address = True

# Servidor con hilos (Threading)
class ThreadedServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    """Servidor que crea un hilo por conexión"""
    allow_reuse_address = True
    daemon_threads = True

# Servidor con procesos (Forking) - Solo Unix/Linux
class ForkedServer(socketserver.ForkingMixIn, socketserver.TCPServer):
    """Servidor que crea un proceso por conexión"""
    allow_reuse_address = True

def demo_concurrent_servers():
    """Demostración de diferentes modelos de concurrencia"""
    
    servers = [
        ("Secuencial", SequentialServer, 9001),
        ("Con Hilos", ThreadedServer, 9002),
        # ("Con Procesos", ForkedServer, 9003),  # Descomentar en Unix/Linux
    ]
    
    print("Iniciando servidores de demostración...")
    print("Usa múltiples conexiones telnet para probar concurrencia:")
    
    for name, server_class, port in servers:
        print(f"  telnet localhost {port}  # {name}")
    
    print("\nPresiona Ctrl+C para detener todos los servidores\n")
    
    # Iniciar todos los servidores en hilos separados
    server_threads = []
    actual_servers = []
    
    for name, server_class, port in servers:
        try:
            server = server_class(("localhost", port), BenchmarkHandler)
            actual_servers.append(server)
            
            thread = threading.Thread(
                target=server.serve_forever,
                name=f"{name}Server"
            )
            thread.daemon = True
            thread.start()
            server_threads.append(thread)
            
            print(f"✓ Servidor {name} iniciado en puerto {port}")
            
        except Exception as e:
            print(f"✗ Error iniciando servidor {name}: {e}")
    
    try:
        # Mantener el programa principal activo
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nDeteniendo servidores...")
        for server in actual_servers:
            server.shutdown()
            server.server_close()

if __name__ == "__main__":
    demo_concurrent_servers()
```

---

## 6. Ejercicios para Casa

### Ejercicio 1: Servidor de Archivos UDP (Básico)
**Objetivo**: Implementar un servidor UDP que permita listar y obtener archivos de un directorio específico.

**Requisitos**:
- Comando `LIST`: Devuelve lista de archivos en el directorio
- Comando `GET <archivo>`: Devuelve el contenido del archivo
- Manejo de errores para archivos inexistentes
- Limitación de tamaño de respuesta UDP

**Pista**: Usar `os.listdir()` y considerar fragmentación para archivos grandes.

### Ejercicio 2: Sistema de Chat Mejorado (Intermedio)
**Objetivo**: Extender el ejemplo de chat con funcionalidades adicionales.

**Funcionalidades a implementar**:
- Salas de chat (`/join <sala>`, `/leave`)
- Historial de mensajes (últimos 10 mensajes al conectarse)
- Comandos de administración (`/kick <usuario>`)
- Límite de usuarios por sala
- Autenticación básica

### Ejercicio 3: Proxy HTTP Básico (Avanzado)
**Objetivo**: Crear un proxy HTTP que redirija peticiones a otros servidores.

**Características**:
- Interceptar peticiones HTTP GET
- Reenviar peticiones al servidor destino
- Devolver la respuesta al cliente original
- Logging de todas las peticiones
- Cache básico para respuestas frecuentes

**Extensión**: Implementar filtrado de URLs (blacklist/whitelist).

### Ejercicio 4: Servidor de Métricas con Múltiples Protocolos (Desafío)
**Objetivo**: Sistema que recolecta métricas via UDP y las expone via HTTP.

**Componentes**:
1. **Recolector UDP**: Recibe métricas en formato "metrica:valor:timestamp"
2. **API HTTP**: Expone métricas recolectadas en JSON
3. **Dashboard**: Página web simple que muestra las métricas
4. **Persistencia**: Almacenar métricas en archivos

**Métricas a manejar**:
- CPU usage, memoria, conexiones de red
- Agregaciones: promedio, máximo, mínimo por período

---

## 7. Recursos Adicionales

### Enlaces de Referencia:
- [Documentación oficial socketserver](https://docs.python.org/3/library/socketserver.html)
- [Guía de programación de sockets](https://docs.python.org/3/howto/sockets.html)
- [Patrones de concurrencia en Python](https://docs.python.org/3/library/threading.html)

### Herramientas de Prueba:
```bash
# Para servidores TCP
telnet localhost <puerto>
nc localhost <puerto>

# Para servidores UDP  
nc -u localhost <puerto>
echo "mensaje" | nc -u localhost <puerto>

# Para servidores HTTP
curl http://localhost:<puerto>/path
wget http://localhost:<puerto>/path
```

### Comandos útiles para debugging:
```bash
# Ver puertos en uso
netstat -tlnp | grep :<puerto>

# Monitorear conexiones
ss -tulpn | grep :<puerto>

# Probar conectividad
telnet <host> <puerto>
```

---

## Conclusión

El módulo `socketserver` proporciona una base sólida para desarrollar servidores de red en Python. Su arquitectura basada en clases y mixins permite crear soluciones escalables y mantenibles. La comprensión de estos patrones es fundamental para el desarrollo de sistemas distribuidos y aplicaciones de red robustas.

**Puntos clave para recordar**:
- Elegir el modelo de concurrencia apropiado según el caso de uso
- Manejar adecuadamente los errores de red y desconexiones
- Considerar las limitaciones de UDP vs las garantías de TCP  
- Implementar logging y monitoreo para depuración
- Probar con múltiples clientes concurrentes