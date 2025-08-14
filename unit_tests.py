#!/usr/bin/env python3
"""
Unit tests for the Supabase upload fix
Tests core functionality without requiring actual Supabase credentials
"""

import unittest
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# Import our modules
from audio_pipeline import SupabaseUploader

class TestSupabaseUploadFix(unittest.TestCase):
    """Test the fix for Supabase upload error"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.mock_url = "https://test.supabase.co"
        self.mock_key = "test_key"
        
        # Create temporary test file
        self.temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
        self.temp_file.write(b"mock audio data")
        self.temp_file.close()
        self.test_file_path = self.temp_file.name
    
    def tearDown(self):
        """Clean up test fixtures"""
        if os.path.exists(self.test_file_path):
            os.unlink(self.test_file_path)
    
    @patch('audio_pipeline.create_client')
    def test_uploader_initialization(self, mock_create_client):
        """Test that SupabaseUploader initializes correctly"""
        mock_client = Mock()
        mock_create_client.return_value = mock_client
        
        uploader = SupabaseUploader(self.mock_url, self.mock_key)
        
        self.assertEqual(uploader.supabase_url, self.mock_url)
        self.assertEqual(uploader.supabase_key, self.mock_key)
        self.assertEqual(uploader.bucket_name, "audio_files")
        mock_create_client.assert_called_once()
    
    def test_content_type_detection(self):
        """Test content type detection for different file formats"""
        with patch('audio_pipeline.create_client'):
            uploader = SupabaseUploader(self.mock_url, self.mock_key)
            
            test_cases = [
                ("test.wav", "audio/wav"),
                ("test.mp3", "audio/mpeg"),
                ("test.m4a", "audio/mp4"),
                ("test.flac", "audio/flac"),
                ("test.ogg", "audio/ogg"),
                ("test.unknown", "audio/mpeg"),  # Default fallback
            ]
            
            for filename, expected_type in test_cases:
                with self.subTest(filename=filename):
                    content_type = uploader._get_content_type(filename)
                    self.assertEqual(content_type, expected_type)
    
    def test_public_url_generation(self):
        """Test public URL generation with different response formats"""
        with patch('audio_pipeline.create_client'):
            uploader = SupabaseUploader(self.mock_url, self.mock_key)
            
            # Mock supabase client
            mock_storage = Mock()
            uploader.supabase.storage.from_.return_value = mock_storage
            
            # Test case 1: String response
            mock_storage.get_public_url.return_value = "https://example.com/file.wav"
            url = uploader._get_public_url("test.wav")
            self.assertEqual(url, "https://example.com/file.wav")
            
            # Test case 2: Object with url attribute
            mock_response = Mock()
            mock_response.url = "https://example.com/file2.wav"
            mock_storage.get_public_url.return_value = mock_response
            url = uploader._get_public_url("test2.wav")
            self.assertEqual(url, "https://example.com/file2.wav")
            
            # Test case 3: Object with public_url attribute
            mock_response = Mock()
            mock_response.public_url = "https://example.com/file3.wav"
            del mock_response.url  # Remove url attribute
            mock_storage.get_public_url.return_value = mock_response
            url = uploader._get_public_url("test3.wav")
            self.assertEqual(url, "https://example.com/file3.wav")
    
    @patch('audio_pipeline.create_client')
    def test_upload_success_without_status_code(self, mock_create_client):
        """Test successful upload without relying on status_code"""
        # Setup mocks
        mock_client = Mock()
        mock_storage = Mock()
        mock_bucket = Mock()
        
        mock_create_client.return_value = mock_client
        mock_client.storage.from_.return_value = mock_bucket
        mock_client.storage.list_buckets.return_value = [Mock(name="audio_files")]
        
        # Mock successful upload response (new format without status_code)
        mock_upload_response = Mock()
        mock_upload_response.path = "/audio_files/test.wav"
        mock_bucket.upload.return_value = mock_upload_response
        mock_bucket.get_public_url.return_value = "https://example.com/test.wav"
        
        uploader = SupabaseUploader(self.mock_url, self.mock_key)
        
        # Test upload
        result_url = uploader.upload_audio_to_supabase(self.test_file_path, "test.wav")
        
        # Verify upload was called correctly
        mock_bucket.upload.assert_called_once()
        call_args = mock_bucket.upload.call_args
        self.assertEqual(call_args[1]['path'], "test.wav")
        self.assertIn('content-type', call_args[1]['file_options'])
        
        # Verify URL was returned
        self.assertEqual(result_url, "https://example.com/test.wav")
    
    @patch('audio_pipeline.create_client')
    def test_upload_with_upsert_fallback(self, mock_create_client):
        """Test upsert fallback when file already exists"""
        # Setup mocks
        mock_client = Mock()
        mock_bucket = Mock()
        
        mock_create_client.return_value = mock_client
        mock_client.storage.from_.return_value = mock_bucket
        mock_client.storage.list_buckets.return_value = [Mock(name="audio_files")]
        
        # First upload fails with "already exists"
        mock_bucket.upload.side_effect = [
            Exception("File already exists"),
            Mock(path="/audio_files/test.wav")  # Second call (upsert) succeeds
        ]
        mock_bucket.get_public_url.return_value = "https://example.com/test.wav"
        
        uploader = SupabaseUploader(self.mock_url, self.mock_key)
        result_url = uploader.upload_audio_to_supabase(self.test_file_path, "test.wav")
        
        # Verify upsert was attempted
        self.assertEqual(mock_bucket.upload.call_count, 2)
        
        # Check that second call had upsert=True
        second_call_args = mock_bucket.upload.call_args_list[1]
        self.assertTrue(second_call_args[1]['file_options']['upsert'])
        
        # Verify URL was returned
        self.assertEqual(result_url, "https://example.com/test.wav")
    
    @patch('audio_pipeline.create_client')
    def test_problematic_filename_handling(self, mock_create_client):
        """Test handling of the exact filename that caused the original error"""
        mock_client = Mock()
        mock_storage = Mock()
        mock_bucket = Mock()
        
        mock_create_client.return_value = mock_client
        mock_client.storage.from_.return_value = mock_bucket
        
        uploader = SupabaseUploader(self.mock_url, self.mock_key)
        
        # The exact filename from the error report
        problematic_filename = "A1-4.1 Talk about time and routines - Easy Vietnamese Conversation for Beginners #hoctiengviet (1)_20250813_202306.wav"
        
        # Should not crash on content type detection
        content_type = uploader._get_content_type(problematic_filename)
        self.assertEqual(content_type, "audio/wav")
        
        # Mock URL response and test fallback URL generation
        mock_bucket.get_public_url.side_effect = Exception("Mock error")
        url = uploader._get_public_url(problematic_filename)
        
        # Should use fallback URL construction
        expected_url = f"{self.mock_url}/storage/v1/object/public/audio_files/{problematic_filename}"
        self.assertEqual(url, expected_url)

class TestPipelineIntegration(unittest.TestCase):
    """Test integration with the complete pipeline"""
    
    def test_upload_function_interface(self):
        """Test the main upload_audio_to_supabase function interface"""
        # Test without environment variables
        with self.assertRaises(Exception) as context:
            from audio_pipeline import upload_audio_to_supabase
            upload_audio_to_supabase("fake_file.wav", "test.wav")
        
        self.assertIn("Supabase credentials not found", str(context.exception))
    
    @patch.dict(os.environ, {'SUPABASE_URL': 'https://test.supabase.co', 'SUPABASE_ANON_KEY': 'test_key'})
    @patch('audio_pipeline.SupabaseUploader')
    def test_upload_function_with_credentials(self, mock_uploader_class):
        """Test upload function with environment credentials"""
        # Setup mock
        mock_uploader = Mock()
        mock_uploader.test_connection.return_value = True
        mock_uploader.upload_audio_to_supabase.return_value = "https://example.com/test.wav"
        mock_uploader_class.return_value = mock_uploader
        
        # Create test file
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
            temp_file.write(b"test audio")
            temp_path = temp_file.name
        
        try:
            from audio_pipeline import upload_audio_to_supabase
            result = upload_audio_to_supabase(temp_path, "test.wav")
            
            # Verify result
            self.assertEqual(result, "https://example.com/test.wav")
            
            # Verify mocks were called correctly
            mock_uploader.test_connection.assert_called_once()
            mock_uploader.upload_audio_to_supabase.assert_called_once_with(temp_path, "test.wav")
            
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

def run_tests():
    """Run all unit tests"""
    print("🧪 RUNNING UNIT TESTS")
    print("=" * 50)
    
    # Discover and run tests
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(__import__(__name__))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 50)
    if result.wasSuccessful():
        print("✅ ALL UNIT TESTS PASSED")
        print("🎯 The Supabase upload fix is working correctly!")
        return True
    else:
        print("❌ SOME UNIT TESTS FAILED")
        print(f"Failures: {len(result.failures)}")
        print(f"Errors: {len(result.errors)}")
        return False

if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)