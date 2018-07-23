from django.urls import path
from classrooms import views


urlpatterns = [
    # path('home/', views.user, name='user'),
   path('', views.home, name='home'),
   path('quiz/', views.QuizListView.as_view(), name='quiz_list'),
   path('taken/', views.TakenQuizListView.as_view(), name='taken_quiz_list'),
   path('quiz/<int:pk>/', views.take_quiz, name='take_quiz'),
   path('interests/', views.StudentInterestsView.as_view(), name='student_interests'),

]
