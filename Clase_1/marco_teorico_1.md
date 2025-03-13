# **Control de Versiones con Git**

## **Capítulo 1: Historia del Control de Versiones y la Revolución de Git**

### **1.1 Introducción**
El control de versiones es un pilar fundamental en el desarrollo de software moderno. Permite a los programadores gestionar cambios en el código fuente, colaborar de manera eficiente y mantener un historial detallado de modificaciones. Antes de Git, los sistemas de control de versiones centralizados presentaban diversas limitaciones que dificultaban el trabajo en proyectos distribuidos. En este capítulo, exploraremos la evolución de estos sistemas, desde los primeros métodos rudimentarios hasta la creación de Git, el estándar actual en la industria.

### **1.2 Primeros Métodos de Control de Versiones**
En los primeros días del desarrollo de software, la gestión de versiones se realizaba manualmente. Los desarrolladores creaban copias de archivos con nombres como `programa_v1.c`, `programa_v2.c`, `programa_final.c`, lo que generaba desorden y propiciaba errores.

A medida que los proyectos crecieron en complejidad, surgió la necesidad de herramientas automatizadas para gestionar versiones. A finales de los años 70 y principios de los 80, nacieron los primeros sistemas de control de versiones:

- **SCCS (Source Code Control System, 1972)**: Desarrollado por Bell Labs, fue el primer sistema de control de versiones. Su modelo de almacenamiento era secuencial, lo que limitaba la colaboración.
- **RCS (Revision Control System, 1982)**: Mejoró SCCS al utilizar un modelo basado en deltas, almacenando solo los cambios entre versiones sucesivas de un archivo.
- **CVS (Concurrent Versions System, 1986)**: Introdujo la posibilidad de trabajo colaborativo, permitiendo a múltiples desarrolladores modificar un código base al mismo tiempo.

### **1.3 Sistemas de Control de Versiones Centralizados**
Durante los años 90 y principios de los 2000, el desarrollo de software se organizó en torno a sistemas centralizados como:

- **Subversion (SVN, 2000)**: Permitía transacciones atómicas y mejor gestión de versiones en proyectos grandes.
- **Perforce**: Ampliamente utilizado en la industria de los videojuegos y software propietario debido a su alto rendimiento.

Sin embargo, estos sistemas tenían una gran limitación: dependían de un servidor central, lo que los hacía vulnerables a fallos en la infraestructura y dificultaba el trabajo distribuido.

### **1.4 El Nacimiento de Git: 2005 y la Crisis de BitKeeper**
En los años 2000, el desarrollo del kernel de Linux utilizaba **BitKeeper**, un sistema de control de versiones distribuido, pero de código cerrado. En 2005, por disputas de licencia, BitKeeper dejó de ser gratuito para el proyecto Linux. Como resultado, Linus Torvalds creó **Git**, un sistema distribuido, rápido y seguro, diseñado para manejar el desarrollo de software a gran escala.

Las principales innovaciones de Git fueron:
- **Arquitectura distribuida**: Cada clon del repositorio es una copia completa del historial.
- **Modelo basado en snapshots**: En lugar de almacenar diferencias entre versiones, Git toma capturas de estado de los archivos.
- **Integridad criptográfica**: Cada commit se identifica con un hash SHA-1, asegurando la integridad de los datos.

Desde su lanzamiento, Git se ha convertido en el estándar para la industria del software, siendo utilizado en proyectos de todos los tamaños, desde startups hasta gigantes tecnológicos como Google, Microsoft y Facebook.

---

## **Capítulo 2: Fundamentos de Git y su Arquitectura Interna**

### **2.1 Conceptos Básicos de Git**
Git opera bajo un modelo distribuido, donde cada desarrollador mantiene una copia completa del repositorio. Para entender su funcionamiento, es esencial conocer los siguientes conceptos:

- **Repositorio (`.git/`)**: Contiene toda la información del proyecto, incluyendo commits, ramas y referencias.
- **Área de trabajo (Working Directory)**: La carpeta donde se encuentran los archivos en su versión actual.
- **Área de preparación (Staging Area o Index)**: Un espacio intermedio donde se almacenan cambios antes de confirmarlos.
- **Commit**: Un snapshot de los archivos en un punto determinado del tiempo.
- **Branch (rama)**: Una línea de desarrollo separada del historial principal.
- **Remote Repository**: Repositorios alojados en servidores como GitHub, GitLab o Bitbucket.

### **2.2 Modelo de Datos de Git**
A diferencia de sistemas como SVN, que almacenan diferencias entre versiones, Git usa un **modelo basado en snapshots**:

- Cada commit es una instantánea completa del estado de los archivos.
- Si un archivo no cambia entre commits, Git solo almacena una referencia al archivo anterior.
- La integridad de los datos se garantiza mediante algoritmos hash SHA-1.

Este modelo ofrece grandes ventajas en términos de eficiencia y confiabilidad.

### **2.3 Flujos de Trabajo en Git**
Git permite múltiples flujos de trabajo según las necesidades del equipo de desarrollo:

- **Centralizado**: Similar a SVN, con una única rama principal (`main` o `master`).
- **Feature Branching**: Cada nueva funcionalidad se desarrolla en una rama separada y luego se fusiona.
- **Git Flow**: Introduce ramas estructuradas como `develop`, `feature`, `release` y `hotfix` para gestionar versiones de manera formal.
- **Forking Workflow**: Utilizado en proyectos open-source, donde cada contribuyente trabaja en su propio fork.

Estos flujos permiten escalar desde pequeños proyectos hasta sistemas con cientos de colaboradores.

---

# **Entrada/Salida en Unix/Linux**

## **Capítulo 3: Entrada y Salida en Unix/Linux**

### **3.1 Fundamentos de Entrada/Salida (E/S) en Unix/Linux**

El sistema operativo Unix y sus derivados, como Linux, adoptan un modelo unificado de entrada y salida (E/S) basado en el principio de que **todo es un archivo**. Este enfoque permite tratar dispositivos de hardware, procesos en ejecución, sockets de red y archivos regulares de manera homogénea, lo que simplifica el diseño y la manipulación de datos en el sistema.

Las tres abstracciones fundamentales de la E/S en Unix/Linux son:

- **Entrada estándar (`stdin`)**: Fuente predeterminada de datos para un proceso (generalmente el teclado).
- **Salida estándar (`stdout`)**: Destino predeterminado donde un proceso envía su salida (normalmente la terminal).
- **Salida de error estándar (`stderr`)**: Canal separado para mensajes de error, lo que permite diferenciarlos de la salida normal.

Cada flujo de datos está representado internamente por un número llamado **descriptor de archivo**:

- `0` → Entrada estándar (`stdin`)
- `1` → Salida estándar (`stdout`)
- `2` → Salida de error estándar (`stderr`)

### **3.2 ¿Qué es un Descriptor de Archivo?**

Un **descriptor de archivo** es un identificador numérico asignado por el kernel de Unix/Linux a cada archivo, proceso o dispositivo abierto en el sistema. Estos descriptores permiten la abstracción de la E/S y hacen posible el manejo uniforme de flujos de datos, ya sea desde el teclado, un archivo, un socket de red o un dispositivo físico.

Cada proceso tiene su propia tabla de descriptores de archivo, y estos pueden ser manipulados mediante llamadas al sistema. Los descriptores más comunes son:

- **Descriptor 0 (`stdin`)**: Entrada estándar, generalmente asociada con el teclado.
- **Descriptor 1 (`stdout`)**: Salida estándar, generalmente asociada con la terminal.
- **Descriptor 2 (`stderr`)**: Salida de error estándar, separada de `stdout` para diferenciar errores de la salida normal.

Los descriptores de archivo permiten operaciones avanzadas como redirección de salida, pipes, y manipulación eficiente de flujos de datos.

---

### **3.3 Redirección de Entrada y Salida**

La redirección es una técnica poderosa en Unix/Linux que permite cambiar la fuente o destino de los datos de entrada y salida de un proceso sin modificar el código fuente del programa.

#### **3.3.1 Redirección de Salida**

- `>` → Redirige la salida estándar a un archivo, sobrescribiendo su contenido.
  
  ```sh
  ls > archivos.txt
  ```
  
  El comando anterior guarda la lista de archivos en `archivos.txt`, reemplazando cualquier contenido previo.

- `>>` → Redirige la salida estándar a un archivo, añadiendo nuevos datos sin sobrescribirlo.
  
  ```sh
  echo "Nueva línea" >> archivos.txt
  ```
  
  Esto agrega la línea "Nueva línea" al final de `archivos.txt`.

#### **3.3.2 Redirección de Entrada**

- `<` → Usa un archivo como entrada estándar en lugar del teclado.
  
  ```sh
  wc -l < archivo.txt
  ```
  
  Cuenta las líneas del archivo `archivo.txt` en lugar de esperar entrada del usuario.

#### **3.3.3 Redirección de Errores**

- `2>` → Redirige la salida de error estándar a un archivo.
  
  ```sh
  comando_inexistente 2> error.log
  ```
  
  Captura los mensajes de error en `error.log`.

- `2>>` → Añade errores al archivo sin sobrescribirlo.
  
  ```sh
  comando_inexistente 2>> error.log
  ```

- `&>` → Redirige tanto `stdout` como `stderr` al mismo archivo.
  
  ```sh
  script.sh &> salida.log
  ```

- `/dev/null` → Un "sumidero" que descarta cualquier dato enviado a él.
  
  ```sh
  comando 2>/dev/null
  ```
  
  Silencia los mensajes de error.

---

### **3.4 Uso de Pipes (`|`)**

Los pipes (`|`) permiten encadenar comandos, usando la salida de uno como entrada de otro. Son fundamentales en la filosofía Unix de "hacer una cosa bien" y combinarlas en flujos de procesamiento.

#### **Ejemplo básico:**

```sh
ls -l | grep ".txt" | wc -l
```

Este comando:

1. Lista archivos detalladamente (`ls -l`).
2. Filtra aquellos que contienen `.txt` en su nombre (`grep ".txt"`).
3. Cuenta cuántos hay (`wc -l`).

#### **Ejemplo con múltiples comandos:**

```sh
df -h | grep "/dev/sda"
```

Muestra el uso de disco de `/dev/sda`, aplicando un filtro sobre la salida de `df -h`.

---

### **3.5 Dispositivos de E/S en Unix/Linux**

Además de archivos normales, Unix/Linux maneja dispositivos especiales en `/dev/`:

- **`/dev/null`** → Descarta cualquier dato enviado a él.
- **`/dev/zero`** → Proporciona un flujo infinito de bytes nulos (`\0`).
- **`/dev/random` y `/dev/urandom`** → Generan números aleatorios basados en la entropía del sistema.
- **`/dev/tty`** → Representa la terminal actual.

Ejemplo de escritura en `/dev/null`:

```sh
cat archivo.txt > /dev/null
```

Esto descarta la salida de `cat`, evitando que se muestre en pantalla.


### **3.6 Ejercicios Prácticos**

A continuación, se presentan **10 ejercicios** diseñados para reforzar la comprensión de los conceptos de **entrada/salida en Unix/Linux**, desde lo básico hasta un nivel avanzado. La dificultad de los ejercicios aumenta progresivamente.

#### **Ejercicio 1: Redirección de Salida Básica**
**Objetivo:** Crear un archivo con el listado de archivos y carpetas de un directorio.

**Instrucción:**
Ejecuta un comando que guarde la salida del listado de archivos de tu directorio actual en un archivo llamado `listado.txt`.

---

#### **Ejercicio 2: Redirección de Entrada y Contar Líneas**
**Objetivo:** Leer un archivo y contar sus líneas sin usar la interfaz interactiva de `wc`.

**Instrucción:**
Utiliza redirección para contar cuántas líneas tiene el archivo `listado.txt` que creaste en el ejercicio anterior.

---

#### **Ejercicio 3: Redirección de Errores**
**Objetivo:** Capturar errores generados por comandos inválidos.

**Instrucción:**
Ejecuta un comando que intente listar un directorio inexistente y redirige el mensaje de error a un archivo llamado `errores.log`.

---

#### **Ejercicio 4: Uso de Pipes**
**Objetivo:** Encadenar comandos para filtrar información.

**Instrucción:**
Lista los archivos de tu directorio actual y usa `grep` para mostrar solo los archivos que contienen la palabra "log" en su nombre.

---

#### **Ejercicio 5: Contar Archivos con Pipes**
**Objetivo:** Contar cuántos archivos cumplen con un criterio.

**Instrucción:**
Usa un pipe para contar cuántos archivos en tu directorio contienen la palabra "txt" en su nombre.

---

#### **Ejercicio 6: Redirección Combinada de Salida y Errores**
**Objetivo:** Guardar la salida estándar y los errores en un solo archivo.

**Instrucción:**
Ejecuta un comando que liste un directorio válido e inválido al mismo tiempo, y redirige toda la salida (éxito y errores) a `resultado_completo.log`.

---

#### **Ejercicio 7: Uso de `/dev/null` para Silenciar Salida**
**Objetivo:** Ejecutar un comando sin mostrar nada en pantalla.

**Instrucción:**
Ejecuta un comando que intente listar un directorio inexistente y envía **toda** su salida a `/dev/null`.

---

#### **Ejercicio 8: Creación de Alias con Descriptores de Archivo**
**Objetivo:** Manipular descriptores de archivo manualmente.

**Instrucción:**
Ejecuta un comando que cree un descriptor de archivo adicional para `stdout`, lo use para escribir en `salida_custom.log` y luego lo cierre.

---

#### **Ejercicio 9: Redirección Avanzada con `exec`**
**Objetivo:** Usar `exec` para establecer una redirección persistente.

**Instrucción:**
Utiliza `exec` para redirigir toda la salida de comandos ejecutados en la sesión actual a un archivo llamado `sesion.log`.

---

#### **Ejercicio 10: Uso Complejo de Pipes y Redirección**
**Objetivo:** Procesar múltiples flujos de datos encadenados.

**Instrucción:**
Construye un pipeline que:
1. Liste todos los archivos en `/var/log`.
2. Filtre los que contengan "syslog" en su nombre.
3. Cuente cuántos hay.
4. Redirija tanto la salida estándar como la de error a `conteo_syslog.log`.

---

### **3.7 Ejercicios Resueltos**

A continuación, se presentan las soluciones a los ejercicios anteriores:

#### **Solución 1: Redirección de Salida Básica**
```sh
ls > listado.txt
```

---

#### **Solución 2: Redirección de Entrada y Contar Líneas**
```sh
wc -l < listado.txt
```

---

#### **Solución 3: Redirección de Errores**
```sh
ls /directorio_inexistente 2> errores.log
```

---

#### **Solución 4: Uso de Pipes**
```sh
ls | grep "log"
```

---

#### **Solución 5: Contar Archivos con Pipes**
```sh
ls | grep "txt" | wc -l
```

---

#### **Solución 6: Redirección Combinada de Salida y Errores**
```sh
ls /home /directorio_inexistente &> resultado_completo.log
```

---

#### **Solución 7: Uso de `/dev/null` para Silenciar Salida**
```sh
ls /directorio_inexistente &> /dev/null
```

---

#### **Solución 8: Creación de Alias con Descriptores de Archivo**
```sh
exec 3> salida_custom.log
echo "Este es un mensaje" >&3
exec 3>&-
```

---

#### **Solución 9: Redirección Avanzada con `exec`**
```sh
exec > sesion.log 2>&1
echo "Toda la salida de este shell ahora está en sesion.log"
ls /home
ls /no_existe
exec >&-
```

---

#### **Solución 10: Uso Complejo de Pipes y Redirección**
```sh
ls /var/log | grep "syslog" | wc -l &> conteo_syslog.log
```

---

