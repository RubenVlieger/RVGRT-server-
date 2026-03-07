import os
import requests
from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.conf import settings

@staff_member_required
def admin_logs_view(request):
    log_file = os.path.abspath(os.path.join(settings.BASE_DIR, '..', '..', 'logs', 'server.log'))
    
    # Handle chat broadcast
    if request.method == 'POST':
        message = request.POST.get('message', '').strip()
        if message:
            try:
                # Docker internal networking: fastapi service is 'rvgrt-backend' or 'localhost' if running locally
                backend_url = os.environ.get('FASTAPI_URL', 'http://rvgrt-backend:8000')
                requests.post(f"{backend_url}/internal/broadcast", json={"message": message}, timeout=2)
            except Exception as e:
                pass # Ignore if backend is down
        return redirect('admin_logs')

    # Read last 1000 lines
    lines = []
    if os.path.exists(log_file):
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                # Naive approach, good enough for small logs
                all_lines = f.readlines()
                lines = all_lines[-1000:]
        except Exception:
            lines = ["Error reading log file."]
    else:
        lines = ["Log file does not exist yet. Please start the FastAPI server."]

    return render(request, 'admin_app/logs.html', {'logs': lines})
