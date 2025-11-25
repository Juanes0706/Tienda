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
    # Esta línea ahora usará "tienda"
    response = supabase.storage.from_(bucket_name).upload(unique_filename, file_content)

    if response.get("error"):
        # Esto capturará cualquier otro error de Supabase
        raise RuntimeError(f"Error uploading file to Supabase: {response['error']['message']}")

    # Get public URL
    public_url_response = supabase.storage.from_(bucket_name).get_public_url(unique_filename)
    public_url = public_url_response.get("publicUrl")
    if not public_url:
        raise RuntimeError("Failed to get public URL after upload")

    return public_url