import os
import tempfile
import logging
import shutil
import requests
import re
import io

from urllib.parse import unquote
from dotenv import load_dotenv
from github import Github

from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from xhtml2pdf import pisa

from github_analyzer.models import AnalysisHistory
from github_analyzer.utils import analyze_with_together

load_dotenv()

BASE_CLONE_DIR = os.path.join(tempfile.gettempdir(), "cloned_repos")
os.makedirs(BASE_CLONE_DIR, exist_ok=True)


# Landing
def landing_page(request):
    return render(request, 'landing.html')


import os
import requests
from django.shortcuts import render, redirect
from github import Github
from .utils import analyze_with_ollama, analyze_with_together

def profile_input_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        return redirect("repo_list")
    return render(request, "profile.html")

def repo_list_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        g = Github(os.getenv("GITHUB_TOKEN"))
        try:
            user = g.get_user(username)
            repos = [repo.name for repo in user.get_repos()]
            return render(request, "analyze_repo.html", {"repos": repos, "username": username})
        except Exception as e:
            return render(request, "profile.html", {"error": str(e)})
    return render(request, "profile.html")

def repo_chatbot_view(request, repo_name):
    username = request.GET.get("username") or request.POST.get("username")
    access_token = os.getenv("GITHUB_TOKEN")
    g = Github(access_token)
    try:
        repo = g.get_user(username).get_repo(repo_name)
        default_branch = repo.default_branch
        contents = repo.get_contents("", ref=default_branch)
        source_files = []
        while contents:
            file_content = contents.pop(0)
            if file_content.type == "dir":
                contents.extend(repo.get_contents(file_content.path, ref=default_branch))
            else:
                source_files.append(file_content.path)
        return render(request, "repo_code.html", {
            "repo_name": repo_name,
            "username": username,
            "source_files": source_files
        })
    except Exception as e:
        return render(request, "repo_code.html", {"error": str(e), "repo_name": repo_name})

def analyze_file_view(request, username, repo_name, file_path):
    repo_url = f"https://api.github.com/repos/{username}/{repo_name}"
    repo_response = requests.get(repo_url)
    if repo_response.status_code == 200:
        default_branch = repo_response.json().get('default_branch', 'main')
    else:
        default_branch = "main"

    raw_url = f"https://raw.githubusercontent.com/{username}/{repo_name}/{default_branch}/{file_path}"
    file_response = requests.get(raw_url)
    if file_response.status_code == 200:
        file_content = file_response.text
        analysis_result = analyze_with_ollama(f"Analyze this file:\n{file_content}")
        return render(request, "file_analysis.html", {
            "username": username,
            "repo_name": repo_name,
            "file_path": file_path,
            "analysis": analysis_result
        })
    else:
        return render(request, "repo_code.html", {"error": "Could not fetch file content."})


# Chatbot interaction
@csrf_exempt
def chatbot_view(request):
    if request.method == "POST":
        user_question = request.POST.get("question", "").strip()
        code = request.session.get("code_for_chatbot", "")
        last_file_path = request.session.get("last_file_path", "")
        last_repo_name = request.session.get("last_repo_name", "")

        if not user_question:
            return JsonResponse({"error": "Empty question received."})

        if not code:
            return JsonResponse({"response": "⚠️ Code not loaded. Please analyze a file first."})

        full_prompt = f"The following code was analyzed:\n\n{code}\n\nUser asks: {user_question}\n\nPlease respond clearly:"

        try:
            bot_reply = analyze_with_together(full_prompt)
        except Exception as e:
            return JsonResponse({"response": f"❌ Error from model: {str(e)}"})

        # Save to chat history
        if request.user.is_authenticated:
            try:
                history = AnalysisHistory.objects.filter(
                    user=request.user,
                    repo_name=last_repo_name,
                    file_path=last_file_path
                ).latest("created_at")
                chat_entry = f"\n\n👤 {user_question}\n🤖 {bot_reply}"
                history.chat_history += chat_entry
                history.save()
            except AnalysisHistory.DoesNotExist:
                pass

        session_history = request.session.get("chat_history", [])
        session_history.append({"question": user_question, "answer": bot_reply})
        request.session["chat_history"] = session_history

        return JsonResponse({
            "question": user_question,
            "response": bot_reply
        })

    return JsonResponse({"error": "Invalid request method."}, status=405)


# Repo chatbot view
@csrf_exempt
def repo_chatbot_view(request, repo_name):
    access_token = request.session.get('github_access_token')
    if not access_token:
        return redirect('github_login')

    headers = {
        'Authorization': f'token {access_token}',
        'Accept': 'application/vnd.github.v3+json',
    }

    user_response = requests.get('https://api.github.com/user', headers=headers)
    if user_response.status_code != 200:
        return HttpResponse("Failed to fetch user data.")
    username = user_response.json().get('login')

    repo_url = f'https://api.github.com/repos/{username}/{repo_name}'
    repo_response = requests.get(repo_url, headers=headers)
    if repo_response.status_code != 200:
        return HttpResponse("Failed to fetch repository details.")
    repo_data = repo_response.json()

    tree_url = f'https://api.github.com/repos/{username}/{repo_name}/git/trees/{repo_data["default_branch"]}?recursive=1'
    tree_response = requests.get(tree_url, headers=headers)
    if tree_response.status_code != 200:
        return HttpResponse("Failed to fetch file tree.")
    tree_data = tree_response.json()

    source_files = [
        item['path'] for item in tree_data.get('tree', [])
        if item['type'] == 'blob' and item['path'].endswith(('.py', '.js', '.java', '.cpp', '.c', '.ts'))
    ]

    summary_text = f"The repository **{repo_name}** contains `{len(source_files)}` source code files like: {', '.join(source_files[:5])}..."

    context = {
        'repo_name': repo_name,
        'summary': summary_text,
        'source_files': source_files,
    }

    return render(request, 'repo_code.html', context)


# View user history
@login_required
def user_history_view(request):
    history = AnalysisHistory.objects.filter(user=request.user).order_by('-created_at')
    return render(request, "history.html", {"history": history})


# Detail of a single analysis
@login_required
def view_analysis_detail(request, pk):
    try:
        item = AnalysisHistory.objects.get(pk=pk, user=request.user)
    except AnalysisHistory.DoesNotExist:
        return render(request, "history.html", {"error": "History item not found."})

    return render(request, "analysis_detail.html", {"item": item})


# Download as PDF
@login_required
def download_pdf_view(request, history_id):
    try:
        history = AnalysisHistory.objects.get(id=history_id)
    except AnalysisHistory.DoesNotExist:
        return HttpResponse("History not found.", status=404)

    html = f"""
    <html>
      <head>
        <style>
          body {{ font-family: Arial; }}
          pre {{ background: #f4f4f4; padding: 10px; border: 1px solid #ddd; }}
        </style>
      </head>
      <body>
        <h2>📁 {history.repo_name} / {history.file_path}</h2>
        <p><strong>Date:</strong> {history.created_at.strftime('%d %B %Y, %I:%M %p')}</p>

        <h3>🧠 Code:</h3>
        <pre>{history.code or 'No code available.'}</pre>

        <h3>🔍 Analysis:</h3>
        <p>{history.analysis or 'No analysis available.'}</p>

        <h3>🐞 Bug Analysis:</h3>
        <p>{history.bug_analysis or 'No bug analysis available.'}</p>

        <h3>💬 Chat History:</h3>
        <pre>{history.chat_history or 'No chat yet.'}</pre>
      </body>
    </html>
    """

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="analysis_{history_id}.pdf"'
    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse("Error generating PDF", status=500)
    return response
