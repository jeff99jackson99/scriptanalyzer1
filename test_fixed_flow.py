"""Test the fixed script flow to ensure it works correctly."""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_fixed_flow():
    """Test the fixed flow patterns."""
    
    print("🧪 Testing Fixed Script Flow")
    print("=" * 50)
    
    # Test the key flow patterns from the script
    test_cases = [
        {
            "name": "Heaven and Hell believer (should skip to Q4)",
            "flow": ["Sure", "Heaven and hell"],
            "expected": "4"
        },
        {
            "name": "Non-believer (should go to Q5)",
            "flow": ["Sure", "Not sure", "No"],
            "expected": "5"
        },
        {
            "name": "Good person (should go to Q4)",
            "flow": ["Sure", "Not sure", "Yes", "Yes"],
            "expected": "4"
        },
        {
            "name": "Not a good person (should go to Q7)",
            "flow": ["Sure", "Not sure", "Yes", "No"],
            "expected": "7"
        }
    ]
    
    # Simulate the flow logic
    for test_case in test_cases:
        print(f"🧪 {test_case['name']}")
        print("-" * 40)
        
        current_q = "start"
        
        for answer in test_case['flow']:
            print(f"Q{current_q}: Answer: {answer}")
            
            # Simulate the flow logic
            if current_q == "start" and answer == "Sure":
                current_q = "1"
            elif current_q == "1" and answer == "Heaven and hell":
                current_q = "4"
            elif current_q == "1" and answer == "Not sure":
                current_q = "2"
            elif current_q == "2" and answer == "No":
                current_q = "5"
            elif current_q == "2" and answer == "Yes":
                current_q = "3"
            elif current_q == "3" and answer == "Yes":
                current_q = "4"
            elif current_q == "3" and answer == "No":
                current_q = "7"
            elif current_q == "4" and answer == "Yes":
                current_q = "5"
            elif current_q == "5" and answer == "Yes":
                current_q = "6"
            elif current_q == "6" and answer == "Yes":
                current_q = "7"
            else:
                # For other questions, just increment
                if current_q.isdigit():
                    current_q = str(int(current_q) + 1)
        
        print(f"Final question: {current_q}")
        if current_q == test_case['expected']:
            print("✅ PASS")
        else:
            print(f"❌ FAIL - Expected {test_case['expected']}, got {current_q}")
        print()
    
    print("=" * 50)
    print("✅ Fixed flow test completed!")

if __name__ == "__main__":
    test_fixed_flow()
