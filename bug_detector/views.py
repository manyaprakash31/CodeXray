from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import DebugHistory
from .utils import generate_code, debug_code
from django.shortcuts import render, redirect

def code_debugger_view(request):
    return render(request, "code_debugger.html")

def generate_code_view(request):
    if request.method == "POST":
        import json
        data = json.loads(request.body)
        prompt = data.get("prompt", "")
        language = data.get("language", "python")
        code = generate_code(prompt, language)
        return JsonResponse({"code": code})
    return JsonResponse({"error": "Invalid request"}, status=400)

def debug_code_view(request):
    if request.method == "POST":
        import json
        data = json.loads(request.body)
        input_code = data.get("code", "")
        corrected_code = debug_code(input_code)
        if request.user.is_authenticated:
            DebugHistory.objects.create(
                user=request.user,
                input_code=input_code,
                corrected_code=corrected_code,
            )
        return JsonResponse({"corrected_code": corrected_code})
    return JsonResponse({"error": "Invalid request"}, status=400)


@login_required
def debug_history_view(request):
    """Show history of bug detector's debug sessions for the logged-in user."""
    history = DebugHistory.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'debug_history.html', {'history': history})
def auth_required_view(request):
    return render(request, "auth_required.html")
