"""Interactive PDF Script Questionnaire Application."""

import re
import streamlit as st
from typing import Dict, List, Any, Optional
import PyPDF2
import os

class ScriptAnalyzer:
    """Main class for analyzing PDF scripts and managing question flow."""
    
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.questions: Dict[str, Dict[str, Any]] = {}
        self.current_question_id: str = "1"
        self.raw_text = ""
        
    def extract_text_from_pdf(self) -> str:
        """Extract text content from PDF file."""
        try:
            with open(self.pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                self.raw_text = text
                return text
        except Exception as e:
            st.error(f"Error reading PDF: {str(e)}")
            return ""
    
    def parse_script(self) -> bool:
        """Parse the PDF script and extract questions with flow logic."""
        text = self.extract_text_from_pdf()
        if not text:
            return False
            
        # Split text into lines and clean them
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # Advanced parsing to handle various script formats
        self._advanced_parse(lines)
        
        # If no questions found with advanced parsing, try basic parsing
        if not self.questions:
            self._basic_parse(lines)
        
        # If still no questions, create a fallback structure
        if not self.questions:
            self._create_fallback_structure()
        
        return True
    
    def _advanced_parse(self, lines: List[str]) -> None:
        """Advanced parsing for complex script formats."""
        current_q_id = None
        current_q_text = ""
        current_suggestions = []
        current_flow = {}
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Look for question patterns: number followed by text
            question_patterns = [
                r'^(\d+)[\.\)]\s*(.+)$',  # "1. Question text"
                r'^(\d+)\s+(.+)$',        # "1 Question text"
                r'^Question\s+(\d+)[\.\)]\s*(.+)$',  # "Question 1. Text"
            ]
            
            question_match = None
            for pattern in question_patterns:
                question_match = re.match(pattern, line, re.IGNORECASE)
                if question_match:
                    break
            
            if question_match:
                # Save previous question
                if current_q_id:
                    self.questions[current_q_id] = {
                        "question": current_q_text,
                        "suggestions": current_suggestions,
                        "next_questions": current_flow
                    }
                
                # Start new question
                current_q_id = question_match.group(1)
                current_q_text = question_match.group(2)
                current_suggestions = []
                current_flow = {}
                
                # Look ahead for answer options and flow
                j = i + 1
                while j < len(lines):
                    next_line = lines[j]
                    
                    # Stop if we hit another question
                    if any(re.match(pattern, next_line, re.IGNORECASE) for pattern in question_patterns):
                        break
                    
                    # Look for flow patterns
                    flow_patterns = [
                        r'^(.+?)\s*\(go\s+to\s+(\d+)\)$',  # "Answer (go to 5)"
                        r'^(.+?)\s*\((\d+)\)$',            # "Answer (5)"
                        r'^(.+?)\s*->\s*(\d+)$',           # "Answer -> 5"
                        r'^(.+?)\s*→\s*(\d+)$',            # "Answer → 5"
                    ]
                    
                    flow_match = None
                    for pattern in flow_patterns:
                        flow_match = re.match(pattern, next_line, re.IGNORECASE)
                        if flow_match:
                            answer = flow_match.group(1).strip()
                            next_id = flow_match.group(2)
                            current_flow[answer] = next_id
                            current_suggestions.append(answer)
                            break
                    
                    # If no flow match, check if it's a simple answer option
                    if not flow_match and len(next_line) > 2:
                        # Look for bullet points or answer indicators
                        answer_patterns = [
                            r'^[•\-\*]\s*(.+)$',  # Bullet points
                            r'^[a-zA-Z]\)\s*(.+)$',  # a) Answer
                            r'^[a-zA-Z][\.\)]\s*(.+)$',  # a. Answer
                        ]
                        
                        for pattern in answer_patterns:
                            answer_match = re.match(pattern, next_line)
                            if answer_match:
                                answer = answer_match.group(1).strip()
                                if answer not in current_suggestions:
                                    current_suggestions.append(answer)
                                break
                        else:
                            # If no pattern matches but line looks like an answer
                            if (not next_line.startswith('(') and 
                                len(next_line.split()) < 10 and 
                                next_line not in current_suggestions):
                                current_suggestions.append(next_line)
                    
                    j += 1
                
                i = j - 1
            
            i += 1
        
        # Save the last question
        if current_q_id:
            self.questions[current_q_id] = {
                "question": current_q_text,
                "suggestions": current_suggestions,
                "next_questions": current_flow
            }
    
    def _basic_parse(self, lines: List[str]) -> None:
        """Basic parsing for simple numbered lists."""
        question_pattern = re.compile(r'^(\d+)[\.\)]\s*(.+)$')
        
        for i, line in enumerate(lines):
            match = question_pattern.match(line)
            if match:
                q_id = match.group(1)
                q_text = match.group(2)
                
                # Look for next question to create simple flow
                next_q_id = str(int(q_id) + 1)
                
                self.questions[q_id] = {
                    "question": q_text,
                    "suggestions": ["Yes", "No", "Continue"],
                    "next_questions": {
                        "Yes": next_q_id,
                        "No": next_q_id, 
                        "Continue": next_q_id
                    }
                }
    
    def _create_fallback_structure(self) -> None:
        """Create a basic fallback structure if parsing fails."""
        self.questions = {
            "1": {
                "question": "I've loaded your script, but couldn't parse the question structure automatically. Please provide your response to the script content.",
                "suggestions": ["Yes", "No", "Maybe", "I need more information"],
                "next_questions": {
                    "Yes": "2",
                    "No": "2", 
                    "Maybe": "2",
                    "I need more information": "2"
                }
            },
            "2": {
                "question": "Thank you for your response. Would you like to review the raw script content?",
                "suggestions": ["Yes, show me the content", "No, that's all", "Start over"],
                "next_questions": {
                    "Yes, show me the content": "3",
                    "No, that's all": "1",
                    "Start over": "1"
                }
            },
            "3": {
                "question": f"Here's the content I extracted from your PDF:\n\n{self.raw_text[:1000]}...",
                "suggestions": ["Start over", "That's helpful"],
                "next_questions": {
                    "Start over": "1",
                    "That's helpful": "1"
                }
            }
        }
    
    def get_current_question(self) -> Optional[Dict[str, Any]]:
        """Get the current question details."""
        if self.current_question_id not in self.questions:
            return None
        
        question_data = self.questions[self.current_question_id]
        return {
            "question_id": self.current_question_id,
            "question": question_data["question"],
            "suggestions": question_data["suggestions"]
        }
    
    def submit_answer(self, answer: str) -> bool:
        """Submit an answer and move to next question."""
        if self.current_question_id not in self.questions:
            return False
        
        question_data = self.questions[self.current_question_id]
        next_questions = question_data.get("next_questions", {})
        
        # Look for exact match first
        if answer in next_questions:
            self.current_question_id = next_questions[answer]
            return True
        
        # Look for partial match (case insensitive)
        for suggestion, next_id in next_questions.items():
            if (answer.lower() in suggestion.lower() or 
                suggestion.lower() in answer.lower()):
                self.current_question_id = next_id
                return True
        
        # If no specific flow, try to go to next sequential question
        try:
            next_seq_id = str(int(self.current_question_id) + 1)
            if next_seq_id in self.questions:
                self.current_question_id = next_seq_id
                return True
        except ValueError:
            pass
        
        # If no match found, stay on current question
        return False
    
    def reset_to_beginning(self):
        """Reset to the first question."""
        self.current_question_id = "1"
    
    def get_script_summary(self) -> str:
        """Get a summary of the parsed script."""
        total_questions = len(self.questions)
        return f"Script loaded with {total_questions} questions. Current: {self.current_question_id}"

def main():
    """Main Streamlit application."""
    st.set_page_config(
        page_title="Script Analyzer",
        page_icon="📋",
        layout="wide"
    )
    
    st.title("📋 Interactive Script Questionnaire")
    st.markdown("---")
    
    # Initialize session state
    if "analyzer" not in st.session_state:
        st.session_state.analyzer = None
    if "script_loaded" not in st.session_state:
        st.session_state.script_loaded = False
    
    # Sidebar controls
    with st.sidebar:
        st.header("📁 Controls")
        
        # Load script button
        if st.button("🔄 Load Script", type="primary"):
            pdf_path = "script.pdf"
            if os.path.exists(pdf_path):
                with st.spinner("🔍 Analyzing script..."):
                    analyzer = ScriptAnalyzer(pdf_path)
                    if analyzer.parse_script():
                        st.session_state.analyzer = analyzer
                        st.session_state.script_loaded = True
                        st.success("✅ Script loaded successfully!")
                        st.balloons()
                    else:
                        st.error("❌ Failed to parse script")
            else:
                st.error("❌ script.pdf not found in current directory")
        
        # Reset button
        if st.button("🔄 Reset Script") and st.session_state.analyzer:
            st.session_state.analyzer.reset_to_beginning()
            st.success("🏁 Script reset to beginning!")
        
        # Script info
        if st.session_state.analyzer:
            st.markdown("### 📊 Script Info")
            st.info(st.session_state.analyzer.get_script_summary())
        
        st.markdown("---")
        st.markdown("### 📖 Instructions")
        st.markdown("""
        1. **Load Script**: Click the button above to load your PDF
        2. **Read Question**: Review the current question displayed
        3. **Choose Answer**: Click a suggestion or type your own
        4. **Auto-Navigate**: App moves to next question automatically
        """)
        
        if st.session_state.script_loaded:
            st.markdown("---")
            st.markdown("### 🎯 Quick Actions")
            if st.button("🏠 Go to Question 1"):
                st.session_state.analyzer.current_question_id = "1"
                st.rerun()
    
    # Main content area
    if not st.session_state.script_loaded or not st.session_state.analyzer:
        st.info("👆 Please load the script first using the sidebar button.")
        
        # Show PDF status
        if os.path.exists("script.pdf"):
            st.success("✅ script.pdf found and ready to load!")
            
            # Show file info
            file_size = os.path.getsize("script.pdf")
            st.markdown(f"**File size:** {file_size:,} bytes")
        else:
            st.error("❌ script.pdf not found. Please ensure the PDF file is in the current directory.")
        return
    
    # Get current question
    current_q = st.session_state.analyzer.get_current_question()
    if not current_q:
        st.error("❌ No current question available.")
        return
    
    # Display current question
    st.header(f"❓ Question {current_q['question_id']}")
    
    # Question text in a nice container
    with st.container():
        st.markdown(f"### {current_q['question']}")
    
    st.markdown("---")
    
    # Display suggested answers
    suggestions = current_q.get("suggestions", [])
    if suggestions:
        st.subheader("💡 Suggested Answers")
        st.markdown("*Click on a suggestion to automatically proceed:*")
        
        # Create columns for suggestions (max 3 per row)
        num_cols = min(len(suggestions), 3)
        cols = st.columns(num_cols)
        
        for i, suggestion in enumerate(suggestions):
            with cols[i % num_cols]:
                if st.button(
                    f"✅ {suggestion}", 
                    key=f"suggestion_{i}", 
                    use_container_width=True,
                    type="secondary"
                ):
                    with st.spinner("🔄 Processing..."):
                        if st.session_state.analyzer.submit_answer(suggestion):
                            st.success("✅ Answer submitted!")
                            st.rerun()
                        else:
                            st.warning("⚠️ Answer not recognized. Staying on current question.")
    
    st.markdown("---")
    
    # Manual answer input
    st.subheader("✍️ Or Type Your Own Answer")
    
    with st.form("answer_form", clear_on_submit=True):
        user_answer = st.text_area(
            "Your Answer:",
            placeholder="Type your answer here...",
            height=120,
            help="Enter your response and click Submit to proceed"
        )
        
        col1, col2 = st.columns([3, 1])
        with col1:
            submitted = st.form_submit_button("🚀 Submit Answer", type="primary")
        with col2:
            clear_btn = st.form_submit_button("🗑️ Clear")
        
        if submitted:
            if user_answer.strip():
                with st.spinner("🔄 Processing your answer..."):
                    if st.session_state.analyzer.submit_answer(user_answer.strip()):
                        st.success("✅ Answer submitted! Moving to next question.")
                        st.rerun()
                    else:
                        st.warning("⚠️ Answer not recognized. Try using one of the suggested answers above or rephrase your response.")
            else:
                st.warning("⚠️ Please enter an answer before submitting.")
    
    # Footer with debug info (expandable)
    with st.expander("🔍 Debug Information"):
        debug_info = {
            "Current Question ID": st.session_state.analyzer.current_question_id,
            "Total Questions": len(st.session_state.analyzer.questions),
            "Available Questions": list(st.session_state.analyzer.questions.keys()),
            "Current Question Data": current_q
        }
        st.json(debug_info)
        
        if st.button("📋 Show Raw PDF Text"):
            st.text_area("Raw PDF Content", st.session_state.analyzer.raw_text, height=200)

if __name__ == "__main__":
    main()
