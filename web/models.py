from django.db import models


class User(models.Model):
    user_id = models.AutoField(primary_key=True)
    full_name = models.CharField(max_length=255, verbose_name="Full Name")
    email = models.CharField(max_length=255, unique=True, verbose_name="Email Address")
    phone = models.CharField(max_length=20, verbose_name="Phone Number")
    registration_date = models.DateTimeField(auto_now_add=True, verbose_name="Registration Date")

    class Meta:
        db_table = "user"
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return f"{self.full_name} ({self.email})"


class UserMatchingProfile(models.Model):
    user_profile_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        db_column="user_id",
        null=True,
        blank=True,
        related_name="matching_profiles",
        verbose_name="User",
    )
    residence_type = models.CharField(max_length=255, verbose_name="Residence Type")
    residence_details = models.TextField(verbose_name="Residence Details")
    budget_range = models.CharField(max_length=100, verbose_name="Monthly Budget Range")
    available_time_daily = models.CharField(max_length=100, verbose_name="Daily Available Time")
    pet_care_experience = models.CharField(max_length=100, verbose_name="Pet Care Experience")
    preferred_pet_type = models.CharField(max_length=255, verbose_name="Preferred Pet Type")
    additional_preferences = models.TextField(blank=True, null=True, verbose_name="Additional Preferences")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")

    class Meta:
        db_table = "user_matching_profile"
        verbose_name = "User Matching Profile"
        verbose_name_plural = "User Matching Profiles"

    def __str__(self):
        name = self.user.full_name if self.user else "Anonymous"
        return f"Profile #{self.user_profile_id} - {name} ({self.residence_type})"


class Pet(models.Model):
    AVAILABILITY_CHOICES = [
        ("Common", "Common"),
        ("Specialized", "Specialized"),
    ]

    pet_id = models.AutoField(primary_key=True)
    pet_name = models.CharField(max_length=255, verbose_name="Pet / Breed Name")
    species = models.CharField(max_length=100, verbose_name="Species")
    breed = models.CharField(max_length=100, verbose_name="Breed")
    pet_description = models.TextField(verbose_name="Pet Description")
    basic_info_summary = models.TextField(verbose_name="Basic Info Summary")
    detailed_bio = models.TextField(verbose_name="Detailed Bio / Personality")
    species_care_needs = models.CharField(max_length=255, verbose_name="Species Care Needs")
    special_requirements = models.TextField(verbose_name="Special Health & Care Requirements")
    general_availability = models.CharField(
        max_length=50,
        choices=AVAILABILITY_CHOICES,
        default="Common",
        verbose_name="General Availability",
    )

    class Meta:
        db_table = "pet"
        verbose_name = "Pet"
        verbose_name_plural = "Pets"

    def __str__(self):
        return f"{self.pet_name} ({self.breed})"

    @property
    def primary_photo(self):
        photo = self.photos.filter(is_primary=True).first()
        if not photo:
            photo = self.photos.first()
        return photo.image_url if photo else "https://images.unsplash.com/photo-1543466835-00a7907e9de1?auto=format&fit=crop&w=600&q=80"


class PetPhoto(models.Model):
    PHOTO_TYPE_CHOICES = [
        ("Profile", "Profile"),
        ("Detailed", "Detailed"),
    ]

    photo_id = models.AutoField(primary_key=True)
    pet = models.ForeignKey(
        Pet,
        on_delete=models.CASCADE,
        db_column="pet_id",
        related_name="photos",
        verbose_name="Pet",
    )
    image_url = models.CharField(max_length=500, verbose_name="Image URL")
    is_primary = models.BooleanField(default=False, verbose_name="Is Primary Photo")
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    photo_type = models.CharField(
        max_length=50,
        choices=PHOTO_TYPE_CHOICES,
        default="Profile",
        verbose_name="Photo Type",
    )

    class Meta:
        db_table = "pet_photo"
        verbose_name = "Pet Photo"
        verbose_name_plural = "Pet Photos"

    def __str__(self):
        return f"Photo #{self.photo_id} for {self.pet.pet_name}"


class Result(models.Model):
    result_id = models.AutoField(primary_key=True)
    user_profile = models.ForeignKey(
        UserMatchingProfile,
        on_delete=models.CASCADE,
        db_column="user_profile_id",
        related_name="results",
        verbose_name="Matching Profile",
    )
    overall_compatibility_score = models.FloatField(
        default=0.0, verbose_name="Overall Compatibility Score (%)"
    )
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Timestamp")

    class Meta:
        db_table = "result"
        verbose_name = "Result"
        verbose_name_plural = "Results"

    def __str__(self):
        return f"Result #{self.result_id} - Profile #{self.user_profile.user_profile_id}"


class TopPetRecommendation(models.Model):
    recommendation_id = models.AutoField(
        primary_key=True, db_column="Top_Pet_Recommendation"
    )
    result = models.ForeignKey(
        Result,
        on_delete=models.CASCADE,
        db_column="result_id",
        related_name="recommendations",
        verbose_name="Result",
    )
    pet = models.ForeignKey(
        Pet,
        on_delete=models.CASCADE,
        db_column="pet_id",
        related_name="recommendations",
        verbose_name="Pet",
    )
    rank = models.IntegerField(default=1, verbose_name="Rank (1-3)")
    matching_reason = models.TextField(verbose_name="Matching Reason")
    matching_score = models.FloatField(default=0.0, verbose_name="Matching Score (%)")

    class Meta:
        db_table = "top_pet_recommendation"
        verbose_name = "Top Pet Recommendation"
        verbose_name_plural = "Top Pet Recommendations"

    def __str__(self):
        return f"Rank #{self.rank}: {self.pet.pet_name} ({self.matching_score:.1f}%)"
