from trading.serializers import (
    AttachPaymentMethodToCustomerSerializer, CreatePaymentMethodCardSerializer, ConfirmPaymentSerializer,
    CreatePaymentIntentSerializer
)
import stripe


class PaymentService:
    @staticmethod
    def create_payment_method_card(request):
        serializer = CreatePaymentMethodCardSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        payment_method = stripe.PaymentMethod.create(
            type="card",
            card={
                "number": serializer.validated_data['number'],
                "exp_month": serializer.validated_data['exp_month'],
                "exp_year": serializer.validated_data['exp_year'],
                "cvc": serializer.validated_data['cvc'],
            },
        )

        # for test
        # payment_method = stripe.PaymentMethod.retrieve(
        #     "pm_1JaLO3EYdpQ6mE0ASQzn2koT"  # for user3
        # )

        payment_method_attach = PaymentService.attach_payment_method_to_customer(request.user, payment_method['id'])
        return payment_method_attach

    @staticmethod
    def attach_payment_method_to_customer(user, payment_method_id):
        serializer = AttachPaymentMethodToCustomerSerializer(
            data={"payment_method_id": payment_method_id},
            context={'user': user}
        )
        serializer.is_valid(raise_exception=True)

        payment_method = stripe.PaymentMethod.attach(
            serializer.validated_data['payment_method_id'],
            customer=serializer.validated_data['customer']
        )
        # for test
        # payment_method = stripe.PaymentMethod.list(
        #     customer=serializer.validated_data['customer'],
        #     type="card"
        # )
        return payment_method

    @staticmethod
    def confirm_payment_intent(request):
        serializer = ConfirmPaymentSerializer(
            data=request.data,
            context={'user': request.user}
        )
        serializer.is_valid(raise_exception=True)
        conf = stripe.PaymentIntent.confirm(
            serializer.validated_data['payment_intent_id'],
            payment_method=serializer.validated_data['payment_method_id'],
        )
        return conf

    @staticmethod
    def create_payment_intent(request):
        ser = CreatePaymentIntentSerializer(data=request.data, context={"user": request.user})
        ser.is_valid(raise_exception=True)

        test_payment_intent = stripe.PaymentIntent.create(
            amount=ser.validated_data['amount'],
            currency=ser.validated_data['currency'],
            payment_method_types=[ser.validated_data['payment_method_types']],
            customer=ser.validated_data['customer'],
            receipt_email=ser.validated_data['receipt_email']
        )

        # test_payment_intent = stripe.PaymentIntent.retrieve(
        #     "pi_3JaKRLEYdpQ6mE0A14ArQIp7"
        # )
        print(test_payment_intent['id'])

        return test_payment_intent
