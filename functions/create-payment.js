'use strict';
const PAYPAY = require('@paypayopa/paypayopa-sdk-node');

exports.handler = async function(event, context) {
  try {
    const body = JSON.parse(event.body || '{}');
    const amount = body.amount || 1;
    const itemName = body.itemName || 'テスト商品';

    const API_KEY = process.env.PAYPAY_API_KEY;
    const API_SECRET = process.env.PAYPAY_API_SECRET;
    const MERCHANT_ID = process.env.PAYPAY_MERCHANT_ID;

    PAYPAY.Configure({
      clientId: API_KEY,
      clientSecret: API_SECRET,
      merchantId: MERCHANT_ID,
      productionMode: false
    });

    const merchantPaymentId = String(Date.now());

    const payload = {
      merchantPaymentId,
      amount: { amount, currency: "JPY" },
      codeType: "ORDER_QR",
      orderDescription: itemName,
      isAuthorization: false,
      redirectUrl: "https://your-site.netlify.app/#post-complete",
      redirectType: "WEB_LINK",
      userAgent: "Mozilla/5.0"
    };

    const qrResponse = await new Promise((resolve, reject) => {
      PAYPAY.QRCodeCreate(payload, (response) => {
        if (response.BODY?.resultInfo?.code === "SUCCESS") {
          resolve(response.BODY);
        } else {
          reject(response.BODY?.resultInfo?.message || 'PayPay API Error');
        }
      });
    });

    return { statusCode: 200, body: JSON.stringify({ success: true, paymentUrl: qrResponse.data.url }) };

  } catch (err) {
    console.error('PayPay QR Error:', err);
    return { statusCode: 500, body: JSON.stringify({ success: false, message: err.toString() }) };
  }
};
