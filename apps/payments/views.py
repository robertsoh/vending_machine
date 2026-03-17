import json
import logging
import os

from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from apps.orders.models import Order
from apps.orders.services import OrderCreationError, create_pending_order


logger = logging.getLogger(__name__)


class CreateOrderView(View):
    def get(self, request, *args, **kwargs) -> HttpResponse:
        logger.info("create-order query params: %s", request.GET.dict())
        machine_id = request.GET.get("mid")
        slot_no = request.GET.get("sid")
        product_id = request.GET.get("pid")
        pri_raw = request.GET.get("pri")
        try:
            order = create_pending_order(
                mid=machine_id,
                sid=slot_no,
                pid=product_id,
                pri_raw=request.GET.get("pri"),
            )
        except OrderCreationError as exc:
            return JsonResponse(
                {
                    "Status": "1",
                }
            )
        payload = {
            "Status": "0",
            "Err": "success",
            "OrderID": order.id,
            "TradeNo": order.trade_no,
            "MachineID": machine_id,
            "SlotNo": slot_no,
            "ProductID": product_id,
            "Amount": 20,
        }
        return JsonResponse(payload)


@method_decorator(csrf_exempt, name="dispatch")
@method_decorator(require_POST, name="dispatch")
class NiubizWebhookView(View):
    def post(self, request: HttpRequest) -> JsonResponse:
        try:
            payload = json.loads(request.body.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return JsonResponse({"error": "invalid json"}, status=400)

        order_id = payload.get("order_id")
        trade_no = payload.get("trade_no")
        status = payload.get("status")
        transaction_id = payload.get("transaction_id")

        if not status:
            return JsonResponse({"error": "missing status"}, status=400)

        try:
            if trade_no:
                order = Order.objects.get(trade_no=trade_no)
            else:
                order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return JsonResponse({"error": "order not found"}, status=404)
        except (ValueError, TypeError):
            return JsonResponse({"error": "invalid order_id"}, status=400)

        if status == "APPROVED":
            order.status = Order.Status.PAID
            order.niubiz_transaction_id = transaction_id
            order.save(update_fields=["status", "niubiz_transaction_id", "updated_at"])

        return JsonResponse({"ok": True})


def build_payment_url(order: Order) -> str:
    payment_url_template = os.environ.get("QR_DYNAMIC_PAYMENT_URL_TEMPLATE")
    if not payment_url_template:
        return ""

    return payment_url_template.format(
        order_id=order.id,
        trade_no=order.trade_no,
        mid=order.machine_id,
        sid=order.slot_number,
        pid=order.product_id,
        pri=f"{order.amount:.2f}",
    )
