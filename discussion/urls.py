# urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.topic_list, name='topic_list'),
    path('create/', views.create_topic, name='create_topic'),
    path('<uuid:uuid>/', views.topic_detail, name='topic_detail'),
    path('<uuid:uuid>/add_comment/', views.add_comment, name='add_comment'),
    path('like_comment/<int:comment_id>/', views.like_comment, name='like_comment'),
    path('dislike_comment/<int:comment_id>/', views.dislike_comment, name='dislike_comment'),
    path('<int:comment_id>/edit/', views.edit_comment, name='edit_comment'),
    path('<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    path('<uuid:topic_uuid>/add_star/', views.add_star, name='add_star'),
    path('<uuid:topic_uuid>/remove_star/', views.remove_star, name='remove_star'),
]
