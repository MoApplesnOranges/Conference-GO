from django.http import JsonResponse
from common.json import ModelEncoder
from events.api_views import ConferenceListEncoder
from .models import Presentation
from django.views.decorators.http import require_http_methods
import pika, json

# class PresentationListEncoder(ModelEncoder):
#     model = Presentation
#     properties = [
#         "presenter_name",
#         "presenter_email",
#         "title",
#     ]
#     encoders = {
#         "conference": ConferenceListEncoder()
#     }

#     def get_extra_data(self, o):
#         return {"status": o.status.name}

@require_http_methods(["GET", "POST"])
def api_list_presentations(request, conference_id):
    if request.method == "GET":
        presentations = [
            {
                "title": p.title,
                "status": p.status.name,
                "href": p.get_api_url(),
            }
            for p in Presentation.objects.filter(conference=conference_id)
        ]
        return JsonResponse({"presentations": presentations})
    else:
        content = json.loads(request.body)
        try:
            presentation = Presentation.objects.get(id=content["presentation"])
            content["presentation"] = presentation
        except Presentation.DoesNotExist:
            return JsonResponse(
                {"message": "Invalid presentation id"},
                status=400
            )
        presentation = Presentation.objects.create(**content)
        return JsonResponse(
            presentation,
            encoder=PresentationDetailEncoder,
            safe=False
        )

class PresentationDetailEncoder(ModelEncoder):
    model = Presentation
    properties = [
        "presenter_name",
        "company_name",
        "presenter_email",
        "title",
        "synopsis",
        "created",
        "conference",
    ]
    encoders = {
        "conference": ConferenceListEncoder()
    }

    def get_extra_data(self, o):
        return {"status": o.status.name}


def api_show_presentation(request, id):
    """
    Returns the details for the Presentation model specified
    by the id parameter.

    This should return a dictionary with the presenter's name,
    their company name, the presenter's email, the title of
    the presentation, the synopsis of the presentation, when
    the presentation record was created, its status name, and
    a dictionary that has the conference name and its URL

    {
        "presenter_name": the name of the presenter,
        "company_name": the name of the presenter's company,
        "presenter_email": the email address of the presenter,
        "title": the title of the presentation,
        "synopsis": the synopsis for the presentation,
        "created": the date/time when the record was created,
        "status": the name of the status for the presentation,
        "conference": {
            "name": the name of the conference,
            "href": the URL to the conference,
        }
    }
    """
    presentation = Presentation.objects.get(id=id)
    return JsonResponse(
        presentation,
        encoder=PresentationDetailEncoder,
        safe=False
    )
    # return JsonResponse({
    #     "presenter_name": presentation.presenter_name,
    #     "company_name": presentation.company_name,
    #     "presenter_email": presentation.presenter_email,
    #     "title": presentation.title,
    #     "synopsis": presentation.synopsis,
    #     "created": presentation.created,
    #     "status": presentation.status.name,
    #     "conference": {
    #         "name": presentation.conference.name,
    #         "href": presentation.conference.get_api_url()
    #     }
    # })

@require_http_methods(["PUT"])
def api_approve_presentation(request, id):
    presentation = Presentation.objects.get(id=id)
    presentation.approve()
    # try:
    parameters = pika.ConnectionParameters(host="rabbitmq")
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    channel.queue_declare(queue="presentation_approvals")
    dic = {
        "presenter_name": presentation.presenter_name,
        "presenter_email": presentation.presenter_email,
        "title": presentation.title
    }
    string_dic = json.dumps(dic)
    channel.basic_publish(
        exchange="",
        routing_key="presentation_approvals",
        body=string_dic,
    )
    print("Hello")
    connection.close()
    # except Exception as e:
    #     print("Error")
    #     print(str(e))
    return JsonResponse(
        presentation,
        encoder=PresentationDetailEncoder,
        safe=False
    )


@require_http_methods(["PUT"])
def api_reject_presentation(request, id):
    presentation = Presentation.objects.get(id=id)
    presentation.reject()
    parameters = pika.ConnectionParameters(host="rabbitmq")
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    channel.queue_declare(queue="presentation_rejections")
    dic = {
        "presenter_name": presentation.presenter_name,
        "presenter_email": presentation.presenter_email,
        "title": presentation.title
    }
    string_dic = json.dumps(dic)
    channel.basic_publish(
        exchange="",
        routing_key="presentation_rejections",
        body=string_dic,
    )
    connection.close()
    return JsonResponse(
        presentation,
        encoder=PresentationDetailEncoder,
        safe=False
    )
