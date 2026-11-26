"""Regenera los dos notebooks (solución y alumno) a partir de dev/lab_source.txt.

Uso (con el .venv activo y `pip install nbformat`):  python dev/build_notebooks.py

Formato de la fuente: cada celda empieza con una línea `@@@ md` o `@@@ code`.
Las partes que el alumno debe completar van entre `# <SOLUCION: pista>` y `# </SOLUCION>`:
en la versión solución se conserva el código; en la versión alumno se reemplaza por un TODO.
"""
import re
from pathlib import Path

import nbformat
from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook

AQUI = Path(__file__).parent
START = re.compile(r"^(\s*)# <SOLUCION(?::\s*(.*))?>\s*$")
END = re.compile(r"^\s*# </SOLUCION>\s*$")


def parse(path: Path):
    cells, kind, buf = [], None, []
    for line in path.read_text(encoding="utf-8").split("\n"):
        m = re.match(r"^@@@ (md|code)\s*$", line)
        if m:
            if kind:
                cells.append((kind, "\n".join(buf).strip("\n")))
            kind, buf = m.group(1), []
        else:
            buf.append(line)
    if kind:
        cells.append((kind, "\n".join(buf).strip("\n")))
    return cells


def transform(src: str, alumno: bool) -> str:
    out, dentro, sangria = [], False, ""
    for line in src.split("\n"):
        if not dentro:
            m = START.match(line)
            if m:
                dentro, sangria = True, m.group(1)
                if alumno:
                    out += [f"{sangria}# TODO: {(m.group(2) or 'completa esta parte').strip()}",
                            f'{sangria}raise NotImplementedError("Completa el TODO")']
                continue
            out.append(line)
        elif END.match(line):
            dentro = False
        elif not alumno:
            out.append(line)
    assert not dentro, "marcador sin cerrar"
    return "\n".join(out)


def build(cells, alumno: bool):
    nb = new_notebook()
    nb.metadata = {"kernelspec": {"display_name": "Python (.venv foodie-lab)", "language": "python", "name": "foodie-lab"},
                   "language_info": {"name": "python"}}
    for kind, src in cells:
        src = transform(src, alumno)
        nb.cells.append(new_markdown_cell(src) if kind == "md" else new_code_cell(src))
    nbformat.validate(nb)
    return nb


if __name__ == "__main__":
    cells = parse(AQUI / "lab_source.txt")
    nbformat.write(build(cells, False), AQUI.parent / "foodie_agent_lab_solucion.ipynb")
    nbformat.write(build(cells, True), AQUI.parent / "foodie_agent_lab_alumno.ipynb")
    print(f"{len(cells)} celdas → notebooks regenerados")
