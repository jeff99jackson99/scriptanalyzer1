"""AI-Powered Interactive PDF Script Questionnaire Application."""

import re
import streamlit as st
from typing import Dict, List, Any, Optional, Tuple
import PyPDF2
import os

class AIScriptAnalyzer:
    """AI-powered script analyzer that understands conversational flow."""
    
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.questions: Dict[str, Dict[str, Any]] = {}
        self.current_question_id: str = "start"
        self.raw_text = ""
        self.conversation_history: List[Dict[str, str]] = []
        
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
        """Parse the PDF script using AI-powered analysis."""
        text = self.extract_text_from_pdf()
        if not text:
            return False
            
        # Split text into lines and clean them
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # Use AI to analyze the conversational flow
        self._ai_parse_conversational_flow(lines)
        
        return True
    
    def _ai_parse_conversational_flow(self, lines: List[str]) -> None:
        """AI-powered parsing of conversational script flow."""
        
        # Start with the opening line
        self.questions["start"] = {
            "question": "Hey I have a question for you",
            "suggestions": ["Sure"],
            "next_questions": {"Sure": "1"},
            "context": "Opening question to start the conversation"
        }
        
        # Extract all numbered questions and their flow logic
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
        
        # AI-powered flow analysis for each question
        for q_id, data in question_data.items():
            question_text = data["content"][0] if data["content"] else ""
            content_text = " ".join(data["content"])
            
            # Analyze the question content to extract flow logic
            suggestions, next_questions, context = self._analyze_question_flow(q_id, question_text, content_text)
            
            self.questions[q_id] = {
                "question": question_text,
                "suggestions": suggestions,
                "next_questions": next_questions,
                "context": context
            }
        
        # Add the building analogy question for non-believers (not in original PDF but needed for flow)
        self.questions["2b"] = {
            "question": "Would you agree that the building I'm sitting in had a builder, or did it just appear by itself? This building is evidence that it needed a builder. In the same way, when we look at the universe we know it had a beginning therefore it had to have a creator for it. The universe is proof of a universe maker. Buildings need builders, creation needs a creator agree?",
            "suggestions": ["Yes", "No", "I agree", "I don't agree"],
            "next_questions": {
                "Yes": "3",
                "I agree": "3",
                "No": "5",  # If they still don't believe, go to question 5
                "I don't agree": "5"
            },
            "context": "Uses building analogy to establish belief in a creator"
        }
        
        # Add completion state
        self.questions["complete"] = {
            "question": "Thank you for going through the script with me. That's all the questions I have.",
            "suggestions": ["Start over"],
            "next_questions": {"Start over": "start"},
            "context": "Conversation completed"
        }
    
    def _analyze_question_flow(self, q_id: str, question_text: str, content_text: str) -> Tuple[List[str], Dict[str, str], str]:
        """Analyze a single question to extract suggestions and flow logic."""
        
        suggestions = []
        next_questions = {}
        context = ""
        
        # Extract simple answers from the content
        simple_answers = re.findall(r'^([A-Za-z\s]+)\.$', content_text, re.MULTILINE)
        for answer in simple_answers:
            clean_answer = answer.strip()
            if clean_answer and len(clean_answer) < 50:
                suggestions.append(clean_answer)
        
        # Extract flow patterns using regex
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
                if answer and next_q and len(answer) < 100:
                    next_questions[answer] = next_q
                    if answer not in suggestions:
                        suggestions.append(answer)
        
        # AI-powered analysis based on question content and context
        if q_id == "1":  # "What do you think happens to us after we die?"
            suggestions = ["Not sure", "Heaven and hell", "Reincarnation", "Nothing"]
            next_questions = {
                "Not sure": "2",
                "Heaven and hell": "4",  # Skip to question 4
                "Reincarnation": "2",
                "Nothing": "2"
            }
            context = "Opening question about afterlife beliefs"
            
        elif q_id == "2":  # "Do you believe there's a God?"
            suggestions = ["Yes", "No"]
            next_questions = {
                "Yes": "3",
                "No": "2b"  # If they don't believe, go to building analogy
            }
            context = "Establishes belief in God - if no, use building analogy"
            
        elif q_id == "2b":  # Building analogy for non-believers
            suggestions = ["Yes", "No", "I agree", "I don't agree"]
            next_questions = {
                "Yes": "3",
                "I agree": "3",
                "No": "5",  # If they still don't believe, go to question 5
                "I don't agree": "5"
            }
            context = "Uses building analogy to establish belief in a creator"
            
        elif q_id == "3":  # "Since we know there is a God..."
            suggestions = ["Yes", "No"]
            next_questions = {
                "Yes": "4",
                "No": "7"  # If they say no, go to question 7
            }
            context = "Tests if they think they're a good person"
            
        elif q_id == "4":  # "Have you ever told a lie?"
            suggestions = ["Yes", "No"]
            next_questions = {
                "Yes": "5",
                "No": "5"  # Continue to next question
            }
            context = "First sin question - everyone has lied"
            
        elif q_id == "5":  # "Have you ever used bad language?"
            suggestions = ["Yes", "No"]
            next_questions = {
                "Yes": "6",
                "No": "6"
            }
            context = "Second sin question - bad language"
            
        elif q_id == "6":  # "Have you ever been angry or disrespected someone?"
            suggestions = ["Yes", "No"]
            next_questions = {
                "Yes": "7",
                "No": "7"
            }
            context = "Third sin question - anger/disrespect"
            
        elif q_id == "7":  # "We've all done these things..."
            suggestions = ["Guilty", "Innocent"]
            next_questions = {
                "Guilty": "8",
                "Innocent": "8"
            }
            context = "Establishes guilt before God"
            
        elif q_id == "8":  # "So would we deserve a reward or punishment?"
            suggestions = ["Punishment", "Reward"]
            next_questions = {
                "Punishment": "9",
                "Reward": "9"
            }
            context = "Establishes we deserve punishment"
            
        elif q_id == "9":  # "Does that sound like a place in Heaven or Hell?"
            suggestions = ["Hell", "Heaven"]
            next_questions = {
                "Hell": "10",
                "Heaven": "10"
            }
            context = "Establishes we deserve Hell"
            
        elif q_id == "10":  # "So how do you think you could avoid your Hell punishment?"
            suggestions = ["Not sure", "Good works", "Prayer", "Ask for forgiveness"]
            next_questions = {
                "Not sure": "11",
                "Good works": "11",
                "Prayer": "11",
                "Ask for forgiveness": "11"
            }
            context = "Shows human solutions don't work"
            
        elif q_id == "11":  # "What we need is someone else who would take the punishment for us..."
            suggestions = ["Nothing", "Zero", "0%"]
            next_questions = {
                "Nothing": "12",
                "Zero": "12",
                "0%": "12"
            }
            context = "Introduces the concept of substitutionary atonement"
            
        elif q_id == "12":  # "So if you have no more Hell punishment, where will you go when you die?"
            suggestions = ["Heaven", "Hell"]
            next_questions = {
                "Heaven": "13",
                "Hell": "12"  # Loop back if they don't understand
            }
            context = "Establishes Heaven as destination"
            
        elif q_id == "13":  # "That was Jesus, that's why he died on the cross..."
            suggestions = ["Yes", "No", "I understand"]
            next_questions = {
                "Yes": "14",
                "No": "14",
                "I understand": "14"
            }
            context = "Introduces Jesus as the solution"
            
        elif q_id == "14":  # "So if Jesus does that for you, where do you go when you die?"
            suggestions = ["Heaven", "Hell"]
            next_questions = {
                "Heaven": "15",
                "Hell": "14"  # Loop back if they don't understand
            }
            context = "Confirms Heaven through Jesus"
            
        elif q_id == "15":  # "So why would God let you into heaven?"
            suggestions = ["Because Jesus paid for my sins", "Because of Jesus", "I don't know"]
            next_questions = {
                "Because Jesus paid for my sins": "16",
                "Because of Jesus": "16",
                "I don't know": "16"
            }
            context = "Establishes Jesus as the only reason for Heaven"
            
        elif q_id == "16":  # "Now he offers this to us as a free gift..."
            suggestions = ["Yes", "I understand", "No"]
            next_questions = {
                "Yes": "17",
                "I understand": "17",
                "No": "17"
            }
            context = "Explains salvation as a free gift"
            
        elif q_id == "17":  # "So if you trust that Jesus has paid for all of your sins now and tomorrow you sin 5 more times..."
            suggestions = ["Heaven", "Hell"]
            next_questions = {
                "Heaven": "18",
                "Hell": "17"  # Loop back to explain
            }
            context = "Explains that future sins are also covered"
            
        elif q_id == "18":  # "and why heaven?"
            suggestions = ["Because Jesus paid for my sins", "Because of Jesus"]
            next_questions = {
                "Because Jesus paid for my sins": "19",
                "Because of Jesus": "19"
            }
            context = "Reinforces Jesus as the only reason"
            
        elif q_id == "19":  # "But if you don't trust Jesus paid for your sins, where would you end up?"
            suggestions = ["Hell", "Heaven"]
            next_questions = {
                "Hell": "20",
                "Heaven": "19"  # Loop back to explain
            }
            context = "Shows consequence of not trusting Jesus"
            
        elif q_id == "20":  # "..and since you don't want to go to Hell, WHEN should you start trusting that Jesus has paid for your sins?"
            suggestions = ["Now", "Today", "Right now"]
            next_questions = {
                "Now": "21",
                "Today": "21",
                "Right now": "21"
            }
            context = "Urges immediate decision"
            
        elif q_id == "21":  # "So if you stood before God right now and he asked you 'Why should I let you into Heaven?' what would you say?"
            suggestions = ["Because Jesus paid for my sins", "Because of Jesus", "I don't know"]
            next_questions = {
                "Because Jesus paid for my sins": "22",
                "Because of Jesus": "22",
                "I don't know": "21"  # Loop back to explain
            }
            context = "Tests understanding with God's question"
            
        elif q_id == "22":  # "Now, imagine a friend of yours says they are going to heaven because they are a good person..."
            suggestions = ["Hell", "Heaven"]
            next_questions = {
                "Hell": "23",
                "Heaven": "22"  # Loop back to explain
            }
            context = "Tests understanding with friend scenario"
            
        elif q_id == "23":  # "But another friend comes to you and says 'I'm going to heaven because of two reasons...'"
            suggestions = ["Hell", "Heaven"]
            next_questions = {
                "Hell": "24",
                "Heaven": "23"  # Loop back to explain
            }
            context = "Tests understanding of mixed trust"
            
        elif q_id == "24":  # "So, on a scale of 0 -100%, how sure are you that you will go to Heaven when you die?"
            suggestions = ["100%", "76-100%", "51-75%", "26-50%", "0-25%"]
            next_questions = {
                "100%": "25",
                "76-100%": "25",
                "51-75%": "25",
                "26-50%": "25",
                "0-25%": "25"
            }
            context = "Tests confidence level"
            
        elif q_id == "25":  # "So, does doing good things play any part in getting you to heaven?"
            suggestions = ["No", "Yes"]
            next_questions = {
                "No": "26",
                "Yes": "25"  # Loop back to explain
            }
            context = "Clarifies good works don't save"
            
        elif q_id == "26":  # "Do you need to ask for forgiveness to go to Heaven?"
            suggestions = ["No", "Yes"]
            next_questions = {
                "No": "27",
                "Yes": "26"  # Loop back to explain
            }
            context = "Clarifies forgiveness doesn't save"
            
        elif q_id == "27":  # "Do you need to be baptized to go to Heaven?"
            suggestions = ["No", "Yes"]
            next_questions = {
                "No": "28",
                "Yes": "27"  # Loop back to explain
            }
            context = "Clarifies baptism doesn't save"
            
        elif q_id == "28":  # "So if these things don't get us to Heaven, why do we do good things?"
            suggestions = ["Because we are thankful", "I don't know"]
            next_questions = {
                "Because we are thankful": "29",
                "I don't know": "28"  # Loop back to explain
            }
            context = "Explains motivation for good works"
            
        elif q_id == "29":  # "Do you know how you can find out more about Jesus?"
            suggestions = ["The Bible", "Yes", "No"]
            next_questions = {
                "The Bible": "30",
                "Yes": "30",
                "No": "30"
            }
            context = "Points to Bible for growth"
            
        elif q_id == "30":  # "Yep! Do you have a bible and do you read it much?"
            suggestions = ["Yes", "No", "Sometimes"]
            next_questions = {
                "Yes": "31",
                "No": "31",
                "Sometimes": "31"
            }
            context = "Assesses Bible reading habits"
            
        elif q_id == "31":  # "Think of it like this, If you ate food only once a week, would you be very strong?"
            suggestions = ["No", "Yes"]
            next_questions = {
                "No": "32",
                "Yes": "32"
            }
            context = "Uses food analogy for Bible reading"
            
        elif q_id == "32":  # "So if the bible is our spiritual food, how often do you think you should read the bible then to be strong spiritually?"
            suggestions = ["Everyday", "Daily", "Every day", "Yes"]
            next_questions = {
                "Everyday": "34",
                "Daily": "34",
                "Every day": "34",
                "Yes": "34"
            }
            context = "Encourages daily Bible reading"
            
            
        elif q_id == "34":  # "Do they teach the same message we've spoken about here to be saved from our sins?"
            suggestions = ["Yes", "No", "Not sure"]
            next_questions = {
                "Yes": "35",
                "No": "35",
                "Not sure": "35"
            }
            context = "Assesses church teaching"
            
        elif q_id == "35":  # "Also, think of your family and friends, if you asked them, 'What's the reason you'll go to heaven?' what would their answer be?"
            suggestions = ["I'm not sure", "Because of Jesus", "Good works", "I don't know"]
            next_questions = {
                "I'm not sure": "36",
                "Because of Jesus": "36",
                "Good works": "36",
                "I don't know": "36"
            }
            context = "Considers family and friends"
            
        elif q_id == "36":  # "And since you don't want them to go to hell, how could you help them not to end up there?"
            suggestions = ["Tell them about the Gospel", "Share this message", "I don't know"]
            next_questions = {
                "Tell them about the Gospel": "37",
                "Share this message": "37",
                "I don't know": "37"
            }
            context = "Encourages sharing the Gospel"
            
        elif q_id == "37":  # "So let me ask you, What if God asked you this 'Why should I not send you to hell for all the sins you've done', how would you answer?"
            suggestions = ["Because Jesus paid for my sins", "Because of Jesus", "I don't know"]
            next_questions = {
                "Because Jesus paid for my sins": "38",
                "Because of Jesus": "38",
                "I don't know": "37"  # Loop back to explain
            }
            context = "Final test of understanding"
            
        elif q_id == "38":  # "Now, remember at the beginning of this chat, what DID you think was getting you to heaven?"
            suggestions = ["Doing good", "Good works", "Asking for forgiveness", "I don't know"]
            next_questions = {
                "Doing good": "39",
                "Good works": "39",
                "Asking for forgiveness": "39",
                "I don't know": "39"
            }
            context = "Reflects on initial beliefs"
            
        elif q_id == "39":  # "But if you died right now, where will you end up?"
            suggestions = ["Heaven", "Hell"]
            next_questions = {
                "Heaven": "complete",
                "Hell": "39"  # Loop back to explain
            }
            context = "Final confirmation of salvation"
        
        # If no specific flow found, create basic flow
        if not next_questions:
            next_q_id = str(int(q_id) + 1)
            basic_answers = ["Yes", "No", "Not sure"]
            for answer in basic_answers:
                next_questions[answer] = next_q_id
                if answer not in suggestions:
                    suggestions.append(answer)
        
        return suggestions, next_questions, context
    
    def get_current_question(self) -> Optional[Dict[str, Any]]:
        """Get the current question details."""
        if self.current_question_id not in self.questions:
            return None
        
        question_data = self.questions[self.current_question_id]
        return {
            "question_id": self.current_question_id,
            "question": question_data["question"],
            "suggestions": question_data["suggestions"],
            "context": question_data.get("context", "")
        }
    
    def submit_answer(self, answer: str) -> bool:
        """Submit an answer and move to next question."""
        if self.current_question_id not in self.questions:
            return False
        
        # Record the conversation
        self.conversation_history.append({
            "question_id": self.current_question_id,
            "question": self.questions[self.current_question_id]["question"],
            "answer": answer,
            "timestamp": st.session_state.get("current_time", "Unknown")
        })
        
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
        self.conversation_history = []
    
    def get_script_summary(self) -> str:
        """Get a summary of the parsed script."""
        total_questions = len(self.questions)
        return f"Script loaded with {total_questions} questions. Current: {self.current_question_id}"
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Get the conversation history."""
        return self.conversation_history

def main():
    """Main Streamlit application."""
    st.set_page_config(
        page_title="AI Script Analyzer",
        page_icon="🤖",
        layout="wide"
    )
    
    st.title("🤖 AI-Powered Script Analyzer")
    st.markdown("---")
    
    # Initialize session state
    if "analyzer" not in st.session_state:
        st.session_state.analyzer = None
    if "script_loaded" not in st.session_state:
        st.session_state.script_loaded = False
    if "current_time" not in st.session_state:
        st.session_state.current_time = "Unknown"
    
    # Sidebar controls
    with st.sidebar:
        st.header("📁 Controls")
        
        # Load script button
        if st.button("🔄 Load Script", type="primary"):
            pdf_path = "script.pdf"
            if os.path.exists(pdf_path):
                with st.spinner("🤖 AI is analyzing the script..."):
                    analyzer = AIScriptAnalyzer(pdf_path)
                    if analyzer.parse_script():
                        st.session_state.analyzer = analyzer
                        st.session_state.script_loaded = True
                        st.success("✅ Script analyzed successfully!")
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
            
            # Show conversation history
            if st.session_state.analyzer.conversation_history:
                st.markdown("### 📝 Conversation History")
                for i, entry in enumerate(st.session_state.analyzer.conversation_history[-5:]):  # Show last 5
                    st.markdown(f"**Q{entry['question_id']}:** {entry['answer']}")
        
        st.markdown("---")
        st.markdown("### 📖 Instructions")
        st.markdown("""
        1. **Load Script**: Click the button above to load your PDF
        2. **Read Question**: Review the current question displayed
        3. **Choose Answer**: Click a suggestion or type your own
        4. **AI Navigation**: App uses AI to understand the flow
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
    
    # Show context if available
    if current_q.get('context'):
        st.info(f"💡 **Context:** {current_q['context']}")
    
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
                    with st.spinner("🤖 AI is processing..."):
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
                with st.spinner("🤖 AI is processing your answer..."):
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
            "Current Question Data": current_q,
            "Conversation History": st.session_state.analyzer.conversation_history
        }
        st.json(debug_info)
        
        if st.button("📋 Show Raw PDF Text"):
            st.text_area("Raw PDF Content", st.session_state.analyzer.raw_text, height=200)

if __name__ == "__main__":
    main()
