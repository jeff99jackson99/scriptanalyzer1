"""Test script to verify the entire conversational flow matches the PDF script."""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from script_analyzer_ai import AIScriptAnalyzer

def test_script_flow():
    """Test the complete script flow to ensure it matches the PDF."""
    
    print("🧪 Testing Complete Script Flow")
    print("=" * 50)
    
    # Initialize analyzer
    analyzer = AIScriptAnalyzer("script.pdf")
    if not analyzer.parse_script():
        print("❌ Failed to parse script")
        return False
    
    print(f"✅ Script parsed successfully with {len(analyzer.questions)} questions")
    print()
    
    # Test scenarios based on the actual script
    test_scenarios = [
        {
            "name": "Scenario 1: Heaven and Hell believer (should skip to Q4)",
            "answers": ["Sure", "Heaven and hell"]
        },
        {
            "name": "Scenario 2: Not sure about afterlife (normal flow)",
            "answers": ["Sure", "Not sure", "Yes", "Yes", "Yes", "Yes", "Guilty", "Punishment", "Hell", "Not sure", "Nothing", "Heaven", "Yes", "Heaven", "Because Jesus paid for my sins", "Yes", "Heaven", "Because Jesus paid for my sins", "Hell", "Now", "Because Jesus paid for my sins", "Hell", "Hell", "100%", "No", "No", "No", "Because we are thankful", "The Bible", "Yes", "No", "Everyday", "Yes", "Yes", "I'm not sure", "Tell them about the Gospel", "Because Jesus paid for my sins", "Doing good", "Heaven"]
        },
        {
            "name": "Scenario 3: Non-believer (should go to Q5)",
            "answers": ["Sure", "Not sure", "No"]
        },
        {
            "name": "Scenario 4: Good person (normal flow)",
            "answers": ["Sure", "Not sure", "Yes", "Yes", "Yes", "Yes", "Guilty", "Punishment", "Hell", "Not sure", "Nothing", "Heaven", "Yes", "Heaven", "Because Jesus paid for my sins", "Yes", "Heaven", "Because Jesus paid for my sins", "Hell", "Now", "Because Jesus paid for my sins", "Hell", "Hell", "100%", "No", "No", "No", "Because we are thankful", "The Bible", "Yes", "No", "Everyday", "Yes", "Yes", "I'm not sure", "Tell them about the Gospel", "Because Jesus paid for my sins", "Doing good", "Heaven"]
        }
    ]
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"🧪 {scenario['name']}")
        print("-" * 40)
        
        # Reset analyzer
        analyzer.reset_to_beginning()
        
        # Follow the conversation
        for j, answer in enumerate(scenario['answers']):
            current_q = analyzer.get_current_question()
            if not current_q:
                print(f"❌ No question available at step {j+1}")
                break
                
            print(f"Q{current_q['question_id']}: {current_q['question']}")
            print(f"Answer: {answer}")
            
            # Submit answer
            success = analyzer.submit_answer(answer)
            if not success:
                print(f"❌ Failed to process answer: {answer}")
                break
                
            print(f"✅ Moved to: {analyzer.current_question_id}")
            print()
            
            # Check if we've completed
            if analyzer.current_question_id == "complete":
                print("🎉 Conversation completed successfully!")
                break
        
        print("=" * 50)
        print()
    
    # Test specific flow patterns from the script
    print("🔍 Testing Specific Flow Patterns")
    print("=" * 50)
    
    # Test 1: Heaven and Hell response should skip to Q4
    print("Test 1: Heaven and Hell response should skip to Q4")
    analyzer.reset_to_beginning()
    analyzer.submit_answer("Sure")
    analyzer.submit_answer("Heaven and hell")
    current_q = analyzer.get_current_question()
    if current_q and current_q['question_id'] == "4":
        print("✅ Correctly skipped to Question 4")
    else:
        print(f"❌ Expected Q4, got Q{current_q['question_id'] if current_q else 'None'}")
    print()
    
    # Test 2: Non-believer should go to Q5
    print("Test 2: Non-believer should go to Q5")
    analyzer.reset_to_beginning()
    analyzer.submit_answer("Sure")
    analyzer.submit_answer("Not sure")
    analyzer.submit_answer("No")
    current_q = analyzer.get_current_question()
    if current_q and current_q['question_id'] == "5":
        print("✅ Correctly went to Question 5")
    else:
        print(f"❌ Expected Q5, got Q{current_q['question_id'] if current_q else 'None'}")
    print()
    
    # Test 3: Good person should go to Q4
    print("Test 3: Good person should go to Q4")
    analyzer.reset_to_beginning()
    analyzer.submit_answer("Sure")
    analyzer.submit_answer("Not sure")
    analyzer.submit_answer("Yes")
    analyzer.submit_answer("Yes")
    current_q = analyzer.get_current_question()
    if current_q and current_q['question_id'] == "4":
        print("✅ Correctly went to Question 4")
    else:
        print(f"❌ Expected Q4, got Q{current_q['question_id'] if current_q else 'None'}")
    print()
    
    # Test 4: Not a good person should go to Q7
    print("Test 4: Not a good person should go to Q7")
    analyzer.reset_to_beginning()
    analyzer.submit_answer("Sure")
    analyzer.submit_answer("Not sure")
    analyzer.submit_answer("Yes")
    analyzer.submit_answer("No")
    current_q = analyzer.get_current_question()
    if current_q and current_q['question_id'] == "7":
        print("✅ Correctly went to Question 7")
    else:
        print(f"❌ Expected Q7, got Q{current_q['question_id'] if current_q else 'None'}")
    print()
    
    # Show all questions and their flow
    print("📋 Complete Question Flow Map")
    print("=" * 50)
    for q_id in sorted(analyzer.questions.keys(), key=lambda x: int(x) if x.isdigit() else 0):
        if q_id == "start":
            continue
        if q_id == "complete":
            continue
            
        question_data = analyzer.questions[q_id]
        print(f"Q{q_id}: {question_data['question']}")
        print(f"  Context: {question_data.get('context', 'No context')}")
        print(f"  Suggestions: {question_data['suggestions']}")
        print(f"  Next Questions: {question_data['next_questions']}")
        print()
    
    return True

if __name__ == "__main__":
    test_script_flow()
