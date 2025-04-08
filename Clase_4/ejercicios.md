# 7 Ejercicios Prácticos sobre Pipes

## Enunciados

### Ejercicio 1: Eco Simple
Crea un programa en Python que establezca comunicación entre un proceso padre y un hijo mediante un pipe. El padre debe enviar un mensaje al hijo, y el hijo debe recibir ese mensaje y devolverlo al padre (eco).

### Ejercicio 2: Contador de Palabras
Implementa un sistema donde el proceso padre lee un archivo de texto y envía su contenido línea por línea a un proceso hijo a través de un pipe. El hijo debe contar las palabras en cada línea y devolver el resultado al padre.

### Ejercicio 3: Pipeline de Filtrado
Crea una cadena de tres procesos conectados por pipes donde: el primer proceso genera números aleatorios entre 1 y 100, el segundo proceso filtra solo los números pares, y el tercer proceso calcula el cuadrado de estos números pares.

### Ejercicio 4: Simulador de Shell
Implementa un programa que simule una versión simplificada del operador pipe (|) de la shell. El programa debe ejecutar dos comandos proporcionados por el usuario y conectar la salida del primero con la entrada del segundo.

### Ejercicio 5: Chat Bidireccional
Desarrolla un sistema de chat simple entre dos procesos usando pipes. Cada proceso debe poder enviar y recibir mensajes simultáneamente, implementando una comunicación bidireccional completa.

### Ejercicio 6: Servidor de Operaciones Matemáticas
Crea un "servidor" de operaciones matemáticas usando pipes. El proceso cliente envía operaciones matemáticas como cadenas (por ejemplo, "5 + 3", "10 * 2"), y el servidor las evalúa y devuelve el resultado. Implementa manejo de errores para operaciones inválidas.

### Ejercicio 7: Sistema de Procesamiento de Transacciones
Implementa un sistema donde múltiples procesos "generadores" crean transacciones (operaciones con un ID, tipo y monto), las envían a un proceso "validador" que verifica su integridad, y finalmente a un proceso "registrador" que acumula las estadísticas. Usa múltiples pipes para manejar este flujo complejo y asegúrate de manejar correctamente la sincronización y el cierre de la comunicación.

## Soluciones Detalladas

### Solución Ejercicio 1: Eco Simple

```python
import os
import sys

def main():
    # Crear dos pipes: uno para enviar del padre al hijo, otro para recibir respuesta
    parent_to_child_r, parent_to_child_w = os.pipe()
    child_to_parent_r, child_to_parent_w = os.pipe()
    
    # Bifurcar el proceso
    pid = os.fork()
    
    if pid > 0:  # Proceso padre
        # Cerrar extremos no utilizados
        os.close(parent_to_child_r)
        os.close(child_to_parent_w)
        
        # Mensaje a enviar
        message = "Hola, proceso hijo!"
        print(f"Padre: Enviando mensaje: '{message}'")
        
        # Enviar mensaje al hijo
        os.write(parent_to_child_w, message.encode())
        os.close(parent_to_child_w)  # Cerrar después de escribir
        
        # Recibir respuesta del hijo
        response = os.read(child_to_parent_r, 1024).decode()
        os.close(child_to_parent_r)  # Cerrar después de leer
        
        print(f"Padre: Recibí respuesta: '{response}'")
        
        # Esperar a que el hijo termine
        os.waitpid(pid, 0)
        
    else:  # Proceso hijo
        # Cerrar extremos no utilizados
        os.close(parent_to_child_w)
        os.close(child_to_parent_r)
        
        # Leer mensaje del padre
        message = os.read(parent_to_child_r, 1024).decode()
        os.close(parent_to_child_r)  # Cerrar después de leer
        
        print(f"Hijo: Recibí mensaje: '{message}'")
        
        # Enviar eco al padre
        os.write(child_to_parent_w, message.encode())
        os.close(child_to_parent_w)  # Cerrar después de escribir
        
        # Salir del proceso hijo
        sys.exit(0)

if __name__ == "__main__":
    main()
```

**Explicación:**
1. Creamos dos pipes para comunicación bidireccional: uno para que el padre envíe mensajes al hijo y otro para que el hijo responda al padre.
2. Después de bifurcar el proceso con `os.fork()`, asignamos roles diferentes al padre y al hijo.
3. Cerramos cuidadosamente los extremos de los pipes que cada proceso no utilizará, lo que es una buena práctica para evitar deadlocks.
4. El padre envía un mensaje, el hijo lo lee y envía el mismo mensaje de vuelta como eco.
5. Cada proceso cierra sus descriptores de archivo después de usarlos.
6. El padre espera a que el hijo termine antes de finalizar.

Este ejercicio ilustra los conceptos básicos de comunicación bidireccional usando pipes y la correcta gestión de descriptores de archivo.

### Solución Ejercicio 2: Contador de Palabras

```python
import os
import sys

def main():
    # Crear pipes para la comunicación
    content_pipe_r, content_pipe_w = os.pipe()  # Para enviar contenido del archivo
    count_pipe_r, count_pipe_w = os.pipe()      # Para enviar conteos de palabras
    
    # Bifurcar el proceso
    pid = os.fork()
    
    if pid > 0:  # Proceso padre
        # Cerrar extremos no utilizados
        os.close(content_pipe_r)
        os.close(count_pipe_w)
        
        # Nombre del archivo a procesar
        filename = "sample_text.txt"
        
        try:
            # Si el archivo no existe, creamos uno de ejemplo
            if not os.path.exists(filename):
                with open(filename, 'w') as f:
                    f.write("Este es un archivo de ejemplo.\n")
                    f.write("Contiene algunas líneas de texto.\n")
                    f.write("Para demostrar el contador de palabras.\n")
                    f.write("Usando pipes en Python.")
            
            # Abrir y leer el archivo
            with open(filename, 'r') as file:
                print(f"Padre: Leyendo archivo '{filename}'")
                
                # Convertir el descriptor a un objeto de archivo para escritura
                pipe_writer = os.fdopen(content_pipe_w, 'w')
                
                # Enviar cada línea al hijo
                line_count = 0
                for line in file:
                    pipe_writer.write(line)
                    pipe_writer.flush()  # Importante para asegurar que los datos se envíen
                    line_count += 1
                
                print(f"Padre: Enviadas {line_count} líneas al hijo")
                pipe_writer.close()  # Esto cierra content_pipe_w
                
                # Leer resultados del hijo
                pipe_reader = os.fdopen(count_pipe_r, 'r')
                
                # Imprimir los conteos recibidos
                print("\nConteo de palabras por línea:")
                total_words = 0
                for i, count in enumerate(pipe_reader, 1):
                    count = int(count.strip())
                    total_words += count
                    print(f"Línea {i}: {count} palabras")
                
                print(f"\nTotal de palabras: {total_words}")
                pipe_reader.close()  # Esto cierra count_pipe_r
        
        except Exception as e:
            print(f"Error en el padre: {e}")
            # Cerrar los pipes en caso de error
            os.close(content_pipe_w)
            os.close(count_pipe_r)
        
        # Esperar a que el hijo termine
        os.waitpid(pid, 0)
        
    else:  # Proceso hijo
        try:
            # Cerrar extremos no utilizados
            os.close(content_pipe_w)
            os.close(count_pipe_r)
            
            # Convertir descriptores a objetos de archivo
            content_reader = os.fdopen(content_pipe_r, 'r')
            count_writer = os.fdopen(count_pipe_w, 'w')
            
            print("Hijo: Esperando líneas para contar palabras...")
            
            # Procesar cada línea recibida
            for line in content_reader:
                # Contar palabras (dividir por espacios)
                word_count = len(line.split())
                
                # Enviar conteo al padre
                count_writer.write(f"{word_count}\n")
                count_writer.flush()  # Asegurar que los datos se envíen
            
            # Cerrar los pipes
            content_reader.close()
            count_writer.close()
            
        except Exception as e:
            print(f"Error en el hijo: {e}")
            # Cerrar los pipes en caso de error
            os.close(content_pipe_r)
            os.close(count_pipe_w)
        
        # Salir del proceso hijo
        sys.exit(0)

if __name__ == "__main__":
    main()
```

**Explicación:**
1. Creamos dos pipes: uno para enviar el contenido del archivo del padre al hijo y otro para que el hijo devuelva los conteos al padre.
2. El padre lee un archivo línea por línea y envía cada línea al hijo a través del primer pipe.
3. El hijo lee cada línea, cuenta las palabras dividiendo por espacios y envía el conteo al padre a través del segundo pipe.
4. Utilizamos objetos de archivo Python (`os.fdopen()`) para una manipulación más conveniente de los pipes.
5. Implementamos manejo de errores para asegurar que los recursos se liberen correctamente en caso de problemas.
6. Si el archivo de ejemplo no existe, lo creamos automáticamente para facilitar la prueba.

Este ejercicio demuestra un patrón común en el procesamiento de datos con pipes: un proceso envía datos para ser procesados, y otro realiza el procesamiento y devuelve resultados.

### Solución Ejercicio 3: Pipeline de Filtrado

```python
import os
import sys
import random
import time

def generator_process(write_pipe):
    """Genera números aleatorios entre 1 y 100."""
    try:
        with os.fdopen(write_pipe, 'w') as pipe:
            print("Generador: Produciendo 10 números aleatorios...")
            for _ in range(10):
                num = random.randint(1, 100)
                pipe.write(f"{num}\n")
                pipe.flush()
                print(f"Generador: Generé el número {num}")
                time.sleep(0.5)  # Pequeña pausa para mejor visualización
    except Exception as e:
        print(f"Error en generador: {e}")
    finally:
        print("Generador: Terminando...")

def filter_process(read_pipe, write_pipe):
    """Filtra solo los números pares."""
    try:
        with os.fdopen(read_pipe, 'r') as in_pipe, os.fdopen(write_pipe, 'w') as out_pipe:
            print("Filtro: Filtrando números pares...")
            for line in in_pipe:
                num = int(line.strip())
                if num % 2 == 0:  # Solo procesar números pares
                    out_pipe.write(f"{num}\n")
                    out_pipe.flush()
                    print(f"Filtro: Pasando número par {num}")
                else:
                    print(f"Filtro: Descartando número impar {num}")
                time.sleep(0.3)  # Pequeña pausa
    except Exception as e:
        print(f"Error en filtro: {e}")
    finally:
        print("Filtro: Terminando...")

def square_process(read_pipe):
    """Calcula el cuadrado de los números recibidos."""
    try:
        with os.fdopen(read_pipe, 'r') as pipe:
            print("Cuadrador: Calculando cuadrados...")
            results = []
            for line in pipe:
                num = int(line.strip())
                square = num * num
                results.append((num, square))
                print(f"Cuadrador: {num}² = {square}")
                time.sleep(0.3)  # Pequeña pausa
            
            # Mostrar resumen final
            print("\nResultados finales:")
            for num, square in results:
                print(f"{num}² = {square}")
            print(f"Total de números procesados: {len(results)}")
    except Exception as e:
        print(f"Error en cuadrador: {e}")
    finally:
        print("Cuadrador: Terminando...")

def main():
    # Crear pipes para conectar los procesos
    pipe1_r, pipe1_w = os.pipe()  # Conecta generador -> filtro
    pipe2_r, pipe2_w = os.pipe()  # Conecta filtro -> cuadrador
    
    # Crear el primer proceso hijo (generador)
    pid1 = os.fork()
    
    if pid1 == 0:  # Proceso generador
        # Cerrar pipes no utilizados
        os.close(pipe1_r)
        os.close(pipe2_r)
        os.close(pipe2_w)
        
        # Ejecutar la función generadora
        generator_process(pipe1_w)
        sys.exit(0)
    
    # Crear el segundo proceso hijo (filtro)
    pid2 = os.fork()
    
    if pid2 == 0:  # Proceso filtro
        # Cerrar pipes no utilizados
        os.close(pipe1_w)
        os.close(pipe2_r)
        
        # Ejecutar la función de filtrado
        filter_process(pipe1_r, pipe2_w)
        sys.exit(0)
    
    # Proceso principal (cuadrador)
    # Cerrar pipes no utilizados
    os.close(pipe1_r)
    os.close(pipe1_w)
    os.close(pipe2_w)
    
    # Ejecutar la función cuadradora
    square_process(pipe2_r)
    
    # Esperar a que los procesos hijos terminen
    os.waitpid(pid1, 0)
    os.waitpid(pid2, 0)
    
    print("Pipeline completado.")

if __name__ == "__main__":
    main()
```

**Explicación:**
1. Implementamos tres procesos conectados mediante dos pipes, formando un pipeline de procesamiento:
   - El proceso generador produce números aleatorios.
   - El proceso filtro recibe estos números y solo deja pasar los pares.
   - El proceso cuadrador calcula el cuadrado de los números pares recibidos.
2. Cada proceso tiene su propia función dedicada con manejo de excepciones.
3. Usamos pequeñas pausas (sleep) para facilitar la visualización del flujo de datos.
4. Incluimos mensajes de depuración para mostrar cada paso del procesamiento.
5. El proceso principal (padre) cierra adecuadamente los descriptores que no utiliza y espera a que ambos hijos terminen.

Este ejercicio ilustra el poderoso patrón de pipeline, donde los datos fluyen a través de múltiples etapas de procesamiento, cada una realizando una transformación específica.

### Solución Ejercicio 4: Simulador de Shell

```python
import os
import sys
import subprocess

def simulate_pipe(cmd1, cmd2):
    """
    Simula el operador pipe (|) de la shell conectando
    la salida de cmd1 con la entrada de cmd2.
    """
    # Crear un pipe
    read_fd, write_fd = os.pipe()
    
    # Bifurcar para el primer comando
    pid1 = os.fork()
    
    if pid1 == 0:  # Proceso hijo para cmd1
        # Redirigir stdout al extremo de escritura del pipe
        os.close(read_fd)  # Cerrar el extremo de lectura que no usamos
        os.dup2(write_fd, sys.stdout.fileno())  # Redirigir stdout
        os.close(write_fd)  # Cerrar el descriptor original ahora que está duplicado
        
        # Ejecutar el primer comando
        try:
            cmd1_parts = cmd1.split()
            os.execvp(cmd1_parts[0], cmd1_parts)
        except Exception as e:
            print(f"Error executing {cmd1}: {e}", file=sys.stderr)
            sys.exit(1)
    
    # Bifurcar para el segundo comando
    pid2 = os.fork()
    
    if pid2 == 0:  # Proceso hijo para cmd2
        # Redirigir stdin al extremo de lectura del pipe
        os.close(write_fd)  # Cerrar el extremo de escritura que no usamos
        os.dup2(read_fd, sys.stdin.fileno())  # Redirigir stdin
        os.close(read_fd)  # Cerrar el descriptor original ahora que está duplicado
        
        # Ejecutar el segundo comando
        try:
            cmd2_parts = cmd2.split()
            os.execvp(cmd2_parts[0], cmd2_parts)
        except Exception as e:
            print(f"Error executing {cmd2}: {e}", file=sys.stderr)
            sys.exit(1)
    
    # Proceso padre: cerrar ambos extremos del pipe y esperar
    os.close(read_fd)
    os.close(write_fd)
    
    # Esperar a que ambos procesos terminen
    os.waitpid(pid1, 0)
    os.waitpid(pid2, 0)

def main():
    print("Simulador de Pipes de Shell")
    print("Ingrese 'exit' para salir")
    print("Ejemplo: ls -l | grep .py")
    
    while True:
        try:
            user_input = input("\n$ ")
            
            if user_input.lower() == 'exit':
                break
            
            # Verificar si el input contiene el operador pipe
            if '|' not in user_input:
                print("Error: Debe incluir el operador '|' para conectar dos comandos")
                continue
            
            # Dividir la entrada en dos comandos
            cmd1, cmd2 = [cmd.strip() for cmd in user_input.split('|', 1)]
            
            if not cmd1 or not cmd2:
                print("Error: Debe proporcionar dos comandos válidos")
                continue
            
            print(f"Ejecutando: '{cmd1}' | '{cmd2}'")
            simulate_pipe(cmd1, cmd2)
            
        except KeyboardInterrupt:
            print("\nInterrumpido por el usuario")
            break
        except Exception as e:
            print(f"Error: {e}")
    
    print("Saliendo del simulador")

if __name__ == "__main__":
    main()
```

**Explicación:**
1. Creamos un programa interactivo que simula el operador pipe (|) de la shell UNIX.
2. La función principal:
   - Solicita al usuario comandos separados por |
   - Divide el input en dos comandos (antes y después del |)
   - Llama a simulate_pipe() para ejecutar los comandos conectados
3. La función simulate_pipe():
   - Crea un pipe usando os.pipe()
   - Bifurca dos procesos hijos, uno para cada comando
   - Usa os.dup2() para redirigir stdout del primer proceso al pipe
   - Usa os.dup2() para redirigir stdin del segundo proceso desde el pipe
   - Usa os.execvp() para ejecutar los comandos del sistema
4. Implementamos manejo de errores y una forma de salir del programa.

Este ejercicio proporciona una visión profunda de cómo funciona realmente el operador pipe (|) en las shells UNIX, demostrando técnicas avanzadas como la redirección de descriptores de archivo y la ejecución de programas externos.

### Solución Ejercicio 5: Chat Bidireccional

```python
import os
import sys
import select
import signal
import threading

def setup_signal_handler():
    """Configura el manejador de señales para salir limpiamente con Ctrl+C"""
    def signal_handler(sig, frame):
        print("\nSaliendo del chat...")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)

def read_messages(pipe, name, should_exit):
    """Función para leer mensajes del pipe en un hilo separado"""
    with os.fdopen(pipe, 'r') as reader:
        while not should_exit[0]:
            # Usar select para comprobar si hay datos para leer sin bloquear
            readable, _, _ = select.select([reader], [], [], 0.5)
            if readable:
                message = reader.readline().strip()
                if message:
                    print(f"\n{name}: {message}")
                    print("Tú > ", end='', flush=True)
                else:
                    # EOF - el otro extremo cerró el pipe
                    print(f"\n{name} ha dejado el chat.")
                    should_exit[0] = True
                    break

def chat_process(read_pipe, write_pipe, name, other_name):
    """Gestiona el proceso de chat para un participante"""
    try:
        # Inicializar objeto para controlar la salida del hilo
        should_exit = [False]
        
        # Configurar el manejador de señales
        setup_signal_handler()
        
        # Crear un hilo para leer mensajes del otro participante
        reader_thread = threading.Thread(
            target=read_messages, 
            args=(read_pipe, other_name, should_exit)
        )
        reader_thread.daemon = True  # El hilo terminará cuando el programa principal termine
        reader_thread.start()
        
        # Abrir el pipe de escritura
        with os.fdopen(write_pipe, 'w') as writer:
            print(f"¡Bienvenido al chat, {name}!")
            print(f"Estás chateando con {other_name}.")
            print("Escribe 'exit' para salir.\n")
            
            # Bucle principal para enviar mensajes
            while not should_exit[0]:
                message = input(f"Tú > ")
                
                if message.lower() == 'exit':
                    print("Saliendo del chat...")
                    should_exit[0] = True
                    break
                
                # Enviar el mensaje
                writer.write(f"{message}\n")
                writer.flush()
        
    except Exception as e:
        print(f"Error en el proceso de chat: {e}")
    finally:
        # Asegurarse de que los descriptores se cierren
        try:
            os.close(read_pipe)
            os.close(write_pipe)
        except:
            pass  # Ignorar errores al cerrar descriptores ya cerrados

def main():
    # Crear pipes para comunicación bidireccional
    pipe_a_to_b_r, pipe_a_to_b_w = os.pipe()  # A envía a B
    pipe_b_to_a_r, pipe_b_to_a_w = os.pipe()  # B envía a A
    
    # Bifurcar el proceso
    pid = os.fork()
    
    if pid > 0:  # Proceso padre (participante A)
        # Cerrar extremos no utilizados
        os.close(pipe_a_to_b_r)
        os.close(pipe_b_to_a_w)
        
        # Gestionar el chat como participante A
        chat_process(pipe_b_to_a_r, pipe_a_to_b_w, "Participante A", "Participante B")
        
        # Esperar a que el proceso hijo termine
        try:
            os.waitpid(pid, 0)
        except:
            pass
        
    else:  # Proceso hijo (participante B)
        # Cerrar extremos no utilizados
        os.close(pipe_a_to_b_w)
        os.close(pipe_b_to_a_r)
        
        # Gestionar el chat como participante B
        chat_process(pipe_a_to_b_r, pipe_b_to_a_w, "Participante B", "Participante A")
        
        # Salir del proceso hijo
        sys.exit(0)

if __name__ == "__main__":
    main()
```

**Explicación:**
1. Implementamos un sistema de chat bidireccional completo entre dos procesos.
2. Utilizamos cuatro descriptores de archivo para crear dos pipes, uno para cada dirección de comunicación:
   - pipe_a_to_b para que A envíe mensajes a B
   - pipe_b_to_a para que B envíe mensajes a A
3. Cada proceso maneja el envío y recepción de mensajes simultáneamente:
   - Un hilo dedicado espera nuevos mensajes entrantes
   - El hilo principal se encarga de capturar la entrada del usuario y enviarla
4. Empleamos `select.select()` para verificar si hay datos disponibles para leer sin bloquear el hilo.
5. Implementamos un mecanismo para salir limpiamente del chat, tanto por comando del usuario como por señal (Ctrl+C).
6. Utilizamos manejo de excepciones para asegurar que los recursos se liberen correctamente en todos los casos.

Este ejercicio demuestra cómo implementar comunicación bidireccional completa entre procesos, incluyendo aspectos avanzados como la gestión de múltiples descriptores de archivo, hilos y señales.

### Solución Ejercicio 6: Servidor de Operaciones Matemáticas

```python
import os
import sys
import re
import signal
import time

def setup_signal_handler():
    """Configura el manejador de señales para salir limpiamente con Ctrl+C"""
    def signal_handler(sig, frame):
        print("\nFinalizando servidor...")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)

def math_server(request_pipe, response_pipe):
    """
    Proceso servidor que recibe operaciones matemáticas,
    las evalúa y devuelve el resultado.
    """
    try:
        print("Servidor: Iniciando servidor de operaciones matemáticas...")
        
        # Abrir pipes para lectura/escritura
        with os.fdopen(request_pipe, 'r') as requests, os.fdopen(response_pipe, 'w') as responses:
            while True:
                # Leer una operación del cliente
                operation = requests.readline().strip()
                
                if not operation or operation.lower() == "exit":
                    print("Servidor: Recibida señal de finalización")
                    break
                
                print(f"Servidor: Recibida operación: '{operation}'")
                
                # Procesar la operación con un pequeño retraso para simular procesamiento
                time.sleep(0.5)
                result = evaluate_expression(operation)
                
                # Enviar el resultado al cliente
                responses.write(f"{result}\n")
                responses.flush()
                print(f"Servidor: Enviado resultado: '{result}'")
                
    except Exception as e:
        print(f"Error en el servidor: {e}")
    finally:
        print("Servidor: Finalizando...")

def evaluate_expression(expression):
    """
    Evalúa una expresión matemática y devuelve el resultado.
    Maneja errores y validaciones.
    """
    try:
        # Verificar si la expresión tiene formato válido
        if not re.match(r'^[\d\s\+\-\*\/\(\)\.]+$', expression):
            return "ERROR: Expresión inválida. Solo se permiten números y operadores +,-,*,/,(,)"
        
        # Evaluar la expresión de forma segura
        # Limitamos a operaciones matemáticas básicas
        result = eval(expression)
        return str(result)
        
    except ZeroDivisionError:
        return "ERROR: División por cero"
    except SyntaxError:
        return "ERROR: Sintaxis incorrecta"
    except Exception as e:
        return f"ERROR: {str(e)}"

def math_client(request_pipe, response_pipe):
    """
    Proceso cliente que envía operaciones matemáticas al servidor
    y muestra los resultados.
    """
    try:
        print("\nCliente: Conectando al servidor de operaciones matemáticas...")
        print("Ingrese operaciones matemáticas o 'exit' para salir")
        print("Ejemplos: '5 + 3', '10 * (2 + 3)', '15 / 2'")
        
        # Abrir pipes para lectura/escritura
        with os.fdopen(request_pipe, 'w') as requests, os.fdopen(response_pipe, 'r') as responses:
            while True:
                # Solicitar una operación al usuario
                expression = input("\nIngrese operación > ")
                
                if expression.lower() == "exit":
                    print("Cliente: Enviando señal de finalización al servidor")
                    requests.write("exit\n")
                    requests.flush()
                    break
                
                # Enviar la operación al servidor
                requests.write(f"{expression}\n")
                requests.flush()
                print(f"Cliente: Enviada operación: '{expression}'")
                
                # Recibir y mostrar el resultado
                result = responses.readline().strip()
                if result.startswith("ERROR"):
                    print(f"Cliente: Error - {result}")
                else:
                    print(f"Cliente: Resultado: {expression} = {result}")
    
    except Exception as e:
        print(f"Error en el cliente: {e}")
    finally:
        print("Cliente: Finalizando...")

def main():
    # Configurar manejador de señales
    setup_signal_handler()
    
    # Crear pipes para comunicación bidireccional
    client_to_server_r, client_to_server_w = os.pipe()  # Cliente -> Servidor
    server_to_client_r, server_to_client_w = os.pipe()  # Servidor -> Cliente
    
    # Bifurcar el proceso
    pid = os.fork()
    
    if pid > 0:  # Proceso padre (cliente)
        # Cerrar extremos no utilizados
        os.close(client_to_server_r)
        os.close(server_to_client_w)
        
        # Ejecutar cliente
        math_client(client_to_server_w, server_to_client_r)
        
        # Esperar a que el servidor termine
        try:
            os.waitpid(pid, 0)
        except:
            pass
        
        print("Terminando programa")
        
    else:  # Proceso hijo (servidor)
        # Cerrar extremos no utilizados
        os.close(client_to_server_w)
        os.close(server_to_client_r)
        
        # Ejecutar servidor
        math_server(client_to_server_r, server_to_client_w)
        
        # Salir del proceso hijo
        sys.exit(0)

if __name__ == "__main__":
    main()
```

**Explicación:**
1. Implementamos un sistema cliente-servidor para operaciones matemáticas utilizando pipes para la comunicación.
2. El programa crea dos pipes para establecer comunicación bidireccional entre cliente y servidor:
   - Un pipe para enviar solicitudes del cliente al servidor
   - Un pipe para enviar respuestas del servidor al cliente
3. El servidor:
   - Recibe expresiones matemáticas como cadenas
   - Valida y evalúa las expresiones usando la función `eval()` con medidas de seguridad
   - Maneja diferentes tipos de errores (división por cero, sintaxis incorrecta, etc.)
   - Envía resultados o mensajes de error al cliente
4. El cliente:
   - Proporciona una interfaz interactiva para el usuario
   - Envía las expresiones al servidor y muestra los resultados
   - Permite salir limpiamente con el comando "exit"
5. Implementamos validación con expresiones regulares para evitar la ejecución de código arbitrario.
6. Usamos manejadores de señales para una terminación limpia con Ctrl+C.

Este ejercicio demuestra un patrón cliente-servidor completo utilizando pipes, incluyendo aspectos de seguridad, manejo de errores, y comunicación bidireccional.

### Solución Ejercicio 7: Sistema de Procesamiento de Transacciones

```python
import os
import sys
import time
import random
import json
from collections import defaultdict

# Estructura para representar una transacción
class Transaction:
    def __init__(self, id=None, tipo=None, monto=None):
        self.id = id or random.randint(1000, 9999)
        self.tipo = tipo or random.choice(["deposito", "retiro", "transferencia", "pago"])
        self.monto = monto or round(random.uniform(10.0, 1000.0), 2)
    
    def to_json(self):
        """Convierte la transacción a formato JSON para transmisión"""
        return json.dumps({
            "id": self.id,
            "tipo": self.tipo,
            "monto": self.monto
        })
    
    @classmethod
    def from_json(cls, json_str):
        """Crea una transacción desde una cadena JSON"""
        try:
            data = json.loads(json_str)
            return cls(data["id"], data["tipo"], data["monto"])
        except Exception as e:
            print(f"Error al deserializar transacción: {e}")
            return None
    
    def __str__(self):
        return f"Transacción #{self.id}: {self.tipo} ${self.monto:.2f}"

def generator_process(name, write_pipe, num_transactions):
    """
    Proceso generador que crea transacciones aleatorias
    y las envía al validador.
    """
    try:
        with os.fdopen(write_pipe, 'w') as pipe:
            print(f"Generador {name}: Iniciando generación de {num_transactions} transacciones")
            
            for i in range(num_transactions):
                # Crear una transacción aleatoria
                transaction = Transaction()
                
                # Enviarla al validador
                pipe.write(transaction.to_json() + "\n")
                pipe.flush()
                
                print(f"Generador {name}: Enviada {transaction}")
                
                # Pequeña pausa aleatoria
                time.sleep(random.uniform(0.3, 0.8))
            
            # Enviar señal de finalización
            pipe.write("END\n")
            pipe.flush()
            print(f"Generador {name}: Finalizando")
            
    except Exception as e:
        print(f"Error en generador {name}: {e}")

def validator_process(read_pipes, write_pipe):
    """
    Proceso validador que recibe transacciones de múltiples generadores,
    verifica su validez y las pasa al registrador.
    """
    try:
        # Abrir todos los pipes de lectura y el pipe de escritura
        readers = [os.fdopen(pipe, 'r') for pipe in read_pipes]
        writer = os.fdopen(write_pipe, 'w')
        
        active_readers = len(readers)
        transactions_processed = 0
        transactions_valid = 0
        transactions_invalid = 0
        
        print(f"Validador: Iniciando con {active_readers} generadores")
        
        # Procesar mientras haya generadores activos
        while active_readers > 0:
            for i, reader in enumerate(readers):
                if reader is None:
                    continue  # Saltear pipes cerrados
                
                # Leer una línea (no bloqueante)
                line = reader.readline().strip()
                
                if not line:
                    continue  # No hay datos disponibles, continuar
                
                if line == "END":
                    print(f"Validador: Generador {i} ha terminado")
                    readers[i] = None  # Marcar el reader como inactivo
                    active_readers -= 1
                    continue
                
                # Procesar la transacción
                transactions_processed += 1
                
                try:
                    # Deserializar la transacción
                    transaction = Transaction.from_json(line)
                    
                    # Validar la transacción (reglas de ejemplo)
                    valid = True
                    error_msg = None
                    
                    if transaction.monto <= 0:
                        valid = False
                        error_msg = "Monto debe ser positivo"
                    elif transaction.tipo == "retiro" and transaction.monto > 500:
                        valid = False
                        error_msg = "Retiros no pueden exceder $500"
                    
                    # Enviar al registrador (con resultado de validación)
                    result = {
                        "transaction": transaction.__dict__,
                        "valid": valid,
                        "error": error_msg,
                        "timestamp": time.time()
                    }
                    
                    writer.write(json.dumps(result) + "\n")
                    writer.flush()
                    
                    if valid:
                        transactions_valid += 1
                        print(f"Validador: Transacción #{transaction.id} válida")
                    else:
                        transactions_invalid += 1
                        print(f"Validador: Transacción #{transaction.id} inválida: {error_msg}")
                
                except Exception as e:
                    print(f"Validador: Error procesando transacción: {e}")
            
            # Pequeña pausa para no saturar la CPU
            time.sleep(0.1)
        
        # Enviar estadísticas finales al registrador
        stats = {
            "final_stats": True,
            "processed": transactions_processed,
            "valid": transactions_valid,
            "invalid": transactions_invalid
        }
        
        writer.write(json.dumps(stats) + "\n")
        writer.flush()
        writer.write("END\n")
        writer.flush()
        
        print(f"Validador: Finalizado. Procesadas {transactions_processed} transacciones")
        
    except Exception as e:
        print(f"Error en validador: {e}")
    finally:
        # Cerrar todos los pipes
        for reader in readers:
            if reader is not None:
                reader.close()
        writer.close()

def logger_process(read_pipe):
    """
    Proceso registrador que recibe transacciones validadas
    y mantiene estadísticas.
    """
    try:
        # Estadísticas
        stats = {
            "total_valid": 0,
            "total_invalid": 0,
            "total_amount": 0,
            "by_type": defaultdict(int),
            "by_type_amount": defaultdict(float)
        }
        
        transactions = []
        
        with os.fdopen(read_pipe, 'r') as reader:
            print("Registrador: Iniciando registro de transacciones")
            
            while True:
                line = reader.readline().strip()
                
                if not line:
                    continue
                
                if line == "END":
                    break
                
                data = json.loads(line)
                
                # Verificar si son estadísticas finales
                if data.get("final_stats"):
                    print("\nRegistrador: Recibidas estadísticas finales del validador:")
                    print(f"  Total procesadas: {data['processed']}")
                    print(f"  Válidas: {data['valid']}")
                    print(f"  Inválidas: {data['invalid']}")
                    continue
                
                # Procesar la transacción validada
                transaction = data["transaction"]
                valid = data["valid"]
                
                if valid:
                    stats["total_valid"] += 1
                    stats["total_amount"] += transaction["monto"]
                    stats["by_type"][transaction["tipo"]] += 1
                    stats["by_type_amount"][transaction["tipo"]] += transaction["monto"]
                    
                    # Guardar para resumen final
                    transactions.append(transaction)
                else:
                    stats["total_invalid"] += 1
                
                # Mostrar progreso
                total = stats["total_valid"] + stats["total_invalid"]
                if total % 5 == 0:  # Mostrar cada 5 transacciones
                    print(f"Registrador: Procesadas {total} transacciones hasta ahora")
            
            # Mostrar resumen final
            print("\n===== RESUMEN FINAL DE TRANSACCIONES =====")
            print(f"Total de transacciones válidas: {stats['total_valid']}")
            print(f"Total de transacciones inválidas: {stats['total_invalid']}")
            print(f"Monto total procesado: ${stats['total_amount']:.2f}")
            
            print("\nTransacciones por tipo:")
            for tipo, count in stats["by_type"].items():
                amount = stats["by_type_amount"][tipo]
                print(f"  {tipo.capitalize()}: {count} transacciones, ${amount:.2f}")
            
            # Mostrar las 5 transacciones más grandes
            if transactions:
                print("\nTop 5 transacciones por monto:")
                top_transactions = sorted(transactions, key=lambda x: x["monto"], reverse=True)[:5]
                for i, t in enumerate(top_transactions, 1):
                    print(f"  {i}. #{t['id']} ({t['tipo']}): ${t['monto']:.2f}")
            
            print("==========================================")
            
    except Exception as e:
        print(f"Error en registrador: {e}")

def main():
    # Número de generadores
    num_generators = 3
    
    # Pipes para comunicación generadores -> validador
    gen_to_val_pipes = []
    for i in range(num_generators):
        r, w = os.pipe()
        gen_to_val_pipes.append((r, w))
    
    # Pipe para comunicación validador -> registrador
    val_to_log_r, val_to_log_w = os.pipe()
    
    # Crear procesos generadores
    generator_pids = []
    for i in range(num_generators):
        pid = os.fork()
        
        if pid == 0:  # Proceso hijo (generador)
            # Cerrar todos los pipes excepto el de escritura de este generador
            for j, (r, w) in enumerate(gen_to_val_pipes):
                if j != i:
                    os.close(r)
                    os.close(w)
                else:
                    os.close(r)  # Solo necesitamos el extremo de escritura
            
            # Cerrar el pipe validador -> registrador
            os.close(val_to_log_r)
            os.close(val_to_log_w)
            
            # Ejecutar el proceso generador
            generator_process(f"G{i+1}", gen_to_val_pipes[i][1], 
                            random.randint(8, 15))  # Generar entre 8-15 transacciones
            
            # Salir del proceso hijo
            sys.exit(0)
        
        generator_pids.append(pid)
    
    # Crear proceso validador
    val_pid = os.fork()
    
    if val_pid == 0:  # Proceso hijo (validador)
        # Cerrar extremos no utilizados de los pipes generador -> validador
        for r, w in gen_to_val_pipes:
            os.close(w)  # Solo necesitamos los extremos de lectura
        
        # Cerrar extremo de lectura del pipe validador -> registrador
        os.close(val_to_log_r)
        
        # Ejecutar el proceso validador
        validator_process([r for r, _ in gen_to_val_pipes], val_to_log_w)
        
        # Salir del proceso hijo
        sys.exit(0)
    
    # Crear proceso registrador
    log_pid = os.fork()
    
    if log_pid == 0:  # Proceso hijo (registrador)
        # Cerrar todos los pipes generador -> validador
        for r, w in gen_to_val_pipes:
            os.close(r)
            os.close(w)
        
        # Cerrar extremo de escritura del pipe validador -> registrador
        os.close(val_to_log_w)
        
        # Ejecutar el proceso registrador
        logger_process(val_to_log_r)
        
        # Salir del proceso hijo
        sys.exit(0)
    
    # Proceso principal: cerrar todos los pipes
    for r, w in gen_to_val_pipes:
        os.close(r)
        os.close(w)
    
    os.close(val_to_log_r)
    os.close(val_to_log_w)
    
    # Esperar a que todos los procesos terminen
    for pid in generator_pids:
        os.waitpid(pid, 0)
    
    os.waitpid(val_pid, 0)
    os.waitpid(log_pid, 0)
    
    print("Sistema de procesamiento de transacciones completado.")

if __name__ == "__main__":
    main()
```

**Explicación:**
1. Implementamos un sistema complejo de procesamiento de transacciones con tres tipos de procesos:
   - **Generadores**: Múltiples procesos que crean transacciones aleatorias
   - **Validador**: Recibe transacciones de todos los generadores, verifica su validez
   - **Registrador**: Recibe transacciones validadas y mantiene estadísticas
2. Utilizamos múltiples pipes para establecer los flujos de comunicación:
   - Un pipe separado desde cada generador al validador
   - Un pipe desde el validador al registrador
3. Serializamos las transacciones en formato JSON para facilitar la transmisión y procesamiento.
4. Implementamos un sistema de señalización de finalización (mensaje "END") para indicar cuando un proceso ha terminado de enviar datos.
5. El validador implementa reglas de negocio para verificar la validez de las transacciones.
6. El registrador acumula estadísticas completas y genera un informe detallado al final.
7. Gestionamos adecuadamente la apertura y cierre de todos los descriptores de archivo en cada proceso.

Este ejercicio representa un sistema completo y realista que podría servir como base para aplicaciones de procesamiento de datos distribuidas. Demuestra técnicas avanzadas para:
- Manejar múltiples procesos concurrentes
- Establecer pipelines complejos de comunicación
- Serializar y deserializar datos estructurados
- Implementar protocolos de señalización entre procesos
- Manejar el cierre adecuado de recursos
- Generar estadísticas y reportes a partir de flujos de datos