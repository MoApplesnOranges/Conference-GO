from django.http import JsonResponse
from common.json import ModelEncoder
from django.views.decorators.http import require_http_methods
from .models import Attendee, ConferenceVO, AccountVO
import json

class ConferenceVODetailEncoder(ModelEncoder):
    model = ConferenceVO
    properties = ["name", "import_href"]

class AttendeeListEncoder(ModelEncoder):
    model = Attendee
    properties = ["email", "name"]

class AttendeeDetailEncoder(ModelEncoder):
    model = Attendee
    properties = [
        "email",
        "name",
        "company_name",
        "created",
        "conference",
    ]
    encoders = {
        "conference": ConferenceVODetailEncoder(),
    }
    def get_extra_data(self, o):
        count = len(AccountVO.objects.filter(email=o.email))
        if count > 0:
            return {"has_account": True}
        else:
            return {"has_account": False}


@require_http_methods(["GET", "POST"])
def api_list_attendees(request, conference_vo_id=None):
    if request.method == "GET":
        attendees = Attendee.objects.filter(conference=conference_vo_id)
        return JsonResponse({"attendees": attendees}, encoder=AttendeeListEncoder)
    else:
        content = json.loads(request.body)
        try:
            conference_href = f"/api/conferences/{conference_vo_id}/"
            conference = ConferenceVO.objects.get(import_href=conference_href)
            content["conference"] = conference
        except ConferenceVO.DoesNotExist:
            return JsonResponse({"message": "Invalid conference id"}, status=400)
        attendee = Attendee.objects.create(**content)
        return JsonResponse(attendee, encoder=AttendeeDetailEncoder, safe=False)


def api_show_attendee(request, id):
    attendee = Attendee.objects.get(id=id)

    return JsonResponse(
        {
            "email": attendee.email,
            "name": attendee.name,
            "company_name": attendee.company_name,
            "created": attendee.created,
            "conference": {
                "name": attendee.conference.name,
                "href": attendee.conference.import_href
            },
            # "has_account": attendee.has_account
        }
    )
