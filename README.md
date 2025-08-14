# Audio Processing Pipeline - Vietnamese ASR with Supabase Integration

## Overview

This repository contains a complete audio processing pipeline for Vietnamese speech recognition with Supabase Storage integration. The pipeline has been specifically fixed to handle Vietnamese diacritics and special characters in filenames to prevent Supabase `InvalidKey` errors.

## Problem Solved

**Issue**: Audio segment uploads were failing with `InvalidKey` errors when filenames contained Vietnamese diacritics or special characters.

**Example Error**:
```
❌ Lỗi upload A1-4.1 Talk about time and routines - Easy Vietnamese Conversation for Beginners #hoctiengviet (1)_20250814_053436/segments/segment_001_01_Giám Đốc Đức (1).wav: {'statusCode': 400, 'error': InvalidKey, 'message': Invalid key: A1-4.1_Talk_about_time_and_routines_-_Easy_Vietnamese_Conversation_for_Beginners_hoctiengviet__1__20250814_053436/segments/segment_001_01_Giám_Đốc_Đức__1_.wav}
```

**Solution**: Implemented robust filename sanitization that converts Vietnamese diacritics and special characters to Supabase-safe equivalents while maintaining meaningful filenames.

## Key Features

### 1. Vietnamese Diacritics Support
- ✅ Converts `Giám Đốc Đức` → `Giam_Doc_Duc`
- ✅ Handles all Vietnamese characters: `áàảãạêềểễệ...` → `aaeee...`
- ✅ Special handling for `Đ/đ` → `D/d`

### 2. Special Character Sanitization
- ✅ Spaces → underscores
- ✅ `#()[]{}@!` → `_`
- ✅ Preserves safe characters: `a-z`, `A-Z`, `0-9`, `.`, `_`, `-`, `/`

### 3. Folder Structure Management
- ✅ Maintains nested folder paths
- ✅ Creates organized structure: `audio_name_timestamp/segments/segment_001_...`
- ✅ Sanitizes both folder names and filenames

### 4. File Extension Preservation
- ✅ Keeps `.wav`, `.mp3`, `.m4a` extensions
- ✅ Handles filenames with multiple dots correctly

## Installation

1. Install dependencies:
```bash
pip install supabase
```

2. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your Supabase credentials
```

## Usage

### Basic Upload
```python
from audio_pipeline import upload_audio_to_supabase

# Upload with automatic filename sanitization
url = upload_audio_to_supabase(
    "path/to/audio.wav", 
    "segment_001_Giám Đốc Đức (1).wav"  # Will be sanitized automatically
)
```

### Complete Pipeline
```python
from complete_pipeline import AudioTranscriptPipeline

pipeline = AudioTranscriptPipeline()
result = pipeline.process_audio("vietnamese_audio.wav")

# All segments uploaded with sanitized names
print(f"Uploaded {len(result.supabase_urls)} files successfully")
```

### Manual Sanitization
```python
from audio_pipeline import sanitize_filename_for_supabase

# Test with problematic filename
original = "A1-4.1 Talk #test/segments/Giám Đốc Đức (1).wav"
sanitized = sanitize_filename_for_supabase(original)
print(f"Safe filename: {sanitized}")
# Output: A1-4.1_Talk_test/segments/Giam_Doc_Duc_1.wav
```

## Testing

### Run All Tests
```bash
# Test filename sanitization
python test_filename_sanitization.py

# Test integration
python test_integration.py
```

### Test Results
All test categories pass:
- ✅ Vietnamese Diacritics (10/10 tests)
- ✅ Special Characters (7/7 tests) 
- ✅ Folder Paths (5/5 tests)
- ✅ Real-World Examples (4/4 tests)
- ✅ Edge Cases (12/12 tests)

## Files

- **`audio_pipeline.py`** - Core Supabase upload functionality with sanitization
- **`complete_pipeline.py`** - Full 4-module audio processing pipeline
- **`test_filename_sanitization.py`** - Comprehensive sanitization tests
- **`test_integration.py`** - End-to-end integration tests
- **`.env.example`** - Environment variables template
- **`requirements.txt`** - Python dependencies

## Example Transformations

| Original | Sanitized | Status |
|----------|-----------|---------|
| `Giám Đốc Đức.wav` | `Giam_Doc_Duc.wav` | ✅ Safe |
| `Lesson #1 (intro).wav` | `Lesson_1_intro.wav` | ✅ Safe |
| `Speaker: Nguyễn Thị Hoa` | `Speaker_Nguyen_Thi_Hoa` | ✅ Safe |
| `folder/sub folder/file.wav` | `folder/sub_folder/file.wav` | ✅ Safe |

## Architecture

The pipeline consists of 4 modules:

1. **Module 1** - Speaker Diarization & Segmentation
2. **Module 2** - ASR (PhoWhisper) Vietnamese Speech Recognition  
3. **Module 3** - Storage/Data Processing (Supabase)
4. **Module 4** - Search Engine

## Environment Variables

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key-here
```

## Error Handling

The pipeline includes robust error handling for:
- ✅ Invalid file paths
- ✅ Network connectivity issues
- ✅ Malformed filenames
- ✅ File already exists (automatic upsert)
- ✅ Empty or invalid sanitization results

## Contributing

When adding new functionality:
1. Test with Vietnamese characters
2. Verify Supabase compatibility
3. Run all test suites
4. Document any breaking changes

## License

This project is part of the Vietnamese speech recognition pipeline development.