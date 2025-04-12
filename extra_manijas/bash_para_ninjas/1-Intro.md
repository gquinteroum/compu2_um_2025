# Bash para ninjas – Documento 1

## El primer paso en el camino del ninja: la terminal

Si alguna vez miraste una consola negra con letras verdes y pensaste que era cosa de hackers o de gente que ya no tiene salvación, tranquilo. Lo que tenés frente a vos es mucho más interesante: es una katana. Una herramienta precisa, poderosa, y letal en las manos correctas. Lo que vamos a hacer en este primer documento es aprender a desenvainarla.

### ¿Qué es Bash?

Bash no es "la terminal". Es un *intérprete de comandos*, uno entre muchos. La terminal es la ventana que abrís para poder escribir comandos. Bash es el que los recibe, los interpreta, y se encarga de pedirle al sistema operativo que haga lo que le pediste. Si la terminal es tu dojo, Bash es tu maestro silencioso.

Bash significa **Bourne Again SHell**, un juego de palabras con la shell original del sistema Unix. Pero no te hace falta saber historia para pelear bien: te hace falta saber usarla.

### El prompt no muerde

Cada vez que abrís la terminal, Bash te recibe con una señal. Algo como:

```bash
usuario@computadora:~$
```

Esto se llama *prompt*. Te está diciendo varias cosas:
- Quién sos (usuario)
- En qué computadora estás (computadora)
- En qué carpeta estás parado (`~` significa tu carpeta personal, o `$HOME`)
- Y lo más importante: está listo para recibir un comando

Ese `$` es una invitación. Está diciendo: *adelante, ordename algo*.

### Tu primer movimiento

Empecemos con algo suave. Escribí esto y apretá Enter:

```bash
echo "Hola mundo ninja"
```

El comando `echo` simplemente imprime en pantalla lo que le digas. Es el equivalente a decir "repetí esto". Pero ya hiciste algo enorme: escribiste un comando, Bash lo recibió, lo interpretó y lo ejecutó. Ya estás en camino.

Ahora, movete por el sistema:

```bash
pwd
```

Esto significa *print working directory*. Te dice exactamente en qué parte del sistema estás parado. Es como pedirle al GPS que te diga tu ubicación.

Y para ver lo que hay alrededor:

```bash
ls
```

Esto te muestra lo que hay en la carpeta actual. Archivos, carpetas, lo que sea.

### La historia también es poder

Un verdadero ninja no repite movimientos innecesarios. Para eso está el *historial de comandos*. Bash recuerda lo que hiciste.

Si querés repetir el último comando:
```bash
!!
```

Si querés repetir el último argumento de lo que hiciste:
```bash
!$
```

Imaginá que escribiste:
```bash
cat informe.txt
```

Y querés ahora mover ese archivo:
```bash
mv !$ otra_carpeta/
```

Eso se convierte en:
```bash
mv informe.txt otra_carpeta/
```

Hay muchas más combinaciones, pero lo importante es entender que la historia está viva, y podés usarla como un recurso táctico.

### Alias: el arte de nombrar tus propios ataques

Hay comandos que repetís tanto que terminás deseando que fueran una palabra corta. Bash te deja crear tus propios comandos. Se llaman *alias*.

```bash
alias ll='ls -lha'
```

Esto hace que cada vez que escribas `ll`, se ejecute `ls -lha`, que lista archivos en modo largo, legible y con ocultos.

Para que estos alias persistan, los tenés que escribir en tu archivo `~/.bashrc`. Pero por ahora, podés probarlos en caliente.

### Espacios, expansiones y elegancia

Una de las armas secretas de Bash son las *expansiones*. Es decir, cosas que escribís de forma abreviada, pero Bash expande por vos.

```bash
echo archivo_{1..5}.txt
```

Esto imprime:
```bash
archivo_1.txt archivo_2.txt archivo_3.txt archivo_4.txt archivo_5.txt
```

Y si hacés:
```bash
touch archivo_{a,b,c}.log
```

Creás tres archivos: `archivo_a.log`, `archivo_b.log`, y `archivo_c.log`.

Bash también expande variables. Probá esto:

```bash
nombre="Estudiante Ninja"
echo "Hola $nombre, bienvenido a Bash"
```

La variable `$nombre` se expande con su contenido. Aprender a usar variables te permite escribir scripts dinámicos.

### Ejercicio final ninja

Hacé esto en orden:

1. Andá a tu escritorio con `cd ~/Escritorio`
2. Creá una carpeta con tu nombre ninja: `mkdir dojo_ninja`
3. Entrá a esa carpeta: `cd dojo_ninja`
4. Creá cinco archivos que se llamen `nota_1.txt` a `nota_5.txt` usando una sola línea
5. Escribí un alias que te permita listar archivos con detalles y ocultos
6. Usá `!!` para repetir el comando anterior
7. Creamos una variable `saludo="Hola ninja"` y hacé que Bash te salude

---

Esto fue el primer documento. Un paso pequeño, pero esencial. Ya te moviste por el sistema, imprimiste mensajes, usaste el historial y comenzaste a escribir como un verdadero ninja de la terminal. 

En el próximo, vamos a hablar de variables, quoting, comandos encadenados, y empezar a entender por qué Bash puede ser también una herramienta para pensar con elegancia.

*No cierres la katana. Esto recién empieza.*

