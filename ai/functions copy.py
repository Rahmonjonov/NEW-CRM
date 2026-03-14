import difflib
from board.models import District, Region, Lead
from django.db.models import Q

def get_status_type_id(user_input):
    if not user_input: return None
    status_types = {
        "lead yaratildi": 0, "lead taxrirlandi": 1, 
        "status o'zgardi": 2, "izoh qo'shildi": 3, "pole o'zgardi": 4,
    }
    user_input = user_input.strip().lower()
    choices = list(status_types.keys())
    match = difflib.get_close_matches(user_input, choices, n=1, cutoff=0.3)
    return {"id": status_types[match[0]], "name": match[0]} if match else None

def get_emotion_id(user_input):
    if not user_input: return None
    status_emotsiya = {
        "qarorsiz": 1, "qayta kelishuv": 2, "info ehtiyoj": 3,
        "tasir etish kerak": 4, "tezkor sotish kerak": 5, "istemolchi": 6,
        "qo'shimcha kelishuv": 7, "etirozli": 8, "shikoyatli": 9,
    }
    user_input = user_input.strip().lower()
    choices = list(status_emotsiya.keys())
    match = difflib.get_close_matches(user_input, choices, n=1, cutoff=0.4)
    return {"id": status_emotsiya[match[0]], "name": match[0]} if match else None

def find_location(user_input):
    if not user_input: return None
    user_input = user_input.strip().lower()
    choices = []
    
    # Bug fix: 'name' kalitini qo'shib ketish kerak
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

def search_leads(name_input=None, location_input=None, status_input=None, emotion_input=None):
    leads = Lead.objects.all()

    # 1. Joylashuv bo'yicha filtr
    location = find_location(location_input)
    if location:
        if location['type'] == 'district':
            leads = leads.filter(district_id=location['id'])
        else:
            leads = leads.filter(district__region_id=location['id'])
    
    # 2. Status va Emotsiya bo'yicha filtr (faqat ID sini olamiz)
    status_res = get_status_type_id(status_input)
    if status_res:
        leads = leads.filter(status=status_res['id'])
    
    emotion_res = get_emotion_id(emotion_input)
    if emotion_res:
        leads = leads.filter(emotsiya=emotion_res['id'])

    # 3. Ism bo'yicha "Fuzzy" saralash
    if not name_input:
        # Agar ism kiritilmagan bo'lsa, shunchaki topilganlarni qaytaramiz
        final_leads = leads.select_related('district__region', 'district')[:10]
    else:
        name_input = name_input.strip().lower()
        # values('id', 'name') modeldagi nomga mos bo'lishi kerak
        leads_data = leads.values('id', 'name')
        
        exact_matches, starts_with, fuzzy_matches = [], [], []

        for item in leads_data:
            name = item['name'].lower()
            lead_id = item['id']
            
            if name_input == name:
                exact_matches.append(lead_id)
            elif name.startswith(name_input):
                starts_with.append(lead_id)
            elif difflib.SequenceMatcher(None, name_input, name).ratio() > 0.7:
                fuzzy_matches.append(lead_id)

        final_ids = (exact_matches + starts_with + fuzzy_matches)[:10]
        if not final_ids:
            return {"status": "error", "message": "Hech kim topilmadi."}
        
        final_leads = Lead.objects.filter(id__in=final_ids).select_related('district__region', 'district')

    # 4. Natijani shakllantirish
    results = [
        {
            "id": l.id, 
            "ism": l.name, 
            "phone": l.phone, 
            "manzil": f"{l.district.region.name}, {l.district.name}" if l.district else "Nomalum"
        } for l in final_leads
    ]
    print(results)
    return {"status": "success", "data": results}

