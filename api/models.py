from django.db import models


class MLocations(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)

    class Meta:
        db_table = 'm_locations'


class MSkills(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)

    class Meta:
        db_table = 'm_skills'


class Resumes(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=255)

    user_id = models.IntegerField()
    m_location = models.ForeignKey(MLocations, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'resumes'


class Jobs(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    number_of_recruit = models.IntegerField()
    deadline = models.DateField()
    description = models.TextField()
    active = models.IntegerField()

    company_id = models.IntegerField()
    m_working_from_id = models.IntegerField()
    m_location_id = models.IntegerField()
    m_experience_id = models.IntegerField()
    m_salary_id = models.IntegerField()

    class Meta:
        db_table = 'jobs'


# Create model with name is ResumeSkills and table name is resume_skills, and add field id, resume_id, m_skill_id. resume_id is foreign key from table resumes and m_skill_id is foreign key from table m_skills

class ResumeSkills(models.Model):
    id = models.AutoField(primary_key=True)
    resume = models.ForeignKey(Resumes, on_delete=models.CASCADE)
    m_skill = models.ForeignKey(MSkills, on_delete=models.CASCADE)

    class Meta:
        db_table = 'resume_skills'
