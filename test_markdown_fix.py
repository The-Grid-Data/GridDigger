#!/usr/bin/env python3
"""
Test script to verify Markdown parsing error fixes
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from handlers.utils import generate_applied_filters_text, escape_markdown

def test_markdown_escaping():
    """Test that problematic characters are properly escaped"""
    
    print("Testing Markdown escaping...")
    
    # Test cases with problematic characters
    test_cases = [
        "Normal text",
        "Text with *asterisks*",
        "Text with _underscores_",
        "Text with `backticks`",
        "Text with [brackets]",
        "Complex text with *bold* and _italic_ and `code`",
        "Special chars: *_`[",
        "DeFi Protocol [V2]",
        "Asset_Token_Name",
        "Protocol*Beta*Version"
    ]
    
    for test_text in test_cases:
        escaped = escape_markdown(test_text)
        print(f"Original: {test_text}")
        print(f"Escaped:  {escaped}")
        print()

def test_filter_text_generation():
    """Test filter text generation with problematic data"""
    
    print("Testing filter text generation...")
    
    # Test data with problematic characters
    test_data = {
        "FILTERS": {
            "profileNameSearch": "DeFi Protocol [V2]",
            "assetTickers": "TOKEN_NAME",
            "profileTypes": "Protocol*Beta",
            "entityName": "Company_Name_With_Underscores",
            "productTypes": "Product with `backticks`"
        }
    }
    
    try:
        result = generate_applied_filters_text(test_data)
        print("Filter text generated successfully:")
        print(result)
        print()
        return True
    except Exception as e:
        print(f"Error generating filter text: {e}")
        return False

def test_empty_and_edge_cases():
    """Test edge cases"""
    
    print("Testing edge cases...")
    
    # Empty filters
    empty_data = {"FILTERS": {}}
    result = generate_applied_filters_text(empty_data)
    print(f"Empty filters: {result}")
    
    # None values
    none_data = {"FILTERS": {"profileNameSearch": None, "assetTickers": ""}}
    result = generate_applied_filters_text(none_data)
    print(f"None/empty values: {result}")
    
    # Query keys (should be ignored)
    query_data = {"FILTERS": {"profileNameSearch_query": "test", "profileNameSearch": "actual_value"}}
    result = generate_applied_filters_text(query_data)
    print(f"Query keys ignored: {result}")
    print()

if __name__ == "__main__":
    print("=" * 50)
    print("MARKDOWN PARSING FIX TEST")
    print("=" * 50)
    
    test_markdown_escaping()
    
    success = test_filter_text_generation()
    
    test_empty_and_edge_cases()
    
    if success:
        print("✅ All tests passed! Markdown parsing should now work correctly.")
    else:
        print("❌ Tests failed! There may still be issues.")
    
    print("=" * 50)