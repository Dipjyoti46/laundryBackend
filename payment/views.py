
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from saikialaundry.models import order
import razorpay
import json

client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_SECRET_KEY))

class CreateOrderView(APIView):
    def post(self, request):
        try:
            amount = request.data.get('amount')
            if not amount:
                return Response(
                    {"error": "Amount is required"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Amount should already be in paise from frontend
            amount = int(amount)
            currency = request.data.get('currency', 'INR')
            
            print("Creating Razorpay order with amount:", amount)
            
            razorpay_order = client.order.create({
                'amount': amount,
                'currency': currency,
                'payment_capture': '1'
            })
            
            print("Razorpay order created:", razorpay_order)
            
            response_data = {
                'id': razorpay_order['id'],  # This is the razorpay_order_id that will be needed later
                'amount': razorpay_order['amount'],
                'currency': razorpay_order['currency']
            }
            
            print("Sending response:", response_data)
            
            return Response(response_data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
class VerifyPaymentView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # Log the received data
            print("Received payment verification data:", request.data)
            
            # Get the required parameters from the request
            params_dict = {
                'razorpay_payment_id': request.data.get('razorpay_payment_id'),
                'razorpay_order_id': request.data.get('razorpay_order_id'),
                'razorpay_signature': request.data.get('razorpay_signature')
            }
            
            # Log the extracted parameters
            print("Extracted parameters:", params_dict)
            
            # Verify that all required parameters are present
            if not all(params_dict.values()):
                return Response(
                    {
                        'status': 'failed',
                        'error': 'Missing required parameters',
                        'required': [k for k, v in params_dict.items() if not v]
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Verify the payment signature
            try:
                client.utility.verify_payment_signature(params_dict)
            except Exception as e:
                return Response(
                    {'status': 'failed', 'error': 'Invalid payment signature'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # If we get here, the signature is valid
            # Update the order status in your database here if needed
            order_id = request.data.get('order_id')
            if order_id:
                # Here you would typically update your order status
                order.objects.filter(order_id=order_id).update(payment_status='paid', transection_id=params_dict['razorpay_payment_id'])

            return Response(
                {
                    'status': 'success',
                    'message': 'Payment verified successfully',
                    'order_id': order_id
                },
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            return Response(
                {
                    'status': 'failed',
                    'error': str(e)
                },
                status=status.HTTP_400_BAD_REQUEST
            )
