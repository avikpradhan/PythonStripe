from django.conf import settings
from stripe import Customer, PaymentMethod, Price, Subscription, Account, PaymentIntent, AccountLink

SECRET_KEY = settings.STRIPE_SECRET_KEY
 
 
class StripeClient:
    def __init__(self) -> None:
        stripe.api_key = SECRET_KEY
        self.api_key = SECRET_KEY
        self.currency = "usd"
 
    def customers(self):
        customers = Customer.list()
        return customers
 
    def customer_detail(self, customer_id: str) -> Customer:
        customer = Customer.retrieve(
            customer_id,
            api_key=self.api_key,
        )
        return customer
 
    def create_customer(
        self,
        name: str,
        email: str,
        user_id: str,
    ) -> Customer:
        customer = Customer.create(
            name=name,
            email=email,
            metadata={"user_id": user_id},
        )
 
        return customer
 
    def attach_payment_method(self, card_token, customer_id,):
        setup_method = PaymentMethod.attach(card_token, customer=customer_id,)
        return setup_method
    
    def detach_payment_method(self, payment_method_id):
        return PaymentMethod.detach(payment_method_id)

    def create_monthly_stripe_price(self, amount):
        return Price.create(
          currency=self.currency,
          unit_amount=amount,
          recurring={"interval": "month"},
          product_data={"name": "Monthly"},
        )

    def create_yearly_stripe_price(self, amount):
        return Price.create(
          currency=self.currency,
          unit_amount=amount,
          recurring={"interval": "year"},
          product_data={"name": "Yearly"},
        )

    def list_price(self):
        return Price.list(limit=3)

    def create_stripe_subscription(self, customer_id, price_id):
        return Subscription.create(
          customer=customer_id,
          items=[{"price": price_id}],
        )
    
    def make_default_payment_method(self, user, payment_method_id):
        Customer.modify(user,
                invoice_settings={
                    'default_payment_method': payment_method_id,
                },
            )
        
    def retrieve_payment_method(self, payment_method_id):
        return PaymentMethod.retrieve(payment_method_id)
    
    def create_stripe_account(self, email):
        return Account.create(type="custom",
                       country="US",
                       email=email ,
                       capabilities={
                           "card_payments": {"requested": True},
                           "transfers": {"requested": True},},  
                           settings={
                               "payouts":{
                                   "schedule": {
                                       "interval": "weekly", 
                                       "weekly_anchor": "monday"
                                       }}},)
    

    def create_account_link_for_connected_account(self, account_id, refresh_url, return_url):
        return AccountLink.create(account=account_id,
                                  refresh_url=refresh_url,
                                  return_url=return_url,
                                  type="account_onboarding",)
        
    def retrieve_connected_account_details(self, account_id):
        return Account.retrieve(account_id)

    def create_payment_intent(self, total_amount, customer_id, connected_account_id, payment_method_id):
        return PaymentIntent.create(
                amount=total_amount, 
                currency="usd",
                customer=customer_id,
                application_fee_amount=total_amount, # set commission 
                transfer_data={"destination": connected_account_id},
                confirm=True,
                automatic_payment_methods={"enabled": True, "allow_redirects": "never"},
                on_behalf_of=connected_account_id,
                capture_method="automatic",
                payment_method=payment_method_id,
                metadata={}) # meta data if any additional data is required