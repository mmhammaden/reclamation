from django.urls import path
from . import views

urlpatterns = [
    path('', views.UserListCreateView.as_view(), name='admin-user-list-create'),
    path('<int:pk>/', views.UserDetailView.as_view(), name='admin-user-detail'),
]