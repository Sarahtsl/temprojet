from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny
from .models import Dht11
from .serializer import Dht11Serializer


class DList(ListAPIView):
    queryset = Dht11.objects.all().order_by("-created_at")
    serializer_class = Dht11Serializer
    permission_classes = [AllowAny]

class DhtViews(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        try:
            data = request.data

            sensor_id = data.get("sensor_id", 1)
            temperature = data.get("temperature")
            humidity = data.get("humidity")

            if temperature is None or humidity is None:
                return Response(
                    {"error": "temperature ou humidity manquant"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            dht = Dht11.objects.create(
                sensor_id=int(sensor_id),
                temperature=float(temperature),
                humidity=float(humidity)
            )

            return Response(
                {"message": "OK"},
                status=status.HTTP_201_CREATED
            )

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
