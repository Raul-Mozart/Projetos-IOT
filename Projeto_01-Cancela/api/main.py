import os
from contextlib import asynccontextmanager
import psycopg
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime, timezone, timedelta

# Fuso horário de Brasília (UTC-3)
BR_TZ = timezone(timedelta(hours=-3))

# Conexão com o TimescaleDB
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://cancela:cancela123@localhost:5432/cancela_db",
)

conn: psycopg.Connection | None = None


def get_conn() -> psycopg.Connection:
    """Retorna a conexão ativa ou reconecta se estiver fechada/quebrada."""
    global conn
    try:
        if conn and not conn.closed:
            conn.execute("SELECT 1")
            return conn
    except Exception:
        pass
    conn = psycopg.connect(DATABASE_URL, autocommit=True)
    print("Conectado ao TimescaleDB")
    return conn


@asynccontextmanager
async def lifespan(app: FastAPI):
    global conn
    conn = psycopg.connect(DATABASE_URL, autocommit=True)
    print("Conectado ao TimescaleDB")
    yield
    if conn:
        conn.close()
        print("Conexão com TimescaleDB encerrada")


app = FastAPI(
    title="API Cancela Automática",
    version="1.0.0",
    description="API para receber dados do ESP32 - Sistema de Cancela Automática (Edge Computing)",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Helpers ---


def unix_to_br(timestamp_str: str) -> datetime:
    """Converte Unix timestamp (string) para datetime no fuso de Brasília."""
    ts = int(timestamp_str)
    return datetime.fromtimestamp(ts, tz=BR_TZ)


# --- Modelos ---


class EventoCancela(BaseModel):
    deviceId: str
    timestamp: str
    distancia: float
    cancelaAberta: bool
    tempoAbertura: int
    localizacao: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "deviceId": "esp32-cancela-01",
                    "timestamp": "1772668220",
                    "distancia": 85.5,
                    "cancelaAberta": True,
                    "tempoAbertura": 5000,
                    "localizacao": "Entrada Principal",
                }
            ]
        }
    }


# --- Endpoints ---


@app.get("/")
def health_check():
    return {"message": "API Cancela Automática is running"}


@app.post("/data")
def receber_evento(evento: EventoCancela):
    timestamp_br = unix_to_br(evento.timestamp)

    registro = evento.model_dump()
    registro["timestamp"] = timestamp_br.strftime("%d/%m/%Y %H:%M:%S")
    registro["recebido_em"] = datetime.now(BR_TZ).strftime("%d/%m/%Y %H:%M:%S")

    print(f"Evento recebido: {registro}")

    # Salva no TimescaleDB apenas quando a cancela está aberta
    if evento.cancelaAberta:
        get_conn().execute(
            """
            INSERT INTO eventos_cancela
                (timestamp, device_id, distancia, cancela_aberta, tempo_abertura, localizacao)
            VALUES
                (%s, %s, %s, %s, %s, %s)
            """,
            (
                timestamp_br,
                evento.deviceId,
                evento.distancia,
                evento.cancelaAberta,
                evento.tempoAbertura,
                evento.localizacao,
            ),
        )
        print("Evento salvo no TimescaleDB")

    return {"status": "ok", "timestamp_br": registro["timestamp"]}


@app.get("/data")
def listar_eventos(limit: int = 50):
    rows = get_conn().execute(
        """
        SELECT timestamp, device_id, distancia, cancela_aberta, tempo_abertura, localizacao
        FROM eventos_cancela
        ORDER BY timestamp DESC
        LIMIT %s
        """,
        (limit,),
    ).fetchall()

    eventos = [
        {
            "timestamp": row[0].astimezone(BR_TZ).strftime("%d/%m/%Y %H:%M:%S"),
            "deviceId": row[1],
            "distancia": row[2],
            "cancelaAberta": row[3],
            "tempoAbertura": row[4],
            "localizacao": row[5],
        }
        for row in rows
    ]

    return {"total": len(eventos), "eventos": eventos}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=3000)
