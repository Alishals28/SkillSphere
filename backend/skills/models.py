from django.db import models

# Create your models here.
from django.db import models

class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True)

    def __str__(self):
        return self.name

class MentorSkill(models.Model):
    mentor = models.ForeignKey('mentors.MentorProfile', on_delete=models.CASCADE)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    proficiency = models.PositiveSmallIntegerField(null=True)  # 1-10 scale

    class Meta:
        unique_together = ('mentor', 'skill')
