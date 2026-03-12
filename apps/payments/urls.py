from django.urls import path

from .views import CreateOrderView, NiubizWebhookView

urlpatterns = [
    path("s", CreateOrderView.as_view(), name="create-order"),
    path("niubiz-webhook", NiubizWebhookView.as_view(), name="niubiz-webhook"),
]
