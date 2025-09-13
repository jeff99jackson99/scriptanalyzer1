#!/usr/bin/env python3
"""
Complete Interactive PDF Script Questionnaire Application.
Based on the full script v4.1 provided by the user.
"""

import streamlit as st
import PyPDF2
import re
from typing import Dict, List, Tuple, Optional
import io

class CompleteScriptAnalyzer:
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.questions = {}
        self.current_question_id = "start"
        self.conversation_history = []
        
    def parse_script(self):
        """Parse the PDF and create the complete question structure based on the full script."""
        
        # Create the complete question structure based on the provided script
        self.questions = {
            "start": {
                "question": "Hey I have a question for you",
                "suggestions": ["Sure"],
                "next_questions": {"Sure": "1"},
                "context": "Opening greeting"
            },
            
            "1": {
                "question": "What do you think happens to us after we die?",
                "suggestions": ["Not sure", "Heaven and Hell", "Reincarnation", "Nothing", "Heaven", "Hell"],
                "next_questions": {
                    "Not sure": "2",
                    "Reincarnation": "2",  # Usually best to go straight to next question
                    "Nothing": "2",
                    "Heaven": "1a",  # Ask if they think they'll go to heaven and why
                    "Hell": "2",
                    "Heaven and Hell": "1a"  # Ask if they think they'll go to heaven and why
                },
                "context": "Opening question about afterlife beliefs - if reincarnation, go straight to Q2"
            },
            
            "1a": {
                "question": "Do you think you will go to heaven and why?",
                "suggestions": ["Yes", "No", "Because Jesus died for my sins", "Because I'm a good person", "Because I ask for forgiveness"],
                "next_questions": {
                    "Because Jesus died for my sins": "1b",  # Ask about deserving heaven/hell
                    "Yes": "1b",  # Ask about deserving heaven/hell
                    "No": "2",  # Go to God belief question first, then building analogy
                    "Because I'm a good person": "2",
                    "Because I ask for forgiveness": "2"
                },
                "context": "Follow-up to heaven belief - determines flow direction"
            },
            
            "1b": {
                "question": "Based on how you've lived your life, do you deserve to go to Heaven or Hell after you die?",
                "suggestions": ["Heaven", "Hell"],
                "next_questions": {
                    "Heaven": "4",  # Skip to Q4
                    "Hell": "17"   # Skip to Q17
                },
                "context": "Determines if they understand their sinfulness"
            },
            
            "2": {
                "question": "Do you believe there's a God?",
                "suggestions": ["Yes", "No"],
                "next_questions": {
                    "Yes": "3",
                    "No": "2b"  # If they don't believe, go to building analogy
                },
                "context": "Establishes belief in God - if no, use building analogy"
            },
            
            "2b": {
                "question": "Would you agree that the building I'm sitting in had a builder, or did it just appear by itself? This building is evidence that it needed a builder. In the same way, when we look at the universe we know it had a beginning therefore it had to have a creator for it. The universe is proof of a universe maker. Buildings need builders, creation needs a creator agree?",
                "suggestions": ["Yes", "No", "I agree", "I don't agree"],
                "next_questions": {
                    "Yes": "3",
                    "I agree": "3",
                    "No": "2c",  # If they still don't believe, try one more time
                    "I don't agree": "2c"
                },
                "context": "Uses building analogy to establish belief in a creator"
            },
            
            "2c": {
                "question": "I respect your choice, but I want you to know the good news: God offers forgiveness through Jesus Christ so you can avoid eternal punishment and have everlasting life. If you ever want to explore further, here are some links you can check out later: [Insert your social/media links]",
                "suggestions": ["I understand", "I'll think about it", "I still don't believe", "Thank you", "I'll check those out"],
                "next_questions": {
                    "I understand": "3",  # Continue with the conversation
                    "I'll think about it": "3",  # Continue with the conversation
                    "Thank you": "2d",  # End conversation
                    "I'll check those out": "2d",  # End conversation
                    "I still don't believe": "2d"  # End conversation
                },
                "context": "Shares good news and social links when they remain resistant"
            },
            
            "2d": {
                "question": "Since you don't want to take the chat seriously, I wish you well and here are our social links for when you're ready for a serious chat.",
                "suggestions": ["Start over"],
                "next_questions": {"Start over": "start"},
                "context": "Ends conversation due to unbelief"
            },
            
            "3": {
                "question": "Since we know there is a God, it matters how we live. So, do you think you are a good person?",
                "suggestions": ["Yes", "No"],
                "next_questions": {
                    "Yes": "4",
                    "No": "3b"  # If they say no, thank them and explain
                },
                "context": "Establishes if they think they're good - if no, thank them and explain"
            },
            
            "3b": {
                "question": "Thank you for your honesty and explain how we have all done things wrong - give examples: lying, taking things we shouldn't have, being angry, using bad language. Then move to question 7.",
                "suggestions": ["I understand", "You're right"],
                "next_questions": {
                    "I understand": "7",
                    "You're right": "7"
                },
                "context": "Thanks them for honesty and explains universal sinfulness"
            },
            
            "4": {
                "question": "Have you ever told a lie?",
                "suggestions": ["Yes", "No"],
                "next_questions": {
                    "Yes": "5",  # Go to Q5 (bad language) first
                    "No": "4b"  # If they say no, challenge them
                },
                "context": "First sin question - need YES to proceed"
            },
            
            "4b": {
                "question": "You could say that you're telling me a lie right now as everybody alive has lied.",
                "suggestions": ["Yes", "You're right", "I have lied"],
                "next_questions": {
                    "Yes": "5",  # Go to Q5 (bad language) first
                    "You're right": "5",
                    "I have lied": "5"
                },
                "context": "Challenges denial of lying"
            },
            
            "5": {
                "question": "Have you ever used bad language?",
                "suggestions": ["Yes", "No"],
                "next_questions": {
                    "Yes": "6",  # Go to Q6 (anger/disrespect) first
                    "No": "6"  # If no, try next question
                },
                "context": "Second sin question - need YES to proceed"
            },
            
            "6": {
                "question": "Have you ever been angry or disrespected someone?",
                "suggestions": ["Yes", "No"],
                "next_questions": {
                    "Yes": "7",  # Now go to Q7 "We've all done these things"
                    "No": "6b"  # If still no, challenge them
                },
                "context": "Third sin question - need YES to proceed"
            },
            
            "6b": {
                "question": "Have you ever sinned against God?",
                "suggestions": ["Yes", "No"],
                "next_questions": {
                    "Yes": "7",
                    "No": "6c"  # If still no, use Romans 3:23
                },
                "context": "Direct question about sinning against God"
            },
            
            "6c": {
                "question": "Romans 3:23 tells us – for all have sinned and fall short of the Glory of God. Would you agree you're a sinner before God?",
                "suggestions": ["Yes", "No"],
                "next_questions": {
                    "Yes": "7",
                    "No": "6d"  # If still no, call out pride
                },
                "context": "Uses scripture to establish sinfulness"
            },
            
            "6d": {
                "question": "You have just committed the sin of pride. See if that humbles them, if not since they don't want to take the chat seriously, wish them well and send socials for them to contact us when they're ready for a serious chat.",
                "suggestions": ["I understand", "You're right", "I have sinned"],
                "next_questions": {
                    "I understand": "7",
                    "You're right": "7", 
                    "I have sinned": "7",
                    "Start over": "start"
                },
                "context": "Calls out pride and gives final chance"
            },
            
            "7": {
                "question": "We've all done these things and so if God was to judge you based on these things would you be innocent or guilty?",
                "suggestions": ["Guilty", "Innocent", "But I make sure to ask for forgiveness", "But God is forgiving", "But I am trying to do better"],
                "next_questions": {
                    "Guilty": "8",
                    "Innocent": "7b",  # If innocent, challenge them
                    "But I make sure to ask for forgiveness": "7c",  # Challenge with courtroom analogy
                    "But God is forgiving": "7c",  # Challenge with courtroom analogy
                    "But I am trying to do better": "7c"  # Challenge with courtroom analogy
                },
                "context": "Establishes guilt before God"
            },
            
            "7b": {
                "question": "Innocent means you've never done anything wrong your whole life, and guilty means you've done at least one bad thing - so which one would you be?",
                "suggestions": ["Guilty", "Innocent"],
                "next_questions": {
                    "Guilty": "8",
                    "Innocent": "7b"  # Keep asking until they admit guilt
                },
                "context": "Challenges claim of innocence"
            },
            
            "7c": {
                "question": "But we are still guilty of what we have done wrong and so we need someone else to take the punishment for us.",
                "suggestions": ["I understand", "You're right"],
                "next_questions": {
                    "I understand": "8",
                    "You're right": "8"
                },
                "context": "Uses courtroom analogy to show we're still guilty despite trying to do better"
            },
            
            "8": {
                "question": "So would we deserve a reward or punishment?",
                "suggestions": ["Punishment", "Reward"],
                "next_questions": {
                    "Punishment": "9",
                    "Reward": "8b"  # If reward, challenge them
                },
                "context": "Establishes we deserve punishment"
            },
            
            "8b": {
                "question": "Would a policeman give me a bunch of flowers for speeding OR a penalty notice? What country would give flowers for speeding?",
                "suggestions": ["Punishment", "Penalty notice"],
                "next_questions": {
                    "Punishment": "9",
                    "Penalty notice": "9"
                },
                "context": "Uses speeding analogy to establish punishment"
            },
            
            "9": {
                "question": "Does that sound like a place in Heaven or Hell?",
                "suggestions": ["Hell", "Heaven"],
                "next_questions": {
                    "Hell": "10",
                    "Heaven": "9b"  # If heaven, challenge them
                },
                "context": "Establishes we deserve hell"
            },
            
            "9b": {
                "question": "Does heaven sound like punishment or would it be hell? Would a Judge send a criminal to Disneyland or Prison?",
                "suggestions": ["Hell", "Prison"],
                "next_questions": {
                    "Hell": "10",
                    "Prison": "10"
                },
                "context": "Uses judge analogy to establish hell as punishment"
            },
            
            "10": {
                "question": "So how do you think you could avoid your Hell punishment?",
                "suggestions": ["Not sure", "Do good things", "Ask for forgiveness", "Pray", "Repent"],
                "next_questions": {
                    "Not sure": "11",
                    "Do good things": "10b",  # Challenge with crimes analogy
                    "Ask for forgiveness": "10c",  # Challenge with judge analogy
                    "Pray": "10c",  # Challenge with judge analogy
                    "Repent": "10d"  # Ask what they mean by repent
                },
                "context": "Explores how to avoid hell punishment"
            },
            
            "10b": {
                "question": "Imagine if you did 5 serious crimes today and then tomorrow you did no more crimes and instead did 10 good things, would the police ignore your crimes? Right, same with God. Stopping sin and doing good doesn't take away the sins we have done, we still deserve the punishment which is hell.",
                "suggestions": ["I understand", "You're right"],
                "next_questions": {
                    "I understand": "11",
                    "You're right": "11"
                },
                "context": "Uses crimes analogy to show good works don't remove guilt"
            },
            
            "10c": {
                "question": "Imagine you break a serious law in society and standing before the judge you ask for forgiveness. Will the judge let you go free? Right, same with God. Asking for forgiveness doesn't take away the punishment for breaking God's laws. Good to do but doesn't pay our hell fine.",
                "suggestions": ["I understand", "You're right"],
                "next_questions": {
                    "I understand": "11",
                    "You're right": "11"
                },
                "context": "Uses judge analogy to show asking forgiveness doesn't remove punishment"
            },
            
            "10d": {
                "question": "What do you mean by repent?",
                "suggestions": ["Ask for forgiveness", "Change of mind", "Turn from sin"],
                "next_questions": {
                    "Ask for forgiveness": "10c",  # Use judge analogy
                    "Change of mind": "10e",  # Explain true repentance
                    "Turn from sin": "10e"  # Explain true repentance
                },
                "context": "Clarifies what repentance means"
            },
            
            "10e": {
                "question": "Repentance is a change of mind to trusting in Christ instead of NOT trusting in Christ. Asking for forgiveness and turning from sin is the 'result' of repentance, not repentance itself.",
                "suggestions": ["I understand", "That makes sense"],
                "next_questions": {
                    "I understand": "11",
                    "That makes sense": "11"
                },
                "context": "Explains true repentance as change of mind to trust Christ"
            },
            
            "11": {
                "question": "What we need is someone else who would take the punishment for us. If someone took 100% of your Hell punishment, how much would be left for you to take?",
                "suggestions": ["Nothing", "Zero", "0%", "None", "I'm not sure"],
                "next_questions": {
                    "Nothing": "12",
                    "Zero": "12",
                    "0%": "12",
                    "None": "12",
                    "I'm not sure": "11b"  # Use fingers analogy
                },
                "context": "Introduces concept of substitutionary atonement"
            },
            
            "11b": {
                "question": "If someone chops off all of your fingers, do you have any left? So if someone took 100% of your Hell punishment, how much would be left for you to take?",
                "suggestions": ["Nothing", "Zero", "None"],
                "next_questions": {
                    "Nothing": "12",
                    "Zero": "12",
                    "None": "12"
                },
                "context": "Uses fingers analogy to clarify 100% substitution"
            },
            
            "12": {
                "question": "So if you have no more Hell punishment, where will you go when you die?",
                "suggestions": ["Heaven", "Hell"],
                "next_questions": {
                    "Heaven": "13",
                    "Hell": "12b"  # If they still say hell, challenge them
                },
                "context": "Establishes heaven as destination if punishment is paid"
            },
            
            "12b": {
                "question": "How is our Hell punishment paid for? (By having someone take it for us) Think of it like this: If you had a $1000 speeding fine and someone pays all $1000 for you as a gift. How much is left for you to pay? In the same way, we deserve hell that is our fine (punishment) for our sins, but if Jesus pays 100% of our hell fine there would none left, so where would you get to go? And why?",
                "suggestions": ["Heaven", "Because Jesus paid for my sins"],
                "next_questions": {
                    "Heaven": "13",
                    "Because Jesus paid for my sins": "13"
                },
                "context": "Uses speeding fine analogy to clarify substitutionary atonement"
            },
            
            "13": {
                "question": "That was Jesus, that's why he died on the cross, to take the punishment for our sins and he rose from the dead 3 days later.",
                "suggestions": ["I understand", "That makes sense"],
                "next_questions": {
                    "I understand": "14",
                    "That makes sense": "14"
                },
                "context": "Introduces Jesus as the one who paid for our sins"
            },
            
            "14": {
                "question": "So if Jesus does that for you, where do you go when you die?",
                "suggestions": ["Heaven", "Hell"],
                "next_questions": {
                    "Heaven": "15",
                    "Hell": "14b"  # If they still say hell, challenge them
                },
                "context": "Confirms heaven as destination through Jesus"
            },
            
            "14b": {
                "question": "If Jesus takes ALL of your hell punishment, then how much is left for you to get in hell? None. So if Jesus does that for you, where do you go when you die?",
                "suggestions": ["Heaven", "Because Jesus paid for my sins"],
                "next_questions": {
                    "Heaven": "15",
                    "Because Jesus paid for my sins": "15"
                },
                "context": "Reinforces that Jesus paid for all punishment"
            },
            
            "15": {
                "question": "So why would God let you into heaven?",
                "suggestions": ["Because Jesus paid for my sins", "Because of my good works", "Because I ask for forgiveness"],
                "next_questions": {
                    "Because Jesus paid for my sins": "16",
                    "Because of my good works": "10",  # Go back to Q10
                    "Because I ask for forgiveness": "10"  # Go back to Q10
                },
                "context": "Establishes Jesus as the only reason for heaven"
            },
            
            "16": {
                "question": "Now he offers this to us as a free gift and all I have to do to receive this free gift is to simply trust that Jesus died on the cross paying for 100% of our Hell punishment.",
                "suggestions": ["I understand", "That makes sense"],
                "next_questions": {
                    "I understand": "17",
                    "That makes sense": "17"
                },
                "context": "Introduces faith as the means of receiving the gift"
            },
            
            "17": {
                "question": "So if you trust that Jesus has paid for all of your sins now and tomorrow you sin 5 more times and then die, would you go to Heaven or Hell?",
                "suggestions": ["Heaven", "Hell"],
                "next_questions": {
                    "Heaven": "18",
                    "Hell": "17b"  # If they say hell, challenge them
                },
                "context": "Tests understanding of complete atonement"
            },
            
            "17b": {
                "question": "What was getting you into heaven again? Jesus. And does Jesus pay for just your past sins or also your future sins?",
                "suggestions": ["Future", "Past only", "All sins", "Past, present and future"],
                "next_questions": {
                    "Future": "17",
                    "All sins": "17",
                    "Past, present and future": "17",
                    "Past only": "17c"  # Challenge them about past only
                },
                "context": "Clarifies that Jesus paid for all sins including future ones"
            },
            
            "17c": {
                "question": "If Jesus died for 100% of your sins, that would have to include your future sins right?",
                "suggestions": ["Yes", "I understand"],
                "next_questions": {
                    "Yes": "17",
                    "I understand": "17"
                },
                "context": "Challenges the idea that Jesus only paid for past sins"
            },
            
            "18": {
                "question": "and why heaven?",
                "suggestions": ["Because Jesus paid for my sins", "Because of my good works", "Because I ask for forgiveness"],
                "next_questions": {
                    "Because Jesus paid for my sins": "19",
                    "Because of my good works": "10",  # Go back to Q10
                    "Because I ask for forgiveness": "10"  # Go back to Q10
                },
                "context": "Reinforces Jesus as the only reason for heaven"
            },
            
            "19": {
                "question": "But if you don't trust Jesus paid for your sins, where would you end up?",
                "suggestions": ["Hell", "Heaven"],
                "next_questions": {
                    "Hell": "20",
                    "Heaven": "19b"  # If they say heaven, challenge them
                },
                "context": "Establishes hell as destination without faith in Jesus"
            },
            
            "19b": {
                "question": "If I offered you a gift today, but you didn't accept it from me, have you actually received that gift? In the same way, Jesus is offering to pay for our sins as a gift but if we don't accept it, we won't receive it and so where would we end up?",
                "suggestions": ["No", "Hell"],
                "next_questions": {
                    "No": "20",
                    "Hell": "20"
                },
                "context": "Uses gift analogy to show need to accept Jesus' gift"
            },
            
            "20": {
                "question": "and since you don't want to go to Hell, WHEN should you start trusting that Jesus has paid for your sins?",
                "suggestions": ["Now", "Before I die", "Today"],
                "next_questions": {
                    "Now": "21",
                    "Before I die": "20b",  # Challenge them about knowing when they'll die
                    "Today": "21"
                },
                "context": "Urges immediate decision for Jesus"
            },
            
            "20b": {
                "question": "Do you know when you will die? If not, when should you start trusting that Jesus paid for your sins?",
                "suggestions": ["No", "Now", "Today"],
                "next_questions": {
                    "No": "21",
                    "Now": "21",
                    "Today": "21"
                },
                "context": "Emphasizes urgency of decision"
            },
            
            "21": {
                "question": "So if you stood before God right now and he asked you 'Why should I let you into Heaven?' what would you say?",
                "suggestions": ["Because Jesus paid for my sins", "I don't know", "I accept Jesus", "I believe in Jesus", "Both"],
                "next_questions": {
                    "Because Jesus paid for my sins": "22",
                    "I don't know": "21b",  # Challenge them
                    "I accept Jesus": "21c",  # Challenge about first person
                    "I believe in Jesus": "21c",  # Challenge about first person
                    "Both": "21d"  # Challenge about mixing reasons
                },
                "context": "Tests their understanding of salvation"
            },
            
            "21b": {
                "question": "What was the reason you could go to heaven again?",
                "suggestions": ["Because Jesus paid for my sins"],
                "next_questions": {
                    "Because Jesus paid for my sins": "21"
                },
                "context": "Reminds them of the correct answer"
            },
            
            "21c": {
                "question": "Now do we go to heaven because of what WE have done for God, or because of what HE has done for us? (He has done) Right, and so if our answer to God starts in the first person 'I' we are about to point to what WE have done for God rather than what Jesus has done for us in dying for our sins. Make sense? So How would you re-answer the question..",
                "suggestions": ["Because Jesus paid for my sins", "I understand"],
                "next_questions": {
                    "Because Jesus paid for my sins": "22",
                    "I understand": "21c"  # Keep asking until they get it right
                },
                "context": "Corrects first person language to third person"
            },
            
            "21d": {
                "question": "If Jesus takes 100% of our hell punishment, we get to go to heaven. So are you going to heaven because of YOU or because of HIM? (Him) Our answer shouldn't start with 'Because I', but in the third person 'Because Jesus...'. So how would you re-word your answer to God's question as to why he should let you into heaven?",
                "suggestions": ["Because Jesus paid for my sins", "I understand"],
                "next_questions": {
                    "Because Jesus paid for my sins": "22",
                    "I understand": "21d"  # Keep asking until they get it right
                },
                "context": "Corrects mixed reasons to Jesus only"
            },
            
            "22": {
                "question": "Now, imagine a friend of yours says they are going to heaven because they are a good person, where would they go when they die?",
                "suggestions": ["Hell", "Heaven"],
                "next_questions": {
                    "Hell": "23",
                    "Heaven": "22b"  # Challenge them
                },
                "context": "Tests understanding that good works don't save"
            },
            
            "22b": {
                "question": "What's the reason why God would let someone into heaven? Jesus. So then is your friend trusting in Jesus to get them to heaven, or their own actions? Right, and because they are trusting in their own actions where would they end up? That's right, and why?",
                "suggestions": ["Hell", "Because they're trusting in their own actions"],
                "next_questions": {
                    "Hell": "23",
                    "Because they're trusting in their own actions": "23"
                },
                "context": "Uses friend analogy to show works don't save"
            },
            
            "23": {
                "question": "But another friend comes to you and says 'I'm going to heaven because of two reasons. The first reason is because Jesus died for my sins and the second reason is because I've been a good person.' Would that person go to Heaven or Hell?",
                "suggestions": ["Hell", "Heaven"],
                "next_questions": {
                    "Hell": "24",
                    "Heaven": "23b"  # Challenge them
                },
                "context": "Tests understanding that partial faith doesn't save"
            },
            
            "23b": {
                "question": "By trusting in two things they aren't trusting 100% in Jesus to save them. It would be 50% Jesus and 50% their actions. So if Jesus only contributes 50%, where do they end up? Again, we have to trust that Jesus is the ONLY reason we are saved, not our actions.",
                "suggestions": ["Hell", "I understand"],
                "next_questions": {
                    "Hell": "24",
                    "I understand": "24"
                },
                "context": "Explains that partial faith doesn't save"
            },
            
            "24": {
                "question": "So, on a scale of 0-100%, how sure are you that you will go to Heaven when you die?",
                "suggestions": ["100%", "Less than 100%", "Not sure", "50%", "75%", "90%"],
                "next_questions": {
                    "100%": "25",
                    "Less than 100%": "24b",  # Challenge them
                    "Not sure": "24b",  # Challenge them
                    "50%": "24b",  # Challenge them
                    "75%": "24b",  # Challenge them
                    "90%": "24b"  # Challenge them
                },
                "context": "Tests confidence in salvation"
            },
            
            "24b": {
                "question": "What was the reason you would go to heaven again? Jesus. Right, and how much of your punishment did Jesus take for you? So how much punishment is then left for you to still get in hell? None. So if you trust in that, on a scale of 0-100%, how sure could you be that you will go to Heaven?",
                "suggestions": ["100%", "I understand", "Less than 100%"],
                "next_questions": {
                    "100%": "25",
                    "I understand": "25",
                    "Less than 100%": "24c"  # Ask what makes them unsure
                },
                "context": "Reinforces 100% confidence through Jesus"
            },
            
            "24c": {
                "question": "What makes you less than 100% sure? Reminding them that Jesus paid for past, present and future sins.",
                "suggestions": ["I understand", "You're right", "100%"],
                "next_questions": {
                    "I understand": "25",
                    "You're right": "25",
                    "100%": "25"
                },
                "context": "Addresses specific doubts about salvation"
            },
            
            "25": {
                "question": "So, does doing good things play any part in getting you to heaven?",
                "suggestions": ["No", "Yes"],
                "next_questions": {
                    "No": "26",
                    "Yes": "25b"  # Challenge them
                },
                "context": "Tests understanding that works don't save"
            },
            
            "25b": {
                "question": "Is it our good deeds/things that saves us or Jesus dying on the cross?",
                "suggestions": ["Jesus dying on the cross", "Our good deeds"],
                "next_questions": {
                    "Jesus dying on the cross": "26",
                    "Our good deeds": "10"  # Go back to Q10
                },
                "context": "Clarifies that Jesus saves, not works"
            },
            
            "26": {
                "question": "Do you need to ask for forgiveness to go to Heaven?",
                "suggestions": ["No", "Yes"],
                "next_questions": {
                    "No": "27",
                    "Yes": "26b"  # Challenge them
                },
                "context": "Tests understanding that asking forgiveness doesn't save"
            },
            
            "26b": {
                "question": "Is it our asking for forgiveness that saves us or Jesus dying on the cross?",
                "suggestions": ["Jesus dying on the cross", "Asking for forgiveness"],
                "next_questions": {
                    "Jesus dying on the cross": "27",
                    "Asking for forgiveness": "10"  # Go back to Q10
                },
                "context": "Clarifies that Jesus saves, not asking forgiveness"
            },
            
            "27": {
                "question": "Do you need to be baptized to go to Heaven?",
                "suggestions": ["No", "Yes"],
                "next_questions": {
                    "No": "28",
                    "Yes": "27b"  # Challenge them
                },
                "context": "Tests understanding that baptism doesn't save"
            },
            
            "27b": {
                "question": "Is it our baptism that saves us or Jesus dying on the cross?",
                "suggestions": ["Jesus dying on the cross", "Baptism"],
                "next_questions": {
                    "Jesus dying on the cross": "28",
                    "Baptism": "10"  # Go back to Q10
                },
                "context": "Clarifies that Jesus saves, not baptism"
            },
            
            "28": {
                "question": "So if these things don't get us to Heaven, why do we do good things?",
                "suggestions": ["Because we are thankful", "I don't know"],
                "next_questions": {
                    "Because we are thankful": "28b",
                    "I don't know": "28c"  # Use fireman analogy
                },
                "context": "Explains motivation for good works"
            },
            
            "28b": {
                "question": "And because we are thankful to Jesus for what he has done for us, that motivates us now to live our lives for him and avoid sinning. Does that make sense? We don't stop our sins and do good things for Jesus to save us, we do good things for him and desire to live better because he HAS saved us. Make sense?",
                "suggestions": ["Yes", "I understand"],
                "next_questions": {
                    "Yes": "29",
                    "I understand": "29"
                },
                "context": "Explains that good works are result of salvation, not cause"
            },
            
            "28c": {
                "question": "If you are in a burning building and a fireman risks his life to bring you out to safety, what would you want to do for that fireman who saved you? Yeah, and you definitely don't want to punch him in the face, right? Same with Jesus, if He has laid his life down to save you from hell, what would you want to do for Jesus? If you're unconscious in the fire, you're relying on the fireman to do all the work as you can't help him at all because you're unconscious, Same for Jesus, we are dead in our sins and can't assist Jesus in saving us from the eternal Hell fire, He does all the work by dying on the cross for our sins, make sense?",
                "suggestions": ["Yes", "I understand", "Thank him", "Help him"],
                "next_questions": {
                    "Yes": "29",
                    "I understand": "29",
                    "Thank him": "29",
                    "Help him": "29"
                },
                "context": "Uses fireman analogy to explain motivation for good works"
            },
            
            "29": {
                "question": "Do you know how you can find out more about Jesus?",
                "suggestions": ["The Bible", "Church", "I don't know"],
                "next_questions": {
                    "The Bible": "30",
                    "Church": "30",
                    "I don't know": "29b"  # Tell them about the Bible
                },
                "context": "Points to Bible as source of knowledge about Jesus"
            },
            
            "29b": {
                "question": "The Bible is God's word and tells us all about Jesus and how to live for him.",
                "suggestions": ["I understand", "That makes sense"],
                "next_questions": {
                    "I understand": "30",
                    "That makes sense": "30"
                },
                "context": "Introduces the Bible as God's word"
            },
            
            "30": {
                "question": "Yep! Do you have a bible and do you read it much?",
                "suggestions": ["Yes", "No", "Sometimes"],
                "next_questions": {
                    "Yes": "31",
                    "No": "30b",  # Offer to share a link
                    "Sometimes": "31"
                },
                "context": "Asks about Bible reading habits"
            },
            
            "30b": {
                "question": "I can share a link with you to get one.",
                "suggestions": ["Thank you", "That would be helpful"],
                "next_questions": {
                    "Thank you": "31",
                    "That would be helpful": "31"
                },
                "context": "Offers to help get a Bible"
            },
            
            "31": {
                "question": "Think of it like this, If you ate food only once a week, would you be very strong? Right. We eat food everyday to stay strong physically. Our bible is like our spiritual food.",
                "suggestions": ["No", "I understand", "Yes"],
                "next_questions": {
                    "No": "32",
                    "I understand": "32",
                    "Yes": "32"
                },
                "context": "Uses food analogy to explain need for regular Bible reading"
            },
            
            "32": {
                "question": "So if the bible is our spiritual food, how often do you think you should read the bible then to be strong spiritually?",
                "suggestions": ["Everyday", "Daily", "Every day", "Yes"],
                "next_questions": {
                    "Everyday": "34",  # Skip Q33 as it's missing from script
                    "Daily": "34",
                    "Every day": "34",
                    "Yes": "34"
                },
                "context": "Encourages daily Bible reading"
            },
            
            "34": {
                "question": "Do you go to church?... what kind of church is it?",
                "suggestions": ["Yes", "No"],
                "next_questions": {
                    "Yes": "35",
                    "No": "34b"  # Explain importance of church
                },
                "context": "Asks about church attendance"
            },
            
            "34b": {
                "question": "Church is where you'll be able to hear God's word being preached and where you'll meet other Christians who can help you in your faith. Does that sound good? Here's a link you can use to find a great church in your area.",
                "suggestions": ["Yes", "That sounds good"],
                "next_questions": {
                    "Yes": "35",
                    "That sounds good": "35"
                },
                "context": "Explains importance of church and offers help finding one"
            },
            
            "35": {
                "question": "Do they teach the same message we've spoken about here to be saved from our sins?",
                "suggestions": ["Yes", "No", "Not really"],
                "next_questions": {
                    "Yes": "36",
                    "No": "35b",  # Warn about wrong teaching
                    "Not really": "35b"  # Warn about wrong teaching
                },
                "context": "Tests if their church teaches correct gospel"
            },
            
            "35b": {
                "question": "So do you think it's a good idea to keep attending a church that teaches the wrong way to heaven? Spend time in personal prayer and reading the Bible to strengthen your faith on your own. Think about who you could share the gospel with at your church, because you want them to be saved. Make sure to check anything you are hearing at church, with the Bible. Don't be bowing down to any statues/pictures or praying to anyone other than God. Listen in to some good preachers online, such as Alistair Begg (search his name on YouTube).",
                "suggestions": ["I understand", "That makes sense"],
                "next_questions": {
                    "I understand": "36",
                    "That makes sense": "36"
                },
                "context": "Warns about false teaching and gives guidance"
            },
            
            "36": {
                "question": "Also, think of your family and friends, if you asked them, 'What's the reason you'll go to heaven?' what would their answer be?",
                "suggestions": ["I'm not sure", "Because Jesus died for my sins", "Because they're good people", "Because they ask for forgiveness"],
                "next_questions": {
                    "I'm not sure": "37",
                    "Because Jesus died for my sins": "37",
                    "Because they're good people": "36b",  # Challenge them
                    "Because they ask for forgiveness": "36b"  # Challenge them
                },
                "context": "Tests understanding of others' salvation"
            },
            
            "36b": {
                "question": "So where would they end up? (Hell) Because they're trusting in their own actions instead of Jesus.",
                "suggestions": ["Hell", "I understand"],
                "next_questions": {
                    "Hell": "37",
                    "I understand": "37"
                },
                "context": "Explains that trusting in works leads to hell"
            },
            
            "37": {
                "question": "And since you don't want them to go to hell, how could you help them not to end up there?",
                "suggestions": ["Tell them about the Gospel", "Share the good news", "I don't know"],
                "next_questions": {
                    "Tell them about the Gospel": "38",
                    "Share the good news": "38",
                    "I don't know": "37b"  # Explain how to help
                },
                "context": "Encourages sharing the gospel with others"
            },
            
            "37b": {
                "question": "You can share the same message we've talked about today - that Jesus died for their sins and they need to trust in him to be saved.",
                "suggestions": ["I understand", "That makes sense"],
                "next_questions": {
                    "I understand": "38",
                    "That makes sense": "38"
                },
                "context": "Explains how to share the gospel"
            },
            
            "38": {
                "question": "So let me ask you, What if God asked you this 'Why should I not send you to hell for all the sins you've done', how would you answer?",
                "suggestions": ["Because Jesus paid for my sins", "I don't know"],
                "next_questions": {
                    "Because Jesus paid for my sins": "39",
                    "I don't know": "38b"  # Remind them of the answer
                },
                "context": "Tests their understanding of salvation"
            },
            
            "38b": {
                "question": "What was the reason you could go to heaven again?",
                "suggestions": ["Because Jesus paid for my sins"],
                "next_questions": {
                    "Because Jesus paid for my sins": "39"
                },
                "context": "Reminds them of the correct answer"
            },
            
            "39": {
                "question": "Now, remember at the beginning of this chat, what DID you think was getting you to heaven?",
                "suggestions": ["Doing good", "Asking for forgiveness", "Being a good person", "Because Jesus died for my sins"],
                "next_questions": {
                    "Doing good": "39b",
                    "Asking for forgiveness": "39b",
                    "Being a good person": "39b",
                    "Because Jesus died for my sins": "39c"  # Challenge them
                },
                "context": "Reflects on their original understanding"
            },
            
            "39b": {
                "question": "So, since you were trusting in yourself to get you to heaven, if you had died before this chat, where would you have ended up?",
                "suggestions": ["Hell", "Heaven"],
                "next_questions": {
                    "Hell": "39d",
                    "Heaven": "39e"  # Challenge them
                },
                "context": "Shows consequences of trusting in works"
            },
            
            "39c": {
                "question": "You may need to remind me at the start you weren't pointing to their actions (if they were) and ask them to remind me of why we get to heaven again.",
                "suggestions": ["Because Jesus paid for my sins"],
                "next_questions": {
                    "Because Jesus paid for my sins": "39d"
                },
                "context": "Clarifies their original understanding"
            },
            
            "39d": {
                "question": "But if you died right now, where will you end up?",
                "suggestions": ["Heaven", "Hell"],
                "next_questions": {
                    "Heaven": "complete",
                    "Hell": "39f"  # Challenge them
                },
                "context": "Confirms their current destination"
            },
            
            "39e": {
                "question": "But what should we be trusting in as the ONLY reason we go to heaven? So, you weren't trusting in Jesus but in your own actions and by trusting in your own actions where would you have gone?",
                "suggestions": ["Jesus", "Hell"],
                "next_questions": {
                    "Jesus": "39d",
                    "Hell": "39d"
                },
                "context": "Corrects their understanding"
            },
            
            "39f": {
                "question": "Why do you still think hell? What are you still trusting in to get you to heaven?",
                "suggestions": ["Because Jesus paid for my sins", "I'm not sure"],
                "next_questions": {
                    "Because Jesus paid for my sins": "complete",
                    "I'm not sure": "complete"
                },
                "context": "Addresses remaining doubts"
            },
            
            "complete": {
                "question": "So awesome you understand all this, if you'd like to see some more awesome stuff, check us out on the social media platforms: needgod.net (press Socials button) Do you have any other questions I can help you with? This has been a fantastic chat! My name is …… been great chatting with you.",
                "suggestions": ["Start over"],
                "next_questions": {"Start over": "start"},
                "context": "Conversation completed"
            }
        }
    
    def get_current_question(self) -> Optional[Dict]:
        """Get the current question."""
        return self.questions.get(self.current_question_id)
    
    def submit_answer(self, answer: str) -> bool:
        """Submit an answer and move to the next question."""
        current_q = self.get_current_question()
        if not current_q:
            return False
        
        # Check if answer is valid
        if answer in current_q["next_questions"]:
            next_q = current_q["next_questions"][answer]
            self.current_question_id = next_q
            self.conversation_history.append({
                "question": current_q["question"],
                "answer": answer,
                "next_question": next_q
            })
            return True
        
        # Try to find a close match
        for suggestion in current_q["suggestions"]:
            if answer.lower() in suggestion.lower() or suggestion.lower() in answer.lower():
                next_q = current_q["next_questions"][suggestion]
                self.current_question_id = next_q
                self.conversation_history.append({
                    "question": current_q["question"],
                    "answer": answer,
                    "next_question": next_q
                })
                return True
        
        return False
    
    def reset_to_beginning(self):
        """Reset the conversation to the beginning."""
        self.current_question_id = "start"
        self.conversation_history = []

def main():
    st.set_page_config(page_title="Script Analyzer", layout="wide")
    
    st.title("📋 Interactive Script Questionnaire")
    st.markdown("**Correct Interactive PDF Script Questionnaire Application**")
    
    # Initialize the analyzer
    if 'analyzer' not in st.session_state:
        st.session_state.analyzer = CompleteScriptAnalyzer('script.pdf')
        st.session_state.analyzer.parse_script()
    
    analyzer = st.session_state.analyzer
    
    # Display current question
    current_q = analyzer.get_current_question()
    
    if current_q:
        st.subheader(f"Question {analyzer.current_question_id}")
        st.write(current_q["question"])
        
        if current_q["context"]:
            st.info(f"💡 Context: {current_q['context']}")
        
        # Display suggestions as clickable buttons
        st.write("**Click an answer below or type your own:**")
        
        # Create columns for suggestion buttons
        cols = st.columns(2)
        
        for i, suggestion in enumerate(current_q["suggestions"]):
            col_idx = i % 2
            with cols[col_idx]:
                if st.button(suggestion, key=f"suggestion_{analyzer.current_question_id}_{i}", use_container_width=True):
                    if analyzer.submit_answer(suggestion):
                        st.success("✅ Answer accepted!")
                        st.rerun()
                    else:
                        st.error("❌ Answer not recognized. Please try again.")
        
        # Answer input as fallback
        answer = st.text_input("Or type your answer:", key=f"answer_{analyzer.current_question_id}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Submit Answer", type="primary"):
                if answer:
                    if analyzer.submit_answer(answer):
                        st.success("✅ Answer accepted!")
                        st.rerun()
                    else:
                        st.error("❌ Answer not recognized. Please try one of the suggested answers.")
                else:
                    st.warning("Please enter an answer.")
        
        with col2:
            if st.button("Reset to Beginning"):
                analyzer.reset_to_beginning()
                st.rerun()
        
        # Display conversation history
        if analyzer.conversation_history:
            st.subheader("📝 Conversation History")
            for i, entry in enumerate(analyzer.conversation_history[-5:], 1):  # Show last 5
                st.write(f"{i}. **Q:** {entry['question'][:100]}...")
                st.write(f"   **A:** {entry['answer']}")
                st.write(f"   **→** Q{entry['next_question']}")
                st.write("---")
    
    else:
        st.error("No question found. Please reset to beginning.")

if __name__ == "__main__":
    main()
