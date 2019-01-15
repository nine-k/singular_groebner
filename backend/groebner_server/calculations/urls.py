from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('submit_calculation', views.submit_calculation, name='submit_calculation'),
]
