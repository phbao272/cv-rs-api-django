from django.http import JsonResponse
from rest_framework.response import Response

from rest_framework.decorators import api_view
from api.models import Resumes
from api.models import Jobs


@api_view(['GET'])
def testFn(request):
    resume_id = request.query_params['resume_id']

    resume = getMyResume(resume_id)

    jobs = getJobForResume(resume)

    return Response(jobs)


def getMyResume(resume_id: int):

    resume = Resumes.objects.get(id=resume_id)

    resumeSkills = resume.resumeskills_set.all()

    data = {
        "id": resume.id,
        "title": resume.title,
        "name": resume.name,
        "email": resume.email,
        "phone_number": resume.phone_number,
        "user_id": resume.user_id,
        "m_location_id": resume.m_location.id,
        "resume_skills": resumeSkills.values('m_skill__id', 'm_skill__name'),
    }

    return data


def getJobForResume(resume):
    jobs = Jobs.objects.filter(m_location=resume['m_location_id'])

    print("resume['m_location_id']", resume['m_location_id'])

    list_jobs = []
    for x in jobs:
        list_jobs.append({"id": x.id, "title": x.title,
                         "m_location_id": x.m_location.id})

    return list_jobs
