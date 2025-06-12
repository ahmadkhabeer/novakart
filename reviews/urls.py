from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    path('add/<int:product_id>/', views.add_review, name='add_review'),
    
    # NEW Q&A URLS
    path('ask/<int:product_id>/', views.ask_question_view, name='ask_question'),
    path('answer/<int:question_id>/', views.post_answer_view, name='post_answer'),
]
