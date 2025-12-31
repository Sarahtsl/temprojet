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
        serializer = Dht11Serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "OK"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, *args, **kwargs):
        last = Dht11.objects.order_by("-created_at").first()  # adapte si ton champ s'appelle autrement
        if not last:
            return Response({"detail": "no data"}, status=status.HTTP_404_NOT_FOUND)

        data = Dht11Serializer(last).data
        return Response(data, status=status.HTTP_200_OK)
