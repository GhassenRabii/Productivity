import json
import requests
from django.conf import settings

class SchedulerError(Exception):
    pass

def schedule_task(task_id: str, due_at_iso: str, owner_id: str, user_email: str):
    url = f"{settings.API_BASE_URL}/tasks/{task_id}/schedule"
    payload = {
        "dueAtIso": due_at_iso,                     # ISO 8601
        "ownerId": owner_id,
        "userEmail": user_email,
        "template": "TaskReminder",
        "ctaUrl": f"https://productivity.dunedivision.com/tasks/{task_id}",
        "unsubUrl": f"https://productivity.dunedivision.com/unsub?u={owner_id}",
        "timezone": "Europe/Berlin",
    }
    headers = {"Content-Type": "application/json"}
    if settings.API_KEY:
        headers["x-api-key"] = settings.API_KEY

    r = requests.post(url, headers=headers, data=json.dumps(payload), timeout=10)
    if r.status_code >= 300:
        raise SchedulerError(f"{r.status_code} {r.text}")
    return r.json() if r.content else {}
