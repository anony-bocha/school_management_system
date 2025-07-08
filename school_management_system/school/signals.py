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
                gender='Male'  # TODO: Consider capturing real gender info later
            )
        elif instance.role == 'STUDENT':
            # Get or create a default classroom, adjust "Default" and "A" as needed
            classroom, _ = ClassRoom.objects.get_or_create(name="Default", section="A")
            Student.objects.create(
                user=instance,
                name=full_name,
                age=18,  # Default age; ideally gather this later
                gender='Male',  # TODO: Capture real gender info later
                classroom=classroom,
            )
