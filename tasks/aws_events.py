import os, json, boto3

REGION = os.getenv("AWS_DEFAULT_REGION", "eu-central-1")
BUS_NAME = os.getenv("APP_EVENT_BUS_NAME", "domain-events-bus")

_events = None
def _client():
    global _events
    if _events is None:
        _events = boto3.client("events", region_name=REGION)
    return _events

def put_task_created(detail: dict):
    """
    detail schema we send:
    {
      "task_id": str,
      "owner_id": str,
      "owner_email": str,
      "owner_name": str,
      "task_title": str,
      "dueAtIso": "YYYY-MM-DDTHH:MM:SSZ"
    }
    """
    _client().put_events(Entries=[{
        "Source": "yourapp.tasks",
        "DetailType": "TaskCreated",
        "EventBusName": BUS_NAME,
        "Detail": json.dumps(detail),
    }])
