from django.test import TestCase

from apps.orders.models import Order
from apps.producto.models import Producto


class PollViewTests(TestCase):
    def test_poll_1000_saves_producto(self):
        response = self.client.post(
            "/machine/poll",
            data={
                "FunCode": "1000",
                "MachineID": "2001160092",
                "TradeNo": "20260312184942145",
                "SlotNo": "58",
                "Status": "0",
                "Quantity": "15",
                "Stock": "15",
                "Capacity": "15",
                "ProductID": "1",
                "Name": "Vending machine",
                "Price": "1.0",
                "SPrice": "6553.5",
                "Type": "",
                "Introduction": "",
                "ModifyType": "5",
                "LockGoodsCount": "0",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["Status"], "0")

        producto = Producto.objects.get(machine_id="2001160092", slot_no="58")
        self.assertEqual(producto.trade_no, "20260312184942145")
        self.assertEqual(str(producto.price), "1.00")
        self.assertEqual(str(producto.s_price), "6553.50")

    def test_poll_returns_no_order_when_nothing_paid(self):
        response = self.client.post(
            "/machine/poll",
            data={"FunCode": "4000", "MachineID": "M1"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["Status"], "1")

    def test_poll_4000_returns_last_producto(self):
        Producto.objects.create(
            machine_id="M1",
            trade_no="202603120001",
            slot_no="10",
            product_id="P100",
            status=0,
            quantity=10,
            stock=10,
            capacity=10,
            name="Prod A",
            price="1.00",
            s_price="1.00",
        )
        latest = Producto.objects.create(
            machine_id="M1",
            trade_no="202603120002",
            slot_no="11",
            product_id="P101",
            status=0,
            quantity=10,
            stock=10,
            capacity=10,
            name="Prod B",
            price="2.00",
            s_price="2.00",
        )

        response = self.client.post(
            "/machine/poll",
            data={"FunCode": "4000", "MachineID": "M1"},
        )
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(data["Status"], "0")
        self.assertEqual(data["MsgType"], "0")
        self.assertEqual(data["TradeNo"], latest.trade_no)
        self.assertEqual(data["SlotNo"], latest.slot_no)
        self.assertEqual(data["ProductID"], latest.product_id)


class FeedbackViewTests(TestCase):
    def test_feedback_marks_order_completed(self):
        order = Order.objects.create(
            machine_id="M1",
            trade_no="202603120003",
            slot_number="12",
            product_id="P102",
            amount="5.50",
            status=Order.Status.DISPENSING,
        )

        response = self.client.post(
            "/machine/feedback",
            data='{"FunCode":"5000","MachineID":"M1","TradeNo":"202603120003","Status":0}',
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["Status"], "0")
        self.assertEqual(response.json()["TradeNo"], "202603120003")
        self.assertEqual(response.json()["SlotNo"], "12")

        order.refresh_from_db()
        self.assertEqual(order.status, Order.Status.COMPLETED)

    def test_feedback_unknown_order_returns_404(self):
        response = self.client.post(
            "/machine/feedback",
            data='{"FunCode":"5000","MachineID":"M1","TradeNo":"NOT-FOUND","Status":1}',
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 404)
