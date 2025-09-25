import os
import json
import datetime
import paypayopa

def handler(event, context):
    try:
        API_KEY = os.environ.get('PAYPAY_API_KEY')
        API_SECRET = os.environ.get('PAYPAY_API_SECRET')
        MERCHANT_ID = os.environ.get('PAYPAY_MERCHANT_ID')

        if not API_KEY or not API_SECRET or not MERCHANT_ID:
            return {
                'statusCode': 500,
                'body': json.dumps({'success': False, 'message': 'API keys or Merchant ID are missing.'})
            }

        body = json.loads(event.get('body', '{}'))
        amount = body.get('amount')

        if not amount:
            return {
                'statusCode': 400,
                'body': json.dumps({'success': False, 'message': 'Amount is missing.'})
            }

        client = paypayopa.Client(auth=(API_KEY, API_SECRET), production_mode=False)
        client.set_assume_merchant(MERCHANT_ID)

        merchant_payment_id = str(int(datetime.datetime.now().timestamp() * 1000))

        request_payload = {
            "merchantPaymentId": merchant_payment_id,
            "amount": {"amount": amount, "currency": "JPY"},
            "orderDescription": "Lazyum 質問投稿",
            "codeType": "ORDER_QR",
            "redirectUrl": "https://lazyum.netlify.app/#post-complete",
            "redirectType": "WEB_LINK",
        }

        response = client.Code.create_qr_code(request_payload)

        if response and response['resultInfo']['code'] == "SUCCESS":
            payment_url = response['data']['url']
            return {'statusCode': 200, 'body': json.dumps({'success': True, 'paymentUrl': payment_url})}
        else:
            error_message = response['resultInfo'].get('message', 'PayPay API Error')
            return {'statusCode': 500, 'body': json.dumps({'success': False, 'message': error_message})}

    except Exception as e:
        return {'statusCode': 500, 'body': json.dumps({'success': False, 'message': f'Internal Server Error: {str(e)}'})}
