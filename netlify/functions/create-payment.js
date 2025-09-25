import crypto from "crypto";        // 署名作成用
import fetch from "node-fetch";     // APIにリクエスト送る

export async function handler(event, context) {
  try {
    // 1. フロントから送られてきた金額を取得
    const { amount } = JSON.parse(event.body);

    // 2. 支払い情報を作成
    const payload = {
      merchantPaymentId: Date.now().toString(),  // 一意のID
      amount: { amount, currency: "JPY" },
      orderDescription: "Lazyum 質問投稿",
      codeType: "ORDER_QR",
      // 💡 修正点 1: サイトURLに置き換え
      redirectUrl: "https://lazyum.netlify.app/#post-complete", 
      redirectType: "WEB_LINK",
    };

    // 3. HMAC署名作成（秘密鍵を使う）
    const hmac = crypto
      .createHmac("sha256", process.env.PAYPAY_API_SECRET)
      .update(JSON.stringify(payload))
      .digest("base64");

    // 4. PayPay API に支払い作成リクエスト
    const response = await fetch("https://stg-api.paypay.ne.jp/v2/payments", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-API-KEY": process.env.PAYPAY_API_KEY,
        "X-REQUEST-ID": payload.merchantPaymentId,
        "X-SIGNATURE": hmac, 
        "Cache-Control": "no-cache",
      },
      body: JSON.stringify(payload),
    });

    const result = await response.json();

    // 5. PayPay APIからのレスポンスをチェックし、フロントにURLを返す
    if (response.ok && result.resultInfo.code === "SUCCESS") {
      // 💡 修正点 2: paymentUrlのパスを result.data.url に修正
      return {
        statusCode: 200,
        body: JSON.stringify({ success: true, paymentUrl: result.data?.url }),
      };
    } else {
      // PayPay APIからのエラーを返す (認証失敗など)
      console.error("PayPay API Error:", result);
      return {
        statusCode: 500,
        body: JSON.stringify({ success: false, message: result.resultInfo?.message || "PayPay API Error" }),
      };
    }

  } catch (err) {
    console.error("Function execution error:", err);
    return { 
      statusCode: 500, 
      body: JSON.stringify({ success: false, message: err.message || "Internal Server Error" }) 
    };
  }
}