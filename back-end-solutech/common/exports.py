"""Exports CSV en streaming, partagés par les vues de rapport (CDC §3.2)."""

import csv
from typing import Iterable, Sequence

from django.http import StreamingHttpResponse


class _EchoBuffer:
    """Buffer qui renvoie la ligne écrite, requis par csv.writer en streaming."""

    def write(self, value):
        return value


def csv_safe(value: object) -> str:
    """Neutralise l'injection de formules (Excel/LibreOffice) dans une cellule."""
    text = "" if value is None else str(value)
    if text[:1] in ("=", "+", "-", "@", "\t", "\r"):
        text = "'" + text
    return text


def stream_csv_response(
    filename: str,
    header: Sequence[str],
    rows: Iterable[Sequence[object]],
) -> StreamingHttpResponse:
    """Réponse CSV streamée, avec BOM UTF-8 pour compatibilité Excel."""
    writer = csv.writer(_EchoBuffer())

    def generate():
        yield "\ufeff" + writer.writerow(header)
        for row in rows:
            yield writer.writerow([csv_safe(v) for v in row])

    response = StreamingHttpResponse(generate(), content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response
