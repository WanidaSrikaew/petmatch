from django.contrib import admin
from .models import (
    User,
    UserMatchingProfile,
    Pet,
    PetPhoto,
    Result,
    TopPetRecommendation,
)


class PetPhotoInline(admin.TabularInline):
    model = PetPhoto
    extra = 1


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("user_id", "full_name", "email", "phone", "registration_date")
    search_fields = ("full_name", "email", "phone")


@admin.register(UserMatchingProfile)
class UserMatchingProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user_profile_id",
        "user",
        "residence_type",
        "budget_range",
        "available_time_daily",
        "pet_care_experience",
        "created_at",
    )
    list_filter = ("residence_type", "pet_care_experience", "preferred_pet_type")


@admin.register(Pet)
class PetAdmin(admin.ModelAdmin):
    list_display = (
        "pet_id",
        "pet_name",
        "breed",
        "species",
        "general_availability",
    )
    list_filter = (
        "species",
        "general_availability",
    )
    search_fields = ("pet_name", "breed", "pet_description", "basic_info_summary")
    inlines = [PetPhotoInline]


@admin.register(PetPhoto)
class PetPhotoAdmin(admin.ModelAdmin):
    list_display = ("photo_id", "pet", "photo_type", "is_primary", "image_url")
    list_filter = ("photo_type", "is_primary")


class TopPetRecommendationInline(admin.TabularInline):
    model = TopPetRecommendation
    extra = 0


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = (
        "result_id",
        "user_profile",
        "overall_compatibility_score",
        "timestamp",
    )
    inlines = [TopPetRecommendationInline]


@admin.register(TopPetRecommendation)
class TopPetRecommendationAdmin(admin.ModelAdmin):
    list_display = ("recommendation_id", "result", "pet", "rank", "matching_score")
    list_filter = ("rank",)
