"""Script del INSTRUCTOR: descarga transcripciones de YouTube a data/transcripts/.

Ejecútalo UNA vez, en tu máquina local (las IPs de Colab/servidores suelen estar bloqueadas por YouTube):

    source .venv/bin/activate
    python collect_transcripts.py

Los archivos de data/transcripts/ son contenido de terceros y están en .gitignore: no los subas al repo.
Luego, el Anexo A del notebook los convierte en data/menciones.csv (tabla derivada y resumida).
"""
import csv
from pathlib import Path

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api import IpBlocked, RequestBlocked

# >>> COMPLETA con los canales y los IDs de video (lo que va después de ?v= en la URL) <<<
CANALES: dict[str, list[str]] = {
    "Canal 1": ["VIDEO_ID_1", "VIDEO_ID_2"],
    "Canal 2": ["VIDEO_ID_3"],
    "Canal 3": [],
}
IDIOMAS = ["es", "es-419", "es-PE"]

OUT = Path("data/transcripts")
OUT.mkdir(parents=True, exist_ok=True)
api = YouTubeTranscriptApi()
index_rows = []

for youtuber, video_ids in CANALES.items():
    for vid in video_ids:
        if vid.startswith("VIDEO_ID"):
            continue  # marcador de posición sin completar
        try:
            snippets = api.fetch(vid, languages=IDIOMAS)
            texto = " ".join(s.text.replace("\n", " ") for s in snippets)
            (OUT / f"{vid}.txt").write_text(texto, encoding="utf-8")
            index_rows.append({"youtuber": youtuber, "video_id": vid, "video_url": f"https://www.youtube.com/watch?v={vid}"})
            print(f"OK   {youtuber} {vid} ({len(texto)} caracteres)")
        except (IpBlocked, RequestBlocked):
            print(f"BLOQUEADO {vid}: YouTube bloqueó la IP. Prueba desde una red doméstica o con proxy.")
        except Exception as exc:  # video sin subtítulos, privado, etc.
            print(f"FALLÓ {vid}: {type(exc).__name__}: {exc}")

with open("data/transcripts_index.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["youtuber", "video_id", "video_url"])
    w.writeheader()
    w.writerows(index_rows)
print(f"Listo: {len(index_rows)} transcripciones en {OUT}/")
