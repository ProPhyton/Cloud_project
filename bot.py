import requests
import random
import time
import sys

# La URL local donde el comando 'port-forward' expone tu frontend/backend proxy
BASE_URL = "http://localhost:8080/api"

# Bancos de datos de prueba para que el bot invente encuestas realistas
TEMAS_PREGUNTAS = [
    "¿Cuál es el mejor lenguaje de programación?",
    "¿Quién ganará la Champions League este año?",
    "¿Qué base de datos prefieres para entornos distribuidos?",
    "¿Cuál es tu servicio favorito de Cloud Computing?",
    "¿Cada cuánto tiempo haces commits en GitHub?",
    "¿Qué tecnología de containerización utilizas más?"
]

BANCO_OPCIONES = [
    ["Python", "Go", "Java", "Rust"],
    ["Real Madrid", "Olympiacos", "Panathinaikos", "Bayern"],
    ["PostgreSQL", "MongoDB", "Redis", "MySQL"],
    ["Kubernetes", "Docker Desktop", "AWS", "Google Cloud"],
    ["Cada hora", "Una vez al día", "Nunca, me gusta el riesgo"],
    ["Docker", "Podman", "Containerd"]
]

print("==================================================")
print("🤖 BOT INTELIGENTE V2: CREADOR Y VOTANTE DE ENCUESTAS")
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

encuestas_creadas = 0
votos_totales = 0

while True:
    try:
        # Decisión inteligente: 20% crear encuesta, 80% votar
        accion = random.choices(["crear", "votar"], weights=[20, 80], k=1)[0]

        if accion == "crear":
            # --- SIMULAR TRÁFICO DE ESCRITURA (POST /polls) ---
            indice_aleatorio = random.randint(0, len(TEMAS_PREGUNTAS) - 1)
            nueva_pregunta = f"{TEMAS_PREGUNTAS[indice_aleatorio]} (#{random.randint(100, 999)})"
            nuevas_opciones = BANCO_OPCIONES[indice_aleatorio]

            payload_crear = {
                "question": nueva_pregunta,
                "options": nuevas_opciones
            }

            # Tu app.py responde con la id de la nueva encuesta creada
            respuesta = requests.post(f"{BASE_URL}/polls", json=payload_crear, timeout=2)
            if respuesta.status_code == 201:
                encuestas_creadas += 1
                print(f"➕ [Creada #{encuestas_creadas}] Nueva encuesta en el sistema: \"{nueva_pregunta}\"")

        else:
            # --- SIMULAR TRÁFICO DE LECTURA Y VOTO (GET y POST /vote) ---
            respuesta = requests.get(f"{BASE_URL}/polls", timeout=2)
            encuestas = respuesta.json()

            if not encuestas:
                print("📭 No hay encuestas en el sistema. Esperando que el bot cree una...")
                time.sleep(2)
                continue

            # Selecciona una encuesta y un botón de opción de manera aleatoria
            encuesta_elegida = random.choice(encuestas)
            poll_id = encuesta_elegida["id"]
            pregunta = encuesta_elegida["question"]
            opciones = encuesta_elegida["options"]

            if len(opciones) == 0:
                continue

            opcion_indice = random.randint(0, len(opciones) - 1)
            nombre_opcion = opciones[opcion_indice]

            # Enviar el voto simulando el clic
            payload_votar = {"option_index": opcion_indice}
            requests.post(f"{BASE_URL}/polls/{poll_id}/vote", json=payload_votar, timeout=2)

            votos_totales += 1
            print(f"🎯 [Voto #{votos_totales}] Click en '{nombre_opcion}' para la encuesta: \"{pregunta}\"")

        # Carga variable por segundo (QPS variables para simular picos reales)
        time.sleep(random.uniform(0.02, 0.1))

    except requests.exceptions.RequestException:
        print("🔥 El servidor está bajo mucho estrés... El bot continúa atacando.")
        time.sleep(0.1)
    except KeyboardInterrupt:
        print(f"\n🛑 Bot detenido. Resumen: {encuestas_creadas} encuestas creadas y {votos_totales} votos inyectados.")
        break