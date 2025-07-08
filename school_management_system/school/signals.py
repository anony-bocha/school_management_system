from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, Teacher, Student, ClassRoom

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        full_name = instance.get_full_name() or instance.username
        if instance.role == 'TEACHER':
            Teacher.objects.create(
                user=instance,
                name=full_name,
                gender='Male'  # You might want to improve this later
            )
        elif instance.role == 'STUDENT':
            # Get or create a default classroom (adjust as needed)
            classroom, _ = ClassRoom.objects.get_or_create(name="Default", section="A")
            Student.objects.create(
                user=instance,
                name=full_name,
                age=18,  # Default age; adjust as necessary
                gender='Male',  # Default gender; consider collecting this info later
                classroom=classroom,
            )
