"""Comprehensive test of all questions and answer suggestions."""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from script_analyzer_ai import AIScriptAnalyzer

def test_all_questions():
    """Test all questions and their answer suggestions."""
    
    print("🧪 Testing All Questions and Answer Suggestions")
    print("=" * 60)
    
    # Initialize analyzer
    analyzer = AIScriptAnalyzer("script.pdf")
    if not analyzer.parse_script():
        print("❌ Failed to parse script")
        return False
    
    print(f"✅ Script parsed successfully with {len(analyzer.questions)} questions")
    print()
    
    # Test each question individually
    test_results = []
    
    for q_id in sorted(analyzer.questions.keys(), key=lambda x: int(x) if x.isdigit() else 0):
        if q_id in ["start", "complete"]:
            continue
            
        print(f"🔍 Testing Question {q_id}")
        print("-" * 40)
        
        question_data = analyzer.questions[q_id]
        suggestions = question_data.get("suggestions", [])
        next_questions = question_data.get("next_questions", {})
        
        print(f"Question: {question_data['question']}")
        print(f"Suggestions: {suggestions}")
        print(f"Next Questions: {next_questions}")
        
        # Test each suggestion
        suggestion_results = []
        for suggestion in suggestions:
            # Reset to this question
            analyzer.current_question_id = q_id
            
            # Test the suggestion
            success = analyzer.submit_answer(suggestion)
            next_q = analyzer.current_question_id
            
            if success:
                print(f"  ✅ '{suggestion}' -> Q{next_q}")
                suggestion_results.append(True)
            else:
                print(f"  ❌ '{suggestion}' -> FAILED")
                suggestion_results.append(False)
        
        # Check if all suggestions work
        all_work = all(suggestion_results)
        test_results.append({
            "question_id": q_id,
            "all_suggestions_work": all_work,
            "working_suggestions": sum(suggestion_results),
            "total_suggestions": len(suggestions)
        })
        
        print(f"Result: {sum(suggestion_results)}/{len(suggestions)} suggestions work")
        print()
    
    # Summary
    print("📊 Test Summary")
    print("=" * 60)
    
    total_questions = len(test_results)
    fully_working = sum(1 for r in test_results if r["all_suggestions_work"])
    partially_working = sum(1 for r in test_results if r["working_suggestions"] > 0 and not r["all_suggestions_work"])
    not_working = sum(1 for r in test_results if r["working_suggestions"] == 0)
    
    print(f"Total Questions Tested: {total_questions}")
    print(f"Fully Working: {fully_working}")
    print(f"Partially Working: {partially_working}")
    print(f"Not Working: {not_working}")
    print()
    
    # Show problematic questions
    if partially_working > 0 or not_working > 0:
        print("⚠️  Problematic Questions:")
        for result in test_results:
            if not result["all_suggestions_work"]:
                print(f"  Q{result['question_id']}: {result['working_suggestions']}/{result['total_suggestions']} suggestions work")
        print()
    
    # Test specific flow scenarios
    print("🔄 Testing Flow Scenarios")
    print("=" * 60)
    
    scenarios = [
        {
            "name": "Heaven and Hell believer (skip to Q4)",
            "answers": ["Sure", "Heaven and hell"],
            "expected_final": "4"
        },
        {
            "name": "Non-believer (go to Q5)",
            "answers": ["Sure", "Not sure", "No"],
            "expected_final": "5"
        },
        {
            "name": "Good person (go to Q4)",
            "answers": ["Sure", "Not sure", "Yes", "Yes"],
            "expected_final": "4"
        },
        {
            "name": "Not good person (go to Q7)",
            "answers": ["Sure", "Not sure", "Yes", "No"],
            "expected_final": "7"
        },
        {
            "name": "Complete flow with correct answers",
            "answers": [
                "Sure", "Not sure", "Yes", "Yes", "Yes", "Yes", "Guilty",
                "Punishment", "Hell", "Not sure", "Nothing", "Heaven", "Yes",
                "Heaven", "Because Jesus paid for my sins", "Yes", "Heaven",
                "Because Jesus paid for my sins", "Hell", "Now", "Because Jesus paid for my sins",
                "Hell", "Hell", "100%", "No", "No", "No", "Because we are thankful",
                "The Bible", "Yes", "No", "Everyday", "Yes", "Yes", "I am not sure",
                "Tell them about the Gospel", "Because Jesus paid for my sins", "Doing good", "Heaven"
            ],
            "expected_final": "complete"
        }
    ]
    
    for scenario in scenarios:
        print(f"🧪 {scenario['name']}")
        print("-" * 40)
        
        analyzer.reset_to_beginning()
        success = True
        
        for i, answer in enumerate(scenario['answers']):
            current_q = analyzer.get_current_question()
            if not current_q:
                print(f"❌ No question available at step {i+1}")
                success = False
                break
            
            print(f"Q{current_q['question_id']}: {answer}")
            
            if not analyzer.submit_answer(answer):
                print(f"❌ Failed to process answer: {answer}")
                success = False
                break
            
            if analyzer.current_question_id == "complete":
                break
        
        final_q = analyzer.current_question_id
        if success and final_q == scenario['expected_final']:
            print(f"✅ PASS - Final question: {final_q}")
        else:
            print(f"❌ FAIL - Expected {scenario['expected_final']}, got {final_q}")
        print()
    
    return True

if __name__ == "__main__":
    test_all_questions()
