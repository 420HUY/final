# Documentation

This directory contains documentation for the audio processing pipeline.

## Files

- `pipeline.md` - Complete documentation of the 4-module audio processing pipeline
- `mermaid-test.md` - Test file to verify Mermaid diagram compatibility with GitHub

## Pipeline Overview

The audio processing pipeline consists of 4 modules:

1. **Speaker Diarization & Segmentation** - Identifies speakers and segments audio
2. **ASR (PhoWhisper)** - Transcribes speech to text using Vietnamese-optimized model
3. **Storage/Data Processing** - Stores transcripts in database
4. **Search** - Enables searching through stored transcripts

## GitHub Compatibility Notes

All Mermaid diagrams in this documentation are designed to be compatible with GitHub's renderer:
- No `direction TB` used in subgraphs (causes parse errors)
- Uses `<br/>` instead of `\n` for line breaks in node labels
- ASCII and GitHub-compatible characters only
- Includes both simple and colored diagram versions

## Technical Features

- Smart memory management with `torch.cuda.empty_cache()` and `gc.collect()`
- Batch processing for efficiency
- FP16 precision for memory optimization
- Robust error handling
- Vietnamese speech recognition optimization