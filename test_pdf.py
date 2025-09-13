"""Test script to verify PDF parsing functionality."""

import PyPDF2
import re
import os

def test_pdf_parsing():
    """Test the PDF parsing functionality with the existing script.pdf."""
    print("=" * 60)
    print("🔍 PDF Parsing Test")
    print("=" * 60)
    
    # Check if PDF exists
    if not os.path.exists("script.pdf"):
        print("❌ script.pdf not found in current directory")
        return False
    
    try:
        # Read the PDF
        print("📖 Reading PDF file...")
        with open('script.pdf', 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page_num, page in enumerate(pdf_reader.pages):
                page_text = page.extract_text()
                text += page_text + "\n"
                print(f"   Page {page_num + 1}: {len(page_text)} characters")
        
        print(f"✅ PDF read successfully! Total characters: {len(text):,}")
        
        # Analyze the content
        print("\n📊 Content Analysis:")
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        print(f"   Total lines: {len(lines)}")
        
        # Look for question patterns
        question_patterns = [
            r'^(\d+)[\.\)]\s*(.+)$',  # "1. Question text"
            r'^(\d+)\s+(.+)$',        # "1 Question text"
            r'^Question\s+(\d+)[\.\)]\s*(.+)$',  # "Question 1. Text"
        ]
        
        questions_found = []
        for line in lines:
            for pattern in question_patterns:
                match = re.match(pattern, line, re.IGNORECASE)
                if match:
                    questions_found.append((match.group(1), match.group(2)))
                    break
        
        print(f"   Questions found: {len(questions_found)}")
        
        if questions_found:
            print("\n📝 First 5 questions found:")
            for i, (q_num, q_text) in enumerate(questions_found[:5]):
                print(f"   {i+1}. Q{q_num}: {q_text[:80]}{'...' if len(q_text) > 80 else ''}")
        
        # Look for flow patterns
        flow_patterns = [
            r'^(.+?)\s*\(go\s+to\s+(\d+)\)$',  # "Answer (go to 5)"
            r'^(.+?)\s*\((\d+)\)$',            # "Answer (5)"
            r'^(.+?)\s*->\s*(\d+)$',           # "Answer -> 5"
            r'^(.+?)\s*→\s*(\d+)$',            # "Answer → 5"
        ]
        
        flows_found = []
        for line in lines:
            for pattern in flow_patterns:
                match = re.match(pattern, line, re.IGNORECASE)
                if match:
                    flows_found.append((match.group(1), match.group(2)))
                    break
        
        print(f"   Flow indicators found: {len(flows_found)}")
        
        if flows_found:
            print("\n🔄 First 5 flow indicators found:")
            for i, (answer, next_q) in enumerate(flows_found[:5]):
                print(f"   {i+1}. '{answer}' -> Q{next_q}")
        
        # Show sample content
        print(f"\n📄 Sample content (first 500 characters):")
        print("-" * 40)
        print(text[:500])
        print("-" * 40)
        
        # Test the actual parser
        print("\n🧪 Testing ScriptAnalyzer class...")
        try:
            from script_analyzer import ScriptAnalyzer
            analyzer = ScriptAnalyzer("script.pdf")
            if analyzer.parse_script():
                print("✅ ScriptAnalyzer parsing successful!")
                print(f"   Questions parsed: {len(analyzer.questions)}")
                print(f"   Question IDs: {list(analyzer.questions.keys())}")
                
                # Show first question details
                if analyzer.questions:
                    first_q_id = list(analyzer.questions.keys())[0]
                    first_q = analyzer.questions[first_q_id]
                    print(f"\n📋 First question details:")
                    print(f"   ID: {first_q_id}")
                    print(f"   Question: {first_q['question'][:100]}{'...' if len(first_q['question']) > 100 else ''}")
                    print(f"   Suggestions: {first_q['suggestions']}")
                    print(f"   Next questions: {first_q['next_questions']}")
            else:
                print("❌ ScriptAnalyzer parsing failed")
        except ImportError as e:
            print(f"⚠️  Could not import ScriptAnalyzer: {e}")
        
        print("\n✅ PDF parsing test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Error during PDF parsing test: {e}")
        return False

if __name__ == "__main__":
    test_pdf_parsing()
