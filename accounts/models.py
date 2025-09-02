from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.text import slugify
from django.utils import timezone


# -------------------
# Custom User Manager
# -------------------
class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        if not username:
            raise ValueError("The Username field must be set")

        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        return self.create_user(email, username, password, **extra_fields)


# -------------------
# Custom User Model
# -------------------
class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, max_length=255)
    username = models.CharField(max_length=150, unique=True)
    first_name = models.CharField(max_length=150, blank=True, null=True)
    last_name = models.CharField(max_length=150, blank=True, null=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.username


# -------------------
# Blog Post Model
# -------------------
class BlogPost(models.Model):
    CATEGORY_CHOICES = [
        ("brand_activation", "Brand Activation"),
        ("brand_identity", "Brand Identity"),
        ("brand_research", "Brand Research"),
        ("brand_strategy", "Brand Strategy"),
        ("branding", "Branding"),
        ("personal_branding", "personal Branding"),
        ("rebranding", "Rebranding"),
    ]

    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    main_image = models.ImageField(upload_to="blog_images/")
    header_text = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default="branding")
    published_at = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title



# -------------------
# Blog Content Sections
# -------------------
class BlogContent(models.Model):
    post = models.ForeignKey(BlogPost, related_name="contents", on_delete=models.CASCADE)
    sub_header = models.CharField(max_length=255, blank=True, null=True)
    content_text = models.TextField()
    image = models.ImageField(upload_to="blog_contents/", blank=True, null=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.post.title} - {self.sub_header or 'Content'}"


# -------------------
# Sales Counter
# -------------------
class SalesCounter(models.Model):
    soft_copy_sold = models.IntegerField(default=0)
    hard_copy_sold = models.IntegerField(default=10)

    def __str__(self):
        return f"Soft: {self.soft_copy_sold}, Hard: {self.hard_copy_sold}"
    





class UserSale(models.Model):
    BOOK_TYPE_CHOICES = [
        ("soft_copy", "Soft Copy"),
        ("hard_copy", "Hard Copy"),
    ]

    referring_user = models.CharField(max_length=255, blank=True, null=True)  # plain text instead of FK
    book_type = models.CharField(max_length=20, choices=BOOK_TYPE_CHOICES)
    page_name = models.CharField(max_length=100, blank=True, null=True)  # e.g., "mary_page", "jazmin_page"
    purchase_date = models.DateTimeField(default=timezone.now)
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # e.g., 50.00 for soft, 70.00 for hard
    transaction_id = models.CharField(max_length=100, unique=True)  # Paystack transaction ID
    buyer_email = models.EmailField(blank=True, null=True)  # optional, in case you want to store customer’s email

    def __str__(self):
        referrer = self.referring_user or "No Referrer"
        return f"{referrer}: {self.book_type} from {self.page_name or 'N/A'} on {self.purchase_date.strftime('%Y-%m-%d %H:%M')}"