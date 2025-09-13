#!/usr/bin/env python3
"""
Comprehensive test script to test every question and answer path in the complete script analyzer.
"""

from script_analyzer_complete import CompleteScriptAnalyzer

def test_every_question():
    """Test every question and all possible answer paths."""
    
    analyzer = CompleteScriptAnalyzer('script.pdf')
    analyzer.parse_script()
    
    print("🧪 COMPREHENSIVE SCRIPT ANALYZER TEST")
    print("=" * 50)
    
    # Test 1: Non-believer flow with building analogy
    print("\n1️⃣ TESTING NON-BELIEVER FLOW WITH BUILDING ANALOGY")
    print("-" * 50)
    analyzer.reset_to_beginning()
    
    # Start -> Q1
    analyzer.submit_answer('Sure')
    print(f"✅ Start -> Q1: {analyzer.current_question_id}")
    
    # Q1 -> Q2
    analyzer.submit_answer('Not sure')
    print(f"✅ Q1 -> Q2: {analyzer.current_question_id}")
    
    # Q2 -> Q2b (building analogy)
    analyzer.submit_answer('No')
    print(f"✅ Q2 -> Q2b (building analogy): {analyzer.current_question_id}")
    
    current_q = analyzer.get_current_question()
    print(f"   Question: {current_q['question'][:80]}...")
    print(f"   Context: {current_q['context']}")
    
    # Test building analogy responses
    print("\n   Testing building analogy responses:")
    for suggestion in current_q['suggestions']:
        analyzer.current_question_id = '2b'
        success = analyzer.submit_answer(suggestion)
        print(f"   {suggestion} -> {'✅' if success else '❌'} -> Q{analyzer.current_question_id}")
    
    # Test 2: Believer flow
    print("\n2️⃣ TESTING BELIEVER FLOW")
    print("-" * 50)
    analyzer.reset_to_beginning()
    analyzer.submit_answer('Sure')
    analyzer.submit_answer('Not sure')
    analyzer.submit_answer('Yes')  # Believe in God
    print(f"✅ Q2 -> Q3: {analyzer.current_question_id}")
    
    # Test 3: Heaven believer flow
    print("\n3️⃣ TESTING HEAVEN BELIEVER FLOW")
    print("-" * 50)
    analyzer.reset_to_beginning()
    analyzer.submit_answer('Sure')
    analyzer.submit_answer('Heaven')  # Say heaven
    print(f"✅ Q1 -> Q1a: {analyzer.current_question_id}")
    
    # Test Q1a responses
    current_q = analyzer.get_current_question()
    print(f"   Question: {current_q['question'][:80]}...")
    print(f"   Testing Q1a responses:")
    for suggestion in current_q['suggestions']:
        analyzer.current_question_id = '1a'
        success = analyzer.submit_answer(suggestion)
        print(f"   {suggestion} -> {'✅' if success else '❌'} -> Q{analyzer.current_question_id}")
    
    # Test 4: Reincarnation flow (should go straight to Q2)
    print("\n4️⃣ TESTING REINCARNATION FLOW")
    print("-" * 50)
    analyzer.reset_to_beginning()
    analyzer.submit_answer('Sure')
    analyzer.submit_answer('Reincarnation')  # Say reincarnation
    print(f"✅ Q1 -> Q2 (reincarnation): {analyzer.current_question_id}")
    
    # Test 5: Test all major question flows
    print("\n5️⃣ TESTING MAJOR QUESTION FLOWS")
    print("-" * 50)
    
    # Test Q3 -> Q7 flow (if they say no to being good)
    analyzer.reset_to_beginning()
    analyzer.submit_answer('Sure')
    analyzer.submit_answer('Not sure')
    analyzer.submit_answer('Yes')  # Believe in God
    analyzer.submit_answer('No')  # Don't think they're good
    print(f"✅ Q3 -> Q3b: {analyzer.current_question_id}")
    
    # Test Q7 courtroom analogy
    analyzer.current_question_id = '7'
    analyzer.submit_answer('But I make sure to ask for forgiveness')
    print(f"✅ Q7 -> Q7c (courtroom analogy): {analyzer.current_question_id}")
    
    # Test Q10 various responses
    analyzer.current_question_id = '10'
    print(f"\n   Testing Q10 responses:")
    for suggestion in ['Do good things', 'Ask for forgiveness', 'Repent']:
        analyzer.current_question_id = '10'
        success = analyzer.submit_answer(suggestion)
        print(f"   {suggestion} -> {'✅' if success else '❌'} -> Q{analyzer.current_question_id}")
    
    # Test Q11 fingers analogy
    analyzer.current_question_id = '11'
    analyzer.submit_answer('I\'m not sure')
    print(f"✅ Q11 -> Q11b (fingers analogy): {analyzer.current_question_id}")
    
    # Test Q17 future sins
    analyzer.current_question_id = '17'
    analyzer.submit_answer('Hell')
    print(f"✅ Q17 -> Q17b (future sins): {analyzer.current_question_id}")
    
    # Test Q21 first person language correction
    analyzer.current_question_id = '21'
    analyzer.submit_answer('I accept Jesus')
    print(f"✅ Q21 -> Q21c (first person correction): {analyzer.current_question_id}")
    
    # Test Q24 confidence levels
    analyzer.current_question_id = '24'
    analyzer.submit_answer('75%')
    print(f"✅ Q24 -> Q24b (confidence challenge): {analyzer.current_question_id}")
    
    # Test Q28 fireman analogy
    analyzer.current_question_id = '28'
    analyzer.submit_answer('I don\'t know')
    print(f"✅ Q28 -> Q28c (fireman analogy): {analyzer.current_question_id}")
    
    # Test Q32 -> Q34 (skip Q33)
    analyzer.current_question_id = '32'
    analyzer.submit_answer('Everyday')
    print(f"✅ Q32 -> Q34 (skip Q33): {analyzer.current_question_id}")
    
    # Test Q35 false teaching warning
    analyzer.current_question_id = '35'
    analyzer.submit_answer('Not really')
    print(f"✅ Q35 -> Q35b (false teaching warning): {analyzer.current_question_id}")
    
    # Test Q36 friend analogies
    analyzer.current_question_id = '36'
    analyzer.submit_answer('Because they\'re good people')
    print(f"✅ Q36 -> Q36b (friend analogy): {analyzer.current_question_id}")
    
    # Test Q39 reflection questions
    analyzer.current_question_id = '39'
    analyzer.submit_answer('Doing good')
    print(f"✅ Q39 -> Q39b (reflection): {analyzer.current_question_id}")
    
    # Test 6: Complete conversation flow
    print("\n6️⃣ TESTING COMPLETE CONVERSATION FLOW")
    print("-" * 50)
    analyzer.reset_to_beginning()
    
    # Complete flow with building analogy - using correct suggestions
    answers = [
        'Sure', 'Not sure', 'No', 'Yes', 'Yes', 'Yes', 'Guilty', 
        'Punishment', 'Hell', 'Not sure', 'Nothing', 'Heaven', 'I understand', 
        'Heaven', 'Because Jesus paid for my sins', 'I understand', 'Heaven', 
        'Because Jesus paid for my sins', 'Hell', 'Now', 'Because Jesus paid for my sins', 
        'Hell', 'Hell', '100%', 'No', 'No', 'No', 'Because we are thankful', 
        'Yes', 'The Bible', 'Yes', 'No', 'Everyday', 'Yes', 'Yes', 'Yes', 
        'I am not sure', 'Tell them about the Gospel', 'Because Jesus paid for my sins', 
        'Doing good', 'Heaven'
    ]
    
    success_count = 0
    for i, answer in enumerate(answers):
        current_q = analyzer.get_current_question()
        if not current_q:
            print(f"❌ No question at step {i+1}")
            break
        
        if not analyzer.submit_answer(answer):
            print(f"❌ Failed at step {i+1}: {answer}")
            break
        
        success_count += 1
        
        if analyzer.current_question_id == 'complete':
            print(f"✅ Complete flow successful! Final question: complete")
            break
    
    print(f"✅ Successfully processed {success_count} answers")
    print(f"✅ Final question: {analyzer.current_question_id}")
    
    # Test 7: Test all question IDs exist
    print("\n7️⃣ TESTING ALL QUESTION IDs EXIST")
    print("-" * 50)
    
    expected_questions = [
        'start', '1', '1a', '1b', '2', '2b', '2c', '2d', '3', '3b', '4', '4b', 
        '5', '6', '6b', '6c', '6d', '7', '7b', '7c', '8', '8b', '9', '9b', 
        '10', '10b', '10c', '10d', '10e', '11', '11b', '12', '12b', '13', 
        '14', '14b', '15', '16', '17', '17b', '17c', '18', '19', '19b', 
        '20', '20b', '21', '21b', '21c', '21d', '22', '22b', '23', '23b', 
        '24', '24b', '24c', '25', '25b', '26', '26b', '27', '27b', '28', 
        '28b', '28c', '29', '29b', '30', '30b', '31', '32', '34', '34b', 
        '35', '35b', '36', '36b', '37', '37b', '38', '38b', '39', '39b', 
        '39c', '39d', '39e', '39f', 'complete'
    ]
    
    missing_questions = []
    for q_id in expected_questions:
        if q_id not in analyzer.questions:
            missing_questions.append(q_id)
    
    if missing_questions:
        print(f"❌ Missing questions: {missing_questions}")
    else:
        print(f"✅ All {len(expected_questions)} expected questions exist")
    
    print(f"\n📊 FINAL STATISTICS")
    print("=" * 50)
    print(f"Total questions in analyzer: {len(analyzer.questions)}")
    print(f"Expected questions: {len(expected_questions)}")
    print(f"Missing questions: {len(missing_questions)}")
    print(f"Complete flow success: {'✅' if analyzer.current_question_id == 'complete' else '❌'}")
    
    return analyzer.current_question_id == 'complete' and len(missing_questions) == 0

if __name__ == "__main__":
    success = test_every_question()
    print(f"\n🎯 OVERALL TEST RESULT: {'✅ PASSED' if success else '❌ FAILED'}")
