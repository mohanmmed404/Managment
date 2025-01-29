from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext as _
from django.contrib.staticfiles.templatetags.staticfiles import static


class Branch(models.Model):
    name = models.CharField(max_length=100, unique=True)
    picture = models.ImageField(upload_to="branches/pictures/", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Branch')
        verbose_name_plural = _('Branches')

    def __str__(self):
        return self.name

class ProfileQuerySet(models.QuerySet):
    def profiles_for_user(self, user):
        """
        Returns all profiles (customers and editors) assigned to the branches of the given userEditor.
        """
        if user.profile.role == Profile.ROLE_USER_EDITOR:
            # Filter profiles based on branches assigned to the userEditor
            return self.filter(branches__in=user.profile.branches.all()).distinct()
        return self.none()  # Return no results if the user is not an editor

class ProfileManager(models.Manager):
    def get_queryset(self):
        return ProfileQuerySet(self.model, using=self._db)

    def profiles_for_user(self, user):
        return self.get_queryset().profiles_for_user(user)


class Profile(models.Model):
    ROLE_Profile = 'profile'
    ROLE_USER_ADMIN = 'userAdmin'
    ROLE_USER_EDITOR = 'userEditor'

    ROLE_CHOICES = [
        (ROLE_Profile, _("Profile User")),
        (ROLE_USER_ADMIN, _("User Admin")),
        (ROLE_USER_EDITOR, _("User Editor")),
    ]

    GENDER_MALE = 1
    GENDER_FEMALE = 2
    GENDER_CHOICES = [
        (GENDER_MALE, _("Male")),
        (GENDER_FEMALE, _("Female")),
    ]

    user = models.OneToOneField(User, related_name="profile", on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to="customers/profiles/avatars/", null=True, blank=True)
    birthday = models.DateField(null=True, blank=True)
    gender = models.PositiveSmallIntegerField(choices=GENDER_CHOICES, null=True, blank=True)
    phone = models.CharField(max_length=32, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    number = models.CharField(max_length=32, null=True, blank=True)
    city = models.CharField(max_length=50, null=True, blank=True)
    zip = models.CharField(max_length=30, null=True, blank=True)
    branches = models.ManyToManyField(Branch, related_name="profiles", blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_Profile)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ProfileManager()

    class Meta:
        verbose_name = _('Profile')
        verbose_name_plural = _('Profiles')

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"

    @property
    def get_avatar(self):
        return self.avatar.url if self.avatar else static('assets/img/team/default-profile-picture.png')
