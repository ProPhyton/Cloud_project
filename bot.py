import requests
import random
import time
import sys

# La URL local donde el comando 'port-forward' expone tu frontend/backend proxy
BASE_URL = "http://localhost:8080/api"

print("==================================================")
print("🤖 SIMULADOR DE TRÁFICO EXTERNO: BOT DE ENCUESTAS")
print("==================================================")
print("-> Apuntando a: http://localhost:8080")
print("-> Presiona Ctrl+C para detener el bot.\n")

# Comprobación inicial de conectividad
try:
    requests.get(f"{BASE_URL}/polls", timeout=3)
except requests.exceptions.ConnectionError:
    print("❌ ERROR: No se puede conectar con http://localhost:8080")
    print("👉 Asegúrate de tener activo el comando: kubectl port-forward svc/frontend-service 8080:80")
    sys.exit(1)

votos_totales = 0

while True:
    try:
        # 1. El bot escanea la web para ver qué encuestas existen actualmente
        respuesta = requests.get(f"{BASE_URL}/polls", timeout=2)
        encuestas = respuesta.json()

        if not encuestas:
            print("📭 No hay encuestas creadas en la web todavía. Esperando...")
            time.sleep(3)
            continue

        # 2. Selecciona una encuesta al azar (Simula al usuario eligiendo qué votar)
        encuesta_elegida = random.choice(encuestas)
        poll_id = encuesta_elegida["id"]
        pregunta = encuesta_elegida["question"]
        opciones = encuesta_elegida["options"]

        # 3. Identifica cuántos botones (opciones) tiene esa encuesta y elige uno al azar
        num_opciones = len(opciones)
        if num_opciones == 0:
            continue
        
        opcion_indice_elegido = random.randint(0, num_opciones - 1)
        nombre_opcion_elegida = opciones[opcion_indice_elegido]

        # 4. Simula el CLICK en el botón enviando la petición POST exacta
        # Estructura del JSON requerida por tu app.py: {"option_index": X}
        payload = {"option_index": opcion_indice_elegido}
        
        url_voto = f"{BASE_URL}/polls/{poll_id}/vote"
        requests.post(url_voto, json=payload, timeout=2)

        votos_totales += 1
        print(f"🎯 [Voto #{votos_totales}] Click en botón '{nombre_opcion_elegida}' de la encuesta: \"{pregunta}\"")

        # 5. Carga variable inteligente (Queries per Second variables)
        # Introduce pausas aleatorias muy cortas para simular ráfagas de usuarios reales (Facebook style)
        pausa = random.uniform(0.01, 0.08)  # Entre 10 y 80 milisegundos
        time.sleep(pausa)

    except requests.exceptions.RequestException:
        # Si el backend empieza a colapsar por el estrés (lo cual es nuestro objetivo),
        # el bot no se detiene con un error en rojo, sino que sigue enviando tráfico tenazmente.
        print("🔥 Servidor saturado (Respuesta lenta)... El bot mantiene el ataque.")
        time.sleep(0.1)
    except KeyboardInterrupt:
        print("\n🛑 Bot detenido por el usuario. Total de clicks simulados:", votos_totales)
        break