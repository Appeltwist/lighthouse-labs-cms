import mimetypes
import os
import re
from pathlib import Path

from django.conf import settings
from django.http import FileResponse, Http404, HttpResponse, StreamingHttpResponse
from django.utils._os import safe_join
from django.utils.http import http_date


RANGE_RE = re.compile(r"bytes=(\d*)-(\d*)$")
CHUNK_SIZE = 8192


def _iter_file_range(file_path: str, start: int, length: int):
    remaining = length
    with open(file_path, "rb") as file_handle:
        file_handle.seek(start)
        while remaining > 0:
            chunk = file_handle.read(min(CHUNK_SIZE, remaining))
            if not chunk:
                break
            remaining -= len(chunk)
            yield chunk


def _build_headers(file_path: str, content_length: int) -> dict[str, str]:
    return {
        "Accept-Ranges": "bytes",
        "Content-Disposition": f'inline; filename="{Path(file_path).name}"',
        "Content-Length": str(content_length),
        "Last-Modified": http_date(os.path.getmtime(file_path)),
    }


def serve_media(request, path: str):
    file_path = safe_join(settings.MEDIA_ROOT, path)
    if not file_path or not os.path.exists(file_path) or os.path.isdir(file_path):
        raise Http404("Media file does not exist.")

    file_size = os.path.getsize(file_path)
    content_type, _ = mimetypes.guess_type(file_path)
    content_type = content_type or "application/octet-stream"
    range_header = request.headers.get("Range") or request.META.get("HTTP_RANGE")

    if range_header:
        match = RANGE_RE.match(range_header.strip())
        if not match:
            return HttpResponse(status=416, headers={"Content-Range": f"bytes */{file_size}"})

        start_text, end_text = match.groups()
        if not start_text and not end_text:
            return HttpResponse(status=416, headers={"Content-Range": f"bytes */{file_size}"})

        if start_text:
            start = int(start_text)
            end = int(end_text) if end_text else file_size - 1
        else:
            suffix_length = int(end_text)
            if suffix_length <= 0:
                return HttpResponse(status=416, headers={"Content-Range": f"bytes */{file_size}"})
            start = max(file_size - suffix_length, 0)
            end = file_size - 1

        if start >= file_size or start < 0 or end < start:
            return HttpResponse(status=416, headers={"Content-Range": f"bytes */{file_size}"})

        end = min(end, file_size - 1)
        content_length = end - start + 1
        headers = _build_headers(file_path, content_length)
        headers["Content-Range"] = f"bytes {start}-{end}/{file_size}"

        if request.method == "HEAD":
            return HttpResponse(status=206, content_type=content_type, headers=headers)

        return StreamingHttpResponse(
            _iter_file_range(file_path, start, content_length),
            status=206,
            content_type=content_type,
            headers=headers,
        )

    headers = _build_headers(file_path, file_size)
    if request.method == "HEAD":
        return HttpResponse(status=200, content_type=content_type, headers=headers)

    response = FileResponse(open(file_path, "rb"), content_type=content_type)
    for key, value in headers.items():
        response[key] = value
    return response
