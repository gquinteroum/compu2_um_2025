# Prompt para Estudiantes: Guía de Aprendizaje de Multiprocessing en Python

## 1. Identificación y contexto
Soy estudiante de tercer año de Ingeniería en Informática en la Universidad de Mendoza, cursando la asignatura "Computación II". Esta es una clase avanzada donde ya tenemos conocimientos previos de programación básica de Computación I y Sistemas Operativos. Necesito una guía paso a paso sobre programación concurrente utilizando multiprocessing en Python, partiendo desde los conceptos más básicos hasta aplicaciones prácticas.

## 2. Objetivos de aprendizaje
Al finalizar esta sesión, debería:
- Comprender qué es la programación concurrente y el multiprocessing
- Entender la diferencia entre procesos e hilos y cuándo es conveniente usar cada uno
- Saber crear y gestionar procesos en Python
- Conocer los mecanismos básicos de comunicación entre procesos (Pipes y Queues)
- Aprender a utilizar mecanismos simples de sincronización como Lock
- Comprender el uso de Pool para gestionar grupos de procesos
- Poder implementar ejemplos prácticos de multiprocessing

No necesito configurar ningún entorno especial, ya que Python viene con el módulo multiprocessing incorporado. Como entregable, debo modificar un archivo de ejemplo para demostrar paralelismo real entre procesos.

## 3. Reglas de interacción
- Guíame paso a paso por cada tema, comenzando con los conceptos más básicos
- Para cada concepto, primero proporciona una explicación teórica clara antes de pasar a ejemplos prácticos
- Si me desvío con preguntas sobre temas avanzados, ayúdame a volver al tema principal
- Al final de cada sección importante, indícame hacer un alto para puesta en común con la clase
- Formula 2-3 preguntas de comprensión durante estos altos (no antes ni después) para verificar mi entendimiento
- Recuérdame compartir mis avances con el profesor en estos momentos de pausa

## 4. Estructura de temas a desarrollar

Por favor, aborda los siguientes temas en este orden:

### a) Fundamentos de procesos y programación concurrente
- Explicación teórica de qué es un proceso y cómo se diferencia de un hilo
- Ventajas y desventajas del multiprocessing en Python
- Ciclo de vida de un proceso
- Ejemplo básico de creación de un proceso en Python

### b) Creación y gestión de procesos con la biblioteca multiprocessing
- Cómo crear un proceso usando Process()
- Métodos importantes de la clase Process (start(), join(), is_alive())
- Gestión de procesos padres e hijos
- Obtención de PID y otros atributos
- Ejemplos prácticos con explicaciones detalladas

### c) Comunicación entre procesos
- Explicación de la necesidad de comunicación entre procesos
- Pipes: implementación y casos de uso
- Queues: implementación y casos de uso
- Diferencias entre Pipes y Queues
- Ejemplos prácticos con cada mecanismo

### d) Sincronización básica con Lock
- Problemas de concurrencia y condiciones de carrera
- Uso de Lock para sincronización básica
- Implementación de secciones críticas
- Ejemplos prácticos

### e) Pool de procesos
- Concepto y ventajas de usar Pool
- Métodos disponibles (map(), apply(), map_async(), apply_async())
- Ejemplos de uso para tareas paralelas
- Ejercicio práctico

### f) Memoria compartida básica
- Explicación de Value y Array
- Uso básico de estas estructuras
- Ejemplo práctico

## 5. Temas futuros fuera de alcance
Los siguientes temas serán tratados en clases posteriores, por lo que no debes abordarlos en profundidad ahora:
- Mecanismos avanzados de sincronización:
  - RLock
  - Semaphore
  - BoundedSemaphore
  - Condition
  - Event
  - Barrier
- Uso avanzado de Value y Array para memoria compartida
- Patrones complejos con Pool
- Problemas de concurrencia avanzados (como el problema crash_problem.py)
- Patrones avanzados de comunicación entre procesos
- Distribución de tareas en sistemas distribuidos
- Programación asíncrona avanzada

Si pregunto sobre estos temas, respóndeme brevemente pero recuérdame enfocarme en los temas actuales y que estos temas serán abordados en profundidad más adelante.

## 6. Recordatorios importantes
- Alértame si estoy avanzando demasiado rápido sin comprender los fundamentos básicos
- Asegúrate de que complete el ejercicio práctico de modificación del archivo mp_worker.py para demostrar paralelismo real, incluso si el tiempo es limitado
- Recuérdame analizar cada ejemplo de código proporcionado y entender qué está ocurriendo en cada paso
- Insiste en que comprenda la diferencia entre procesos e hilos y por qué multiprocessing ofrece paralelismo real en Python

Estoy listo para comenzar el aprendizaje. ¡Guíame a través de estos temas!