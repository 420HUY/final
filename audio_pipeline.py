#!/usr/bin/env python3
"""
Audio Transcript Pipeline - Vietnamese ASR with Supabase Integration
Fixes Supabase upload error: 'UploadResponse' object has no attribute 'status_code'
"""

import os
import re
import logging
import unicodedata
from typing import Optional, Tuple
from pathlib import Path

try:
    from supabase import create_client, Client
    from supabase.lib.client_options import ClientOptions
except ImportError:
    print("❌ Supabase không được cài đặt. Chạy: pip install supabase")
    exit(1)

def sanitize_filename_for_supabase(filename: str) -> str:
    """
    Sanitize filename for Supabase Storage compatibility.
    
    Supabase Storage only accepts keys with safe characters (a-z, A-Z, 0-9, '.', '_', '-', '/').
    This function:
    - Removes Vietnamese diacritics (á→a, ê→e, ô→o, etc.)
    - Replaces spaces and special characters with underscores
    - Handles nested folder paths properly
    - Ensures compatibility with Supabase Storage requirements
    
    Args:
        filename: Original filename or path
        
    Returns:
        Sanitized filename safe for Supabase Storage
    """
    if not filename:
        return ""
    
    # Split path into components to handle nested folders
    path_parts = filename.split('/')
    sanitized_parts = []
    
    for i, part in enumerate(path_parts):
        if not part:  # Skip empty parts
            continue
        
        is_last_part = i == len(path_parts) - 1
        
        # Check if this is the last part (filename) and has extension
        # A file has extension if it has a dot and the part after the last dot is not empty
        has_extension = (is_last_part and 
                        '.' in part and 
                        not part.startswith('.') and 
                        not part.endswith('.') and
                        part.rsplit('.', 1)[1])  # Extension part is not empty
        
        if has_extension:
            # Split filename and extension
            name_part, ext_part = part.rsplit('.', 1)
            # Process the name part only
            processed_name = _sanitize_part(name_part)
            # Combine with extension
            if processed_name:
                sanitized_part = f"{processed_name}.{ext_part}"
            else:
                sanitized_part = f"file.{ext_part}"  # Fallback if name becomes empty
        else:
            # Process as regular folder/filename without extension
            sanitized_part = _sanitize_part(part)
        
        # Ensure part is not empty after sanitization
        if sanitized_part:
            sanitized_parts.append(sanitized_part)
    
    # Join back with forward slashes for path
    result = '/'.join(sanitized_parts)
    
    # Final cleanup - ensure no double slashes
    result = re.sub(r'/+', '/', result)
    
    return result

def _sanitize_part(part: str) -> str:
    """
    Helper function to sanitize a single filename part.
    """
    if not part:
        return ""
    
    # Special handling for Vietnamese characters that don't normalize well
    vietnamese_map = {
        'Đ': 'D', 'đ': 'd',
        'Ď': 'D', 'ď': 'd'
    }
    
    # Apply Vietnamese character replacements first
    for vn_char, latin_char in vietnamese_map.items():
        part = part.replace(vn_char, latin_char)
    
    # Remove Vietnamese diacritics using unicodedata
    # This converts á→a, ê→e, ô→o, ư→u, etc.
    normalized = unicodedata.normalize('NFD', part)
    ascii_part = ''.join(c for c in normalized if unicodedata.category(c) != 'Mn')
    
    # Replace spaces and special characters with underscores
    # Keep only alphanumeric, dots, hyphens, and underscores
    sanitized_part = re.sub(r'[^a-zA-Z0-9._-]', '_', ascii_part)
    
    # Remove consecutive underscores
    sanitized_part = re.sub(r'_+', '_', sanitized_part)
    
    # Remove leading/trailing underscores and dots
    sanitized_part = sanitized_part.strip('_.')
    
    return sanitized_part

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SupabaseUploader:
    """Handle Supabase Storage operations for audio files"""
    
    def __init__(self, url: str, key: str, bucket_name: str = "audio_files"):
        """
        Initialize Supabase client
        
        Args:
            url: Supabase project URL
            key: Supabase anon/service role key
            bucket_name: Storage bucket name (default: 'audio_files')
        """
        self.supabase_url = url
        self.supabase_key = key
        self.bucket_name = bucket_name
        
        # Create client with proper options
        try:
            client_options = ClientOptions(auto_refresh_token=False)
            self.supabase: Client = create_client(url, key, options=client_options)
            logger.info(f"✅ Supabase client initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Supabase client: {e}")
            raise
    
    def test_connection(self) -> bool:
        """Test Supabase connection and bucket access"""
        try:
            # Test basic connection by trying to list buckets
            result = self.supabase.storage.list_buckets()
            logger.info(f"📡 Connection test successful. Available buckets: {len(result)}")
            
            # Check if our bucket exists
            bucket_exists = any(bucket.name == self.bucket_name for bucket in result)
            if bucket_exists:
                logger.info(f"✅ Bucket '{self.bucket_name}' exists")
            else:
                logger.warning(f"⚠️ Bucket '{self.bucket_name}' not found. Available buckets: {[b.name for b in result]}")
                # Try to create bucket
                try:
                    self.supabase.storage.create_bucket(self.bucket_name, options={"public": True})
                    logger.info(f"✅ Created bucket '{self.bucket_name}'")
                except Exception as create_error:
                    logger.error(f"❌ Failed to create bucket: {create_error}")
                    return False
            
            return True
        except Exception as e:
            logger.error(f"❌ Connection test failed: {e}")
            return False

    def upload_audio_to_supabase(self, file_path: str, file_name: str) -> Optional[str]:
        """
        Upload audio file to Supabase Storage with proper error handling
        
        Args:
            file_path: Local path to the audio file
            file_name: Name to use in storage (will be sanitized for Supabase)
            
        Returns:
            Public URL of uploaded file, or None if upload failed
        """
        if not os.path.exists(file_path):
            logger.error(f"❌ File not found: {file_path}")
            return None
        
        # Sanitize filename for Supabase Storage compatibility
        sanitized_file_name = sanitize_filename_for_supabase(file_name)
        
        if sanitized_file_name != file_name:
            logger.info(f"🔧 Sanitized filename: '{file_name}' → '{sanitized_file_name}'")
        
        file_size = os.path.getsize(file_path)
        logger.info(f"📤 Uploading {sanitized_file_name} ({file_size} bytes) to Supabase...")
        
        try:
            # Read file content
            with open(file_path, 'rb') as file:
                file_content = file.read()
            
            # First attempt: regular upload
            try:
                result = self.supabase.storage.from_(self.bucket_name).upload(
                    path=sanitized_file_name,
                    file=file_content,
                    file_options={"content-type": self._get_content_type(sanitized_file_name)}
                )
                
                # NEW: Handle new Supabase response format without status_code
                # Check if upload was successful by examining the result object
                if result and hasattr(result, 'path'):
                    logger.info(f"✅ Upload successful: {sanitized_file_name}")
                    return self._get_public_url(sanitized_file_name)
                elif result:
                    # Even if no path attribute, consider successful if no exception
                    logger.info(f"✅ Upload completed: {sanitized_file_name}")
                    return self._get_public_url(sanitized_file_name)
                else:
                    raise Exception("Upload returned empty result")
                    
            except Exception as upload_error:
                error_msg = str(upload_error).lower()
                
                # Handle "file already exists" scenario with upsert
                if "already exists" in error_msg or "duplicate" in error_msg:
                    logger.warning(f"⚠️ File exists, attempting upsert: {sanitized_file_name}")
                    try:
                        # Use upsert to overwrite existing file
                        result = self.supabase.storage.from_(self.bucket_name).upload(
                            path=sanitized_file_name,
                            file=file_content,
                            file_options={
                                "content-type": self._get_content_type(sanitized_file_name),
                                "upsert": True  # Overwrite if exists
                            }
                        )
                        
                        # Handle upsert result
                        if result:
                            logger.info(f"✅ Upsert successful: {sanitized_file_name}")
                            return self._get_public_url(sanitized_file_name)
                        else:
                            raise Exception("Upsert returned empty result")
                            
                    except Exception as upsert_error:
                        logger.error(f"❌ Upsert failed for {sanitized_file_name}: {upsert_error}")
                        return None
                else:
                    # Re-raise other upload errors
                    raise upload_error
                    
        except Exception as e:
            logger.error(f"❌ Lỗi upload {sanitized_file_name}: {e}")
            return None
    
    def _get_content_type(self, file_name: str) -> str:
        """Get MIME type for audio file"""
        ext = Path(file_name).suffix.lower()
        content_types = {
            '.wav': 'audio/wav',
            '.mp3': 'audio/mpeg',
            '.m4a': 'audio/mp4',
            '.flac': 'audio/flac',
            '.ogg': 'audio/ogg'
        }
        return content_types.get(ext, 'audio/mpeg')
    
    def _get_public_url(self, file_name: str) -> str:
        """Get public URL for uploaded file"""
        try:
            # Get public URL
            result = self.supabase.storage.from_(self.bucket_name).get_public_url(file_name)
            if isinstance(result, str):
                return result
            elif hasattr(result, 'url'):
                return result.url
            elif hasattr(result, 'public_url'):
                return result.public_url
            else:
                # Fallback: construct URL manually
                return f"{self.supabase_url}/storage/v1/object/public/{self.bucket_name}/{file_name}"
        except Exception as e:
            logger.warning(f"⚠️ Could not get public URL for {file_name}: {e}")
            # Return fallback URL
            return f"{self.supabase_url}/storage/v1/object/public/{self.bucket_name}/{file_name}"


def upload_audio_to_supabase(file_path: str, file_name: str) -> str:
    """
    Main function to upload audio file to Supabase Storage
    
    Args:
        file_path: Path to audio file
        file_name: Name for the file in storage
        
    Returns:
        Public URL of uploaded file
        
    Raises:
        Exception: If upload fails after all retry attempts
    """
    # Get Supabase credentials from environment
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_ANON_KEY')
    
    if not supabase_url or not supabase_key:
        raise Exception("❌ Supabase credentials not found. Set SUPABASE_URL and SUPABASE_ANON_KEY environment variables")
    
    # Create uploader instance
    uploader = SupabaseUploader(supabase_url, supabase_key)
    
    # Test connection first
    if not uploader.test_connection():
        raise Exception("❌ Cannot connect to Supabase")
    
    # Upload file
    public_url = uploader.upload_audio_to_supabase(file_path, file_name)
    
    if not public_url:
        raise Exception(f"❌ Không thể upload file audio lên Supabase: {file_name}")
    
    logger.info(f"✅ File uploaded successfully: {public_url}")
    return public_url


if __name__ == "__main__":
    # Example usage and testing
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python audio_pipeline.py <file_path> <file_name>")
        print("Example: python audio_pipeline.py /path/to/audio.wav audio_file.wav")
        sys.exit(1)
    
    file_path = sys.argv[1]
    file_name = sys.argv[2]
    
    try:
        public_url = upload_audio_to_supabase(file_path, file_name)
        print(f"🎉 Upload thành công! URL: {public_url}")
    except Exception as e:
        print(f"❌ Upload thất bại: {e}")
        sys.exit(1)