from django.contrib import admin
from unfold.admin import ModelAdmin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, BlogPost, BlogContent, SalesCounter, UserSale


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin, ModelAdmin):
    list_display = ("email", "username", "is_staff", "is_active", "date_joined")
    list_filter = ("is_staff", "is_active")
    search_fields = ("email", "username")
    ordering = ("-date_joined",)

    fieldsets = (
        (None, {"fields": ("email", "username", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "username", "password1", "password2", "is_active", "is_staff"),
        }),
    )


@admin.register(BlogPost)
class BlogPostAdmin(ModelAdmin):
    list_display = ("title", "author", "category", "date", "published_at")
    search_fields = ("title", "author__username")
    list_filter = ("category", "published_at", "author")
    prepopulated_fields = {"slug": ("title",)}

    def date(self, obj):
        return obj.published_at.date()
    date.admin_order_field = "published_at"
    date.short_description = "Date"


@admin.register(BlogContent)
class BlogContentAdmin(ModelAdmin):
    list_display = ("post", "sub_header")
    search_fields = ("sub_header", "post__title")


@admin.register(SalesCounter)
class SalesCounterAdmin(ModelAdmin):
    list_display = ("soft_copy_sold", "hard_copy_sold")
    search_fields = ("soft_copy_sold", "hard_copy_sold")


@admin.register(UserSale)
class UserSaleAdmin(ModelAdmin):
    list_display = ("referring_user", "buyer_email", "book_type", "page_name", "amount", "purchase_date", "transaction_id")
    list_filter = ("book_type", "page_name", "purchase_date")
    search_fields = ("referring_user", "buyer_email", "transaction_id", "page_name")
    date_hierarchy = "purchase_date"
    ordering = ("-purchase_date",)
    list_per_page = 25