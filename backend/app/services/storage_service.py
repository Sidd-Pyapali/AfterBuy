import uuid
from app.core import config
from app.core.supabase_client import get_supabase


def upload_image(file_bytes: bytes, original_filename: str, content_type: str) -> str:
    """Upload image bytes to Supabase Storage and return the public URL."""
    client = get_supabase()
    bucket = config.SUPABASE_STORAGE_BUCKET

    ext = original_filename.rsplit(".", 1)[-1] if "." in original_filename else "jpg"
    storage_path = f"{uuid.uuid4()}.{ext}"

    client.storage.from_(bucket).upload(
        path=storage_path,
        file=file_bytes,
        file_options={"content-type": content_type},
    )

    return client.storage.from_(bucket).get_public_url(storage_path)
