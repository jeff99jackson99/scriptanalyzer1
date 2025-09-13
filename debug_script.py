"""Debug script to understand the PDF structure better."""

import PyPDF2
import re

def debug_script_structure():
    """Debug the script structure to understand the flow."""
    try:
        with open('script.pdf', 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        print("=" * 80)
        print("🔍 DETAILED SCRIPT STRUCTURE ANALYSIS")
        print("=" * 80)
        
        # Look for the first few questions and their complete structure
        question_count = 0
        i = 0
        
        while i < len(lines) and question_count < 5:
            line = lines[i]
            
            # Look for question patterns
            question_match = re.match(r'^(\d+)[\.\)]\s*(.+)$', line)
            if question_match:
                question_count += 1
                q_num = question_match.group(1)
                q_text = question_match.group(2)
                
                print(f"\n📋 QUESTION {q_num}: {q_text}")
                print("-" * 60)
                
                # Look at the next few lines to see the structure
                j = i + 1
                line_count = 0
                while j < len(lines) and line_count < 10:
                    next_line = lines[j]
                    
                    # Stop if we hit another question
                    if re.match(r'^\d+[\.\)]\s*(.+)$', next_line):
                        break
                    
                    print(f"   {j-i:2d}. {next_line}")
                    
                    # Look for flow indicators in this line
                    flow_patterns = [
                        r'If they say (.+?),',
                        r'If (.+?),',
                        r'go straight on to asking them the next question',
                        r'go to question (\d+)',
                        r'ask them question (\d+)',
                    ]
                    
                    for pattern in flow_patterns:
                        match = re.search(pattern, next_line, re.IGNORECASE)
                        if match:
                            print(f"      🔄 FLOW: {match.group(0)}")
                    
                    j += 1
                    line_count += 1
                
                i = j - 1
            
            i += 1
        
        print("\n" + "=" * 80)
        print("📊 SUMMARY")
        print("=" * 80)
        
        # Count total questions
        total_questions = 0
        for line in lines:
            if re.match(r'^\d+[\.\)]\s*(.+)$', line):
                total_questions += 1
        
        print(f"Total questions found: {total_questions}")
        
        # Look for common patterns
        if_patterns = []
        for line in lines:
            if 'If they say' in line or 'If ' in line:
                if_patterns.append(line)
        
        print(f"Flow patterns found: {len(if_patterns)}")
        if if_patterns:
            print("Sample flow patterns:")
            for pattern in if_patterns[:5]:
                print(f"  - {pattern}")
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    debug_script_structure()
