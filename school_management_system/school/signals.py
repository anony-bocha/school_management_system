from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import User, Teacher, Student, ClassRoom

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        if instance.role == 'TEACHER':
            Teacher.objects.create(user=instance, name=instance.get_full_name() or instance.username, gender='Male')  # default gender
        elif instance.role == 'STUDENT':
            # Get or create a default classroom
            classroom, _ = ClassRoom.objects.get_or_create(name="Default", section="A")
            Student.objects.create(
                user=instance,
                name=instance.get_full_name() or instance.username,
                age=18,  # default age
                gender='Male',  # default gender
                classroom=classroom,
            )
