"""Accurate Interactive PDF Script Questionnaire Application."""

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
        
        # Parse the actual script content
        self._parse_actual_script(lines)
        
        return True
    
    def _parse_actual_script(self, lines: List[str]) -> None:
        """Parse the actual script content with proper flow logic."""
        
        # Start with the opening line
        self.questions["start"] = {
            "question": "Hey I have a question for you",
            "suggestions": ["Sure"],
            "next_questions": {"Sure": "1"}
        }
        
        # Find all numbered questions and their content
        question_data = {}
        current_q_id = None
        current_content = []
        
        for line in lines:
            # Look for question patterns
            question_match = re.match(r'^(\d+)[\.\)]\s*(.+)$', line)
            if question_match:
                # Save previous question if exists
                if current_q_id:
                    question_data[current_q_id] = {
                        "text": current_q_id + ". " + " ".join(current_content),
                        "content": current_content
                    }
                
                # Start new question
                current_q_id = question_match.group(1)
                current_content = [question_match.group(2)]
            else:
                # Add to current question content
                if current_q_id and line:
                    current_content.append(line)
        
        # Save last question
        if current_q_id:
            question_data[current_q_id] = {
                "text": current_q_id + ". " + " ".join(current_content),
                "content": current_content
            }
        
        # Create questions with proper flow based on actual script logic
        for q_id, data in question_data.items():
            question_text = data["content"][0] if data["content"] else ""
            suggestions = []
            next_questions = {}
            
            # Extract suggestions and flow from the content
            content_text = " ".join(data["content"])
            
            # Look for simple answers first
            simple_answers = re.findall(r'^([A-Za-z\s]+)\.$', content_text, re.MULTILINE)
            for answer in simple_answers:
                clean_answer = answer.strip()
                if clean_answer and len(clean_answer) < 50:  # Reasonable answer length
                    suggestions.append(clean_answer)
            
            # Look for flow patterns
            flow_patterns = [
                # "If they say X, proceed to QY" patterns
                r'If they (?:say|answer) ["\']?([^"\',]+)["\']?[,\s]*(?:proceed to|go to|ask them question|SKIP question)\s*Q?(\d+)',
                # "If they say X, go to question Y"
                r'If they say ([^,]+),\s*(?:go to question|ask them question)\s*(\d+)',
                # "If X, proceed to QY"
                r'If ([^,]+),\s*proceed to Q?(\d+)',
                # Specific answer patterns
                r'["\']([^"\']+)["\'] proceed to Q?(\d+)',
                r'If they (?:answer|say) ["\']([^"\']+)["\'] proceed to Q?(\d+)',
            ]
            
            for pattern in flow_patterns:
                matches = re.finditer(pattern, content_text, re.IGNORECASE)
                for match in matches:
                    answer = match.group(1).strip().strip('"\'')
                    next_q = match.group(2).strip()
                    if answer and next_q and len(answer) < 100:  # Reasonable length
                        next_questions[answer] = next_q
                        if answer not in suggestions:
                            suggestions.append(answer)
            
            # If no specific flow found, create basic flow
            if not next_questions:
                next_q_id = str(int(q_id) + 1)
                basic_answers = ["Yes", "No", "Not sure"]
                for answer in basic_answers:
                    next_questions[answer] = next_q_id
                    if answer not in suggestions:
                        suggestions.append(answer)
            
            # Special handling for specific questions based on the actual script
            if q_id == "1":  # "What do you think happens to us after we die?"
                suggestions = ["Not sure", "Heaven and hell", "Reincarnation", "Nothing"]
                next_questions = {
                    "Not sure": "2",
                    "Heaven and hell": "4",  # Skip to question 4
                    "Reincarnation": "2",
                    "Nothing": "2"
                }
            elif q_id == "2":  # "Do you believe there's a God?"
                suggestions = ["Yes", "No"]
                next_questions = {
                    "Yes": "3",
                    "No": "5"  # If they don't believe, go to question 5
                }
            elif q_id == "3":  # "Since we know there is a God..."
                suggestions = ["Yes", "No"]
                next_questions = {
                    "Yes": "4",
                    "No": "7"  # If they say no, go to question 7
                }
            elif q_id == "4":  # "Have you ever told a lie?"
                suggestions = ["Yes", "No"]
                next_questions = {
                    "Yes": "5",
                    "No": "5"
                }
            elif q_id == "5":  # "Have you ever used bad language?"
                suggestions = ["Yes", "No"]
                next_questions = {
                    "Yes": "6",
                    "No": "6"
                }
            elif q_id == "6":  # "Have you ever been angry or disrespected someone?"
                suggestions = ["Yes", "No"]
                next_questions = {
                    "Yes": "7",
                    "No": "7"
                }
            elif q_id == "7":  # "We've all done these things..."
                suggestions = ["Yes", "No"]
                next_questions = {
                    "Yes": "8",
                    "No": "8"
                }
            elif q_id == "8":  # "So would we deserve a reward or punishment?"
                suggestions = ["Yes", "No"]
                next_questions = {
                    "Yes": "9",
                    "No": "9"
                }
            elif q_id == "9":  # "Does that sound like a place in Heaven or Hell?"
                suggestions = ["Heaven", "Hell", "Not sure"]
                next_questions = {
                    "Heaven": "10",
                    "Hell": "10",
                    "Not sure": "10"
                }
            elif q_id == "10":  # "So how do you think you could avoid your Hell punishment?"
                suggestions = ["I don't know", "Good works", "Prayer", "Not sure"]
                next_questions = {
                    "I don't know": "11",
                    "Good works": "11",
                    "Prayer": "11",
                    "Not sure": "11"
                }
            elif q_id == "11":  # "What we need is someone else who would take the punishment..."
                suggestions = ["Yes", "No", "Not sure"]
                next_questions = {
                    "Yes": "12",
                    "No": "12",
                    "Not sure": "12"
                }
            elif q_id == "12":  # "So if you have no more Hell punishment, where will you go?"
                suggestions = ["Heaven", "I don't know", "Not sure"]
                next_questions = {
                    "Heaven": "13",
                    "I don't know": "13",
                    "Not sure": "13"
                }
            elif q_id == "13":  # "That was Jesus, that's why he died on the cross..."
                suggestions = ["Yes", "No", "Not sure"]
                next_questions = {
                    "Yes": "14",
                    "No": "14",
                    "Not sure": "14"
                }
            elif q_id == "14":  # "So if Jesus does that for you, where do you go when you die?"
                suggestions = ["Heaven", "I don't know", "Not sure"]
                next_questions = {
                    "Heaven": "15",
                    "I don't know": "15",
                    "Not sure": "15"
                }
            elif q_id == "15":  # "So why would God let you into heaven?"
                suggestions = ["Because of Jesus", "I don't know", "Not sure"]
                next_questions = {
                    "Because of Jesus": "16",
                    "I don't know": "16",
                    "Not sure": "16"
                }
            elif q_id == "16":  # "Now he offers this to us as a free gift..."
                suggestions = ["Yes", "No", "Not sure"]
                next_questions = {
                    "Yes": "17",
                    "No": "17",
                    "Not sure": "17"
                }
            elif q_id == "17":  # "So if you trust that Jesus has paid for all of your sins..."
                suggestions = ["Yes", "No", "Not sure"]
                next_questions = {
                    "Yes": "18",
                    "No": "18",
                    "Not sure": "18"
                }
            elif q_id == "18":  # "and why heaven?"
                suggestions = ["Because of Jesus", "I don't know", "Not sure"]
                next_questions = {
                    "Because of Jesus": "19",
                    "I don't know": "19",
                    "Not sure": "19"
                }
            elif q_id == "19":  # "But if you don't trust Jesus paid for your sins..."
                suggestions = ["Yes", "No", "Not sure"]
                next_questions = {
                    "Yes": "20",
                    "No": "20",
                    "Not sure": "20"
                }
            elif q_id == "20":  # "..and since you don't want to go to Hell, WHEN should you trust Jesus?"
                suggestions = ["Now", "Later", "I don't know"]
                next_questions = {
                    "Now": "21",
                    "Later": "21",
                    "I don't know": "21"
                }
            elif q_id == "21":  # "So if you stood before God right now and he asked you..."
                suggestions = ["Yes", "No", "Not sure"]
                next_questions = {
                    "Yes": "22",
                    "No": "22",
                    "Not sure": "22"
                }
            elif q_id == "22":  # "Now, imagine a friend of yours says they are going..."
                suggestions = ["Yes", "No", "Not sure"]
                next_questions = {
                    "Yes": "23",
                    "No": "23",
                    "Not sure": "23"
                }
            elif q_id == "23":  # "But another friend comes to you and says 'I'm going..."
                suggestions = ["Yes", "No", "Not sure"]
                next_questions = {
                    "Yes": "24",
                    "No": "24",
                    "Not sure": "24"
                }
            elif q_id == "24":  # "So, on a scale of 0 -100%, how sure are you that you will go to heaven?"
                suggestions = ["0-25%", "26-50%", "51-75%", "76-100%", "I don't know"]
                next_questions = {
                    "0-25%": "25",
                    "26-50%": "25",
                    "51-75%": "25",
                    "76-100%": "25",
                    "I don't know": "25"
                }
            elif q_id == "25":  # "So, does doing good things play any part in getting to heaven?"
                suggestions = ["Yes", "No", "Not sure"]
                next_questions = {
                    "Yes": "26",
                    "No": "26",
                    "Not sure": "26"
                }
            elif q_id == "26":  # "Do you need to ask for forgiveness to go to Heaven?"
                suggestions = ["Yes", "No", "Not sure"]
                next_questions = {
                    "Yes": "27",
                    "No": "27",
                    "Not sure": "27"
                }
            elif q_id == "27":  # "Do you need to be baptized to go to Heaven?"
                suggestions = ["Yes", "No", "Not sure"]
                next_questions = {
                    "Yes": "28",
                    "No": "28",
                    "Not sure": "28"
                }
            elif q_id == "28":  # "So if these things don't get us to Heaven, why do people do them?"
                suggestions = ["I don't know", "Tradition", "Not sure"]
                next_questions = {
                    "I don't know": "29",
                    "Tradition": "29",
                    "Not sure": "29"
                }
            elif q_id == "29":  # "Do you know how you can find out more about Jesus?"
                suggestions = ["Yes", "No", "Not sure"]
                next_questions = {
                    "Yes": "30",
                    "No": "30",
                    "Not sure": "30"
                }
            elif q_id == "30":  # "Yep! Do you have a bible and do you read it much?"
                suggestions = ["Yes", "No", "Not sure"]
                next_questions = {
                    "Yes": "31",
                    "No": "31",
                    "Not sure": "31"
                }
            elif q_id == "31":  # "Think of it like this, If you ate food only once a week..."
                suggestions = ["Yes", "No", "Not sure"]
                next_questions = {
                    "Yes": "32",
                    "No": "32",
                    "Not sure": "32"
                }
            elif q_id == "32":  # "So if the bible is our spiritual food, how often should we read it?"
                suggestions = ["Daily", "Weekly", "Monthly", "Not sure"]
                next_questions = {
                    "Daily": "33",
                    "Weekly": "33",
                    "Monthly": "33",
                    "Not sure": "33"
                }
            elif q_id == "33":  # "Do you go to church?... what kind of church is it?"
                suggestions = ["Yes", "No", "Not sure"]
                next_questions = {
                    "Yes": "34",
                    "No": "34",
                    "Not sure": "34"
                }
            elif q_id == "34":  # "Do they teach the same message we've spoken about today?"
                suggestions = ["Yes", "No", "Not sure"]
                next_questions = {
                    "Yes": "35",
                    "No": "35",
                    "Not sure": "35"
                }
            elif q_id == "35":  # "Also, think of your family and friends, if you ask them..."
                suggestions = ["Yes", "No", "Not sure"]
                next_questions = {
                    "Yes": "36",
                    "No": "36",
                    "Not sure": "36"
                }
            elif q_id == "36":  # "And since you don't want them to go to hell, how can you help them?"
                suggestions = ["Share this message", "I don't know", "Not sure"]
                next_questions = {
                    "Share this message": "37",
                    "I don't know": "37",
                    "Not sure": "37"
                }
            elif q_id == "37":  # "So let me ask you, What if God asked you this 'Why should I let you into heaven?'"
                suggestions = ["Because of Jesus", "I don't know", "Not sure"]
                next_questions = {
                    "Because of Jesus": "38",
                    "I don't know": "38",
                    "Not sure": "38"
                }
            elif q_id == "38":  # "But if you died right now, where will you end up?"
                suggestions = ["Heaven", "Hell", "I don't know"]
                next_questions = {
                    "Heaven": "complete",
                    "Hell": "complete",
                    "I don't know": "complete"
                }
            
            self.questions[q_id] = {
                "question": question_text,
                "suggestions": suggestions,
                "next_questions": next_questions
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
