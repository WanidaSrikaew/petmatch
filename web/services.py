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

    pref_pet = user_profile_data.get("preferred_pet_type", "Any")

    # Create UserMatchingProfile
    profile = UserMatchingProfile.objects.create(
        user=user,
        residence_type=f"{residence} ({space})",
        residence_details=f"Space: {space}, Allergy concern: {allergy}",
        budget_range=f"{budget:,} THB/mo",
        available_time_daily=time_avail,
        pet_care_experience=experience,
        preferred_pet_type=pref_pet,
        additional_preferences=f"Allergy concern: {allergy}, Space: {space}",
    )

    pets = Pet.objects.all()
    scored_pets = []

    for pet in pets:
        score = 50.0  # Base score
        reasons = []

        b_name = pet.breed.lower()
        s_name = pet.species.lower()
        # Species preference filter/bonus
        if pref_pet == "Dog" and not ("dog" in s_name or "สุนัข" in s_name):
            score -= 50
        elif pref_pet == "Cat" and not ("cat" in s_name or "แมว" in s_name):
            score -= 50
        elif pref_pet == "Rabbit" and not ("rabbit" in s_name or "กระต่าย" in s_name):
            score -= 50
        elif pref_pet in ("Dog", "Cat", "Rabbit"):
            score += 10

        # ================= DOGS MATCHING LOGIC =================
        if "dog" in s_name or "สุนัข" in s_name:
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
                if budget >= 1000:
                    score += 15
                    reasons.append("งบประมาณเฉลี่ย 800 - 3,000 บาท/เดือน สอดคล้องกับงบที่คุณตั้งไว้")
            elif "poodle" in b_name or "พุดเดิ้ล" in b_name:
                if budget >= 1500:
                    score += 15
                    reasons.append("งบประมาณเฉลี่ย 1,500 - 3,500 บาท/เดือน ตรงกับงบประมาณที่วางไว้")
            elif "golden" in b_name or "โกลเด้น" in b_name:
                if budget >= 2000:
                    score += 15
                    reasons.append("งบประมาณเฉลี่ย 2,000 - 4,000 บาท/เดือน พอดีกับค่าดูแลและอาหาร")
                else:
                    score -= 10
                    reasons.append("โกลเด้นมีค่าอาหารและการดูแลสุขภาพที่อาจเกินงบเริ่มต้นเล็กน้อย")
            elif "pomeranian" in b_name or "ปอม" in b_name:
                if budget >= 4000:
                    score += 18
                    reasons.append("งบประมาณครอบคลุมค่าตัดแต่งขนและอาหารบำรุงสุขภาพระดับพรีเมียม")
                else:
                    score -= 8
                    reasons.append("ปอมเมอเรเนียนมีค่าดูแลตัดแต่งขนและตรวจฟันเฉลี่ย 4,000 - 6,000 บาท/เดือน")
            elif "husky" in b_name or "ฮัสกี้" in b_name:
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

        # ================= CATS MATCHING LOGIC =================
        elif "cat" in s_name or "แมว" in s_name:
            # 1. Residence & Space
            if "condo" in residence.lower() or "compact" in space.lower():
                if "munchkin" in b_name or "มันช์กิ้น" in b_name:
                    score += 22
                    reasons.append("ขนาดตัวกะทัดรัด ขาสั้น เหมาะกับการเลี้ยงแบบ Indoor ในคอนโดมากที่สุด")
                elif "persian" in b_name or "เปอร์เซีย" in b_name:
                    score += 20
                    reasons.append("รักความสงบ ไม่ส่งเสียงดัง ไม่รบกวนเพื่อนบ้าน เหมาะกับคอนโด")
                elif "ragdoll" in b_name or "แร็กดอล" in b_name:
                    score += 18
                    reasons.append("นิสัยนิ่ง เชื่อง และรักสงบ สามารถปรับตัวเข้ากับชีวิตคอนโดได้ดีเยี่ยม")
                elif "siamese" in b_name or "วิเชียรมาศ" in b_name:
                    score += 16
                    reasons.append("ขนาดกลาง ปราดเปรียว เลี้ยงในห้องพักได้ดีเพียงจัดคอนโดแมวให้ปีนป่าย")
                elif "maine coon" in b_name or "เมนคูน" in b_name:
                    score -= 15
                    reasons.append("เป็นแมวขนาดใหญ่ที่สุดในโลก อาจรู้สึกอึดอัดหากห้องพักมีพื้นที่แคบ")
            else:  # House with yard
                if "maine coon" in b_name or "เมนคูน" in b_name:
                    score += 25
                    reasons.append("บ้านที่มีพื้นที่กว้างขวางตอบโจทย์โครงสร้างตัวใหญ่และพละกำลังของเมนคูนได้ดีที่สุด")
                elif "siamese" in b_name or "วิเชียรมาศ" in b_name:
                    score += 20
                    reasons.append("บ้านมีพื้นที่ให้ปีนป่ายและวิ่งเล่นสำรวจตอบรับสัญชาตญาณนักล่าได้อย่างดี")
                elif "ragdoll" in b_name or "persian" in b_name or "munchkin" in b_name:
                    score += 16
                    reasons.append("เลี้ยงในบ้านได้อย่างสุขสบาย ปลอดภัยและมีพื้นที่ส่วนตัว")

            # 2. Budget
            if "siamese" in b_name or "วิเชียรมาศ" in b_name:
                # 800 - 2,000
                if budget >= 1000:
                    score += 16
                    reasons.append("งบประมาณเฉลี่ย 800 - 2,000 บาท/เดือน สอดคล้องกับงบที่คุณตั้งไว้")
            elif "persian" in b_name or "เปอร์เซีย" in b_name:
                # 1,000 - 3,000
                if budget >= 1500:
                    score += 15
                    reasons.append("งบประมาณเฉลี่ย 1,000 - 3,000 บาท/เดือน เพียงพอสำหรับอาหารและการบำรุงขนสวย")
            elif "munchkin" in b_name or "มันช์กิ้น" in b_name:
                # 1,000 - 3,000
                if budget >= 1500:
                    score += 15
                    reasons.append("งบประมาณเฉลี่ย 1,000 - 3,000 บาท/เดือน สอดคล้องกับค่าดูแลสุขภาพและอาหาร")
            elif "ragdoll" in b_name or "แร็กดอล" in b_name:
                # 1,500 - 3,500
                if budget >= 2000:
                    score += 16
                    reasons.append("งบประมาณเฉลี่ย 1,500 - 3,500 บาท/เดือน เหมาะสมกับการดูแลขนหนานุ่มและอาหารพรีเมียม")
            elif "maine coon" in b_name or "เมนคูน" in b_name:
                # 3,000 - 8,000
                if budget >= 4000:
                    score += 18
                    reasons.append("งบประมาณเฉลี่ย 3,000 - 8,000 บาท/เดือน รองรับปริมาณอาหารโปรตีนสูงและบำรุงแมวยักษ์ได้เต็มที่")
                else:
                    score -= 15
                    reasons.append("เมนคูนมีค่าอาหารและการดูแลแมวยักษ์เฉลี่ย 3,000 - 8,000 บาท/เดือน ซึ่งอาจเกินงบที่ตั้งไว้")

            # 3. Allergy & Shedding
            if allergy.lower() in ("yes", "true", "1"):
                if "siamese" in b_name or "วิเชียรมาศ" in b_name:
                    score += 18
                    reasons.append("ขนสั้นและแน่น ผลัดขนน้อย ดูแลง่าย คนแพ้ขนสามารถดูแลได้ง่าย")
                elif "ragdoll" in b_name or "แร็กดอล" in b_name:
                    score += 14
                    reasons.append("ขนกึ่งยาวละเอียดเหมือนเส้นไหม ไม่มีขนชั้นในสังกะตัง ดูแลง่ายกว่าแมวขนยาวทั่วไป")
                elif "persian" in b_name or "เปอร์เซีย" in b_name:
                    score -= 15
                    reasons.append("ขนยาวและหนา ต้องแปรงทุกวัน อาจมีเศษขนหลุดร่วงบ่อย")
                elif "maine coon" in b_name or "เมนคูน" in b_name:
                    score -= 15
                    reasons.append("ขนสองชั้นดกหนา มีการผลัดขนตามฤดูกาล ต้องหมั่นแปรงและดูดฝุ่น")

            # 4. Lifestyle / Time
            if time_avail == "WFH" or "home" in time_avail.lower():
                if "ragdoll" in b_name or "แร็กดอล" in b_name:
                    score += 20
                    reasons.append("นิสัยเหมือนตุ๊กตาผ้า ชอบให้อุ้มและติดคน เหมาะมากกับคนอยู่บ้าน Work From Home")
                elif "siamese" in b_name or "วิเชียรมาศ" in b_name:
                    score += 18
                    reasons.append("ขี้อ้อน ช่างพูดคุย เป็นเพื่อนแก้เหงาระหว่างวันได้เป็นอย่างดี")
                elif "persian" in b_name or "เปอร์เซีย" in b_name:
                    score += 14
                    reasons.append("รักความสงบ นอนเคียงข้างเงียบ ๆ ไม่รบกวนสมาธิการทำงาน")
            elif time_avail == "Busy":
                if "munchkin" in b_name or "มันช์กิ้น" in b_name or "persian" in b_name:
                    score += 16
                    reasons.append("มีความเป็นอิสระ รักสงบ สามารถพักผ่อนรอเจ้าของกลับบ้านได้ดี")
                elif "siamese" in b_name or "วิเชียรมาศ" in b_name:
                    score -= 8
                    reasons.append("ค่อนข้างติดคนและต้องการปฏิสัมพันธ์ อาจรู้สึกเหงาหากต้องอยู่ลำพังนาน")

            # 5. Experience
            if experience.lower() in ("new", "มือใหม่"):
                if "ragdoll" in b_name or "แร็กดอล" in b_name:
                    score += 18
                    reasons.append("อ่อนโยน เชื่องมาก ไม่ดุร้าย เชื่อฟังคำสั่งง่าย เหมาะกับมือใหม่อย่างยิ่ง")
                elif "siamese" in b_name or "วิเชียรมาศ" in b_name:
                    score += 16
                    reasons.append("ฉลาด เรียนรู้ไว ดูแลง่าย ไม่จุกจิก เหมาะสำหรับผู้เริ่มต้น")
                elif "munchkin" in b_name or "มันช์กิ้น" in b_name:
                    score += 15
                    reasons.append("อารมณ์ดี ขี้เล่น เลี้ยงง่ายในระบบปิด")
                elif "maine coon" in b_name or "เมนคูน" in b_name:
                    score -= 8
                    reasons.append("ขนาดตัวใหญ่มากและขนหนา ต้องใช้ความทุ่มเทในการดูแลขนและสุขภาพ")
            else:
                if "maine coon" in b_name or "เมนคูน" in b_name:
                    score += 18
                    reasons.append("ความสง่างามของแมวยักษ์เหมาะกับผู้เลี้ยงที่มีประสบการณ์ดูแลอย่างดี")
                elif "persian" in b_name or "เปอร์เซีย" in b_name:
                    score += 14
                    reasons.append("ผู้มีประสบการณ์จะจัดการดูแลขนยาวสลวยและคราบน้ำตาได้เชี่ยวชาญ")

        # ================= RABBITS MATCHING LOGIC =================
        elif "rabbit" in s_name or "กระต่าย" in s_name:
            # 1. Residence & Space
            if "condo" in residence.lower() or "compact" in space.lower():
                if "mini rex" in b_name or "มินิเร็กซ์" in b_name:
                    score += 24
                    reasons.append("ขนาดกะทัดรัด ตัวเล็ก เลี้ยงในคอนโดได้อย่างเงียบสงบ ไม่ส่งเสียงรบกวน")
                elif "mini lop" in b_name or "มินิลอป" in b_name:
                    score += 22
                    reasons.append("กระต่ายแคระตัวอ้วนกลม ปรับตัวเข้ากับพื้นที่คอนโดหรือห้องพักได้ดีมาก")
                elif "french lop" in b_name or "เฟรนช์ลอป" in b_name:
                    score -= 15
                    reasons.append("กระต่ายสายพันธุ์ใหญ่หนักถึง 9 กก. อาจรู้สึกอึดอัดหากห้องพักมีพื้นที่แคบ")
            else:  # House with yard
                if "french lop" in b_name or "เฟรนช์ลอป" in b_name:
                    score += 25
                    reasons.append("บ้านมีพื้นที่กว้างขวางตอบโจทย์ขนาดตัวยักษ์ใหญ่ของเฟรนช์ลอปได้เป็นอย่างดี")
                elif "mini lop" in b_name or "มินิลอป" in b_name:
                    score += 18
                    reasons.append("มีพื้นที่วิ่งเล่นและกระโดดออกกำลังกายในบ้านได้อย่างร่าเริง")
                elif "mini rex" in b_name or "มินิเร็กซ์" in b_name:
                    score += 16
                    reasons.append("สามารถจัดคอกวิ่งเล่นในบ้านได้อย่างปลอดภัยและเป็นสัดส่วน")

            # 2. Budget
            if "mini rex" in b_name or "มินิเร็กซ์" in b_name:
                # 500 - 1,500
                if budget >= 800:
                    score += 16
                    reasons.append("งบประมาณเฉลี่ย 500 - 1,500 บาท/เดือน สอดคล้องกับงบที่คุณตั้งไว้")
            elif "mini lop" in b_name or "มินิลอป" in b_name:
                # 500 - 2,500
                if budget >= 1000:
                    score += 16
                    reasons.append("งบประมาณเฉลี่ย 500 - 2,500 บาท/เดือน ครอบคลุมค่าหญ้าทิโมธีและอาหารเม็ด")
            elif "french lop" in b_name or "เฟรนช์ลอป" in b_name:
                # 800 - 2,000
                if budget >= 1000:
                    score += 16
                    reasons.append("งบประมาณเฉลี่ย 800 - 2,000 บาท/เดือน เหมาะสมกับปริมาณอาหารของกระต่ายพันธุ์ใหญ่")

            # 3. Allergy & Shedding
            if allergy.lower() in ("yes", "true", "1"):
                if "mini rex" in b_name or "มินิเร็กซ์" in b_name:
                    score += 22
                    reasons.append("ขนสั้นละเอียดนุ่มเหมือนกำมะหยี่ ผลัดขนน้อย ไม่ฟุ้งกระจาย ปลอดภัยกับคนแพ้ง่าย")
                elif "mini lop" in b_name or "มินิลอป" in b_name:
                    score += 12
                    reasons.append("ขนสั้นถึงปานกลาง หมั่นแปรงขนสม่ำเสมอช่วยลดการฟุ้งกระจาย")
                elif "french lop" in b_name or "เฟรนช์ลอป" in b_name:
                    score += 10
                    reasons.append("ขนหนานุ่มแต่มีช่วงผลัดขน ควรแปรงขนสม่ำเสมอ")

            # 4. Lifestyle / Time
            if time_avail == "WFH" or "home" in time_avail.lower():
                if "mini lop" in b_name or "มินิลอป" in b_name:
                    score += 20
                    reasons.append("นิสัยร่าเริง ขี้เล่น ชอบให้เจ้าของลูบคลำและเล่นด้วย เหมาะมากกับคนอยู่บ้าน")
                elif "french lop" in b_name or "เฟรนช์ลอป" in b_name:
                    score += 16
                    reasons.append("รักสงบ เชื่องมาก ชอบนอนนิ่งเคียงข้างเจ้าของ")
                elif "mini rex" in b_name or "มินิเร็กซ์" in b_name:
                    score += 16
                    reasons.append("เป็นมิตร อารมณ์ดี เข้าหาเจ้าของได้ง่าย")
            elif time_avail == "Busy":
                if "french lop" in b_name or "เฟรนช์ลอป" in b_name or "mini rex" in b_name:
                    score += 16
                    reasons.append("เป็นสัตว์เงียบสงบ ไม่ส่งเสียงรบกวน พักผ่อนรอเจ้าของกลับบ้านได้ดี")
                elif "mini lop" in b_name or "มินิลอป" in b_name:
                    score -= 6
                    reasons.append("ชอบการมีปฏิสัมพันธ์กับเจ้าของ อาจรู้สึกเหงาหากต้องอยู่ลำพังนาน")

            # 5. Experience
            if experience.lower() in ("new", "มือใหม่"):
                if "mini rex" in b_name or "มินิเร็กซ์" in b_name:
                    score += 22
                    reasons.append("เลี้ยงง่ายที่สุดสำหรับมือใหม่ เชื่อง ดูแลขนง่าย ไม่ซับซ้อน")
                elif "mini lop" in b_name or "มินิลอป" in b_name:
                    score += 18
                    reasons.append("นิสัยเป็นมิตร ฝึกขับถ่ายในกระบะได้ง่าย เหมาะสำหรับผู้เริ่มเลี้ยง")
                elif "french lop" in b_name or "เฟรนช์ลอป" in b_name:
                    score += 10
                    reasons.append("ตัวใหญ่มาก ต้องรู้วิธีการอุ้มและระวังตอนตกใจตื่นกลัว")
            else:
                if "french lop" in b_name or "เฟรนช์ลอป" in b_name:
                    score += 20
                    reasons.append("ความสุขของการเลี้ยงกระต่ายยักษ์ 9 กก. เหมาะกับผู้เลี้ยงที่มีความพร้อมและประสบการณ์")

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
