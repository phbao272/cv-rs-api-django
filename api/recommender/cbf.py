from sklearn.metrics.pairwise import cosine_similarity
from rest_framework.response import Response
from rest_framework.decorators import api_view
from api.models import Resumes, Jobs

from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer


@api_view(['GET'])
def getByCBF(request):
    user_id = request.query_params['user_id']

    res = cbf(user_id)

    return Response(res)


def cbf(user_id):
    resume = getResumeById(user_id)
    jobs = getJobForResume(resume)

    resume_skill = resume['resume_skills']

    resume_skill_ids = [skill['m_skill__id'] for skill in resume_skill]

    for job in jobs:

        job_skill_ids = [skill['m_skill__id'] for skill in job["job_skills"]]

        filter_resume_skill_ids = list(
            filter(lambda x: x in job_skill_ids, resume_skill_ids))

        similarity = similarity_cbf(filter_resume_skill_ids, job_skill_ids)
        job['similarity'] = similarity

    jobs_sort = sorted(jobs, key=lambda x: x["similarity"], reverse=True)

    n = min(20, len(jobs_sort))

    return jobs_sort[:n]


def similarity_cbf(resume_skill_ids, job_skill_ids):

    doc = [convertSkillToText(resume_skill_ids),
           convertSkillToText(job_skill_ids)]

    # print("doc", doc)

    # Create a CountVectorizer object and fit it to the documents
    count_vectorizer = CountVectorizer()
    count_matrix = count_vectorizer.fit_transform(doc)

    # Create a TfidfTransformer object and fit it to the count matrix
    tfidf_transformer = TfidfTransformer()
    tfidf_matrix = tfidf_transformer.fit_transform(count_matrix)

    # Calculate the cosine similarity between the two documents
    cosine_sim = cosine_similarity(tfidf_matrix[0], tfidf_matrix[1])[0][0]

    # print("The similarity score between the two lists of skills is:", cosine_sim)

    return cosine_sim


def getResumeById(user_id):

    resume = Resumes.objects.get(user=user_id)

    resumeSkills = resume.resumeskills_set.all()

    data = {
        "id": resume.id,
        "title": resume.title,
        "name": resume.name,

        "user_id": resume.user.id,
        "m_location_id": resume.m_location.id,
        "m_education_level_id": resume.m_education_level.id,
        "m_experience_id": resume.m_experience.id,
        "m_working_form_id": resume.m_working_form.id,

        "resume_skills": resumeSkills.values('m_skill__id', 'm_skill__name'),
    }

    return data


def getJobForResume(resume):

    jobs = Jobs.objects.filter(
        m_location=resume['m_location_id'],
        m_working_form=resume['m_working_form_id'],
        m_education_level_id__lte=resume["m_education_level_id"],
        m_experience_id__lte=resume["m_experience_id"],
    )

    data = []

    for job in jobs:
        d = {
            "id": job.id,
            "title": job.title,
            "description": job.description,


            "company": {"id": job.company.id,
                        "name": job.company.name,
                        "photo": job.company.photo},

            "m_location_id": job.m_location.id,
            "location": {"id": job.m_location.id,
                         "name": job.m_location.name},

            "m_education_level_id": job.m_education_level.id,
            "m_education_level_name": job.m_education_level.name,

            "m_experience_id": job.m_experience.id,
            "m_experience_name": job.m_experience.name,

            "m_working_form_id": job.m_working_form.id,

            "m_salary_id": job.m_salary.id,
            "salary": {"id": job.m_salary.id,
                       "name": job.m_salary.name},

            "job_skills": job.jobskills_set.all().values('m_skill__id', 'm_skill__name'),
        }

        data.append(d)

    return data


def convertSkillToText(skills):

    text = ""

    for skill in skills:
        text += "skill_" + str(skill) + " "

    return text
