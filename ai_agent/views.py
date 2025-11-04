from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Query
from student_registration.students.models import Student
import openai
import os

# Set your OpenAI API key here.
# It's recommended to set the API key in your environment variables.
# For example: openai.api_key = os.environ.get("OPENAI_API_KEY")
openai.api_key = "YOUR_API_KEY"

def get_student_data():
    """
    Retrieves all student data from the database.
    """
    students = Student.objects.all()
    data = []
    for student in students:
        data.append({
            "full_name": student.full_name,
            "age": student.age,
            "nationality": student.nationality_name(),
            "last_enrollment": student.last_enrollment,
        })
    return data

@login_required
def index(request):
    answer = None
    if request.method == 'POST':
        question = request.POST.get('question')
        student_data = get_student_data()

        prompt = f"Question: {question}\n\nStudent Data: {student_data}\n\nAnswer:"

        try:
            client = openai.OpenAI()
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that analyzes student data."},
                    {"role": "user", "content": prompt}
                ]
            )
            answer = response.choices[0].message.content

        except Exception as e:
            answer = f"An error occurred: {e}"

        Query.objects.create(question=question, answer=answer)

    return render(request, 'ai_agent/index.html', {'answer': answer})
