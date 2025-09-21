import random


def generate_test_with_gemini(course_id: int, num_questions: int = 10):
    """
    Mock Gemini integration: Replace this with real API call.
    For now, it returns dummy questions and answers.
    """
    questions = []
    correct_answers = []
    for i in range(num_questions):
        questions.append(f"Question {i + 1} for course {course_id}?")
        correct_answers.append(random.choice(["A", "B", "C", "D"]))

    return questions, correct_answers
