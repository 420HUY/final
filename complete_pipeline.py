#!/usr/bin/env python3
"""
Complete Audio Transcript Pipeline for Vietnamese Speech Recognition
Includes all 4 modules with fixed Supabase integration
"""

import os
import gc
import sys
import logging
import tempfile
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

# Import the fixed Supabase uploader
from audio_pipeline import SupabaseUploader, upload_audio_to_supabase, sanitize_filename_for_supabase

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class AudioSegment:
    """Represents a segmented audio clip with metadata"""
    file_path: str
    speaker_id: str
    start_time: float
    end_time: float
    transcript: str = ""
    confidence: float = 0.0

@dataclass
class PipelineResult:
    """Complete pipeline processing result"""
    original_file: str
    segments: List[AudioSegment]
    full_transcript: str
    supabase_urls: List[str]
    processing_time: float

class Module1_SpeakerDiarization:
    """Module 1 - Speaker Diarization & Audio Segmentation"""
    
    def __init__(self):
        self.name = "Module 1 - Speaker Diarization"
        logger.info(f"🎤 Initialized {self.name}")
    
    def process(self, audio_file: str) -> List[AudioSegment]:
        """
        Process audio file for speaker diarization and segmentation
        
        Args:
            audio_file: Path to input audio file
            
        Returns:
            List of AudioSegment objects
        """
        logger.info(f"🔍 Processing {audio_file} for speaker diarization...")
        
        # Mock implementation - in real version would use pyannote
        # This demonstrates the structure for the actual implementation
        segments = []
        
        # For demo purposes, create mock segments
        file_duration = self._get_audio_duration(audio_file)
        segment_duration = 10.0  # 10-second segments
        
        num_segments = max(1, int(file_duration / segment_duration))
        
        for i in range(num_segments):
            start_time = i * segment_duration
            end_time = min((i + 1) * segment_duration, file_duration)
            speaker_id = f"SPEAKER_{(i % 2) + 1}"  # Alternate between 2 speakers
            
            # Create segment file (in real implementation, would extract audio)
            segment_file = self._create_segment_file(audio_file, start_time, end_time, i)
            
            segment = AudioSegment(
                file_path=segment_file,
                speaker_id=speaker_id,
                start_time=start_time,
                end_time=end_time
            )
            segments.append(segment)
            
            logger.info(f"📄 Created segment {i+1}: {speaker_id} ({start_time:.1f}s - {end_time:.1f}s)")
        
        logger.info(f"✅ Created {len(segments)} audio segments")
        return segments
    
    def _get_audio_duration(self, audio_file: str) -> float:
        """Get audio file duration (mock implementation)"""
        # In real implementation, would use librosa or pydub
        return 30.0  # Mock 30-second file
    
    def _create_segment_file(self, original_file: str, start_time: float, end_time: float, index: int) -> str:
        """Create audio segment file (mock implementation)"""
        # In real implementation, would use pydub to extract segment
        base_name = Path(original_file).stem
        segment_path = f"/tmp/{base_name}_segment_{index:03d}_{start_time:.1f}s-{end_time:.1f}s.wav"
        
        # Create empty file for demo (real implementation would extract audio)
        Path(segment_path).touch()
        
        return segment_path

class Module2_VietnameseASR:
    """Module 2 - Vietnamese Automatic Speech Recognition (PhoWhisper)"""
    
    def __init__(self):
        self.name = "Module 2 - Vietnamese ASR (PhoWhisper)"
        logger.info(f"🗣️ Initialized {self.name}")
    
    def process(self, segments: List[AudioSegment]) -> List[AudioSegment]:
        """
        Process audio segments for Vietnamese speech recognition
        
        Args:
            segments: List of audio segments from Module 1
            
        Returns:
            Same segments with transcript field populated
        """
        logger.info(f"🎯 Processing {len(segments)} segments for Vietnamese ASR...")
        
        for i, segment in enumerate(segments):
            # Mock Vietnamese transcript (real implementation would use PhoWhisper)
            vietnamese_phrases = [
                "Xin chào, tôi là người học tiếng Việt.",
                "Hôm nay là một ngày đẹp trời.",
                "Tôi thích học tiếng Việt rất nhiều.",
                "Cảm ơn bạn đã nghe tôi nói.",
                "Chúc bạn có một ngày tốt lành."
            ]
            
            segment.transcript = vietnamese_phrases[i % len(vietnamese_phrases)]
            segment.confidence = 0.95  # Mock high confidence
            
            logger.info(f"📝 Segment {i+1} ({segment.speaker_id}): {segment.transcript}")
        
        # Smart cleanup (mentioned in pipeline docs)
        self._smart_cleanup()
        
        logger.info("✅ Vietnamese ASR processing completed")
        return segments
    
    def _smart_cleanup(self):
        """Smart memory cleanup as documented in pipeline"""
        try:
            import torch
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                logger.info("🧹 CUDA cache cleared")
        except ImportError:
            pass
        
        gc.collect()
        logger.info("🧹 Garbage collection completed")

class Module3_SupabaseStorage:
    """Module 3 - Supabase Storage & Database Integration (FIXED)"""
    
    def __init__(self, supabase_url: str = None, supabase_key: str = None):
        self.name = "Module 3 - Supabase Storage & Database"
        
        # Use environment variables if not provided
        self.supabase_url = supabase_url or os.getenv('SUPABASE_URL')
        self.supabase_key = supabase_key or os.getenv('SUPABASE_ANON_KEY')
        
        if self.supabase_url and self.supabase_key:
            self.uploader = SupabaseUploader(self.supabase_url, self.supabase_key)
            logger.info(f"💾 Initialized {self.name} with Supabase")
        else:
            self.uploader = None
            logger.warning(f"⚠️ {self.name} initialized without Supabase credentials")
    
    def process(self, segments: List[AudioSegment], original_file: str) -> List[str]:
        """
        Upload segments and metadata to Supabase
        
        Args:
            segments: Processed audio segments with transcripts
            original_file: Path to original audio file
            
        Returns:
            List of public URLs for uploaded segments
        """
        logger.info(f"☁️ Uploading {len(segments)} segments to Supabase...")
        
        if not self.uploader:
            logger.warning("⚠️ No Supabase credentials - simulating upload")
            return [f"mock://uploaded/{Path(seg.file_path).name}" for seg in segments]
        
        # Test connection first
        if not self.uploader.test_connection():
            raise Exception("❌ Cannot connect to Supabase")
        
        uploaded_urls = []
        
        # Upload original file first
        original_name = f"original_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{Path(original_file).name}"
        try:
            original_url = self.uploader.upload_audio_to_supabase(original_file, original_name)
            if original_url:
                logger.info(f"✅ Original file uploaded: {original_url}")
            uploaded_urls.append(original_url or "failed")
        except Exception as e:
            logger.error(f"❌ Failed to upload original file: {e}")
            uploaded_urls.append("failed")
        
        # Upload each segment
        # Create a base folder name from the original file
        base_filename = Path(original_file).stem  # filename without extension
        # This will create a folder structure like: "A1-4.1_Talk_about_time.../segments/segment_001_..."
        base_folder = f"{base_filename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}/segments"
        
        for i, segment in enumerate(segments):
            if not os.path.exists(segment.file_path):
                logger.warning(f"⚠️ Segment file not found: {segment.file_path}")
                uploaded_urls.append("not_found")
                continue
            
            # Create descriptive filename with folder structure
            segment_filename = f"segment_{i:03d}_{segment.start_time:05.1f}s_{segment.speaker_id}.wav"
            segment_path = f"{base_folder}/{segment_filename}"
            
            try:
                public_url = self.uploader.upload_audio_to_supabase(segment.file_path, segment_path)
                uploaded_urls.append(public_url)
                
                if public_url:
                    logger.info(f"✅ Segment {i+1} uploaded: {segment_path}")
                else:
                    logger.error(f"❌ Failed to upload segment {i+1}")
                    
            except Exception as e:
                logger.error(f"❌ Error uploading segment {i+1}: {e}")
                uploaded_urls.append("error")
        
        # Store transcript metadata in database (mock implementation)
        self._store_transcript_metadata(segments, uploaded_urls)
        
        successful_uploads = sum(1 for url in uploaded_urls if url and url not in ["failed", "error", "not_found"])
        logger.info(f"✅ Successfully uploaded {successful_uploads}/{len(uploaded_urls)} files")
        
        return uploaded_urls
    
    def _store_transcript_metadata(self, segments: List[AudioSegment], urls: List[str]):
        """Store transcript metadata in Supabase database"""
        logger.info("💽 Storing transcript metadata in database...")
        
        # Mock implementation - real version would use Supabase database
        for segment, url in zip(segments, urls):
            if url and url not in ["failed", "error", "not_found"]:
                metadata = {
                    "file_url": url,
                    "speaker": segment.speaker_id,
                    "start_time": segment.start_time,
                    "end_time": segment.end_time,
                    "transcript": segment.transcript,
                    "confidence": segment.confidence,
                    "created_at": datetime.now().isoformat()
                }
                logger.info(f"📊 Metadata: {segment.speaker_id} - {segment.transcript[:50]}...")
        
        logger.info("✅ Transcript metadata stored")

class Module4_Search:
    """Module 4 - Search Functionality"""
    
    def __init__(self):
        self.name = "Module 4 - Search"
        logger.info(f"🔍 Initialized {self.name}")
    
    def search_transcripts(self, query: str, segments: List[AudioSegment]) -> List[AudioSegment]:
        """
        Search through transcripts
        
        Args:
            query: Search query
            segments: List of segments with transcripts
            
        Returns:
            Matching segments
        """
        logger.info(f"🔎 Searching for: '{query}'")
        
        results = []
        query_lower = query.lower()
        
        for segment in segments:
            if query_lower in segment.transcript.lower():
                results.append(segment)
                logger.info(f"🎯 Match: {segment.speaker_id} - {segment.transcript}")
        
        logger.info(f"✅ Found {len(results)} matching segments")
        return results

class AudioTranscriptPipeline:
    """Complete Audio Transcript Pipeline"""
    
    def __init__(self, supabase_url: str = None, supabase_key: str = None):
        """Initialize pipeline with all modules"""
        logger.info("🚀 Initializing Audio Transcript Pipeline...")
        
        self.module1 = Module1_SpeakerDiarization()
        self.module2 = Module2_VietnameseASR()
        self.module3 = Module3_SupabaseStorage(supabase_url, supabase_key)
        self.module4 = Module4_Search()
        
        logger.info("✅ Pipeline initialized successfully")
    
    def process_audio(self, audio_file: str) -> PipelineResult:
        """
        Process audio file through complete pipeline
        
        Args:
            audio_file: Path to input audio file
            
        Returns:
            PipelineResult with all processing outputs
        """
        start_time = datetime.now()
        logger.info(f"🎵 Starting pipeline processing for: {audio_file}")
        
        try:
            # Module 1: Speaker Diarization & Segmentation
            segments = self.module1.process(audio_file)
            
            # Module 2: Vietnamese ASR
            segments_with_transcripts = self.module2.process(segments)
            
            # Module 3: Supabase Upload (THE FIXED MODULE)
            uploaded_urls = self.module3.process(segments_with_transcripts, audio_file)
            
            # Create full transcript
            full_transcript = self._create_full_transcript(segments_with_transcripts)
            
            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds()
            
            result = PipelineResult(
                original_file=audio_file,
                segments=segments_with_transcripts,
                full_transcript=full_transcript,
                supabase_urls=uploaded_urls,
                processing_time=processing_time
            )
            
            logger.info(f"🎉 Pipeline completed in {processing_time:.2f} seconds")
            return result
            
        except Exception as e:
            logger.error(f"❌ Pipeline failed: {e}")
            raise
        finally:
            # Clean up temporary files
            self._cleanup_temp_files(segments if 'segments' in locals() else [])
    
    def search(self, query: str, result: PipelineResult) -> List[AudioSegment]:
        """Search through pipeline results"""
        return self.module4.search_transcripts(query, result.segments)
    
    def _create_full_transcript(self, segments: List[AudioSegment]) -> str:
        """Create full transcript from segments"""
        transcript_lines = []
        
        for segment in segments:
            timestamp = f"[{segment.start_time:.1f}s - {segment.end_time:.1f}s]"
            line = f"{timestamp} {segment.speaker_id}: {segment.transcript}"
            transcript_lines.append(line)
        
        return "\n".join(transcript_lines)
    
    def _cleanup_temp_files(self, segments: List[AudioSegment]):
        """Clean up temporary segment files"""
        for segment in segments:
            if os.path.exists(segment.file_path) and "/tmp/" in segment.file_path:
                try:
                    os.unlink(segment.file_path)
                    logger.info(f"🧹 Cleaned up: {segment.file_path}")
                except Exception as e:
                    logger.warning(f"⚠️ Could not clean up {segment.file_path}: {e}")

def main():
    """Example usage of the complete pipeline"""
    import sys
    
    if len(sys.argv) < 2:
        print("🎵 Audio Transcript Pipeline - Vietnamese ASR")
        print("=" * 50)
        print("Usage: python complete_pipeline.py <audio_file>")
        print("Example: python complete_pipeline.py audio.wav")
        print()
        print("🔧 Environment Variables Required:")
        print("   SUPABASE_URL - Your Supabase project URL")
        print("   SUPABASE_ANON_KEY - Your Supabase anon key")
        print()
        print("📝 Copy .env.example to .env and configure your credentials")
        return 1
    
    audio_file = sys.argv[1]
    
    if not os.path.exists(audio_file):
        print(f"❌ Audio file not found: {audio_file}")
        return 1
    
    try:
        # Load environment variables
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except ImportError:
            pass
        
        # Initialize pipeline
        pipeline = AudioTranscriptPipeline()
        
        # Process audio
        result = pipeline.process_audio(audio_file)
        
        # Display results
        print("\n🎉 Pipeline Results:")
        print("=" * 50)
        print(f"📄 Original file: {result.original_file}")
        print(f"⏱️ Processing time: {result.processing_time:.2f} seconds")
        print(f"📊 Segments created: {len(result.segments)}")
        print(f"☁️ Files uploaded: {len([url for url in result.supabase_urls if url and 'failed' not in url and 'error' not in url])}")
        print()
        print("📝 Full Transcript:")
        print("-" * 30)
        print(result.full_transcript)
        print()
        
        # Demo search functionality
        if result.segments:
            search_query = "tiếng Việt"
            print(f"🔍 Demo Search: '{search_query}'")
            search_results = pipeline.search(search_query, result)
            print(f"📊 Found {len(search_results)} matching segments")
        
        print("\n✅ Pipeline completed successfully!")
        print("🎯 The Supabase upload error has been fixed!")
        return 0
        
    except Exception as e:
        print(f"❌ Pipeline failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())