#!/usr/bin/env python3
"""
Test script to reproduce and fix the Telegram entity parsing error
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_markdown_escaping():
    """Test the current markdown escaping logic"""
    
    # Current problematic escaping logic
    def current_escape_markdown_text(text: str) -> str:
        """Current escaping logic that might be causing issues"""
        if not text:
            return text
        
        # Current problematic chars list
        problematic_chars = ['_', '*', '[', ']', '`', '\\', '(', ')']
        
        for char in problematic_chars:
            text = text.replace(char, f'\\{char}')
        
        return text
    
    # Fixed escaping logic
    def fixed_escape_markdown_text(text: str) -> str:
        """Fixed escaping logic for Telegram MarkdownV2"""
        if not text:
            return text
        
        # Only escape actual Telegram MarkdownV2 special characters
        # Reference: https://core.telegram.org/bots/api#markdownv2-style
        special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
        
        for char in special_chars:
            text = text.replace(char, f'\\{char}')
        
        return text
    
    # Alternative: Use a simpler approach - remove markdown formatting entirely for problematic text
    def safe_text_format(text: str) -> str:
        """Safe text formatting that avoids markdown issues entirely"""
        if not text:
            return text
        
        # Remove or replace problematic characters instead of escaping
        # This is safer for Telegram's entity parser
        replacements = {
            '_': '-',
            '*': '•',
            '[': '(',
            ']': ')',
            '`': "'",
            '\\': '/',
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        return text
    
    # Test cases that might cause entity parsing errors
    test_cases = [
        "Test_with_underscores",
        "Test*with*asterisks", 
        "Test[with]brackets",
        "Test(with)parentheses",
        "Test`with`backticks",
        "Test\\with\\backslashes",
        "Complex_test*with[multiple]special(chars)`here",
        "DeFi Protocol (DeFi)",
        "Uniswap V3",
        "Compound Finance",
        "Test with unmatched [bracket",
        "Test with unmatched *asterisk",
        "Test with unmatched _underscore",
    ]
    
    print("Testing markdown escaping approaches:")
    print("=" * 60)
    
    for i, test_text in enumerate(test_cases, 1):
        print(f"\nTest {i}: '{test_text}'")
        print(f"Current:  '{current_escape_markdown_text(test_text)}'")
        print(f"Fixed:    '{fixed_escape_markdown_text(test_text)}'")
        print(f"Safe:     '{safe_text_format(test_text)}'")
    
    return test_cases

def test_telegram_message_format():
    """Test a complete message format that might cause the error"""
    
    def safe_escape_markdown(text: str) -> str:
        """Safest approach - minimal escaping"""
        if not text:
            return text
        
        # Only escape the most critical characters that definitely cause issues
        critical_chars = ['*', '_', '`', '[', ']']
        
        for char in critical_chars:
            text = text.replace(char, f'\\{char}')
        
        return text
    
    # Simulate a profile message that might cause the error
    profile_data = {
        'name': 'Uniswap V3',
        'sector': 'DeFi Protocol',
        'description': 'Automated market maker (AMM) protocol',
        'products': ['Uniswap V3 Core', 'Uniswap V3 Periphery'],
        'assets': ['UNI Token']
    }
    
    # Format message like the CardFormatter does
    safe_name = safe_escape_markdown(profile_data['name'])
    safe_sector = safe_escape_markdown(profile_data['sector'])
    safe_description = safe_escape_markdown(profile_data['description'])
    
    message_parts = [
        f"*Name:* {safe_name}",
        f"*Sector:* {safe_sector}",
        f"*Description:* {safe_description}",
        f"*Products:* {len(profile_data['products'])} available",
        f"*Assets:* {len(profile_data['assets'])} available",
    ]
    
    message_text = "\n".join(message_parts)
    
    print("\nTesting complete message format:")
    print("=" * 40)
    print(f"Message text:\n{message_text}")
    print(f"\nMessage length: {len(message_text)} characters")
    print(f"Byte length: {len(message_text.encode('utf-8'))} bytes")
    
    # Check for potential entity parsing issues
    print("\nChecking for potential issues:")
    if message_text.count('*') % 2 != 0:
        print("⚠️  WARNING: Unmatched asterisks detected!")
    if message_text.count('_') % 2 != 0:
        print("⚠️  WARNING: Unmatched underscores detected!")
    if message_text.count('[') != message_text.count(']'):
        print("⚠️  WARNING: Unmatched brackets detected!")
    
    return message_text

if __name__ == "__main__":
    print("Telegram Entity Parsing Fix Test")
    print("=" * 50)
    
    test_markdown_escaping()
    test_telegram_message_format()
    
    print("\n" + "=" * 50)
    print("RECOMMENDATION:")
    print("1. Use minimal escaping - only escape critical characters")
    print("2. Ensure all markdown entities are properly paired")
    print("3. Consider using plain text for problematic content")
    print("4. Add validation to check for unmatched entities before sending")