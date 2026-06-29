from django.urls import path
from . import views

urlpatterns = [
    path('', views.ReclamationListView.as_view(), name='reclamation-list'),
    path('create/', views.ReclamationCreateView.as_view(), name='reclamation-create'),
    path('<int:pk>/', views.ReclamationDetailView.as_view(), name='reclamation-detail'),
    path('<int:pk>/delete/', views.ReclamationDeleteView.as_view(), name='reclamation-delete'),
]