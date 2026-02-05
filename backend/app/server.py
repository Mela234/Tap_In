import os
import json
import stripe
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# -------------------
# Stripe config
# -------------------
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
endpoint_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

# -------------------
# FastAPI app
# -------------------
app = FastAPI()

# Allow React frontend to call backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------
# Create Checkout Session
# -------------------
@app.post("/create-checkout-session")
async def create_checkout_session():
    try:
        session = stripe.checkout.Session.create(
            mode="subscription",
            line_items=[
                {
                    "price": "price_1SxMpfAnZO4xYeTn1jccjCUS",  # 🔴 MUST be a TEST recurring price
                    "quantity": 1,
                }
            ],
            success_url=FRONTEND_URL+ "/success",
            cancel_url=FRONTEND_URL + "/cancel",
        )

        print("✅ Checkout session created:", session.id)
        return {"url": session.url}

    except Exception as e:
        print("❌ Stripe error:", str(e))
        raise HTTPException(status_code=400, detail=str(e))


# -------------------
# Stripe Webhook
# -------------------
@app.post("/webhook")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except stripe.error.SignatureVerificationError as e:
        print("❌ Webhook signature verification failed:", e)
        raise HTTPException(status_code=400, detail="Invalid signature")
    except Exception as e:
        print("❌ Webhook error:", e)
        raise HTTPException(status_code=400, detail="Webhook error")

    # -------------------
    # Handle events
    # -------------------
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        print("✅ Checkout completed")
        print("Customer:", session.get("customer"))
        print("Subscription:", session.get("subscription"))

    elif event["type"] == "customer.subscription.created":
        subscription = event["data"]["object"]
        print("✅ Subscription created:", subscription["id"])

    else:
        print("Unhandled event type:", event["type"])

    return JSONResponse(content={"status": "success"})
