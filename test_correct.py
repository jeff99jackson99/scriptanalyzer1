"""Test the corrected script analyzer."""

from script_analyzer import ScriptAnalyzer

def test_corrected_parser():
    """Test the corrected parsing functionality."""
    print("=" * 60)
    print("🔍 Testing Corrected Script Analyzer")
    print("=" * 60)
    
    try:
        analyzer = ScriptAnalyzer("script.pdf")
        if analyzer.parse_script():
            print("✅ Script parsing successful!")
            print(f"Questions parsed: {len(analyzer.questions)}")
            
            # Show the flow
            print("\n📋 Script Flow:")
            for q_id, q_data in analyzer.questions.items():
                print(f"  {q_id}: {q_data['question'][:50]}...")
                print(f"    Suggestions: {q_data['suggestions']}")
                print(f"    Next: {q_data['next_questions']}")
                print()
            
            return True
        else:
            print("❌ Script parsing failed")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_corrected_parser()
