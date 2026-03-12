from unittest.mock import patch

from django.test import TestCase

from apps.orders.models import Order


class CreateOrderViewTests(TestCase):
    def test_create_order_requires_query_params(self):
        response = self.client.get("/s")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"], "missing required query params: mid, sid, pid, pri")

    def test_create_order_returns_protocol_payload(self):
        response = self.client.get("/s?mid=M1&sid=10&pid=P100&pri=2.50&format=json")
        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertEqual(data["Status"], "0")
        self.assertEqual(data["Err"], "success")
        self.assertEqual(data["MachineID"], "M1")
        self.assertEqual(data["SlotNo"], "10")
        self.assertEqual(data["ProductID"], "P100")
        self.assertEqual(data["Amount"], "2.50")
        self.assertNotIn("PaymentURL", data)
        self.assertTrue(data["TradeNo"])

        order = Order.objects.get(id=data["OrderID"])
        self.assertEqual(order.trade_no, data["TradeNo"])
        self.assertEqual(order.status, Order.Status.PENDING)

    @patch.dict("os.environ", {"QR_DYNAMIC_PAYMENT_URL_TEMPLATE": "https://pay.example.com/checkout?tn={trade_no}"})
    def test_create_order_redirects_when_payment_url_template_exists(self):
        response = self.client.get("/s?mid=M1&sid=10&pid=P100&pri=2.50")
        self.assertEqual(response.status_code, 302)
        self.assertIn("https://pay.example.com/checkout?tn=", response["Location"])


class NiubizWebhookViewTests(TestCase):
    def test_webhook_marks_order_as_paid_by_trade_no(self):
        order = Order.objects.create(
            machine_id="M1",
            trade_no="202603120001",
            slot_number="10",
            product_id="P100",
            amount="3.00",
            status=Order.Status.PENDING,
        )

        response = self.client.post(
            "/niubiz-webhook",
            data='{"trade_no":"202603120001","status":"APPROVED","transaction_id":"TX-1"}',
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)

        order.refresh_from_db()
        self.assertEqual(order.status, Order.Status.PAID)
        self.assertEqual(order.niubiz_transaction_id, "TX-1")
