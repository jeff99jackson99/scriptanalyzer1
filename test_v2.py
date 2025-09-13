"""Test the improved script analyzer."""

from script_analyzer_v2 import ScriptAnalyzer

def test_improved_parser():
    """Test the improved parsing functionality."""
    print("=" * 60)
    print("🔍 Testing Improved Script Analyzer")
    print("=" * 60)
    
    try:
        analyzer = ScriptAnalyzer("script.pdf")
        if analyzer.parse_script():
            print("✅ Script parsing successful!")
            print(f"Questions parsed: {len(analyzer.questions)}")
            
            # Show first few questions with their flow
            for i, (q_id, q_data) in enumerate(list(analyzer.questions.items())[:3]):
                print(f"\n📋 Question {q_id}: {q_data['question']}")
                print(f"   Suggestions: {q_data['suggestions']}")
                print(f"   Next questions: {q_data['next_questions']}")
            
            return True
        else:
            print("❌ Script parsing failed")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_improved_parser()
