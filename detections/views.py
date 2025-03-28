from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from .serializers import VisualDetectionSerializer
from .models import VisualDetection

class VisualDetectionCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = VisualDetectionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
