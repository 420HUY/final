#!/usr/bin/env python3
"""
Test script for filename sanitization function.
Tests the fix for Supabase InvalidKey errors with Vietnamese diacritics.
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from audio_pipeline import sanitize_filename_for_supabase

def test_vietnamese_diacritics():
    """Test Vietnamese diacritic removal"""
    test_cases = [
        ("Giám Đốc Đức", "Giam_Doc_Duc"),
        ("Nguyễn Văn An", "Nguyen_Van_An"),
        ("Trần Thị Hương", "Tran_Thi_Huong"),
        ("âêîôû", "aeiou"),
        ("áàảãạ", "aaaaa"),
        ("éèẻẽẹ", "eeeee"),
        ("íìỉĩị", "iiiii"),
        ("óòỏõọ", "ooooo"),
        ("úùủũụ", "uuuuu"),
        ("ýỳỷỹỵ", "yyyyy"),
    ]
    
    print("🧪 Testing Vietnamese Diacritics Removal:")
    print("=" * 50)
    all_passed = True
    
    for original, expected in test_cases:
        result = sanitize_filename_for_supabase(original)
        status = "✅" if result == expected else "❌"
        print(f"{status} '{original}' → '{result}' (expected: '{expected}')")
        if result != expected:
            all_passed = False
    
    return all_passed

def test_special_characters():
    """Test special character handling"""
    test_cases = [
        ("file name.wav", "file_name.wav"),
        ("file#name@test!.wav", "file_name_test.wav"),
        ("file (1).wav", "file_1.wav"),
        ("file-name_test.wav", "file-name_test.wav"),
        ("file___multiple___underscores.wav", "file_multiple_underscores.wav"),
        ("___leading_trailing___", "leading_trailing"),
        ("A1-4.1 Talk about time and routines #test (1).wav", "A1-4.1_Talk_about_time_and_routines_test_1.wav"),
    ]
    
    print("\n🧪 Testing Special Characters:")
    print("=" * 50)
    all_passed = True
    
    for original, expected in test_cases:
        result = sanitize_filename_for_supabase(original)
        status = "✅" if result == expected else "❌"
        print(f"{status} '{original}' → '{result}' (expected: '{expected}')")
        if result != expected:
            all_passed = False
    
    return all_passed

def test_folder_paths():
    """Test folder path handling"""
    test_cases = [
        ("folder/file.wav", "folder/file.wav"),
        ("Giám Đốc/segments/file.wav", "Giam_Doc/segments/file.wav"),
        ("A1-4.1 Talk #test/segments/Giám Đốc (1).wav", "A1-4.1_Talk_test/segments/Giam_Doc_1.wav"),
        ("multiple/nested/folder/with spaces/file.wav", "multiple/nested/folder/with_spaces/file.wav"),
        ("//double//slashes//", "double/slashes"),
    ]
    
    print("\n🧪 Testing Folder Paths:")
    print("=" * 50)
    all_passed = True
    
    for original, expected in test_cases:
        result = sanitize_filename_for_supabase(original)
        status = "✅" if result == expected else "❌"
        print(f"{status} '{original}' → '{result}' (expected: '{expected}')")
        if result != expected:
            all_passed = False
    
    return all_passed

def test_real_world_examples():
    """Test with real examples from the error message"""
    test_cases = [
        # From the actual error message
        ("A1-4.1 Talk about time and routines - Easy Vietnamese Conversation for Beginners #hoctiengviet (1)_20250814_053436/segments/segment_001_01_Giám Đốc Đức (1).wav",
         "A1-4.1_Talk_about_time_and_routines_-_Easy_Vietnamese_Conversation_for_Beginners_hoctiengviet_1_20250814_053436/segments/segment_001_01_Giam_Doc_Duc_1.wav"),
        
        # Speaker names with Vietnamese characters
        ("segment_001_01_Giám Đốc Đức (1).wav", "segment_001_01_Giam_Doc_Duc_1.wav"),
        ("segment_002_02_Bà Nguyễn Thị Hoa.wav", "segment_002_02_Ba_Nguyen_Thi_Hoa.wav"),
        ("segment_003_03_Ông Trần Văn Minh (giám đốc).wav", "segment_003_03_Ong_Tran_Van_Minh_giam_doc.wav"),
    ]
    
    print("\n🧪 Testing Real-World Examples:")
    print("=" * 70)
    all_passed = True
    
    for original, expected in test_cases:
        result = sanitize_filename_for_supabase(original)
        status = "✅" if result == expected else "❌"
        print(f"{status} Original: {original}")
        print(f"   Result:   {result}")
        print(f"   Expected: {expected}")
        print()
        if result != expected:
            all_passed = False
    
    return all_passed

def test_edge_cases():
    """Test edge cases"""
    test_cases = [
        ("", ""),
        ("   ", ""),
        ("...", ""),  # Only dots should be stripped
        ("file.", "file"),  # Trailing dot should be stripped from folder/file without extension
        ("file..", "file"),  # Trailing dots should be stripped from folder/file without extension
        ("_", ""),
        ("___", ""),
        ("a", "a"),
        ("ạ", "a"),
        ("🎵emoji🎵", "emoji"),  # Emojis should be stripped, leaving the text
        ("test.txt", "test.txt"),  # Files with extensions should keep the dot
        ("test..txt", "test.txt"),  # Double dots in filename should be cleaned up
    ]
    
    print("\n🧪 Testing Edge Cases:")
    print("=" * 50)
    all_passed = True
    
    for original, expected in test_cases:
        result = sanitize_filename_for_supabase(original)
        status = "✅" if result == expected else "❌"
        print(f"{status} '{original}' → '{result}' (expected: '{expected}')")
        if result != expected:
            all_passed = False
    
    return all_passed

def main():
    """Run all tests"""
    print("🧪 Filename Sanitization Tests")
    print("=" * 60)
    print("Testing filename sanitization for Supabase Storage compatibility")
    print("This fixes InvalidKey errors with Vietnamese diacritics and special characters\n")
    
    tests = [
        ("Vietnamese Diacritics", test_vietnamese_diacritics),
        ("Special Characters", test_special_characters),
        ("Folder Paths", test_folder_paths),
        ("Real-World Examples", test_real_world_examples),
        ("Edge Cases", test_edge_cases),
    ]
    
    all_tests_passed = True
    results = []
    
    for test_name, test_func in tests:
        try:
            passed = test_func()
            results.append((test_name, passed))
            if not passed:
                all_tests_passed = False
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
            all_tests_passed = False
    
    # Summary
    print("\n" + "=" * 60)
    print("🏁 TEST RESULTS SUMMARY:")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    print("=" * 60)
    if all_tests_passed:
        print("🎉 ALL TESTS PASSED! The filename sanitization is working correctly.")
        print("✅ Supabase InvalidKey errors should now be fixed.")
        return 0
    else:
        print("💥 SOME TESTS FAILED! Please review the implementation.")
        return 1

if __name__ == "__main__":
    sys.exit(main())