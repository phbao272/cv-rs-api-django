from rest_framework.response import Response
from rest_framework.decorators import api_view
from api.models import Resumes


@api_view(['GET'])
def get_my_resume(request):
    resume_id = request.query_params['resume_id']

    resume = Resumes.objects.get(id=resume_id)

    resumeSkills = resume.resumeskills_set.all()

    data = {
        "id": resume.id,
        "title": resume.title,
        "name": resume.name,
        "email": resume.email,
        "phone_number": resume.phone_number,
        "user_id": resume.user_id,
        "location": resume.m_location.name,
        "resume_skills": resumeSkills.values('m_skill__id', 'm_skill__name'),
    }

    return Response(data)


@api_view(['GET'])
def get_all_jobs(request):

    rows = Resumes.objects.all()
    list_data = []
    for x in rows:
        list_data.append({"id": x.id, "name": x.name, "email": x.email})

    return Response(list_data)
