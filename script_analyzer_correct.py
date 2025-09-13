"""Correct Interactive PDF Script Questionnaire Application."""

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
        self.current_question_id: str = "start"
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
        
        # Create a simple structure based on the actual script
        self._create_script_structure(lines)
        
        return True
    
    def _create_script_structure(self, lines: List[str]) -> None:
        """Create script structure based on the actual content."""
        
        # Start with the opening line
        self.questions["start"] = {
            "question": "Hey I have a question for you",
            "suggestions": ["Sure"],
            "next_questions": {"Sure": "1"}
        }
        
        # Find all numbered questions
        question_numbers = []
        for line in lines:
            match = re.match(r'^(\d+)[\.\)]\s*(.+)$', line)
            if match:
                question_numbers.append((match.group(1), match.group(2)))
        
        # Create questions with basic flow
        for i, (q_num, q_text) in enumerate(question_numbers):
            current_q_id = q_num
            
            # Determine next question (usually next sequential)
            next_q_id = str(int(q_num) + 1)
            
            # Basic suggestions and flow
            suggestions = ["Yes", "No", "Not sure"]
            next_questions = {
                "Yes": next_q_id,
                "No": next_q_id,
                "Not sure": next_q_id
            }
            
            # Special handling for specific questions based on the script flow
            if q_num == "1":  # "What do you think happens to us after we die?"
                suggestions = ["Not sure", "Heaven and hell", "Reincarnation", "Nothing"]
                next_questions = {
                    "Not sure": "2",
                    "Heaven and hell": "4",  # Skip to question 4
                    "Reincarnation": "2",
                    "Nothing": "2"
                }
            elif q_num == "2":  # "Do you believe there's a God?"
                suggestions = ["Yes", "No"]
                next_questions = {
                    "Yes": "3",
                    "No": "5"  # If they don't believe, go to question 5
                }
            elif q_num == "3":  # "Since we know there is a God..."
                suggestions = ["Yes", "No"]
                next_questions = {
                    "Yes": "4",
                    "No": "7"  # If they say no, go to question 7
                }
            elif q_num == "4":  # "Have you ever told a lie?"
                suggestions = ["Yes", "No"]
                next_questions = {
                    "Yes": "5",
                    "No": "5"  # Continue to next question
                }
            elif q_num == "5":  # "Have you ever used bad language?"
                suggestions = ["Yes", "No"]
                next_questions = {
                    "Yes": "6",
                    "No": "6"
                }
            
            self.questions[current_q_id] = {
                "question": q_text,
                "suggestions": suggestions,
                "next_questions": next_questions
            }
        
        # Add a completion question at the end
        last_q = str(len(question_numbers))
        self.questions[last_q]["next_questions"] = {
            "Yes": "complete",
            "No": "complete",
            "Not sure": "complete"
        }
        
        # Add completion state
        self.questions["complete"] = {
            "question": "Thank you for going through the script with me. That's all the questions I have.",
            "suggestions": ["Start over"],
            "next_questions": {"Start over": "start"}
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
        
        # If no match found, try to go to next sequential question
        if self.current_question_id.isdigit():
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
        """Reset to the beginning."""
        self.current_question_id = "start"
    
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
            if st.button("🏠 Go to Start"):
                st.session_state.analyzer.current_question_id = "start"
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
    if current_q['question_id'] == "start":
        st.header("🎬 Script Start")
    elif current_q['question_id'] == "complete":
        st.header("✅ Script Complete")
    else:
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
