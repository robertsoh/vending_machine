# vending_machine

Proyecto Django 5 (Python 3.12.3) para integración de pagos de máquina vending.

## Estructura
- `apps/`
- `config/settings/{base,dev,prod,test}.py`
- `requirements/{base,dev,prod,test}.txt`
- `templates/`
- `static/`
- `media/`

## Endpoints MVP
- `GET /s?mid=...&sid=...&pid=...&pri=...` crea orden con `TradeNo` y redirige al pago dinámico QR (usar `&format=json` para respuesta JSON del protocolo)
- `POST /niubiz-webhook` confirma pago (`status=APPROVED`)
- `POST /machine/poll` FunCode `4000`
- `POST /machine/feedback` FunCode `5000`

## Configuración de pago QR dinámico
- Variable: `QR_DYNAMIC_PAYMENT_URL_TEMPLATE`
- Placeholders disponibles: `{order_id}`, `{trade_no}`, `{mid}`, `{sid}`, `{pid}`, `{pri}`
- Ejemplo:
  `QR_DYNAMIC_PAYMENT_URL_TEMPLATE=https://pay.miapp.com/checkout?tradeNo={trade_no}&machine={mid}&slot={sid}&product={pid}&amount={pri}`

## Ejecutar
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements/dev.txt
python manage.py migrate
python manage.py loaddata apps/common/fixtures/feature_flags.json
python manage.py runserver
```
