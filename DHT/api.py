from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import ListAPIView

from .models import Dht11
from .serializer import Dht11Serializer


class DList(ListAPIView):
    queryset = Dht11.objects.all().order_by("-created_at")
    serializer_class = Dht11Serializer


class DhtViews(APIView):
    def post(self, request, *args, **kwargs):
        serializer = Dht11Serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "OK"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
