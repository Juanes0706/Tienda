import os
from supabase import create_client, Client
from fastapi import UploadFile
import uuid

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --------------------------------------------------------------------------
# ¡CAMBIO AQUÍ! bucket_name ahora es "tienda"
# --------------------------------------------------------------------------
async def upload_image_to_supabase(file: UploadFile, bucket_name: str = "Tienda") -> str:
    """
    Uploads an image file to the Supabase storage bucket and returns the public URL.
    """
    if not SUPABASE_URL or not SUPABASE_KEY:
        # Aunque esto es una buena práctica, asumo que ya lo revisaste
        raise ValueError("Supabase URL or Key not configured in environment variables")

    file_extension = file.filename.split(".")[-1]
    # Generate unique filename using UUID
    unique_filename = f"{uuid.uuid4()}.{file_extension}"

    # Read file content
    file_content = await file.read()

    # Upload file to Supabase bucket
    try:
        response = supabase.storage.from_(bucket_name).upload(unique_filename, file_content)
    except Exception as e:
        raise RuntimeError(f"Failed to upload file to Supabase: {e}")

    # No need to check for error in response since upload raises exceptions on failure

    # Get public URL (returns string)
    public_url = supabase.storage.from_(bucket_name).get_public_url(unique_filename)
    if not public_url:
        raise RuntimeError("Failed to get public URL after upload")

    return public_url
