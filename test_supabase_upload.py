#!/usr/bin/env python3
"""
Test script for Supabase upload functionality
Tests the fix for 'UploadResponse' object has no attribute 'status_code' error
"""

import os
import sys
import tempfile
import wave
import struct
from pathlib import Path

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from audio_pipeline import upload_audio_to_supabase, SupabaseUploader

def create_test_audio_file(file_path: str, duration: float = 1.0, frequency: int = 440) -> None:
    """Create a test WAV file for testing"""
    sample_rate = 16000
    frames = int(duration * sample_rate)
    
    with wave.open(file_path, 'wb') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        
        # Generate sine wave
        for i in range(frames):
            value = int(32767 * 0.3 * (i % (sample_rate // frequency)) / (sample_rate // frequency))
            wav_file.writeframes(struct.pack('<h', value))

def test_supabase_connection():
    """Test basic Supabase connection"""
    print("🧪 Testing Supabase connection...")
    
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_ANON_KEY')
    
    if not supabase_url or not supabase_key:
        print("❌ Supabase credentials not found. Set SUPABASE_URL and SUPABASE_ANON_KEY")
        return False
    
    try:
        uploader = SupabaseUploader(supabase_url, supabase_key)
        return uploader.test_connection()
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False

def test_upload_wav_file():
    """Test uploading a WAV file"""
    print("🧪 Testing WAV file upload...")
    
    # Create temporary test file
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
        temp_path = temp_file.name
    
    try:
        # Create test audio
        create_test_audio_file(temp_path, duration=2.0)
        
        # Test upload
        file_name = f"test_audio_{os.path.basename(temp_path)}"
        public_url = upload_audio_to_supabase(temp_path, file_name)
        
        print(f"✅ WAV upload successful: {public_url}")
        return True
        
    except Exception as e:
        print(f"❌ WAV upload failed: {e}")
        return False
    finally:
        # Clean up
        if os.path.exists(temp_path):
            os.unlink(temp_path)

def test_upload_with_special_characters():
    """Test uploading file with special characters in name"""
    print("🧪 Testing upload with special characters...")
    
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
        temp_path = temp_file.name
    
    try:
        create_test_audio_file(temp_path, duration=1.0)
        
        # Test with Vietnamese and special characters
        file_name = "A1-4.1 Talk about time and routines - Easy Vietnamese #test (1)_20250813_202306.wav"
        public_url = upload_audio_to_supabase(temp_path, file_name)
        
        print(f"✅ Special characters upload successful: {public_url}")
        return True
        
    except Exception as e:
        print(f"❌ Special characters upload failed: {e}")
        return False
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)

def test_upload_existing_file():
    """Test upload behavior when file already exists (test upsert functionality)"""
    print("🧪 Testing upload of existing file (upsert)...")
    
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
        temp_path = temp_file.name
    
    try:
        create_test_audio_file(temp_path, duration=0.5)
        
        file_name = "test_duplicate_upload.wav"
        
        # Upload first time
        public_url1 = upload_audio_to_supabase(temp_path, file_name)
        print(f"✅ First upload: {public_url1}")
        
        # Upload second time (should trigger upsert)
        public_url2 = upload_audio_to_supabase(temp_path, file_name)
        print(f"✅ Second upload (upsert): {public_url2}")
        
        return True
        
    except Exception as e:
        print(f"❌ Duplicate upload test failed: {e}")
        return False
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)

def main():
    """Run all tests"""
    print("🚀 Starting Supabase upload tests...")
    print("=" * 50)
    
    # Track test results
    tests = []
    
    # Test 1: Connection
    tests.append(("Connection Test", test_supabase_connection()))
    
    # Test 2: WAV file upload
    tests.append(("WAV Upload", test_upload_wav_file()))
    
    # Test 3: Special characters
    tests.append(("Special Characters", test_upload_with_special_characters()))
    
    # Test 4: Duplicate file (upsert)
    tests.append(("Upsert Test", test_upload_existing_file()))
    
    # Results summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    
    passed = 0
    for test_name, result in tests:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nTests passed: {passed}/{len(tests)}")
    
    if passed == len(tests):
        print("🎉 All tests passed! Supabase upload is working correctly.")
        return 0
    else:
        print("❌ Some tests failed. Check the logs above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())