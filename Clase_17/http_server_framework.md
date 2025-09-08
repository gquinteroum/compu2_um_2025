# Marco Teórico: Servidores HTTP con Python

## Introducción

En los temas anteriores hemos explorado mecanismos de comunicación entre procesos (IPC) y programación con sockets, trabajando directamente con la capa de transporte. Ahora daremos un paso hacia arriba en la pila de protocolos para explorar la **capa de aplicación**, específicamente el protocolo HTTP y cómo implementar servidores web utilizando Python.

Este salto desde sockets raw hacia protocolos estructurados nos permite construir aplicaciones más robustas y estandarizadas, manteniendo el control sobre el comportamiento del servidor.

---

## 1. El Protocolo HTTP

### 1.1 ¿Qué es HTTP?

El Protocolo de Transferencia de Hipertexto (HTTP) es un protocolo de comunicación de la capa de aplicación diseñado para la transferencia de datos en la World Wide Web. Opera sobre TCP (que ya conocemos de nuestro trabajo con sockets) y sigue un modelo **cliente-servidor** basado en **solicitud-respuesta**.

HTTP es un protocolo **sin estado (stateless)**, lo que significa que cada solicitud se procesa independientemente, sin memoria de solicitudes anteriores. Esta característica simplifica el diseño del servidor pero requiere mecanismos adicionales (como cookies o sesiones) para mantener estado cuando es necesario.

### 1.2 Estructura de una Comunicación HTTP

Una comunicación HTTP consta de dos partes principales:

#### Solicitud HTTP (Request)
```
GET /index.html HTTP/1.1
Host: www.ejemplo.com
User-Agent: Mozilla/5.0
Accept: text/html,application/xhtml+xml
Connection: keep-alive
```

#### Respuesta HTTP (Response)
```
HTTP/1.1 200 OK
Content-Type: text/html
Content-Length: 1234
Server: Python/HTTPServer

<html>
<body>Contenido de la página</body>
</html>
```

### 1.3 Métodos HTTP

Los métodos HTTP definen la acción que el cliente desea realizar sobre el recurso identificado:

#### Métodos Principales

**GET**: Solicita la representación de un recurso específico. Es el método más común y debe ser **idempotente** (múltiples llamadas idénticas deben tener el mismo efecto).
```
GET /usuarios/123 HTTP/1.1
```

**POST**: Envía datos al servidor para ser procesados. Generalmente usado para crear nuevos recursos o enviar datos de formularios. **No es idempotente**.
```
POST /usuarios HTTP/1.1
Content-Type: application/json

{"nombre": "Juan", "email": "juan@ejemplo.com"}
```

**PUT**: Reemplaza completamente un recurso existente o lo crea si no existe. Es **idempotente**.
```
PUT /usuarios/123 HTTP/1.1
Content-Type: application/json

{"nombre": "Juan Pérez", "email": "juan.perez@ejemplo.com"}
```

**DELETE**: Elimina un recurso específico. Es **idempotente**.
```
DELETE /usuarios/123 HTTP/1.1
```

#### Métodos Adicionales

**HEAD**: Similar a GET pero solicita solo los headers de respuesta, sin el cuerpo. Útil para verificar metadatos sin descargar el contenido completo.

**PATCH**: Realiza modificaciones parciales a un recurso, a diferencia de PUT que lo reemplaza completamente.

**OPTIONS**: Solicita información sobre las opciones de comunicación disponibles para el recurso (métodos permitidos, headers soportados).

**CONNECT**: Establece un túnel hacia el servidor, principalmente usado con proxies para conexiones HTTPS.

**TRACE**: Realiza una prueba de bucle de retorno del mensaje de solicitud, usado principalmente para diagnósticos.

### 1.4 Códigos de Estado HTTP

Los códigos de estado indican el resultado de la solicitud HTTP:

#### 2xx - Respuestas Exitosas
- **200 OK**: La solicitud fue exitosa
- **201 Created**: El recurso fue creado exitosamente
- **204 No Content**: Solicitud exitosa sin contenido en la respuesta

#### 3xx - Redirecciones
- **301 Moved Permanently**: El recurso se movió permanentemente a otra URL
- **302 Found**: Redirección temporal
- **304 Not Modified**: El recurso no ha sido modificado desde la última solicitud

#### 4xx - Errores del Cliente
- **400 Bad Request**: Solicitud malformada
- **401 Unauthorized**: Autenticación requerida
- **403 Forbidden**: Acceso denegado
- **404 Not Found**: Recurso no encontrado
- **405 Method Not Allowed**: Método HTTP no permitido para este recurso

#### 5xx - Errores del Servidor
- **500 Internal Server Error**: Error interno del servidor
- **502 Bad Gateway**: Error de gateway
- **503 Service Unavailable**: Servicio no disponible temporalmente

### 1.5 Headers HTTP Importantes

Los headers proporcionan metadatos sobre la solicitud o respuesta:

- **Content-Type**: Tipo de contenido (text/html, application/json, etc.)
- **Content-Length**: Tamaño del cuerpo en bytes
- **Host**: Dominio del servidor (obligatorio en HTTP/1.1)
- **User-Agent**: Información sobre el cliente
- **Accept**: Tipos de contenido que el cliente puede procesar
- **Authorization**: Credenciales de autenticación
- **Cookie**: Datos de sesión del cliente

---

## 2. El Módulo http.server de Python

### 2.1 De Sockets a Servidores HTTP

En nuestro trabajo previo con sockets, vimos cómo establecer comunicación directa entre procesos utilizando TCP. Sin embargo, cuando cada aplicación define su propio protocolo de comunicación, el resultado puede ser caótico y poco interoperable. Aquí es donde entran los protocolos estandarizados de capa de aplicación como HTTP.

El módulo `http.server` de Python nos permite dar el salto desde los sockets raw hacia un servidor web completamente funcional. Este módulo forma parte de la biblioteca estándar de Python y está construido sobre los mismos fundamentos de sockets que ya conocemos, pero añade toda la infraestructura necesaria para manejar el protocolo HTTP.

**Importante**: Este módulo está diseñado principalmente para desarrollo, pruebas y aprendizaje. No debe usarse en entornos de producción debido a limitaciones de seguridad y rendimiento.

### 2.2 Arquitectura y Diseño del Módulo

El módulo `http.server` sigue un patrón de diseño elegante que separa las responsabilidades en dos componentes principales: el **servidor** (que maneja las conexiones de red) y el **handler** (que procesa las solicitudes HTTP).

Esta separación nos resulta familiar si recordamos nuestro trabajo con sockets: el servidor se encarga de la parte de red (similar a nuestros `socket.bind()` y `socket.listen()`), mientras que el handler maneja la lógica de aplicación (similar a lo que hacíamos en nuestro bucle de procesamiento de conexiones).

La jerarquía de clases del módulo se estructura de la siguiente manera:

```
socketserver.BaseServer
    └── socketserver.TCPServer
        └── http.server.HTTPServer
            └── http.server.ThreadingHTTPServer

socketserver.BaseRequestHandler
    └── http.server.BaseHTTPRequestHandler
        └── http.server.SimpleHTTPRequestHandler
        └── http.server.CGIHTTPRequestHandler
```

### 2.3 Los Servidores: HTTPServer y ThreadingHTTPServer

#### HTTPServer: El Servidor Base

La clase `HTTPServer` es nuestra puerta de entrada al mundo de los servidores web. Esta clase extiende `socketserver.TCPServer` (que a su vez está construido sobre sockets TCP que ya conocemos) y añade la capacidad de entender y procesar solicitudes HTTP.

Cuando creamos un `HTTPServer`, internamente este realiza las mismas operaciones que hacíamos manualmente con sockets: crea un socket TCP, lo vincula a una dirección y puerto, y entra en modo de escucha. La diferencia radica en que ahora toda esta complejidad está encapsulada y el servidor puede automáticamente parsear solicitudes HTTP entrantes.

```python
import http.server

# Esto internamente crea un socket TCP y lo configura para HTTP
servidor = http.server.HTTPServer(('localhost', 8080), MiHandler)
```

#### ThreadingHTTPServer: Concurrencia Simplificada

Una de las limitaciones que enfrentábamos al trabajar directamente con sockets era el manejo de múltiples conexiones simultáneas. Teníamos que implementar manualmente threading o usar técnicas de multiplexación.

`ThreadingHTTPServer` resuelve este problema de manera elegante: automáticamente crea un nuevo hilo para cada solicitud entrante. Esto significa que nuestro servidor puede manejar múltiples clientes simultáneamente sin que tengamos que escribir código adicional de threading.

```python
# Servidor que maneja automáticamente múltiples conexiones
servidor = http.server.ThreadingHTTPServer(('localhost', 8080), MiHandler)
```

### 2.4 Los Handlers: Del Simple al Personalizado

#### SimpleHTTPRequestHandler: Funcionalidad Lista para Usar

`SimpleHTTPRequestHandler` es probablemente la forma más rápida de tener un servidor web funcionando. Esta clase implementa automáticamente un servidor de archivos estáticos completo. Con solo unas pocas líneas de código, obtenemos:

1. **Servir archivos estáticos**: Cualquier archivo en el directorio actual (o especificado) se puede servir automáticamente
2. **Listado de directorios**: Si accedemos a un directorio que no contiene un archivo index, el servidor genera automáticamente una página HTML con el listado de archivos
3. **Tipos MIME automáticos**: El servidor detecta automáticamente el tipo de contenido basándose en la extensión del archivo
4. **Manejo de errores**: Respuestas 404 automáticas para archivos inexistentes

```python
import http.server
import socketserver

PORT = 8000

# Un servidor web completo en 3 líneas
Handler = http.server.SimpleHTTPRequestHandler
with socketserver.TCPServer(("", PORT), Handler) as httpd:
    httpd.serve_forever()
```

#### BaseHTTPRequestHandler: La Base para Personalización

Cuando necesitamos comportamiento personalizado, `BaseHTTPRequestHandler` es nuestra clase base. Esta clase maneja automáticamente el parsing de solicitudes HTTP y nos proporciona una interfaz limpia para implementar nuestros propios servidores.

La filosofía de esta clase es simple pero poderosa: por cada método HTTP que queramos soportar, implementamos un método `do_METODO()`. Por ejemplo:

```python
class MiHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        # Lógica para manejar solicitudes GET
        pass
    
    def do_POST(self):
        # Lógica para manejar solicitudes POST
        pass
```

### 2.5 Anatomía de un Handler Personalizado

Cuando creamos un handler personalizado, tenemos acceso a varios atributos y métodos que nos facilitan el trabajo:

#### Atributos Importantes

- `self.path`: La ruta solicitada (ej: "/usuarios/123")
- `self.headers`: Los headers de la solicitud como un diccionario
- `self.rfile`: Stream de lectura para el cuerpo de la solicitud
- `self.wfile`: Stream de escritura para enviar la respuesta

#### Métodos para Construir Respuestas

El proceso de enviar una respuesta HTTP sigue siempre el mismo patrón: primero enviamos el código de estado, luego los headers, y finalmente el cuerpo.

```python
def do_GET(self):
    # 1. Enviar código de estado
    self.send_response(200)
    
    # 2. Enviar headers
    self.send_header('Content-type', 'text/html')
    self.send_header('Cache-Control', 'no-cache')
    
    # 3. Finalizar headers
    self.end_headers()
    
    # 4. Enviar cuerpo de la respuesta
    self.wfile.write(b'<h1>¡Hola Mundo!</h1>')
```

### 2.6 Ejemplo Práctico: De Simple a Sofisticado

Veamos cómo evolucionar desde un servidor básico hasta uno más sofisticado:

#### Paso 1: Servidor de Archivos Básico

```python
import http.server
import socketserver

PORT = 8000
Handler = http.server.SimpleHTTPRequestHandler

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Servidor ejecutándose en puerto {PORT}")
    httpd.serve_forever()
```

#### Paso 2: Handler Personalizado con Rutas

```python
import http.server
import json
from urllib.parse import urlparse, parse_qs

class CustomHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        # Parseamos la URL para extraer la ruta y parámetros
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/':
            self._send_html_response('<h1>Página Principal</h1>')
        elif parsed_path.path == '/api/status':
            self._send_json_response({'status': 'active', 'version': '1.0'})
        else:
            self._send_error_response(404, 'Página no encontrada')
    
    def do_POST(self):
        # Leemos el cuerpo de la solicitud
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            # Intentamos parsear como JSON
            data = json.loads(post_data.decode('utf-8'))
            response = {'received': data, 'timestamp': time.time()}
            self._send_json_response(response)
        except json.JSONDecodeError:
            self._send_error_response(400, 'JSON inválido')
    
    def _send_html_response(self, content):
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(content.encode('utf-8'))
    
    def _send_json_response(self, data):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def _send_error_response(self, code, message):
        self.send_response(code)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(message.encode())

# Iniciar servidor con threading para manejar múltiples conexiones
if __name__ == "__main__":
    PORT = 8080
    with http.server.ThreadingHTTPServer(("", PORT), CustomHandler) as httpd:
        print(f"Servidor ejecutándose en http://localhost:{PORT}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nCerrando servidor...")
```

### 2.7 Ventajas del Módulo http.server

Al usar `http.server` en lugar de implementar HTTP manualmente sobre sockets, obtenemos:

1. **Parsing automático**: No necesitamos parsear manualmente las solicitudes HTTP
2. **Manejo de headers**: Los headers se parsean automáticamente en un objeto tipo diccionario
3. **Códigos de estado**: Métodos convenientes para enviar respuestas HTTP válidas
4. **Logging**: Sistema de logging integrado que registra todas las solicitudes
5. **Manejo de errores**: Respuestas de error HTTP estándar automáticas
6. **Threading**: Concurrencia simple con `ThreadingHTTPServer`

### 2.8 Limitaciones y Consideraciones

Aunque `http.server` es excelente para aprendizaje y desarrollo, tiene limitaciones importantes:

- **Seguridad**: No incluye protecciones contra ataques comunes
- **Rendimiento**: No está optimizado para alta concurrencia
- **Funcionalidades**: Carece de características avanzadas como compresión, caching, etc.
- **Robustez**: No maneja casos edge como timeouts, límites de tamaño, etc.

Para aplicaciones de producción, se recomiendan servidores como Nginx, Apache, o frameworks como Flask/Django con servidores WSGI/ASGI optimizados.

---

## 3. Herramientas de Testing

### 3.1 Navegador Web
La forma más simple de probar solicitudes GET es usando un navegador web dirigiéndose a `http://localhost:puerto`.

### 3.2 curl
Herramienta de línea de comandos para realizar solicitudes HTTP:

```bash
# GET request
curl http://localhost:8080/

# POST con datos
curl -X POST -d "datos=test" http://localhost:8080/api

# Ver headers de respuesta
curl -i http://localhost:8080/

# POST con JSON
curl -X POST \
     -H "Content-Type: application/json" \
     -d '{"nombre": "test"}' \
     http://localhost:8080/api
```

### 3.3 Apache Benchmark (ab)
Para pruebas de carga y rendimiento:

```bash
# 100 solicitudes con concurrencia de 10
ab -n 100 -c 10 http://localhost:8080/

# POST con archivo de datos
ab -n 50 -c 5 -p datos.txt -T application/json http://localhost:8080/api
```

---

## Ejercicios Prácticos

### Ejercicio 1: Servidor de Archivos Básico
Crea un servidor HTTP que sirva archivos estáticos desde un directorio específico. El servidor debe:
- Responder a solicitudes GET
- Servir archivos HTML, CSS, JS e imágenes
- Mostrar un listado de directorio cuando se accede a una carpeta
- Devolver 404 para archivos inexistentes

### Ejercicio 2: API REST Básica
Implementa un servidor que simule una API REST para gestionar una lista de usuarios. Debe soportar:
- `GET /users` - Listar todos los usuarios
- `GET /users/id` - Obtener un usuario específico
- `POST /users` - Crear un nuevo usuario
- `PUT /users/id` - Actualizar un usuario existente
- `DELETE /users/id` - Eliminar un usuario

Los datos pueden almacenarse en memoria (lista/diccionario).

### Ejercicio 3: Servidor de Formularios
Crea un servidor que:
- Sirva un formulario HTML en `GET /`
- Procese los datos del formulario en `POST /submit`
- Muestre una página de confirmación con los datos recibidos
- Maneje diferentes tipos de input (text, email, select, checkbox)

### Ejercicio 4: Servidor de Upload de Archivos
Implementa un servidor que permita subir archivos:
- Página con formulario de upload en `GET /upload`
- Procesamiento del archivo en `POST /upload`
- Listado de archivos subidos en `GET /files`
- Descarga de archivos en `GET /files/nombre`

### Ejercicio 5: API con Autenticación Básica
Extiende la API del Ejercicio 2 para incluir:
- Autenticación HTTP Basic
- Diferentes niveles de acceso (lectura/escritura)
- Logging de todas las solicitudes con timestamp
- Rate limiting básico (máximo X solicitudes por minuto)

### Ejercicio 6: Servidor de Chat Simple
Crea un servidor que implemente un chat básico:
- Página web con JavaScript para el chat
- `POST /messages` - Enviar un mensaje
- `GET /messages` - Obtener mensajes (con polling)
- `GET /messages/since/timestamp` - Obtener mensajes desde un tiempo específico
- Almacenamiento en memoria con límite de mensajes

---

## Conclusión

El módulo `http.server` nos proporciona una excelente introducción a los protocolos de capa de aplicación, mostrándonos cómo construir sobre los fundamentos de sockets que ya conocemos. Aunque simple, nos permite comprender los conceptos fundamentales de HTTP y prepararnos para herramientas más avanzadas.

En el próximo tema exploraremos el módulo `socketserver`, que nos dará aún más control y flexibilidad para construir servidores de red robustos y eficientes.