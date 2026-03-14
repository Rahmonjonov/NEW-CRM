import difflib
from board.models import District, Region, Lead
from django.db.models import Q, Sum
from datetime import date


# ═══════════════════════════════════════════════════════════════
#  CRM_TOOLS  —  Gemini'ga beriladigan barcha funksiyalar
# ═══════════════════════════════════════════════════════════════

CRM_TOOLS = [
    {
        "function_declarations": [
            {
                "name": "search_leads",
                "description": "Leadlarni ismi, telefon raqami, manzili, holati yoki emotsiyasi bo'yicha qidirish. Faqat berilgan parametrlardan foydalaniladi.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name_input":     {"type": "string", "description": "Mijozning ismi yoki familiyasi"},
                        "phone_input":    {"type": "string", "description": "Telefon raqami yoki uning bir qismi (masalan oxirgi 4 raqam: '1234' yoki to'liq: '+998901234567')"},
                        "location_input": {"type": "string", "description": "Shahar, viloyat yoki tuman nomi"},
                        "status_input":   {"type": "string", "description": "Leadning hozirgi holati (masalan: muvaffaqiyatli, yo'qotish, boardda)"},
                        "emotion_input":  {"type": "string", "description": "Mijozning kayfiyati yoki emotsiyasi"},
                        "limit":          {"type": "integer", "description": "Nechta natija qaytarish kerak (default: 10, max: 50)"}
                    },
                    "required": []
                }
            },
            {
                "name": "get_lead_detail",
                "description": "Bitta mijoz haqida to'liq batafsil ma'lumot olish. ID yoki ism orqali topiladi.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lead_id":    {"type": "integer", "description": "Mijozning ID raqami"},
                        "name_input": {"type": "string",  "description": "Mijozning ismi (ID bo'lmasa shu orqali qidiradi)"}
                    },
                    "required": []
                }
            },
            {
                "name": "get_leads_stats",
                "description": "CRM statistikasi: jami mijozlar soni, jami summa, muvaffaqiyatli/yo'qotilgan leadlar, aktiv/noaktiv mijozlar soni va boshqa umumiy ko'rsatkichlar.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "stat_type": {
                            "type": "string",
                            "description": "Qaysi statistika kerak: 'count' (soni), 'sum' (jami summa), 'status' (holat bo'yicha), 'all' (hammasi)",
                            "enum": ["count", "sum", "status", "all"]
                        }
                    },
                    "required": []
                }
            },
            {
                "name": "get_birthday_leads",
                "description": "Bugun yoki yaqin kunlarda tug'ilgan kuni bo'lgan mijozlar ro'yxati.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "days_ahead": {"type": "integer", "description": "Necha kun oldinga qarash (default: 0 = faqat bugun, 7 = keyingi 7 kun)"}
                    },
                    "required": []
                }
            },
            {
                "name": "get_leads_by_status",
                "description": "Ma'lum bir holat (status) bo'yicha leadlar ro'yxati. Masalan: muvaffaqiyatli yakunlangan, yo'qotilgan, hali boardda turgan mijozlar.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "status_name": {
                            "type": "string",
                            "description": "Holat nomi: 'boardda', 'muvaffaqiyatli', 'yoqotish', 'promouter' yoki 'hammasi'"
                        },
                        "limit": {"type": "integer", "description": "Nechta natija (default: 10)"}
                    },
                    "required": ["status_name"]
                }
            }
        ]
    }
]


# ═══════════════════════════════════════════════════════════════
#  YORDAMCHI FUNKSIYALAR
# ═══════════════════════════════════════════════════════════════

def get_status_type_id(user_input):
    if not user_input: return None
    status_types = {
        "lead yaratildi": 0, "lead taxrirlandi": 1,
        "status o'zgardi": 2, "izoh qo'shildi": 3, "pole o'zgardi": 4,
    }
    user_input = user_input.strip().lower()
    match = difflib.get_close_matches(user_input, list(status_types.keys()), n=1, cutoff=0.3)
    return {"id": status_types[match[0]], "name": match[0]} if match else None


def get_emotion_id(user_input):
    if not user_input: return None
    status_emotsiya = {
        "qarorsiz": 1, "qayta kelishuv": 2, "info ehtiyoj": 3,
        "tasir etish kerak": 4, "tezkor sotish kerak": 5, "istemolchi": 6,
        "qo'shimcha kelishuv": 7, "etirozli": 8, "shikoyatli": 9,
    }
    user_input = user_input.strip().lower()
    match = difflib.get_close_matches(user_input, list(status_emotsiya.keys()), n=1, cutoff=0.4)
    return {"id": status_emotsiya[match[0]], "name": match[0]} if match else None


def find_location(user_input):
    if not user_input: return None
    user_input = user_input.strip().lower()
    choices = []
    for r in Region.objects.exclude(name="nan"):
        choices.append({'id': r.id, 'name': r.name, 'type': 'region'})
    for d in District.objects.exclude(name="nan"):
        choices.append({'id': d.id, 'name': d.name, 'type': 'district'})

    best_score = 0
    winner = None
    for item in choices:
        score = difflib.SequenceMatcher(None, user_input, item['name'].lower()).ratio()
        if user_input in item['name'].lower():
            score += 0.1
        if score > best_score:
            best_score = score
            winner = item
    return winner if best_score > 0.3 else None


def _lead_status_from_name(name):
    """Status nomidan ID qaytaradi"""
    mapping = {
        "boardda": 0, "board": 0,
        "muvaffaqiyatli": 5, "muvaffaqiyat": 5, "yakunlangan": 5, "tugallangan": 5,
        "yoqotish": 4, "yo'qotish": 4, "bekor": 4,
        "promouter": 6,
        "hammasi": None, "barchasi": None,
    }
    if not name: return None
    name = name.strip().lower()
    match = difflib.get_close_matches(name, list(mapping.keys()), n=1, cutoff=0.4)
    if match:
        return mapping[match[0]]
    return None


def _format_price(price):
    """Sonni chiroyli formatda qaytaradi"""
    if price >= 1_000_000_000:
        return f"{price/1_000_000_000:.1f} mlrd so'm"
    elif price >= 1_000_000:
        return f"{price/1_000_000:.1f} mln so'm"
    elif price >= 1_000:
        return f"{price/1_000:.1f} ming so'm"
    return f"{price} so'm"


# ═══════════════════════════════════════════════════════════════
#  ASOSIY FUNKSIYALAR
# ═══════════════════════════════════════════════════════════════

def search_leads(name_input=None, phone_input=None, location_input=None,
                 status_input=None, emotion_input=None, limit=10):
    """
    Kengaytirilgan lead qidirish:
    - Ism/familiya bo'yicha fuzzy qidiruv
    - Telefon raqami bo'yicha (to'liq yoki oxirgi N raqam)
    - Joylashuv bo'yicha
    - Status va emotsiya bo'yicha
    """
    limit = min(int(limit or 10), 50)
    leads = Lead.objects.all()

    # 1. Joylashuv filtri
    location = find_location(location_input)
    if location:
        if location['type'] == 'district':
            leads = leads.filter(district_id=location['id'])
        else:
            leads = leads.filter(district__region_id=location['id'])

    # 2. Status filtri (so'z bilan kelsa)
    if status_input:
        status_lower = status_input.strip().lower()
        status_map = {
            "boardda": 0, "board": 0,
            "muvaffaqiyatli": 5, "yakunlangan": 5,
            "yoqotish": 4, "yo'qotish": 4,
            "promouter": 6,
        }
        match = difflib.get_close_matches(status_lower, list(status_map.keys()), n=1, cutoff=0.4)
        if match:
            leads = leads.filter(status=status_map[match[0]])

    # 3. Emotsiya filtri
    emotion_res = get_emotion_id(emotion_input)
    if emotion_res:
        leads = leads.filter(emotsiya=emotion_res['id'])

    # 4. Telefon raqami bo'yicha qidiruv
    if phone_input:
        phone_clean = phone_input.strip().replace(" ", "").replace("-", "").replace("+", "")
        # Oxirgi 4-8 ta raqam bilan qidirish
        leads = leads.filter(
            Q(phone__endswith=phone_clean) |
            Q(phone__contains=phone_clean) |
            Q(phone2__endswith=phone_clean) |
            Q(phone2__contains=phone_clean) |
            Q(telegram_phone_number__contains=phone_clean)
        )

    # 5. Ism bo'yicha fuzzy qidiruv
    if not name_input:
        final_leads = leads.select_related('district__region', 'district')[:limit]
    else:
        name_input = name_input.strip().lower()
        leads_data = leads.values('id', 'name', 'surname')

        exact_matches, starts_with, fuzzy_matches = [], [], []

        for item in leads_data:
            full_name = f"{item['name']} {item['surname'] or ''}".strip().lower()
            lead_id = item['id']

            if name_input == full_name or name_input == item['name'].lower():
                exact_matches.append(lead_id)
            elif full_name.startswith(name_input) or item['name'].lower().startswith(name_input):
                starts_with.append(lead_id)
            elif (difflib.SequenceMatcher(None, name_input, item['name'].lower()).ratio() > 0.65 or
                  difflib.SequenceMatcher(None, name_input, full_name).ratio() > 0.65):
                fuzzy_matches.append(lead_id)

        final_ids = (exact_matches + starts_with + fuzzy_matches)[:limit]
        if not final_ids:
            return {"status": "error", "message": "Hech kim topilmadi."}

        final_leads = Lead.objects.filter(id__in=final_ids).select_related('district__region', 'district')

    results = [
        {
            "id": l.id,
            "ism": f"{l.name} {l.surname or ''}".strip(),
            "phone": l.phone or "—",
            "manzil": f"{l.district.region.name}, {l.district.name}" if l.district else "Noma'lum",
            "status": dict(Lead.status_types).get(l.status, "—"),
            "narx": _format_price(l.price),
        }
        for l in final_leads
    ]
    print(f"[search_leads] {len(results)} ta natija topildi.")
    return {"status": "success", "data": results, "total": len(results)}


def get_lead_detail(lead_id=None, name_input=None):
    """
    Bitta mijoz haqida to'liq ma'lumot.
    """
    lead = None

    if lead_id:
        try:
            lead = Lead.objects.select_related(
                'district__region', 'district', 'pole', 'created_user'
            ).get(id=lead_id)
        except Lead.DoesNotExist:
            pass

    if not lead and name_input:
        name_lower = name_input.strip().lower()
        candidates = Lead.objects.select_related(
            'district__region', 'district', 'pole', 'created_user'
        ).all()
        best_score = 0
        for l in candidates:
            full = f"{l.name} {l.surname or ''}".strip().lower()
            score = difflib.SequenceMatcher(None, name_lower, full).ratio()
            if score > best_score:
                best_score = score
                lead = l
        if best_score < 0.5:
            lead = None

    if not lead:
        return {"status": "error", "message": "Mijoz topilmadi."}

    status_display = dict(Lead.status_types).get(lead.status, "Noma'lum")
    degree_display = dict(Lead.degr).get(lead.degree, "Noma'lum")
    joinby_display = dict(Lead.joinByChoise).get(lead.joinBy, "Odatiy")

    detail = {
        "id": lead.id,
        "ism": lead.name,
        "familiya": lead.surname or "—",
        "telefon": lead.phone or "—",
        "telefon2": lead.phone2 or "—",
        "email": lead.email or "—",
        "tugilgan_kun": str(lead.birthday) if lead.birthday else "—",
        "manzil": f"{lead.district.region.name}, {lead.district.name}" if lead.district else "Noma'lum",
        "kompaniya": lead.company or "—",
        "kompaniya_manzil": lead.companyAddress or "—",
        "biznes_turi": lead.business_type or "—",
        "status": status_display,
        "daraja": degree_display,
        "qo'shilish_usuli": joinby_display,
        "narx": _format_price(lead.price),
        "investitsiya": _format_price(lead.investment_price),
        "yakuniy_narx": _format_price(lead.finishedPrice),
        "qarz": _format_price(lead.debt),
        "pole": str(lead.pole) if lead.pole else "—",
        "qo'shgan_xodim": str(lead.created_user) if lead.created_user else "—",
        "qo'shilgan_sana": lead.date.strftime("%d.%m.%Y %H:%M") if lead.date else "—",
        "yakunlangan_sana": lead.finishedDate.strftime("%d.%m.%Y") if lead.finishedDate else "—",
        "amal_qilish_muddati": str(lead.validity_period) if lead.validity_period else "—",
        "izoh": lead.note or "—",
        "manba": lead.join_from or "—",
        "abcxyz": lead.abcxyz or "—",
        "aktiv": "Ha" if lead.is_active else "Yo'q",
        "telegram_id": lead.tg_id or "—",
    }
    print(f"[get_lead_detail] '{lead.name}' haqida to'liq ma'lumot qaytarildi.")
    return {"status": "success", "data": detail}


def get_leads_stats(stat_type="all"):
    """
    CRM umumiy statistikasi.
    """
    all_leads = Lead.objects.all()
    active_leads = all_leads.filter(is_active=True)

    stats = {}

    if stat_type in ("count", "all"):
        stats["jami_mijozlar"] = all_leads.count()
        stats["aktiv_mijozlar"] = active_leads.count()
        stats["noaktiv_mijozlar"] = all_leads.filter(is_active=False).count()

    if stat_type in ("sum", "all"):
        total_price = all_leads.aggregate(s=Sum('price'))['s'] or 0
        total_finished = all_leads.filter(status=5).aggregate(s=Sum('finishedPrice'))['s'] or 0
        total_debt = all_leads.aggregate(s=Sum('debt'))['s'] or 0
        total_investment = all_leads.aggregate(s=Sum('investment_price'))['s'] or 0
        stats["jami_summa"] = _format_price(total_price)
        stats["yakunlangan_summa"] = _format_price(total_finished)
        stats["jami_qarz"] = _format_price(total_debt)
        stats["jami_investitsiya"] = _format_price(total_investment)

    if stat_type in ("status", "all"):
        stats["boardda"] = all_leads.filter(status=0).count()
        stats["muvaffaqiyatli_yakunlangan"] = all_leads.filter(status=5).count()
        stats["yo'qotilgan"] = all_leads.filter(status=4).count()
        stats["promouter"] = all_leads.filter(status=6).count()

    print(f"[get_leads_stats] Statistika qaytarildi: {stat_type}")
    return {"status": "success", "data": stats}


def get_birthday_leads(days_ahead=0):
    """
    Bugun yoki yaqin kunlarda tug'ilgan kuni bo'lgan mijozlar.
    """
    days_ahead = int(days_ahead or 0)
    today = date.today()
    results = []

    leads = Lead.objects.filter(
        birthday__isnull=False, is_active=True
    ).select_related('district__region', 'district')

    for lead in leads:
        if not lead.birthday:
            continue
        try:
            # Bu yilgi tug'ilgan kun
            bday_this_year = lead.birthday.replace(year=today.year)
        except ValueError:
            # 29 fevral case
            bday_this_year = lead.birthday.replace(year=today.year, day=28)

        diff = (bday_this_year - today).days

        if 0 <= diff <= days_ahead:
            results.append({
                "id": lead.id,
                "ism": f"{lead.name} {lead.surname or ''}".strip(),
                "phone": lead.phone or "—",
                "tugilgan_kun": lead.birthday.strftime("%d.%m"),
                "kun_qoldi": diff,
                "bugun": diff == 0,
                "manzil": f"{lead.district.region.name}, {lead.district.name}" if lead.district else "Noma'lum",
            })

    results.sort(key=lambda x: x['kun_qoldi'])
    label = "bugun" if days_ahead == 0 else f"keyingi {days_ahead} kunda"
    print(f"[get_birthday_leads] {label}: {len(results)} ta mijoz topildi.")
    return {"status": "success", "data": results, "total": len(results), "period": label}


def get_leads_by_status(status_name, limit=10):
    """
    Belgilangan status bo'yicha leadlar ro'yxati.
    """
    limit = min(int(limit or 10), 50)
    status_id = _lead_status_from_name(status_name)

    if status_id is None and status_name.strip().lower() not in ("hammasi", "barchasi"):
        return {"status": "error", "message": f"'{status_name}' holati topilmadi."}

    leads = Lead.objects.select_related('district__region', 'district')

    if status_id is not None:
        leads = leads.filter(status=status_id)

    leads = leads[:limit]

    results = [
        {
            "id": l.id,
            "ism": f"{l.name} {l.surname or ''}".strip(),
            "phone": l.phone or "—",
            "status": dict(Lead.status_types).get(l.status, "—"),
            "narx": _format_price(l.price),
            "manzil": f"{l.district.region.name}, {l.district.name}" if l.district else "Noma'lum",
            "sana": l.date.strftime("%d.%m.%Y") if l.date else "—",
        }
        for l in leads
    ]
    print(f"[get_leads_by_status] '{status_name}': {len(results)} ta topildi.")
    return {"status": "success", "data": results, "total": len(results)}


# ═══════════════════════════════════════════════════════════════
#  FUNKSIYA DISPATCHER  —  Gemini chaqirgan funksiyani ishga tushiradi
# ═══════════════════════════════════════════════════════════════

FUNCTION_MAP = {
    "search_leads":      search_leads,
    "get_lead_detail":   get_lead_detail,
    "get_leads_stats":   get_leads_stats,
    "get_birthday_leads": get_birthday_leads,
    "get_leads_by_status": get_leads_by_status,
}


def call_function(name, args):
    """Gemini chaqirgan funksiyani topib chaqiradi."""
    fn = FUNCTION_MAP.get(name)
    if not fn:
        return {"status": "error", "message": f"'{name}' funksiyasi topilmadi."}
    try:
        return fn(**args)
    except Exception as e:
        print(f"[call_function] XATO '{name}': {e}")
        return {"status": "error", "message": str(e)}


def format_db_result(function_name, db_result):
    """DB natijasini foydalanuvchiga ko'rsatiladigan matnga aylantiradi."""
    if db_result.get("status") == "error":
        return f"⚠️ {db_result.get('message', 'Xatolik yuz berdi.')}"

    data = db_result.get("data", {})

    # ── search_leads ──────────────────────────────────────
    if function_name == "search_leads":
        total = db_result.get("total", 0)
        if not data:
            return "🔍 Hech qanday mijoz topilmadi."
        text = f"🔍 {total} ta mijoz topildi:\n\n"
        for i, l in enumerate(data, 1):
            text += (f"{i}. 👤 {l['ism']}\n"
                     f"   📞 {l['phone']}  |  📍 {l['manzil']}\n"
                     f"   📊 {l['status']}  |  💰 {l['narx']}\n\n")
        return text.strip()

    # ── get_lead_detail ───────────────────────────────────
    elif function_name == "get_lead_detail":
        d = data
        return (
            f"👤 **{d['ism']} {d['familiya']}**\n\n"
            f"📞 Telefon:       {d['telefon']}\n"
            f"📞 Telefon2:      {d['telefon2']}\n"
            f"📧 Email:         {d['email']}\n"
            f"🎂 Tug'ilgan kun: {d['tugilgan_kun']}\n"
            f"📍 Manzil:        {d['manzil']}\n"
            f"🏢 Kompaniya:     {d['kompaniya']}\n"
            f"💼 Biznes turi:   {d['biznes_turi']}\n"
            f"📊 Status:        {d['status']}\n"
            f"⭐ Daraja:        {d['daraja']}\n"
            f"💰 Narx:          {d['narx']}\n"
            f"💸 Qarz:          {d['qarz']}\n"
            f"🏷️ Pole:          {d['pole']}\n"
            f"📝 Izoh:          {d['izoh']}\n"
            f"🔗 Manba:         {d['manba']}\n"
            f"📅 Qo'shilgan:    {d['qoshilgan_sana']}\n"
            f"✅ Aktiv:         {d['aktiv']}"
        )

    # ── get_leads_stats ───────────────────────────────────
    elif function_name == "get_leads_stats":
        lines = ["📊 **CRM Statistikasi**\n"]
        labels = {
            "jami_mijozlar":              "👥 Jami mijozlar",
            "aktiv_mijozlar":             "✅ Aktiv",
            "noaktiv_mijozlar":           "❌ Noaktiv",
            "jami_summa":                 "💰 Jami summa",
            "yakunlangan_summa":          "🏆 Yakunlangan summa",
            "jami_qarz":                  "💸 Jami qarz",
            "jami_investitsiya":          "📈 Jami investitsiya",
            "boardda":                    "📋 Boardda",
            "muvaffaqiyatli_yakunlangan": "🏆 Muvaffaqiyatli",
            "yo'qotilgan":                "❌ Yo'qotilgan",
            "promouter":                  "🌟 Promouter",
        }
        for key, val in data.items():
            label = labels.get(key, key)
            lines.append(f"{label}: {val}")
        return "\n".join(lines)

    # ── get_birthday_leads ────────────────────────────────
    elif function_name == "get_birthday_leads":
        period = db_result.get("period", "")
        total = db_result.get("total", 0)
        if not data:
            return f"🎂 {period.capitalize()} tug'ilgan kuni bo'lgan mijoz yo'q."
        text = f"🎂 {period.capitalize()} tug'ilgan kuni bo'lgan {total} ta mijoz:\n\n"
        for l in data:
            bugun = "🎉 BUGUN!" if l['bugun'] else f"{l['kun_qoldi']} kun qoldi"
            text += (f"👤 {l['ism']}  —  🎂 {l['tugilgan_kun']}\n"
                     f"   📞 {l['phone']}  |  {bugun}\n\n")
        return text.strip()

    # ── get_leads_by_status ───────────────────────────────
    elif function_name == "get_leads_by_status":
        total = db_result.get("total", 0)
        if not data:
            return "📋 Bu holatda hech qanday mijoz topilmadi."
        text = f"📋 {total} ta mijoz:\n\n"
        for i, l in enumerate(data, 1):
            text += (f"{i}. 👤 {l['ism']}\n"
                     f"   📞 {l['phone']}  |  📅 {l['sana']}\n"
                     f"   📊 {l['status']}  |  💰 {l['narx']}\n\n")
        return text.strip()

    return str(data)