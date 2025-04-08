# Comunicación entre procesos con Pipes en Rust

Rust es un lenguaje que conjuga la potencia del bajo nivel con una robusta seguridad en tiempo de compilación. Esto lo convierte en una excelente herramienta para enseñar conceptos fundamentales del sistema operativo, como la comunicación entre procesos. Una de las formas más clásicas de comunicación es a través de *pipes*, una técnica heredada de Unix que permite enviar datos de un proceso a otro.

En este documento vamos a explorar cómo implementar comunicación entre procesos mediante pipes usando Rust. Veremos cómo hacerlo tanto desde un enfoque de alto nivel, utilizando las herramientas que ofrece la biblioteca estándar, como desde un enfoque de bajo nivel, usando el crate `nix`, que expone las llamadas POSIX típicas del mundo C.

Al final, construiremos un ejemplo completo que consiste en un padre que escribe un mensaje y un hijo que lo lee y lo imprime usando `cat`.

---

## Pipes en Rust: Nivel alto

Cuando se quiere conectar procesos en Rust de forma ergonómica y segura, se puede usar el módulo `std::process`. Este módulo permite crear procesos hijos, redirigir su entrada y salida estándar, y conectar estos flujos entre sí.

Por ejemplo, si quisiéramos replicar un comando como:

```bash
echo "hola" | grep h
```

Podemos hacerlo con Rust así:

```rust
use std::process::{Command, Stdio};

let mut echo = Command::new("echo")
    .arg("hola")
    .stdout(Stdio::piped())
    .spawn()
    .expect("fallo al ejecutar echo");

let echo_stdout = echo.stdout.take().expect("fallo al capturar stdout");

let grep = Command::new("grep")
    .arg("h")
    .stdin(echo_stdout)
    .spawn()
    .expect("fallo al ejecutar grep");
```

Este enfoque es perfecto cuando se trabaja con comandos existentes del sistema y se necesita una forma simple de conectar sus entradas y salidas.

---

## Pipes en Rust: Nivel bajo

Si el objetivo es comprender en detalle cómo se crean los pipes y cómo se conectan los descriptores de archivo, podemos usar el crate `nix`, que proporciona una interfaz segura y idiomática para las llamadas del sistema POSIX como `pipe()`, `fork()`, `dup2()` y `close()`.

A continuación, te muestro un ejemplo completo y didáctico que crea un pipe entre dos procesos:

---

## Ejemplo: Pipe entre padre e hijo en Rust

Este programa crea un pipe. El proceso padre escribe un mensaje, y el hijo lo lee redirigiendo su `stdin` y luego ejecuta `cat` para imprimirlo.

### Código completo

```rust
use nix::unistd::{pipe, fork, ForkResult, dup2, close, write};
use std::process::Command;

fn main() {
    // Crear el pipe
    let (read_fd, write_fd) = pipe().expect("no se pudo crear el pipe");

    match unsafe { fork() } {
        Ok(ForkResult::Parent { .. }) => {
            // Cerrar el extremo de lectura en el padre
            close(read_fd).expect("no se pudo cerrar el read_fd en el padre");

            // Escribir un mensaje en el pipe
            write(write_fd, b"Hola desde el padre\n").expect("fallo al escribir");

            // Cerrar el extremo de escritura después de escribir
            close(write_fd).expect("no se pudo cerrar el write_fd en el padre");
        }
        Ok(ForkResult::Child) => {
            // Cerrar el extremo de escritura en el hijo
            close(write_fd).expect("no se pudo cerrar el write_fd en el hijo");

            // Redirigir stdin (fd 0) al read_fd
            dup2(read_fd, 0).expect("no se pudo redirigir stdin");

            // Ejecutar 'cat' que leerá del stdin redirigido
            let _ = Command::new("cat")
                .status()
                .expect("fallo al ejecutar cat");

            // Cerrar el extremo de lectura
            close(read_fd).expect("no se pudo cerrar el read_fd en el hijo");
        }
        Err(e) => {
            eprintln!("Error al hacer fork: {}", e);
        }
    }
}
```

Este ejemplo es ideal para comprender cómo funciona la redirección de descriptores de archivo, cómo se maneja la bifurcación de procesos y cómo se comunican usando un pipe.

---

## ¿Por qué enseñar esto en Rust?

Trabajar con pipes y procesos en C es muy útil para entender los fundamentos del sistema operativo, pero también es propenso a errores difíciles de depurar, como accesos inválidos a memoria o fugas. Rust ofrece una alternativa moderna: permite el mismo control de bajo nivel, pero con una capa de seguridad que ayuda a evitar errores sutiles.

Además, trabajar con estos conceptos en Rust puede ser una excelente puerta de entrada para aprender sobre:

- Espacios de direcciones entre procesos
- Seguridad y concurrencia
- Manipulación de recursos del sistema operativo

---

## Requisitos

Para correr este ejemplo, necesitás:

- Tener instalado Rust (con `cargo` y `rustc`)
- Agregar el crate `nix` a tu proyecto:

```bash
cargo add nix
```

---

## Conclusión

Este ejemplo muestra cómo Rust puede ser una herramienta poderosa y segura para enseñar programación de sistemas. Desde enfoques simples y modernos hasta interacciones crudas con el sistema operativo, Rust permite aprender sin miedo a errores de segmentación o corrupción de memoria.

Se puede usar este código como base para ejercicios donde se pida modificar el comportamiento del padre o del hijo, crear más procesos, o redirigir la salida a archivos. Así, se combina práctica con conceptos sólidos del sistema operativo.

