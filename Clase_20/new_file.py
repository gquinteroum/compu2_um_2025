import asyncio

# -----------------------------------------------------------
# 🧠 Una corrutina es una función async que puede "pausarse"
# con 'await' para dejar que otras corrutinas sigan corriendo.
# -----------------------------------------------------------
async def cocinar(nombre, tiempo):
    print(f"👨‍🍳 {nombre} ha empezado a cocinar...")
    await asyncio.sleep(tiempo)  # Simula que tarda un tiempo
    print(f"✅ {nombre} ha terminado de cocinar.")
    return f"{nombre} listo"

# -----------------------------------------------------------
# 🧠 Función principal asíncrona
# Aquí creamos y gestionamos tareas.
# -----------------------------------------------------------
async def main():
    print("🍽️ Inicio del programa\n")

    # ✅ Crear tareas con asyncio.create_task()
    # Esto le dice al event loop: “Ejecuta estas corrutinas de forma concurrente”.
    tarea1 = asyncio.create_task(cocinar("Pasta", 3))
    tarea2 = asyncio.create_task(cocinar("Sopa", 2))
    tarea3 = asyncio.create_task(cocinar("Pizza", 4))

    print("🔄 Mientras se cocinan los platos, el chef puede hacer otras cosas...\n")

    # ✅ Podemos hacer otra cosa mientras las tareas se ejecutan en segundo plano
    await asyncio.sleep(1)
    print("🧹 El chef limpia la cocina mientras espera...\n")

    # ✅ Esperamos que terminen todas las tareas
    resultados = await asyncio.gather(tarea1, tarea2, tarea3)

    print("\n🍽️ Todos los platos están listos:")
    for r in resultados:
        print("  -", r)

    print("\n🏁 Fin del programa")

# -----------------------------------------------------------
# 🚀 Ejecutamos el bucle de eventos
# -----------------------------------------------------------
asyncio.run(main())
