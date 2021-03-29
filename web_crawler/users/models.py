from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils import timezone

# Create your models here.
from web_crawler import settings


class APIUserManager(BaseUserManager):
    """Custom user manager."""

    use_in_migrations = True

    def create_user(self, validated_data):
        """Create a user."""
        if not validated_data.get("email"):
            raise ValueError("Users must have an email address")

        user = self.model(
            email=self.normalize_email(validated_data.get("email")),
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
            phone_number=validated_data.get("phone_number", ""),
            username=validated_data.get("user_name", ""),
            department=validated_data.get("department", ""),
            # email_otp_exp_time=validated_data.get("email_otp_exp_time", None),
            # email_otp=validated_data.get("email_otp", 0),
        )

        user.set_password(validated_data.get("password", settings.DEFAULT_PASSWORD))
        user.save()
        return user

    def create_superuser(self, email, password):
        """Create a superuser."""
        super_user_obj = {}
        super_user_obj["email"] = email
        super_user_obj["password"] = password
        super_user_obj["first_name"] = "Admin"
        user = self.create_user(super_user_obj)
        user.is_staff = True
        user.is_superuser = True
        user.is_verified = True
        user.save()
        return user


class APIUser(AbstractBaseUser, PermissionsMixin):
    """Custom user class."""

    USERNAME_FIELD = "email"

    USER_TYPE_ADMIN = "admin"

    # username field not used, only here to make django-rest-auth work
    username = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=False, unique=True)
    first_name = models.CharField("first name", max_length=50, null=True, blank=True)
    last_name = models.CharField("last name", max_length=50, null=True, blank=True)
    phone_number = models.CharField(max_length=20, verbose_name="phone number")

    is_staff = models.BooleanField(
        "staff status",
        default=False,
        help_text="Designates whether the user can log into this admin site.",
    )
    is_active = models.BooleanField(
        "active",
        default=True,
        help_text="Designates whether this user should be treated as active. "
        "Deselect this instead of deleting accounts.",
    )
    is_verified = models.BooleanField(default=True)
    email_otp = models.IntegerField(null=True, blank=True)
    email_otp_exp_time = models.DateTimeField(null=True, blank=True)
    image_url = models.ImageField(blank=True, null=True, upload_to="user_images/")
    department = models.CharField(blank=True, null=True, max_length=300)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    objects = APIUserManager()

    class Meta:
        """Model meta data."""

        verbose_name = "user"
        verbose_name_plural = "users"

    def get_full_name(self):
        """Get full name."""
        full_name = "%s %s" % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        """Get short name."""
        return self.first_name


class Token(models.Model):
    user_id = models.ForeignKey(
        APIUser, blank=True, null=True, on_delete=models.CASCADE
    )
    refresh_token = models.TextField(blank=True, null=True)
    access_token = models.TextField(blank=True, null=True)
    is_expired = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class UserSearch(models.Model):
    user_id = models.ForeignKey(
        APIUser, blank=True, null=True, on_delete=models.CASCADE
    )
    search_value = models.CharField(blank=True, null=True, max_length=100)
    search_type = models.CharField(blank=True, null=True, max_length=100)
    needs_monitoring = models.BooleanField(default=False)
    search_count = models.IntegerField(default=0)
    search_result_id = models.CharField(blank=True, null=True, max_length=100)
    patent_count = models.IntegerField(default=0, null=True, blank=True)
    patent_id = models.CharField(blank=True, null=True, max_length=500)
    patent_name = models.TextField(blank=True, null=True)
    innovator_count = models.IntegerField(default=0, null=True, blank=True)
    innovator_id = models.CharField(blank=True, null=True, max_length=500)
    innovator_name = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class UserBookmark(models.Model):
    user_id = models.ForeignKey(
        APIUser, blank=True, null=True, on_delete=models.CASCADE
    )
    content_id = models.IntegerField(blank=False, null=False)
    content_text = models.CharField(blank=True, null=True, max_length=100)
    content_url = models.CharField(blank=True, null=True, max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class UserNote(models.Model):
    user_id = models.ForeignKey(
        APIUser, blank=True, null=True, on_delete=models.CASCADE
    )
    note_text = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class UserNotification(models.Model):
    user_id = models.ForeignKey(
        APIUser, blank=True, null=True, on_delete=models.CASCADE
    )
    notification_text = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


# class Patent(models.Model):
#     user_id = models.ForeignKey(
#         APIUser, blank=True, null=True, on_delete=models.CASCADE
#     )
#     patent_count = models.IntegerField(default=0, null=True, blank=True)
#     search_value = models.IntegerField(default=0, null=True, blank=True)
#     patent_id = models.CharField(blank=True, null=True, max_length=500)
#     name = models.TextField(blank=True, null=True)
#     country = models.CharField(blank=True, null=True, max_length=200)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#
#
# class Innovators(models.Model):
#     user_id = models.ForeignKey(
#         APIUser, blank=True, null=True, on_delete=models.CASCADE
#     )
#     innovator_count = models.IntegerField(default=0, null=True, blank=True)
#     search_value = models.IntegerField(default=0, null=True, blank=True)
#     innovator_id = models.CharField(blank=True, null=True, max_length=500)
#     name = models.TextField(blank=True, null=True)
#     country = models.CharField(blank=True, null=True, max_length=200)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
