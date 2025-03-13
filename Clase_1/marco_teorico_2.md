# **Guía sobre `getopt` y `argparse` en Python**

## **Capítulo 1: Introducción a los Argumentos de Línea de Comandos en Python**

### **1.1 ¿Qué son los Argumentos de Línea de Comandos?**
Los argumentos de línea de comandos son una forma de pasar información a un programa en el momento de su ejecución sin necesidad de modificar su código fuente. En Python, estos argumentos se pueden acceder a través del módulo `sys.argv`, el cual proporciona una lista de los argumentos pasados al script.

Ejemplo básico de acceso a los argumentos:

```python
import sys
print("Argumentos recibidos:", sys.argv)
```

Ejecutando el script con argumentos:

```sh
python script.py argumento1 argumento2
```
Salida esperada:

```sh
Argumentos recibidos: ['script.py', 'argumento1', 'argumento2']
```

### **1.2 Importancia de Manejar Argumentos Correctamente**
El manejo eficiente de argumentos permite:

- Crear scripts reutilizables y modulares.
- Mejorar la experiencia del usuario al ejecutar programas desde la terminal.
- Permitir una configuración flexible sin necesidad de modificar el código fuente.

Sin embargo, `sys.argv` tiene limitaciones importantes:

- No permite manejar fácilmente opciones con valores (`-o valor`).
- No proporciona validación de datos.
- No ofrece ayuda (`--help`).

Para solucionar estas limitaciones, Python ofrece dos módulos especializados: **`getopt`** y **`argparse`**.

---

## **Capítulo 2: `getopt`: Manejo de Argumentos al Estilo de C**

### **2.1 Introducción a `getopt`**
El módulo `getopt` es similar a la función `getopt()` en C y permite analizar argumentos de línea de comandos de manera estructurada.

### **2.2 Uso Básico de `getopt`**
Estructura general de `getopt.getopt()`:

```python
getopt.getopt(argumentos, opciones_cortas, opciones_largas)
```
- `argumentos`: La lista de argumentos (normalmente `sys.argv[1:]`).
- `opciones_cortas`: Una cadena con las opciones cortas (`-o`), donde los parámetros obligatorios se indican con `:`.
- `opciones_largas`: Una lista de opciones largas (`--opcion=`).

Ejemplo básico:

```python
import getopt
import sys

try:
    opts, args = getopt.getopt(sys.argv[1:], "hi:o:", ["help", "input=", "output="])
except getopt.GetoptError as err:
    print(err)
    sys.exit(2)

for opt, arg in opts:
    if opt in ("-h", "--help"):
        print("Uso: script.py -i <archivo_entrada> -o <archivo_salida>")
        sys.exit()
    elif opt in ("-i", "--input"):
        input_file = arg
    elif opt in ("-o", "--output"):
        output_file = arg
```

Ejecutando el script:

```sh
python script.py -i entrada.txt -o salida.txt
```

### **2.3 Limitaciones de `getopt`**

- No maneja validación de datos.
- No genera ayuda automática.
- Código más complejo en comparación con `argparse`.

---

## **Capítulo 3: `argparse`: Manejo Avanzado de Argumentos**

### **3.1 Introducción a `argparse`**
`argparse` es el módulo recomendado para el manejo de argumentos en Python, ofreciendo una interfaz más flexible y robusta.

### **3.2 Uso Básico de `argparse`**
Ejemplo mínimo:

```python
import argparse

parser = argparse.ArgumentParser(description="Ejemplo de argparse")
parser.add_argument("-i", "--input", required=True, help="Archivo de entrada")
parser.add_argument("-o", "--output", required=True, help="Archivo de salida")
args = parser.parse_args()

print(f"Archivo de entrada: {args.input}")
print(f"Archivo de salida: {args.output}")
```

Ejecutando el script:

```sh
python script.py -i entrada.txt -o salida.txt
```

Salida esperada:

```sh
Archivo de entrada: entrada.txt
Archivo de salida: salida.txt
```

### **3.3 Validación y Tipos de Datos**
Se pueden especificar tipos de datos en los argumentos:

```python
parser.add_argument("-n", "--numero", type=int, help="Número entero obligatorio")
```
Esto permite validar que se ingrese un número entero en lugar de una cadena.

### **3.4 Argumentos Posicionales vs. Opcionales**
- **Argumentos posicionales**: No requieren prefijo (`-` o `--`).

  ```python
  parser.add_argument("archivo", help="Archivo de entrada")
  ```
- **Argumentos opcionales**: Se especifican con `-` o `--`.

  ```python
  parser.add_argument("--modo", choices=["rapido", "lento"], help="Modo de ejecución")
  ```

### **3.5 Generación Automática de Ayuda**
`argparse` genera automáticamente mensajes de ayuda con `--help`:

```sh
python script.py --help
```

Salida esperada:

```sh
usage: script.py [-h] -i INPUT -o OUTPUT

Ejemplo de argparse

optional arguments:

  -h, --help            muestra este mensaje y sale
  -i INPUT, --input INPUT
                        Archivo de entrada
  -o OUTPUT, --output OUTPUT
                        Archivo de salida
```

---

## **Capítulo 4: Comparación Entre `getopt` y `argparse`**

| Característica    | `getopt` | `argparse` |
|------------------|---------|-----------|
| Facilidad de uso | Media   | Alta      |
| Generación de ayuda | No  | Sí      |
| Validación de datos | No  | Sí      |
| Manejo de valores por defecto | No | Sí |

### **¿Cuándo Usar Cada Uno?**
- **`getopt`**: Cuando se requiere compatibilidad con C o scripts muy simples.
- **`argparse`**: Para la mayoría de los casos donde se necesita una interfaz más robusta.

---


## **Capítulo 5: Ejercicios Prácticos y Soluciones**

### **5.1 Ejercicios Prácticos**

1. Escribe un script que acepte tres argumentos: `-i` (entrada), `-o` (salida) y `-n` (número de líneas a procesar).
2. Modifica el script para validar que `-n` sea un entero positivo.
3. Añade una opción `--verbose` para imprimir mensajes detallados.
4. Usa `argparse` para definir argumentos obligatorios y opcionales.
5. Implementa un comando `--help` para que el usuario vea la documentación.

---

### **5.2 Soluciones a los Ejercicios**

#### **Ejercicio 1: Script con argumentos `-i`, `-o` y `-n`**

```python
import argparse

parser = argparse.ArgumentParser(description="Procesador de archivos con número de líneas limitadas")
parser.add_argument("-i", "--input", required=True, help="Archivo de entrada")
parser.add_argument("-o", "--output", required=True, help="Archivo de salida")
parser.add_argument("-n", "--num_lines", required=True, type=int, help="Número de líneas a procesar")
args = parser.parse_args()

print(f"Procesando {args.num_lines} líneas del archivo {args.input} y guardando en {args.output}")
```

---

#### **Ejercicio 2: Validación de que `-n` sea un entero positivo**

```python
def check_positive(value):
    ivalue = int(value)
    if ivalue <= 0:
        raise argparse.ArgumentTypeError("El número de líneas debe ser un entero positivo.")
    return ivalue

parser.add_argument("-n", "--num_lines", type=check_positive, help="Número de líneas a procesar (debe ser positivo)")
```

---

#### **Ejercicio 3: Agregar `--verbose` para mostrar mensajes detallados**

```python
parser.add_argument("--verbose", action="store_true", help="Muestra mensajes detallados de procesamiento")

if args.verbose:
    print("Modo detallado activado.")
```

---

#### **Ejercicio 4: Argumentos obligatorios y opcionales**

```python
parser.add_argument("archivo", help="Archivo de entrada (argumento posicional)")
parser.add_argument("--modo", choices=["rapido", "lento"], help="Modo de ejecución (opcional)")
```

---

#### **Ejercicio 5: Implementar `--help` para mostrar la documentación**

```sh
python script.py --help
```
Salida esperada:

```sh
usage: script.py [-h] -i INPUT -o OUTPUT -n NUM_LINES [--verbose] [--modo {rapido,lento}]
```

---



