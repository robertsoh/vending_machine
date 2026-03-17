import json
import logging

from django.http import HttpRequest, JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from apps.orders.models import Order
from apps.producto.models import Producto


logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name="dispatch")
class PollView(View):
    def post(self, request: HttpRequest, *args, **kwargs) -> JsonResponse:
        logger.info("poll request.POST=%s", request.POST.dict())
        logger.info("poll raw body=%s", request.body.decode("utf-8", errors="replace"))
        if request.POST:
            data = request.POST.dict()
        else:
            try:
                data = json.loads(request.body.decode("utf-8"))
            except (json.JSONDecodeError, UnicodeDecodeError):
                return JsonResponse(
                    {"Status": "1", "Err": "Invalid payload"}, status=400
                )
        func_code = data.get("FunCode")
        machine_id = data.get("MachineID")
        if not func_code or not machine_id:
            return JsonResponse(
                {"Status": "1", "Err": "FunCode and MachineID required"}, status=400
            )
        if func_code == "1000":
            trade_number = data["TradeNo"]
            slot_no = data["SlotNo"]
            product_id = data["ProductID"]
            """
            Producto.objects.update_or_create(
                machine_id=machine_id,
                slot_no=slot_nro,
                defaults={
                    "trade_no": trade_number,
                    "status": int(data["Status"]),
                    "quantity": int(data["Quantity"]),
                    "stock": int(data["Stock"]),
                    "capacity": int(data["Capacity"]),
                    "product_id": product_id,
                    "name": data["Name"],
                    "price": data["Price"],
                    "s_price": data["SPrice"],
                    "product_type": data.get("Type", ""),
                    "introduction": data.get("Introduction", ""),
                    "modify_type": data.get("ModifyType", ""),
                    "lock_goods_count": int(data.get("LockGoodsCount", 0))
                },
            )
            """
            try:
                order = Order.objects.get(
                    machine_id=machine_id,
                    product_id=product_id,
                    slot_number=slot_no,
                    status=Order.Status.PENDING,
                )
                order.trade_no = trade_number
                order.status = Order.Status.PROCCESSING
                order.save(update_fields=["trade_no", "status"])
            except Order.DoesNotExist:
                pass
            except Exception as e:
                logger.info(f"Error al actualizar la orden: {e}")
            return JsonResponse(
                {
                    "Status": "0",
                    "SlotNo": slot_no,
                    "TradeNo": trade_number,
                    "Err": "Success",
                }
            )

        elif func_code == "4000":
            order = Order.objects.filter(
                machine_id=machine_id, status=Order.Status.PROCCESSING
            ).first()
            if not order:
                return JsonResponse({"Status": "1", "Err": "No product found"})
            order.status = Order.Status.PAID
            order.save(update_fields=["status"])
            return JsonResponse(
                {
                    "Status": "0",
                    "MsgType": "0",
                    "TradeNo": order.trade_no,
                    "SlotNo": order.slot_number,
                    "ProductID": order.product_id,
                    "Err": "Succeeded",
                }
            )
        elif func_code == "5000":
            trade_number = data["TradeNo"]
            slot_no = data["SlotNo"]
            status = data["Status"]
            product_id = data["ProductID"]
            try:
                order = Order.objects.get(
                    machine_id=machine_id,
                    trade_no=trade_number,
                    slot_number=slot_no,
                    product_id=product_id,
                )
                if status in ["0", "2"]:
                    order.status = Order.Status.COMPLETED
                else:
                    order.status = Order.Status.FAILED
                order.save(update_fields=["status"])
                return JsonResponse(
                    {
                        "Status": "0",
                        "SlotNo": slot_no,
                        "TradeNo": trade_number,
                        "Err": "Success",
                    }
                )
            except Order.DoesNotExist:
                return JsonResponse(
                    {
                        "Status": "1",
                        "SlotNo": slot_no,
                        "TradeNo": trade_number,
                        "Err": "Error",
                    }
                )
        return JsonResponse({})


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
            return JsonResponse(
                {"Status": "1", "Err": "TradeNo and Status required"}, status=400
            )

        try:
            order = Order.objects.get(trade_no=str(trade_no))
        except Order.DoesNotExist:
            return JsonResponse({"Status": "1", "Err": "Order not found"}, status=404)

        try:
            status_code = int(status)
        except (ValueError, TypeError):
            return JsonResponse({"Status": "1", "Err": "Invalid Status"}, status=400)

        order.status = (
            Order.Status.COMPLETED if status_code == 0 else Order.Status.FAILED
        )
        order.save(update_fields=["status", "updated_at"])

        return JsonResponse(
            {
                "Status": "0",
                "TradeNo": order.trade_no,
                "SlotNo": order.slot_number,
                "Err": "Success",
            }
        )
