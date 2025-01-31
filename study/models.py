from django.db import models

class Study(models.Model):
    title = models.CharField(max_length=30)
    branch = models.CharField(max_length=20)
    year = models.IntegerField()
    subject = models.CharField(max_length=100)
    notes_pdf = models.FileField(upload_to='static/pdf', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


