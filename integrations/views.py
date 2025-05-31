from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Integration
from .serializers import IntegrationSerializer
import json
from django.shortcuts import render
@login_required
def integration_list_create(request):
    if request.method == 'GET':
        integrations = Integration.objects.all()
        serializer = IntegrationSerializer(integrations, many=True)
        return render(request, 'integrations/integration_list.html', {'integrations': serializer.data})
    elif request.method == 'POST':
        data = json.loads(request.body)
        serializer = IntegrationSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)

@login_required
def integration_detail(request, pk):
    integration = get_object_or_404(Integration, pk=pk)
    if request.method == 'GET':
        serializer = IntegrationSerializer(integration)
        return JsonResponse(serializer.data)
    elif request.method == 'PUT':
        data = json.loads(request.body)
        serializer = IntegrationSerializer(integration, data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data)
        return JsonResponse(serializer.errors, status=400)
    elif request.method == 'DELETE':
        integration.delete()
        return JsonResponse({'deleted': True})