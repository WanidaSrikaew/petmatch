from web.models import Pet, Result, TopPetRecommendation, User, UserMatchingProfile


def calculate_pet_matches(user_profile_data, user=None):
    """
    Calculates compatibility scores for all pets based on user answers
    and saves UserMatchingProfile, Result, and TopPetRecommendation records.
    """
    residence = user_profile_data.get("residence_type", "Condo")
    space = user_profile_data.get("space_size", "Compact")
    budget = int(user_profile_data.get("monthly_budget", 3000))
    time_avail = user_profile_data.get("available_time", "WFH")
    experience = user_profile_data.get("experience", "New")
    allergy = user_profile_data.get("allergy_concern", "No")

    # Create UserMatchingProfile
    profile = UserMatchingProfile.objects.create(
        user=user,
        residence_type=f"{residence} ({space})",
        residence_details=f"Space: {space}, Allergy concern: {allergy}",
        budget_range=f"{budget:,} THB/mo",
        available_time_daily=time_avail,
        pet_care_experience=experience,
        preferred_pet_type="Dog",
        additional_preferences=f"Allergy concern: {allergy}, Space: {space}",
    )

    pets = Pet.objects.all()
    scored_pets = []

    for pet in pets:
        score = 50.0  # Base score
        reasons = []

        b_name = pet.breed.lower()

        # 1. Residence & Space
        if "condo" in residence.lower() or "compact" in space.lower():
            if "poodle" in b_name or "shih tzu" in b_name or "ชิสุ" in b_name or "พุดเดิ้ล" in b_name:
                score += 20
                reasons.append("ขนาดตัวกะทัดรัด เหมาะอย่างยิ่งกับที่พักแบบคอนโดและพื้นที่จำกัด")
            elif "pomeranian" in b_name or "ปอม" in b_name:
                score += 15
                reasons.append("ตัวเล็กปรับตัวในคอนโดได้ดี แต่ต้องระวังเรื่องเสียงเห่าเตือน")
            elif "golden" in b_name or "husky" in b_name or "โกลเด้น" in b_name or "ฮัสกี้" in b_name:
                score -= 20
                reasons.append("ต้องการพื้นที่วิ่งเล่นกว้างขวาง อาจอึดอัดหากเลี้ยงในคอนโด")
        else:  # House with yard
            if "golden" in b_name or "โกลเด้น" in b_name:
                score += 25
                reasons.append("บ้านเดี่ยวมีสวนตอบโจทย์ความต้องการวิ่งเล่นและระบายพลังงานได้สมบูรณ์แบบ")
            elif "husky" in b_name or "ฮัสกี้" in b_name:
                score += 22
                reasons.append("บ้านมีรั้วรอบขอบชิดเหมาะกับสายพันธุ์จอมพลังที่รักการสำรวจ")
            else:
                score += 15
                reasons.append("สามารถเลี้ยงในบ้านที่มีพื้นที่ได้อย่างสบายและมีความสุข")

        # 2. Budget
        if "shih tzu" in b_name or "ชิสุ" in b_name:
            # 800 - 3,000
            if budget >= 1000:
                score += 15
                reasons.append("งบประมาณเฉลี่ย 800 - 3,000 บาท/เดือน สอดคล้องกับงบที่คุณตั้งไว้")
        elif "poodle" in b_name or "พุดเดิ้ล" in b_name:
            # 1,500 - 3,500
            if budget >= 1500:
                score += 15
                reasons.append("งบประมาณเฉลี่ย 1,500 - 3,500 บาท/เดือน ตรงกับงบประมาณที่วางไว้")
        elif "golden" in b_name or "โกลเด้น" in b_name:
            # 2,000 - 4,000
            if budget >= 2000:
                score += 15
                reasons.append("งบประมาณเฉลี่ย 2,000 - 4,000 บาท/เดือน พอดีกับค่าดูแลและอาหาร")
            else:
                score -= 10
                reasons.append("โกลเด้นมีค่าอาหารและการดูแลสุขภาพที่อาจเกินงบเริ่มต้นเล็กน้อย")
        elif "pomeranian" in b_name or "ปอม" in b_name:
            # 4,000 - 6,000
            if budget >= 4000:
                score += 18
                reasons.append("งบประมาณครอบคลุมค่าตัดแต่งขนและอาหารบำรุงสุขภาพระดับพรีเมียม")
            else:
                score -= 8
                reasons.append("ปอมเมอเรเนียนมีค่าดูแลตัดแต่งขนและตรวจฟันเฉลี่ย 4,000 - 6,000 บาท/เดือน")
        elif "husky" in b_name or "ฮัสกี้" in b_name:
            # 1,000 - 5,000
            if budget >= 2500:
                score += 12
                reasons.append("งบประมาณครอบคลุมการดูแลและบำรุงขนดกหนาได้เป็นอย่างดี")

        # 3. Allergy & Shedding
        if allergy.lower() in ("yes", "true", "1"):
            if "poodle" in b_name or "พุดเดิ้ล" in b_name:
                score += 25
                reasons.append("ขนชั้นเดียว ไม่ผลัดขน ปลอดภัยสำหรับคนเป็นโรคภูมิแพ้")
            elif "shih tzu" in b_name or "ชิสุ" in b_name:
                score += 18
                reasons.append("ผลัดขนน้อยมากเมื่อเทียบกับพันธุ์อื่น ดูแลง่ายไม่ฟุ้งกระจาย")
            elif "husky" in b_name or "ฮัสกี้" in b_name:
                score -= 25
                reasons.append("ผลัดขนปริมาณมากเป็นประจำ ไม่แนะนำสำหรับผู้ที่มีอาการภูมิแพ้")
            elif "golden" in b_name or "โกลเด้น" in b_name:
                score -= 10
                reasons.append("มีช่วงผลัดขนตามฤดูกาล ต้องหมั่นแปรงขนเป็นประจำ")

        # 4. Lifestyle / Time
        if time_avail == "WFH" or "home" in time_avail.lower():
            if "poodle" in b_name or "shih tzu" in b_name or "พุดเดิ้ล" in b_name or "ชิสุ" in b_name:
                score += 18
                reasons.append("ชอบอยู่ใกล้ชิดเจ้าของ ติดคนมาก มีความสุขที่สุดเมื่อได้อยู่ห้องเดียวกันกับคุณ")
            elif "pomeranian" in b_name or "ปอม" in b_name:
                score += 12
                reasons.append("มีเพื่อนเล่นแก้เหงาตลอดทั้งวัน ให้เอเนอร์จี้สดใสระหว่างทำงาน")
        elif time_avail == "Busy":
            if "shih tzu" in b_name or "ชิสุ" in b_name:
                score += 10
                reasons.append("รักสงบ สามารถพักผ่อนนอนหลับรอเจ้าของกลับบ้านได้ดี")
            elif "poodle" in b_name or "พุดเดิ้ล" in b_name:
                score -= 5
                reasons.append("ติดคนมาก อาจรู้สึกเหงาหากต้องอยู่ลำพังเป็นเวลานานเกินไป")

        # 5. Experience
        if experience.lower() in ("new", "มือใหม่"):
            if "golden" in b_name or "โกลเด้น" in b_name:
                score += 18
                reasons.append("นิสัยใจดี อ่อนโยน เชื่อฟังคำสั่งยอดเยี่ยม เหมาะกับมือใหม่เป็นอันดับหนึ่ง")
            elif "shih tzu" in b_name or "ชิสุ" in b_name:
                score += 16
                reasons.append("ฝึกง่าย อารมณ์นิ่ง ไม่ก้าวร้าว เหมาะอย่างยิ่งสำหรับผู้เริ่มเลี้ยง")
            elif "poodle" in b_name or "พุดเดิ้ล" in b_name:
                score += 15
                reasons.append("แสนรู้และเรียนรู้ไว สื่อสารกับเจ้าของง่ายแม้ไม่เคยเลี้ยงมาก่อน")
            elif "husky" in b_name or "ฮัสกี้" in b_name:
                score -= 12
                reasons.append("มีความดื้อเงียบและอารมณ์ศิลปิน อาจต้องใช้ความอดทนและเทคนิคในการฝึกฝน")
        else:
            if "husky" in b_name or "ฮัสกี้" in b_name:
                score += 15
                reasons.append("ความท้าทายและความขี้เล่นเหมาะกับผู้เลี้ยงที่มีประสบการณ์")

        # Normalize score between 60 and 98
        score = max(55.0, min(98.0, round(score, 1)))
        
        # Primary reason text
        main_reason = " • ".join(reasons[:3]) if reasons else "มีลักษณะนิสัยและการดูแลที่สอดคล้องกับวิถีชีวิตของคุณ"

        scored_pets.append({
            "pet": pet,
            "score": score,
            "reason": main_reason,
            "reasons_list": reasons
        })

    # Sort descending by score
    scored_pets.sort(key=lambda x: x["score"], reverse=True)

    # Calculate overall average for top 3
    top_3 = scored_pets[:3]
    overall_score = round(sum(item["score"] for item in top_3) / len(top_3), 1) if top_3 else 85.0

    # Save Result
    result_obj = Result.objects.create(
        user_profile=profile,
        overall_compatibility_score=overall_score
    )

    # Save TopPetRecommendations
    recommendations = []
    badge_titles = ["#1 BEST MATCH", "#2 GREAT COMPANION", "#3 TOP MATCH"]
    
    for idx, item in enumerate(top_3):
        rank = idx + 1
        rec = TopPetRecommendation.objects.create(
            result=result_obj,
            pet=item["pet"],
            rank=rank,
            matching_reason=item["reason"],
            matching_score=item["score"]
        )
        recommendations.append({
            "rank": rank,
            "badge_title": badge_titles[idx] if idx < len(badge_titles) else f"#{rank} MATCH",
            "pet": item["pet"],
            "score": item["score"],
            "reason": item["reason"],
            "reasons_list": item["reasons_list"]
        })

    return {
        "profile": profile,
        "result": result_obj,
        "recommendations": recommendations,
        "overall_score": overall_score
    }
