# UTEC CDIA Workshop Day 1
# 🍽️ Foodie: tu primer agente con LangChain (workshop hands-on)

Lab para alumnos de ciencia de datos: **workflows vs agentes** (según *Building Effective Agents* de Anthropic), un agente **ReAct** con `gpt-5-mini`, un **servidor MCP propio sobre Tavily**, y **testing/debugging** de agentes. Duración: ≈ 2 h 50 min.

## Contenido

| Archivo | Para qué |
|---|---|
| `foodie_agent_lab_alumno.ipynb` | Versión para los alumnos (celdas con `# TODO`) |
| `foodie_agent_lab_solucion.ipynb` | Versión resuelta (para el instructor) |
| `requirements.txt` | Dependencias con versiones fijadas (probado con Python 3.12) |
| `.env.example` | Plantilla de claves → copiar como `.env` |
| `collect_transcripts.py` | **Instructor:** descarga transcripciones de YouTube (ver "Datos") |
| `data/menciones_demo.csv` | Tabla **ficticia** de menciones (Canal Demo A/B/C) |
| `data/transcripcion_demo.txt` | Transcripción **ficticia** para el workflow de la Parte 1 |
| `dev/` | Fuente única del notebook y script para regenerar ambas versiones |

El servidor MCP (`tavily_mcp_server.py`) **lo genera el notebook** con `%%writefile` en la Parte 3A.

## Inicio rápido

```bash
python3 -m venv .venv
source .venv/bin/activate                 # Windows (PowerShell): .venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m ipykernel install --user --name foodie-lab --display-name "Python (.venv foodie-lab)"
cp .env.example .env                      # completa OPENAI_API_KEY y TAVILY_API_KEY
jupyter lab                               # o abre el notebook en VS Code y elige el kernel «Python (.venv foodie-lab)»
```

`.venv/` y `.env` están en `.gitignore`: nunca subas tus claves.

## Datos

El lab funciona de inmediato con los **datos demo ficticios**. Para usar youtubers reales:

1. Completa `CANALES` en `collect_transcripts.py` y ejecútalo **en tu máquina local** (YouTube suele bloquear las IPs de Colab y de servidores).
2. Ejecuta el **Anexo A** del notebook: aplica el workflow de la Parte 1 a cada transcripción y crea `data/menciones.csv`, que el notebook usa automáticamente.

Las transcripciones son contenido de terceros: `data/transcripts/` está en `.gitignore`. Si publicas el repo, considera publicar solo la tabla derivada (comentarios resumidos) y citar canal y video.

## Notas técnicas

- **`pip install mcp` instala la v2.x**, donde `FastMCP` pasó a llamarse `MCPServer` y el cliente es `Client`. Si ves tutoriales con `FastMCP`, son de la v1. Las versiones están fijadas en `requirements.txt`.
- **`gpt-5-mini`** es un modelo de razonamiento: no admite `temperature` y su razonamiento interno no se expone. El modelo se cambia en una sola variable (`MODEL_NAME`).
- Las respuestas de un LLM no son deterministas: las fallas sembradas de la Parte 4 pueden comportarse distinto entre ejecuciones.

## Solución de problemas

| Síntoma | Causa probable |
|---|---|
| `ModuleNotFoundError` | El kernel no es el del `.venv`: elige «Python (.venv foodie-lab)» |
| `Faltan variables en tu archivo .env` | Falta copiar `.env.example` a `.env` o completar las claves |
| `ERROR de la herramienta web_search: … clave …` | `TAVILY_API_KEY` inválida o sin cuota |
| Tracebacks «Failed to parse JSONRPC message» | Algo imprime a stdout en el servidor (ver Falla 1 de la Parte 4) |
| `IpBlocked` en `collect_transcripts.py` | YouTube bloqueó tu IP: usa una red doméstica o un proxy |

## Estado de verificación

El notebook se ejecutó de punta a punta en un kernel real con un **modelo de lenguaje simulado y Tavily simulado**: valida el flujo, el servidor MCP por stdio, el puente a LangChain, las pruebas por capas, la evaluación, los límites de llamadas y la memoria. **No se probó con claves reales de OpenAI y Tavily ni contra YouTube**: conviene correr la versión solución completa una vez antes del workshop.

## Regenerar los notebooks

Edita `dev/lab_source.txt` y ejecuta (con `pip install nbformat`): `python dev/build_notebooks.py`.

