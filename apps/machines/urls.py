from django.urls import path

from .views import FeedbackView, PollView

urlpatterns = [
    path("poll", PollView.as_view(), name="machine-poll"),
    path("feedback", FeedbackView.as_view(), name="machine-feedback"),
]
