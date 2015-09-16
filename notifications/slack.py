from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from slacker import Slacker

slack = Slacker(settings.SLACK_KEY)


def send(message):
    return slack.chat.post_message(settings.SLACK_CHANNEL, message, username=settings.SLACK_NAME, icon_url=settings.SLACK_ICON)

@csrf_exempt
@require_http_methods(["POST"])
def send_view(request):
    response = send(request.POST["message"])
    return JsonResponse(response.body)
