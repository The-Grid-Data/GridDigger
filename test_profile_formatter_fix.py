#!/usr/bin/env python3
"""
Test script to verify profile formatter Markdown parsing error fixes
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.profile_formatter import CardFormatter, ExpandedFormatter, CompactFormatter
from models.profile_data import ProfileData, ProfileSector, ProfileType, ProfileStatus

def create_test_profile_with_problematic_data():
    """Create a test profile with problematic Markdown characters"""
    
    # Create test objects with problematic characters
    sector = ProfileSector(id="1", name="Data & Analytics [Beta]")
    profile_type = ProfileType(id="1", name="Company*Protocol")
    status = ProfileStatus(id="1", name="Active_Status")
    
    # Create profile with problematic characters in various fields
    profile = ProfileData(
        id=254,
        name="The Grid_Data*Company",
        slug="the_grid_data",
        sector=sector,
        profile_type=profile_type,
        status=status,
        description_short="A data company that provides *structured* information about Web3 projects.",
        description_long="The Grid is a comprehensive data platform that aggregates and structures information about Web3 projects, protocols, and assets. It provides APIs and tools for developers to access this data.",
        tag_line="Structured Web3 Data [API]",
        founding_date="2023-01-01",
        logo="https://example.com/logo.png",
        products=[],
        assets=[],
        urls=[]
    )
    
    return profile

def test_card_formatter():
    """Test CardFormatter with problematic data"""
    print("Testing CardFormatter...")
    
    formatter = CardFormatter()
    profile = create_test_profile_with_problematic_data()
    
    try:
        formatted = formatter.format(profile)
        print("✅ CardFormatter succeeded")
        print("Message text:")
        print(formatted.message_text)
        print()
        return True
    except Exception as e:
        print(f"❌ CardFormatter failed: {e}")
        return False

def test_expanded_formatter():
    """Test ExpandedFormatter with problematic data"""
    print("Testing ExpandedFormatter...")
    
    formatter = ExpandedFormatter()
    profile = create_test_profile_with_problematic_data()
    
    try:
        formatted = formatter.format(profile)
        print("✅ ExpandedFormatter succeeded")
        print("Message text:")
        print(formatted.message_text)
        print()
        return True
    except Exception as e:
        print(f"❌ ExpandedFormatter failed: {e}")
        return False

def test_compact_formatter():
    """Test CompactFormatter with problematic data"""
    print("Testing CompactFormatter...")
    
    formatter = CompactFormatter()
    profile = create_test_profile_with_problematic_data()
    
    try:
        formatted = formatter.format(profile)
        print("✅ CompactFormatter succeeded")
        print("Message text:")
        print(formatted.message_text)
        print()
        return True
    except Exception as e:
        print(f"❌ CompactFormatter failed: {e}")
        return False

def test_escape_markdown_methods():
    """Test the _escape_markdown_text methods directly"""
    print("Testing _escape_markdown_text methods...")
    
    test_strings = [
        "Normal text",
        "Text with *asterisks*",
        "Text with _underscores_",
        "Text with `backticks`",
        "Text with [brackets]",
        "Text with (parentheses)",
        "Complex: *bold* _italic_ `code` [link] (note)",
        "The Grid_Data*Company",
        "Data & Analytics [Beta]",
        "Company*Protocol",
        "Active_Status"
    ]
    
    formatters = [CardFormatter(), ExpandedFormatter(), CompactFormatter()]
    
    for i, formatter in enumerate(formatters):
        formatter_name = ["CardFormatter", "ExpandedFormatter", "CompactFormatter"][i]
        print(f"\n{formatter_name}:")
        
        for test_string in test_strings:
            try:
                escaped = formatter._escape_markdown_text(test_string)
                print(f"  '{test_string}' → '{escaped}'")
            except Exception as e:
                print(f"  ❌ Error escaping '{test_string}': {e}")
                return False
    
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("PROFILE FORMATTER MARKDOWN PARSING FIX TEST")
    print("=" * 60)
    
    success_count = 0
    total_tests = 4
    
    # Test individual formatters
    if test_card_formatter():
        success_count += 1
    
    if test_expanded_formatter():
        success_count += 1
    
    if test_compact_formatter():
        success_count += 1
    
    if test_escape_markdown_methods():
        success_count += 1
    
    print("=" * 60)
    print(f"RESULTS: {success_count}/{total_tests} tests passed")
    
    if success_count == total_tests:
        print("✅ All profile formatter tests passed! Markdown parsing should now work correctly.")
    else:
        print("❌ Some tests failed! There may still be issues with profile formatting.")
    
    print("=" * 60)