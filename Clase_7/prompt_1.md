### Prompt Educativo para IA: Señales en Sistemas Operativos

Hola, soy estudiante de la asignatura **Computación II** en la Universidad de Mendoza. Esta es una clase **avanzada** y necesito una **guía paso a paso** sobre el tema de **señales en sistemas operativos**, centrada en su funcionamiento interno, implementación práctica en Python y relevancia en sistemas concurrentes.

---

### Objetivos de aprendizaje

Al finalizar esta sesión, necesito:

- Comprender profundamente qué son las señales en sistemas UNIX y POSIX.
- Distinguir los tipos de señales (síncronas, asíncronas, tiempo real).
- Implementar correctamente un manejador de señales en Python.
- Saber cómo se manejan señales en entornos multihilo y multiclase.
- Preparar un ejercicio funcional que muestre sincronización entre procesos con señales.
- Completar una entrega obligatoria (código + cuestionario de comprensión).
- No necesito configurar herramientas externas, pero usaré Python desde la terminal.

---

### Reglas de interacción con la IA

Por favor:

- Guíame **paso a paso** en cada subtema que abordemos.
- Comienza **siempre** con una **explicación conceptual detallada**, antes de mostrar código o ejemplos prácticos.
- Si empiezo a desviarme del tema, ayúdame a **volver al objetivo principal**.
- **Al final de cada sección importante**, haz una pausa para una **puesta en común con la clase**.
- En esos momentos, formula **2 a 3 preguntas de comprensión** sobre lo recién aprendido.
- También recordame que comparta mis avances con el profesor en esas pausas.

---

### Estructura para los temas a desarrollar

Para cada uno de los siguientes temas, por favor desarrolla:

1. Una **explicación teórica** clara y profunda.
2. **Instrucciones prácticas paso a paso** para aplicarlo.
3. **Ejemplos de código comentado**, preferentemente en Python.
4. **Ejercicios prácticos** (nivel básico, medio y avanzado).

Temas a desarrollar:
- ¿Qué son las señales y por qué son importantes?
- `signal.signal()` y funciones relacionadas en Python
- `kill`, `sigqueue` y `sigaction` (referencia cruzada con C si es útil)
- Uso de señales para sincronizar procesos
- Manejo seguro y async-signal-safe
- Señales en sistemas multihilo
- Comparaciones con otros mecanismos de IPC

---

### Temas que serán tratados después

- Señales reales (`SIGRTMIN` y `sigqueue`) en detalle
- Manejo avanzado en C con `sigaction`, `siginfo_t`
- Implementación en entornos embebidos o RTOS

Si pregunto sobre estos ahora, por favor respondé **brevemente**, y recordame **volver al foco de esta clase**.

---

### Recordatorios importantes

- Si avanzo demasiado rápido, avisame. Quiero **entender los fundamentos** antes de seguir.
- Si hay **partes críticas que debo completar** (como terminar de escribir un handler), no me dejes pasar hasta que las termine, aunque estemos contra el tiempo.
- Asegurate de que **no me olvide de documentar o testear** mi código final.

---