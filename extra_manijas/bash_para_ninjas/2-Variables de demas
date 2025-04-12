# Bash para ninjas – Documento 2

## El poder escondido: variables, quoting y comandos encadenados

Ahora que ya sabés caminar en el dojo, es momento de aprender a usar **el chi de Bash**. Porque todo ninja de la terminal necesita dominar las variables, entender cómo usar correctamente las comillas, y saber encadenar comandos como si fuesen movimientos fluidos de una misma coreografía.

### Variables: las reservas de energía

Una **variable** es una forma de guardar información para usarla más adelante. Si el primer documento era sobre moverse por el entorno, este es sobre **hacer que ese entorno recuerde cosas**.

```bash
mensaje="Bienvenido al dojo ninja"
echo $mensaje
```

Lo que hicimos arriba fue crear una variable llamada `mensaje` y asignarle un texto. Luego, usamos `$mensaje` para obtener su valor. El símbolo `$` es como un conjuro: le dice a Bash que no queremos ver la palabra "mensaje", sino su contenido.

#### Tipos comunes de variables

```bash
usuario="sensei"
numero=42
ruta=$HOME/dojo
```

- No pongas espacios entre el nombre, el igual y el valor.
- Las variables son solo texto: no existen los tipos de datos estrictos como en otros lenguajes.

#### Ejemplo real:

```bash
backup="respaldo_$(date +%F_%H-%M-%S).tar.gz"
echo "Creando archivo: $backup"
```

Aca usamos `$(...)` para ejecutar un comando dentro de otro. Es la forma moderna (y más legible) de los antiguos backticks `` ` ``, que también funcionan:

```bash
echo "Hoy es: `date`"
```

Pero los ninjas modernos prefieren `$(date)`.

---

### Quoting: el arte de encerrar lo sagrado

Las comillas no son solo ornamentales. En Bash, **el tipo de comillas que usás cambia el significado de lo que escribís**.

#### 1. Comillas dobles `" "`
Permiten la **expansión de variables** y comandos.

```bash
nombre="estudiante ninja"
echo "Hola $nombre"
```

#### 2. Comillas simples `' '`
Todo lo que está dentro se toma literalmente. Ni variables ni comandos se expanden.

```bash
echo 'Hola $nombre'
```

Esto imprime literalmente `Hola $nombre`, sin reemplazar nada.

#### 3. Sin comillas
Es válido, pero Bash puede separar el texto por espacios o caracteres especiales, lo que puede romper comandos si no se está atento.

```bash
archivo=Mi archivo con espacios.txt
```

Eso falla. Pero:

```bash
archivo="Mi archivo con espacios.txt"
```

¡Eso funciona!

#### Ejemplo ninja:

```bash
archivo="log_$(date +%F).txt"
echo "Guardando salida en '$archivo'"
echo "Operación realizada el $(date)" > "$archivo"
```

---

### Comandos encadenados: combos de ataque

Un ninja no golpea una vez. Encadena movimientos. En Bash, eso se hace con:

- `;`  para ejecutar varios comandos, uno tras otro, sin importar si fallan
- `&&` para ejecutar el siguiente **solo si el anterior tuvo éxito**
- `||` para ejecutar el siguiente **solo si el anterior falló**

#### Ejemplos:

```bash
mkdir dojo && cd dojo
```

Solo entrará en la carpeta si la pudo crear.

```bash
false || echo "Algo falló, pero seguimos"
```

En este, `false` siempre falla, por lo tanto el `echo` se ejecuta.

```bash
rm archivo.txt; echo "El archivo fue eliminado"
```

Este ejecuta ambos comandos pase lo que pase.

---

### Ejemplo completo: script de saludo

```bash
nombre="ninja misterioso"

if [ -n "$1" ]; then
  nombre="$1"
fi

hora=$(date +%H)
if [ $hora -lt 12 ]; then
  saludo="Buenos días"
elif [ $hora -lt 18 ]; then
  saludo="Buenas tardes"
else
  saludo="Buenas noches"
fi

echo "$saludo, $nombre. Bienvenido al dojo."
```

Este mini script:
- Usa una variable por defecto
- Permite que se pase un nombre como argumento
- Detecta la hora del sistema
- Saluda según la hora

Guardalo como `saludo.sh`, hacelo ejecutable con `chmod +x saludo.sh`, y corré:
```bash
./saludo.sh
./saludo.sh Estudiante
```

---

### Ejercicios del dojo:

1. Creá una variable con tu nombre ninja y saludate con `echo`
2. Usá `$(date)` para guardar la hora en una variable
3. Probá imprimir el mismo mensaje usando comillas simples y dobles. Observá la diferencia
4. Usá `&&` para crear una carpeta y luego entrar en ella si todo va bien
5. Escribí una línea que diga: "Este archivo se creó el (fecha actual)" y lo guarde en un archivo con nombre `registro_(fecha).txt`

---

Ahora sé que sentís el fluir de Bash en tus dedos. La terminal empieza a responderte con respeto. En el próximo documento, vamos a aprender a repetir tareas con elegancia: **bucles, listas, y lectura de archivos**.

*Seguí entrenando. Tu katana se afila con la práctica.*


