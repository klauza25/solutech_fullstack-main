"""Exports CSV en streaming, partagés par les vues de rapport (CDC §3.2)."""

import csv
from typing import Iterable, Sequence

from django.http import StreamingHttpResponse


class _EchoBuffer:
    """Buffer qui renvoie la ligne écrite, requis par csv.writer en streaming."""

    def write(self, value):
        return value


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
            yield writer.writerow(["" if v is None else v for v in row])

    response = StreamingHttpResponse(generate(), content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response
