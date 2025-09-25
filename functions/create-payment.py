import os, json, datetime
import paypayopa

def handler(event, context):
    API_KEY = os.environ.get('PAYPAY_API_KEY')
    API_SECRET = os.environ.get('PAYPAY_API_SECRET')
    MERCHANT_ID = os.environ.get('PAYPAY_MERCHANT_ID')

    body = json.loads(event.get('body', '{}'))
    amount = body.get('amount', 1)
    itemName = body.get('itemName', 'テスト商品')

    client = paypayopa.Client(auth=(API_KEY, API_SECRET), production_mode=False)
    client.set_assume_merchant(MERCHANT_ID)

    merchant_payment_id = str(int(datetime.datetime.now().timestamp() * 1000))

    request_payload = {
        "merchantPaymentId": merchant_payment_id,
        "amount": {"amount": amount, "currency":"JPY"},
        "codeType": "ORDER_QR",
        "orderDescription": itemName,
        "redirectUrl": "https://your-site.netlify.app/#post-complete",
        "redirectType": "WEB_LINK"
    }

    response = client.Code.create_qr_code(request_payload)

    if response['resultInfo']['code'] == "SUCCESS":
        return {
            'statusCode': 200,
            'body': json.dumps({'success': True, 'paymentUrl': response['data']['url']})
        }
    else:
        return {
            'statusCode': 500,
            'body': json.dumps({'success': False, 'message': response['resultInfo'].get('message','PayPayエラー')})
        }

