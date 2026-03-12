from django.http import JsonResponse
from django.views import View


class HealthView(View):
    def get(self, _request):
        return JsonResponse({"app": "orders", "status": "ok"})
