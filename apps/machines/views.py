import json
import logging

from django.http import HttpRequest, JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from apps.orders.models import Order


logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name="dispatch")
class PollView(View):
    def post(self, request: HttpRequest) -> JsonResponse:
        logger.info("poll request.POST=%s", request.POST.dict())
        logger.info("poll raw body=%s", request.body.decode("utf-8", errors="replace"))
        try:
            payload = json.loads(request.body.decode("utf-8"))
            logger.info("poll payload=%s", payload)
        except (json.JSONDecodeError, UnicodeDecodeError):
            logger.info("poll payload=invalid json")

        return JsonResponse({"Status": "0", "SlotNo": 1, "TradeNo": 1, "Err": "Success"})


@method_decorator(csrf_exempt, name="dispatch")
@method_decorator(require_POST, name="dispatch")
class FeedbackView(View):
    def post(self, request: HttpRequest) -> JsonResponse:
        try:
            payload = json.loads(request.body.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return JsonResponse({"Status": "1", "Err": "Invalid JSON"}, status=400)


        if payload.get("FunCode") != "5000":
            return JsonResponse({"Status": "1", "Err": "Invalid FunCode"}, status=400)

        trade_no = payload.get("TradeNo")
        status = payload.get("Status")
        if trade_no is None or status is None:
            return JsonResponse({"Status": "1", "Err": "TradeNo and Status required"}, status=400)

        try:
            order = Order.objects.get(trade_no=str(trade_no))
        except Order.DoesNotExist:
            return JsonResponse({"Status": "1", "Err": "Order not found"}, status=404)

        try:
            status_code = int(status)
        except (ValueError, TypeError):
            return JsonResponse({"Status": "1", "Err": "Invalid Status"}, status=400)

        order.status = Order.Status.COMPLETED if status_code == 0 else Order.Status.FAILED
        order.save(update_fields=["status", "updated_at"])

        return JsonResponse(
            {
                "Status": "0",
                "TradeNo": order.trade_no,
                "SlotNo": order.slot_number,
                "Err": "Success",
            }
        )
