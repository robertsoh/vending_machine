from decimal import Decimal, InvalidOperation

from django.db import IntegrityError
from django.utils import timezone

from apps.orders.models import Order


class OrderCreationError(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message


def create_pending_order(*, mid, sid, pid, pri_raw):
    if not all([mid, sid, pid, pri_raw]):
        raise OrderCreationError("missing required query params: mid, sid, pid, pri")

    try:
        amount = Decimal(pri_raw)
    except (InvalidOperation, TypeError):
        raise OrderCreationError("invalid pri")
    if amount <= 0:
        raise OrderCreationError("pri must be greater than 0")

    for _ in range(3):
        try:
            return Order.objects.create(
                machine_id=mid,
                trade_no=generate_trade_no(),
                slot_number=sid,
                product_id=pid,
                amount=amount,
                status=Order.Status.PENDING,
            )
        except IntegrityError:
            continue

    raise OrderCreationError("could not generate unique trade number")


def generate_trade_no() -> str:
    # Compact, sortable serial compatible with machine protocol examples.
    return timezone.now().strftime("%Y%m%d%H%M%S%f")[:10]
