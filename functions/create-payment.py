import os
import json
import paypayopa
import datetime

# Netlify Function のエントリポイント
def handler(event, context):
    try:
        # 1. APIキーとシークレットを環境変数から取得
        API_KEY = os.environ.get('PAYPAY_API_KEY')
        API_SECRET = os.environ.get('PAYPAY_API_SECRET')
        
        # 🚨 Merchant ID も環境変数に追加が必要です
        MERCHANT_ID = os.environ.get('PAYPAY_MERCHANT_ID')
        
        if not API_KEY or not API_SECRET or not MERCHANT_ID:
            return {
                'statusCode': 500,
                'body': json.dumps({'success': False, 'message': 'API keys or Merchant ID are missing from environment variables.'})
            }

        # 2. フロントから送られてきた金額を取得
        body = json.loads(event.get('body', '{}'))
        amount = body.get('amount')
        
        if not amount:
            return {
                'statusCode': 400,
                'body': json.dumps({'success': False, 'message': 'Amount is missing.'})
            }

        # 3. PayPayクライアントの初期化（認証と環境設定）
        # production_mode=False でテスト環境に接続
        client = paypayopa.Client(auth=(API_KEY, API_SECRET), production_mode=False)
        client.set_assume_merchant(MERCHANT_ID)
        
        # 一意のIDを生成
        merchant_payment_id = str(int(datetime.datetime.now().timestamp() * 1000))

        # 4. 支払いリクエストペイロードの作成
        request_payload = {
            "merchantPaymentId": merchant_payment_id,
            "amount": { "amount": amount, "currency": "JPY" },
            "orderDescription": "Lazyum 質問投稿",
            "codeType": "ORDER_QR",
            "redirectUrl": "https://lazyum.netlify.app/#post-complete",
            "redirectType": "WEB_LINK",
        }

        # 5. QRコード作成メソッドの呼び出し
        response = client.Code.create_qr_code(request_payload)

        # 6. PayPay APIからのレスポンスをチェック
        if response and response['resultInfo']['code'] == "SUCCESS":
            payment_url = response['data']['url']
            return {
                'statusCode': 200,
                'body': json.dumps({'success': True, 'paymentUrl': payment_url})
            }
        else:
            # PayPay APIからのエラーをログに出力
            print(f"PayPay API Error: {response}")
            error_message = response['resultInfo'].get('message', 'PayPay API Error')
            return {
                'statusCode': 500,
                'body': json.dumps({'success': False, 'message': error_message})
            }

    except Exception as e:
        print(f"Function execution error: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'success': False, 'message': f'Internal Server Error: {str(e)}'})
        }