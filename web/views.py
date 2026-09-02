import json
from django.contrib.auth import logout
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt
from web.models import Pet, PetPhoto, Result, TopPetRecommendation, User, UserMatchingProfile
from web.services import calculate_pet_matches


def index_view(request):
    pets = Pet.objects.prefetch_related("photos").all()
    recent_result = Result.objects.prefetch_related("recommendations__pet__photos").order_by("-timestamp").first()
    
    context = {
        "pets": pets,
        "recent_result": recent_result,
    }
    return render(request, "index.html", context)


@csrf_exempt
def api_match_view(request):
    if request.method == "POST":
        try:
            if request.content_type == "application/json":
                data = json.loads(request.body.decode("utf-8"))
            else:
                data = request.POST.dict()

            full_name = data.get("full_name", "ผู้ใช้งานทั่วไป (Guest)")
            email = data.get("email", "guest@petmatch.local")
            phone = data.get("phone", "08x-xxx-xxxx")

            # Create or get user
            user, _ = User.objects.get_or_create(
                email=email,
                defaults={"full_name": full_name, "phone": phone}
            )

            result_data = calculate_pet_matches(data, user=user)

            # Build serializable response
            recommendations = []
            for item in result_data["recommendations"]:
                pet = item["pet"]
                recommendations.append({
                    "rank": item["rank"],
                    "badge_title": item["badge_title"],
                    "pet_id": pet.pet_id,
                    "pet_name": pet.pet_name,
                    "breed": pet.breed,
                    "species": pet.species,
                    "general_availability": pet.general_availability,
                    "score": item["score"],
                    "reason": item["reason"],
                    "reasons_list": item["reasons_list"],
                    "photo_url": pet.primary_photo,
                    "basic_info_summary": pet.basic_info_summary,
                    "species_care_needs": pet.species_care_needs,
                    "special_requirements": pet.special_requirements,
                    "detailed_bio": pet.detailed_bio,
                })

            return JsonResponse({
                "status": "success",
                "overall_score": result_data["overall_score"],
                "recommendations": recommendations,
            })
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)

    return JsonResponse({"status": "error", "message": "Method not allowed"}, status=405)


@staff_member_required(login_url="/admin/login/?next=/backoffice/")
def backoffice_view(request):
    total_users = User.objects.count()
    total_pets = Pet.objects.count()
    
    common_count = Pet.objects.filter(general_availability="Common").count()
    specialized_count = Pet.objects.filter(general_availability="Specialized").count()
    common_pct = round((common_count / total_pets * 100) if total_pets > 0 else 0)
    specialized_pct = round((specialized_count / total_pets * 100) if total_pets > 0 else 0)

    matching_attempts = Result.objects.count()
    active_listings = PetPhoto.objects.filter(is_primary=True).count()

    profiles = UserMatchingProfile.objects.select_related("user").order_by("-created_at")[:15]
    pets_list = Pet.objects.prefetch_related("photos").all()
    recent_attempts = Result.objects.select_related("user_profile__user").prefetch_related("recommendations__pet__photos").order_by("-timestamp")[:15]

    context = {
        "total_users": total_users,
        "total_pets": total_pets,
        "common_pct": common_pct,
        "specialized_pct": specialized_pct,
        "matching_attempts": matching_attempts,
        "active_listings": active_listings,
        "profiles": profiles,
        "pets_list": pets_list,
        "recent_attempts": recent_attempts,
    }
    return render(request, "backoffice.html", context)


def pet_detail_api(request, pet_id):
    pet = get_object_or_404(Pet, pet_id=pet_id)
    photos = [p.image_url for p in pet.photos.all()]
    return JsonResponse({
        "pet_id": pet.pet_id,
        "pet_name": pet.pet_name,
        "breed": pet.breed,
        "species": pet.species,
        "pet_description": pet.pet_description,
        "basic_info_summary": pet.basic_info_summary,
        "detailed_bio": pet.detailed_bio,
        "species_care_needs": pet.species_care_needs,
        "special_requirements": pet.special_requirements,
        "general_availability": pet.general_availability,
        "photos": photos if photos else [pet.primary_photo],
    })


def logout_view(request):
    logout(request)
    return redirect("/")
