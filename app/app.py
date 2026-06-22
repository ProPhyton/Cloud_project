# Este backend expone una API REST para crear encuestas, votar
# y consultar resultados. Los datos se guardan en PostgreSQL.
# No se usa Redis; el frontend obtiene actualizaciones mediante
# sondeos periódicos (polling).
# ================================================================

import os, json
import psycopg2
from flask import Flask, request, jsonify

app = Flask(__name__)

# ----------------------------------------------------------------
# Configuración desde variables de entorno (inyectadas por Kubernetes)
# ----------------------------------------------------------------
DB_HOST = os.getenv("DB_HOST", "postgres")
DB_NAME = os.getenv("DB_NAME", "pollsdb")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

# ----------------------------------------------------------------
# Conexión a PostgreSQL
# ----------------------------------------------------------------
def get_db():
    return psycopg2.connect(
        host=DB_HOST,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

# ----------------------------------------------------------------
# Endpoints
# ----------------------------------------------------------------

# 1) Crear encuesta
@app.route('/polls', methods=['POST'])
def create_poll():
    data = request.json
    question = data['question']
    options = json.dumps(data['options'])   # lista -> JSON string
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO polls (question, options) VALUES (%s, %s) RETURNING id",
        (question, options)
    )
    poll_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"poll_id": poll_id}), 201

# 2) Listar encuestas
@app.route('/polls', methods=['GET'])
def list_polls():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, question, options FROM polls")
    rows = cur.fetchall()
    polls = []
    for row in rows:
        polls.append({
            "id": row[0],
            "question": row[1],
            "options": json.loads(row[2])
        })
    cur.close()
    conn.close()
    return jsonify(polls)

# 3) Votar
@app.route('/polls/<int:poll_id>/vote', methods=['POST'])
def vote(poll_id):
    option_index = request.json['option_index']
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO votes (poll_id, option_index) VALUES (%s, %s)",
        (poll_id, option_index)
    )
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"status": "ok"}), 200

# 4) Resultados
@app.route('/polls/<int:poll_id>/results')
def results(poll_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT options FROM polls WHERE id = %s", (poll_id,))
    row = cur.fetchone()
    if not row:
        cur.close(); conn.close()
        return jsonify([])
    opts = json.loads(row[0])
    counts = {i: 0 for i in range(len(opts))}
    cur.execute(
        "SELECT option_index, COUNT(*) FROM votes WHERE poll_id = %s GROUP BY option_index",
        (poll_id,)
    )
    for r in cur.fetchall():
        idx = r[0]
        if idx in counts:
            counts[idx] = r[1]
    result = [{"option": opts[i], "count": counts[i]} for i in range(len(opts))]
    cur.close(); conn.close()
    return jsonify(result)

# Health check (para readinessProbe de Kubernetes)
@app.route('/health')
def health():
    return "OK", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)