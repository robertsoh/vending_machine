from django.test import TestCase

from apps.orders.models import Order


class PollViewTests(TestCase):
    def test_poll_returns_no_order_when_nothing_paid(self):
        response = self.client.post(
            "/machine/poll",
            data='{"FunCode":"4000","MachineID":"M1"}',
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["Status"], "1")

    def test_poll_returns_paid_order_and_marks_dispensing(self):
        order = Order.objects.create(
            machine_id="M1",
            trade_no="202603120002",
            slot_number="11",
            product_id="P101",
            amount="4.20",
            status=Order.Status.PAID,
        )

        response = self.client.post(
            "/machine/poll",
            data='{"FunCode":"4000","MachineID":"M1"}',
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(data["Status"], "0")
        self.assertEqual(data["MsgType"], "0")
        self.assertEqual(data["TradeNo"], "202603120002")
        self.assertEqual(data["SlotNo"], "11")
        self.assertEqual(data["ProductID"], "P101")

        order.refresh_from_db()
        self.assertEqual(order.status, Order.Status.DISPENSING)


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
