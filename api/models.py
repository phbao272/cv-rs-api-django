from django.db import models


class Users(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    role = models.IntegerField()

    class Meta:
        db_table = 'users'


class MEducationLevels(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    value = models.IntegerField()

    class Meta:
        db_table = 'm_education_levels'


class MExperiences(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    value = models.IntegerField()

    class Meta:
        db_table = 'm_experiences'


class MJobs(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)

    class Meta:
        db_table = 'm_jobs'


class MLocations(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)

    class Meta:
        db_table = 'm_locations'


class MSalaries(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)

    class Meta:
        db_table = 'm_salaries'


class MSkills(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)

    class Meta:
        db_table = 'm_skills'


class MWorkingForms(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)

    class Meta:
        db_table = 'm_working_forms'


class Resumes(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    birthday = models.DateField()
    phone_number = models.CharField(max_length=255)
    avatar = models.CharField(max_length=255)

    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    m_location = models.ForeignKey(MLocations, on_delete=models.CASCADE)
    m_education_level = models.ForeignKey(
        MEducationLevels, on_delete=models.CASCADE)
    m_experience = models.ForeignKey(MExperiences, on_delete=models.CASCADE)
    m_working_form = models.ForeignKey(MWorkingForms, on_delete=models.CASCADE)
    m_job = models.ForeignKey(MJobs, on_delete=models.CASCADE)

    class Meta:
        db_table = 'resumes'


class ResumeSkills(models.Model):
    id = models.AutoField(primary_key=True)
    resume = models.ForeignKey(Resumes, on_delete=models.CASCADE)
    m_skill = models.ForeignKey(MSkills, on_delete=models.CASCADE)

    class Meta:
        db_table = 'resume_skills'


class Companies(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField()
    photo = models.CharField(max_length=255)

    user = models.ForeignKey(Users, on_delete=models.CASCADE)

    class Meta:
        db_table = 'companies'


class Jobs(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    number_of_recruit = models.IntegerField()
    deadline = models.DateField()
    active = models.IntegerField()

    company = models.ForeignKey(Companies, on_delete=models.CASCADE)
    m_working_form = models.ForeignKey(MWorkingForms, on_delete=models.CASCADE)
    m_location = models.ForeignKey(MLocations, on_delete=models.CASCADE)
    m_education_level = models.ForeignKey(
        MEducationLevels, on_delete=models.CASCADE)
    m_experience = models.ForeignKey(MExperiences, on_delete=models.CASCADE)
    m_salary = models.ForeignKey(MSalaries, on_delete=models.CASCADE)
    m_job = models.ForeignKey(MJobs, on_delete=models.CASCADE)

    class Meta:
        db_table = 'jobs'


class JobSkills(models.Model):
    id = models.AutoField(primary_key=True)
    job = models.ForeignKey(Jobs, on_delete=models.CASCADE)
    m_skill = models.ForeignKey(MSkills, on_delete=models.CASCADE)

    class Meta:
        db_table = 'job_skills'


class UserInteractionJobs(models.Model):
    id = models.AutoField(primary_key=True)
    number_of_click = models.IntegerField()
    applied = models.IntegerField()
    liked = models.IntegerField()
    rating = models.FloatField()
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    job = models.ForeignKey(Jobs, on_delete=models.CASCADE)

    class Meta:
        db_table = 'user_interaction_jobs'


class UserSimilarities(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    user_similarity = models.TextField()

    class Meta:
        db_table = 'user_similarities'


class CFUserJobs(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    job_recommends = models.TextField()

    class Meta:
        db_table = 'cf_user_jobs'
