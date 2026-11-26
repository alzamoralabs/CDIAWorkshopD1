"""MCP Server sobre Tavily: expone web_search y extract_page por stdio."""
import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from tavily import TavilyClient
from tavily.errors import InvalidAPIKeyError, UsageLimitExceededError

# Las claves viven en .env (junto a este archivo); si el cliente ya pasó una variable, esa gana.
load_dotenv(Path(__file__).parent / ".env")

# En Windows, stderr usa por defecto la codificación local (cp1252): forzamos UTF-8 para que el log sea legible.
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# IMPORTANTE: en stdio, stdout es el canal del protocolo. Los logs SIEMPRE van a stderr.
logging.basicConfig(stream=sys.stderr, level=logging.INFO, format="[tavily-mcp] %(levelname)s %(message)s")
log = logging.getLogger("tavily-mcp")

mcp = MCPServer("tavily-foodie")


def _client() -> TavilyClient:
    key = os.getenv("TAVILY_API_KEY")
    if not key:
        raise ToolError("TAVILY_API_KEY no está definida en el servidor (revisa el archivo .env).")
    return TavilyClient(api_key=key)


def _explain(exc: Exception) -> ToolError:
    """Traduce errores de Tavily a mensajes que el MODELO pueda leer y entender.
    (Si dejamos escapar una excepción cualquiera, el modelo solo vería 'Error executing tool <nombre>'.)"""
    if isinstance(exc, InvalidAPIKeyError):
        return ToolError("Tavily rechazó la clave de API (inválida). No se puede buscar en la web ahora.")
    if isinstance(exc, UsageLimitExceededError):
        return ToolError("Se agotó la cuota de Tavily. No se puede buscar en la web ahora.")
    return ToolError(f"Falló la llamada a Tavily: {type(exc).__name__}: {exc}")


@mcp.tool()
def web_search(query: str, max_results: int = 5) -> str:
    """Busca en internet y devuelve títulos, URLs y fragmentos de texto.
    Úsala para DESCUBRIR información actual: si un restaurante sigue abierto, su dirección,
    horarios, reseñas recientes. NO sirve para leer una página completa (para eso, extract_page)."""
    max_results = max(1, min(max_results, 8))
    log.info("web_search query=%r max_results=%s", query, max_results)
    client = _client()
    try:
        data = client.search(query=query, max_results=max_results, search_depth="basic")
    except Exception as exc:
        log.error("web_search falló: %r", exc)
        raise _explain(exc) from exc
    items = data.get("results", [])
    if not items:
        return "SIN_RESULTADOS: la búsqueda no devolvió páginas."
    return "\n\n".join(
        f"[{i}] {r['title']}\nURL: {r['url']}\n{r['content'][:500]}" for i, r in enumerate(items, 1)
    )


@mcp.tool()
def extract_page(url: str) -> str:
    """Descarga y devuelve el texto completo de UNA página web a partir de su URL.
    Úsala solo cuando ya tengas una URL concreta (por ejemplo, devuelta por web_search)
    y necesites leer el detalle: la carta, el horario, una reseña larga."""
    log.info("extract_page url=%s", url)
    client = _client()
    try:
        data = client.extract(urls=[url])
    except Exception as exc:
        log.error("extract_page falló: %r", exc)
        raise _explain(exc) from exc
    results = data.get("results", [])
    if not results:
        raise ToolError(f"No se pudo extraer el contenido de {url}: {data.get('failed_results', [])}")
    return results[0]["raw_content"][:6000]


if __name__ == "__main__":
    mcp.run(transport="stdio")
