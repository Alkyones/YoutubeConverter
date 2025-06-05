from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Integration, TelegramIntegration
from .serializers import IntegrationSerializer
import json
from django.shortcuts import render
from .forms import TelegramIntegrationForm

@login_required
def integration_list_create(request):
    if request.method == 'GET':
        integrations = Integration.objects.all()
        serializer = IntegrationSerializer(integrations, many=True)
        form = TelegramIntegrationForm()
        return render(
            request,
            'integrations/integration_list.html',
            {'integrations': serializer.data, 'user': request.user, 'form': form}
        )
    elif request.method == 'POST':
        if request.content_type == 'application/json':
            data = json.loads(request.body)
        else:
            data = request.POST

        integration_type = data.get('type', 'generic')

        # Handle Telegram integration creation
        if integration_type == 'telegram':
            form = TelegramIntegrationForm(data)
            if form.is_valid():
                print(form.cleaned_data)  # Debugging line to check form data
                telegram_integration = form.save(commit=False)
                telegram_integration.user = request.user
                telegram_integration.save()
                serializer = IntegrationSerializer(telegram_integration)
                if request.content_type == 'application/json':
                    return JsonResponse(serializer.data, status=201)
                else:
                    return render(request, 'integrations/integration_success.html', {'integration': telegram_integration})
            else:
                if request.content_type == 'application/json':
                    return JsonResponse(form.errors, status=400)
                else:
                    integrations = Integration.objects.all()
                    serializer = IntegrationSerializer(integrations, many=True)
                    return render(
                        request,
                        'integrations/integration_list.html',
                        {'integrations': serializer.data, 'user': request.user, 'form': form}
                    )

        # Handle generic or other types
        data = data.copy()
        data['user'] = request.user
        serializer = IntegrationSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            if request.content_type == 'application/json':
                return JsonResponse(serializer.data, status=201)
            else:
                return render(request, 'integrations/integration_success.html', {'integration': serializer.instance})
        if request.content_type == 'application/json':
            return JsonResponse(serializer.errors, status=400)
        else:
            integrations = Integration.objects.all()
            serializer = IntegrationSerializer(integrations, many=True)
            form = TelegramIntegrationForm()
            return render(
                request,
                'integrations/integration_list.html',
                {'integrations': serializer.data, 'user': request.user, 'form': form, 'errors': serializer.errors}
            )