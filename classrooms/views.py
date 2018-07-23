from django.shortcuts import render,HttpResponse
from django.views.generic import CreateView, ListView, UpdateView
from django.contrib.auth import get_user_model
from django.contrib.auth import login
from django.db.models import Count
from django.contrib import messages
from django.db import transaction
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect, render
from django.shortcuts import redirect, render
from django.views.generic import TemplateView

from .models import Student,Quiz,User,TakenQuiz
from .forms import StudentSignUpForm,TeacherSignUpForm,StudentInterestsForm,TakeQuizForm

# Classroom Home Page

class SignUpView(TemplateView):
    template_name = 'registration/signup.html'


def home(request):
    if request.user.is_authenticated:
        if request.user.is_teacher:
            return HttpResponse("welcome to quiz change list")
            # return redirect('take_quiz', pk)
        else:
            # return HttpResponse("Welome to student quiz list")
            return redirect('quiz_list')
    return render(request, 'home.html')


#Student Registration Logic

class StudentSignUpView(CreateView):
    model = User
    form_class = StudentSignUpForm
    template_name = 'registration/signup_form.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'student'
        print(super().get_context_data(**kwargs))
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        print(user)
        login(self.request, user)
        # return HttpResponse('welcome to quiz')
        return redirect('quiz_list')

#Student intrest technology to given quiz

class StudentInterestsView(UpdateView):
    model = Student
    form_class = StudentInterestsForm
    template_name = 'students/interests_form.html'
    success_url = reverse_lazy('quiz_list')

    def get_object(self):
        return self.request.user.student

    def form_valid(self, form):
        messages.success(self.request, 'Interests updated with success!')
        return super().form_valid(form)

#Student Quiz List

class QuizListView(ListView):
    model = Quiz
    ordering = ('name', )
    context_object_name = 'quizzes'
    template_name = 'students/quiz_list.html'

    def get_queryset(self):
        student = self.request.user.student
        student_interests = student.interests.values_list('pk', flat=True)
        taken_quizzes = student.quizzes.values_list('pk', flat=True)
        queryset = Quiz.objects.filter(subject__in=student_interests) \
            .exclude(pk__in=taken_quizzes) \
            .annotate(questions_count=Count('questions')) \
            .filter(questions_count__gt=0)
        return queryset

#Student quiz taken list

class TakenQuizListView(ListView):
    model = TakenQuiz
    context_object_name = 'taken_quizzes'
    template_name = 'students/taken_quiz_list.html'

    def get_queryset(self):
        queryset = self.request.user.student.taken_quizzes \
            .select_related('quiz', 'quiz__subject') \
            .order_by('quiz__name')
        return queryset

#Quiz in which student participate

def take_quiz(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk)
    print(request.user)
    user = User.objects.get(pk = request.user.pk)
    student = user.student
    print(student)
    if student.quizzes.filter(pk=pk).exists():
        return render(request, 'students/taken_quiz_list.html')

    total_questions = quiz.questions.count()
    unanswered_questions = student.get_unanswered_questions(quiz)
    total_unanswered_questions = unanswered_questions.count()
    progress = 100 - round(((total_unanswered_questions - 1) / total_questions) * 100)
    question = unanswered_questions.first()

    if request.method == 'POST':
        form = TakeQuizForm(question=question, data=request.POST)
        if form.is_valid():
            with transaction.atomic():
                student_answer = form.save(commit=False)
                student_answer.student = student
                student_answer.save()
                if student.get_unanswered_questions(quiz).exists():
                    return redirect('take_quiz', pk)
                else:
                    correct_answers = student.quiz_answers.filter(answer__question__quiz=quiz, answer__is_correct=True).count()
                    score = round((correct_answers / total_questions) * 100.0, 2)
                    TakenQuiz.objects.create(student=student, quiz=quiz, score=score)
                    if score < 50.0:
                        messages.warning(request, 'Better luck next time! Your score for the quiz %s was %s.' % (quiz.name, score))
                    else:
                        messages.success(request, 'Congratulations! You completed the quiz %s with success! You scored %s points.' % (quiz.name, score))
                    return redirect('quiz_list')
    else:
        form = TakeQuizForm(question=question)

    return render(request, 'students/take_quiz_form.html', {
        'quiz': quiz,
        'question': question,
        'form': form,
        'progress': progress
    })



#Teacher registration logic

class TeacherSignUpView(CreateView):
    model = User
    form_class = TeacherSignUpForm
    template_name = 'registration/signup_form.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'teacher'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return HttpResponse('welcome to django_schools')


