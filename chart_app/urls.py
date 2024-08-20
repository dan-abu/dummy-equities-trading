from django.urls import path
from . import views

urlpatterns = [
    # path('chart/', views.portfolio_view, name='chart'),
    path('chart/', views.portfolio_view),
]