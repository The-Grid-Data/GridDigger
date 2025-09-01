#!/usr/bin/env python3
"""
Test script to verify the Telegram entity parsing fixes
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.profile_formatter import CardFormatter, ExpandedFormatter, CompactFormatter
from models.profile_data import ProfileData, ProfileSector, ProfileType, ProfileStatus, ProfileURL, Product, Asset

def create_test_profile_with_problematic_text():
    """Create a test profile with text that could cause entity parsing issues"""
    
    # Create test data with problematic characters
    sector = ProfileSector(id="1", name="DeFi_Protocol*Test")
    profile_type = ProfileType(id="1", name="Protocol[Test]")
    status = ProfileStatus(id="1", name="Active`Test")
    
    # URLs with problematic characters
    urls = [
        ProfileURL(url="https://example.com", url_type="Website_Main*"),
        ProfileURL(url="https://docs.example.com", url_type="Documentation[Docs]"),
    ]
    
    # Products with problematic names
    products = [
        Product(id="1", name="DeFi_Protocol*V2", description="Test product with [special] chars"),
        Product(id="2", name="Staking`Pool", description="Another*test_product"),
    ]
    
    # Assets with problematic names
    assets = [
        Asset(id="1", name="TEST_TOKEN*", ticker="TEST*", description="Token with [brackets]"),
        Asset(id="2", name="LP`Token", ticker="LP_TKN", description="LP token with_underscores"),
    ]
    
    profile = ProfileData(
        id="test123",
        name="Test_Protocol*With[Special]Chars`",
        sector=sector,
        profile_type=profile_type,
        status=status,
        description_short="A test protocol with *special* characters and [links] and `code`",
        description_long="This is a longer description with _underscores_ and *asterisks* and [brackets] that might cause issues",
        tag_line="Test*tag_line[with]special`chars",
        slug="test-protocol",
        urls=urls,
        products=products,
        assets=assets,
        logo="https://example.com/logo.png"
    )
    
    return profile

def test_formatters():
    """Test all formatters with problematic text"""
    
    print("Testing Profile Formatters with Problematic Text")
    print("=" * 60)
    
    # Create test profile
    profile = create_test_profile_with_problematic_text()
    
    # Test CardFormatter
    print("\n1. Testing CardFormatter:")
    print("-" * 30)
    card_formatter = CardFormatter()
    
    try:
        formatted_card = card_formatter.format(profile)
        print("✅ CardFormatter succeeded")
        print(f"Message length: {len(formatted_card.message_text)} characters")
        print(f"First 200 chars: {formatted_card.message_text[:200]}...")
        
        # Validate entities
        if card_formatter._validate_markdown_entities(formatted_card.message_text):
            print("✅ Markdown entities are valid")
        else:
            print("⚠️  Markdown entities validation failed")
            
    except Exception as e:
        print(f"❌ CardFormatter failed: {e}")
    
    # Test ExpandedFormatter
    print("\n2. Testing ExpandedFormatter:")
    print("-" * 30)
    expanded_formatter = ExpandedFormatter()
    
    try:
        formatted_expanded = expanded_formatter.format(profile)
        print("✅ ExpandedFormatter succeeded")
        print(f"Message length: {len(formatted_expanded.message_text)} characters")
        print(f"First 200 chars: {formatted_expanded.message_text[:200]}...")
        
        # Validate entities
        if expanded_formatter._validate_markdown_entities(formatted_expanded.message_text):
            print("✅ Markdown entities are valid")
        else:
            print("⚠️  Markdown entities validation failed")
            
    except Exception as e:
        print(f"❌ ExpandedFormatter failed: {e}")
    
    # Test CompactFormatter
    print("\n3. Testing CompactFormatter:")
    print("-" * 30)
    compact_formatter = CompactFormatter()
    
    try:
        formatted_compact = compact_formatter.format(profile)
        print("✅ CompactFormatter succeeded")
        print(f"Message length: {len(formatted_compact.message_text)} characters")
        print(f"Message: {formatted_compact.message_text}")
        
        # Validate entities
        if compact_formatter._validate_markdown_entities(formatted_compact.message_text):
            print("✅ Markdown entities are valid")
        else:
            print("⚠️  Markdown entities validation failed")
            
    except Exception as e:
        print(f"❌ CompactFormatter failed: {e}")

def test_escaping_function():
    """Test the escaping function directly"""
    
    print("\n" + "=" * 60)
    print("Testing Escaping Function Directly")
    print("=" * 60)
    
    formatter = CardFormatter()
    
    test_cases = [
        "Test_with_underscores",
        "Test*with*asterisks", 
        "Test[with]brackets",
        "Test`with`backticks",
        "Complex_test*with[multiple]special`chars",
        "DeFi Protocol (DeFi)",
        "Uniswap V3",
        "Test with unmatched [bracket",
        "Test with unmatched *asterisk",
        "Test with unmatched _underscore",
    ]
    
    for i, test_text in enumerate(test_cases, 1):
        escaped = formatter._escape_markdown_text(test_text)
        is_valid = formatter._validate_markdown_entities(escaped)
        
        print(f"\nTest {i}: '{test_text}'")
        print(f"Escaped: '{escaped}'")
        print(f"Valid: {'✅' if is_valid else '❌'}")

def test_entity_validation():
    """Test the entity validation function"""
    
    print("\n" + "=" * 60)
    print("Testing Entity Validation Function")
    print("=" * 60)
    
    formatter = CardFormatter()
    
    test_cases = [
        ("Valid text with *bold* and _italic_", True),
        ("Valid text with [link](url)", True),
        ("Valid text with `code`", True),
        ("Invalid text with *unmatched bold", False),
        ("Invalid text with _unmatched italic", False),
        ("Invalid text with [unmatched bracket", False),
        ("Invalid text with `unmatched code", False),
        ("Multiple *bold* and _italic_ pairs", True),
        ("Mixed *bold _italic* text_", True),  # This might be tricky
        ("Normal text without special chars", True),
    ]
    
    for i, (test_text, expected) in enumerate(test_cases, 1):
        result = formatter._validate_markdown_entities(test_text)
        status = "✅" if result == expected else "❌"
        
        print(f"\nTest {i}: '{test_text}'")
        print(f"Expected: {expected}, Got: {result} {status}")

if __name__ == "__main__":
    print("Telegram Formatter Fix Verification")
    print("=" * 50)
    
    test_formatters()
    test_escaping_function()
    test_entity_validation()
    
    print("\n" + "=" * 50)
    print("Test completed. Check for any ❌ failures above.")