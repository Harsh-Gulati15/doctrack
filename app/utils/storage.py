"""
storage.py — Unified file-storage abstraction for DocTrack.

When GCS_BUCKET_NAME is configured, files are stored in Google Cloud Storage.
Otherwise, falls back to the local filesystem (for local development).
"""

import io
import os
import tempfile
from datetime import timedelta

from flask import current_app, send_from_directory, redirect, Response


def _use_gcs() -> bool:
    """Return True when the app is configured to use GCS."""
    return bool(current_app.config.get('GCS_BUCKET_NAME'))


def _get_bucket():
    """Return the GCS bucket object (lazily imported)."""
    from google.cloud import storage as gcs
    client = gcs.Client(project=current_app.config.get('GOOGLE_CLOUD_PROJECT'))
    return client.bucket(current_app.config['GCS_BUCKET_NAME'])


# ------------------------------------------------------------------
# Upload
# ------------------------------------------------------------------

def upload_file(file_obj, filename: str) -> str:
    """
    Save an uploaded file and return the stored path/blob name.

    Parameters
    ----------
    file_obj : werkzeug.datastructures.FileStorage
        The uploaded file from request.files.
    filename : str
        The target filename (typically a UUID-based name).

    Returns
    -------
    str
        The blob name (GCS) or the local filename.
    """
    if _use_gcs():
        bucket = _get_bucket()
        blob = bucket.blob(f"uploads/{filename}")
        blob.upload_from_file(file_obj, content_type=file_obj.content_type)
        current_app.logger.info(f"Uploaded {filename} to GCS bucket")
        return f"uploads/{filename}"
    else:
        # Local filesystem
        upload_folder = current_app.config.get('UPLOAD_FOLDER_ABS', 'uploads')
        os.makedirs(upload_folder, exist_ok=True)
        local_path = os.path.join(upload_folder, filename)
        file_obj.save(local_path)
        current_app.logger.info(f"Saved {filename} to local disk")
        return filename


# ------------------------------------------------------------------
# Serve / Download
# ------------------------------------------------------------------

def serve_file(file_path: str):
    """
    Return a Flask response that serves the file.

    For GCS: redirects to a short-lived signed URL.
    For local: uses send_from_directory.

    Parameters
    ----------
    file_path : str
        The stored file_path value from the Document model.
    """
    if _use_gcs():
        bucket = _get_bucket()
        # file_path may be "uploads/xxx.pdf" or just "xxx.pdf"
        blob_name = file_path if file_path.startswith('uploads/') else f"uploads/{file_path}"
        blob = bucket.blob(blob_name)

        if not blob.exists():
            current_app.logger.warning(f"GCS blob not found: {blob_name}")
            return Response("File not found", status=404)

        url = blob.generate_signed_url(
            version="v4",
            expiration=timedelta(hours=1),
            method="GET",
        )
        return redirect(url)
    else:
        upload_folder = current_app.config.get('UPLOAD_FOLDER_ABS', 'uploads')
        basename = os.path.basename(file_path)
        return send_from_directory(upload_folder, basename)


# ------------------------------------------------------------------
# Download to temp file (for OCR processing)
# ------------------------------------------------------------------

def download_to_temp(file_path: str, file_type: str) -> str:
    """
    Download a file to a local temporary path for processing (e.g. OCR).

    Returns the absolute path of the temp file.
    The caller is responsible for cleanup.

    Parameters
    ----------
    file_path : str
        The stored file_path value from the Document model.
    file_type : str
        The file extension/type (e.g. 'pdf', 'jpeg').

    Returns
    -------
    str
        Absolute path to the temporary file.
    """
    if _use_gcs():
        bucket = _get_bucket()
        blob_name = file_path if file_path.startswith('uploads/') else f"uploads/{file_path}"
        blob = bucket.blob(blob_name)

        suffix = f".{file_type}" if file_type else ""
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        blob.download_to_filename(tmp.name)
        tmp.close()
        return tmp.name
    else:
        upload_folder = current_app.config.get('UPLOAD_FOLDER_ABS', 'uploads')
        basename = os.path.basename(file_path)
        return os.path.join(upload_folder, basename)
