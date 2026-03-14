import json
import time
import requests
import random
from django.http import StreamingHttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from .functions import * # call_function va format_db_result shu yerda

# ═══════════════════════════════════════════════════════════════
#  SOZLAMALAR
# ═══════════════════════════════════════════════════════════════

API_KEY = "AIzaSyAn4TX1VqEliKOXgoMHGZykNtTH3WLIBYg"
MODEL_NAME = "gemini-3-flash-preview"

# API URL'lar
GEMINI_URL          = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:streamGenerateContent?alt=sse&key={API_KEY}"
GEMINI_GENERATE_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent?key={API_KEY}"
GEMINI_FILES_URL    = f"https://generativelanguage.googleapis.com/upload/v1beta/files?key={API_KEY}"

HTTP_PROXIES = [
    {'proxy': 'http://vdkddoct:2cqkbc4zn6oo@31.59.20.176:6754',   'country': 'UK'},
    {'proxy': 'http://vdkddoct:2cqkbc4zn6oo@23.95.150.145:6114',  'country': 'USA'},
    {'proxy': 'http://vdkddoct:2cqkbc4zn6oo@198.23.239.134:6540', 'country': 'USA'},
]

def test_proxies():
    working = []
    for p_data in HTTP_PROXIES:
        try:
            r = requests.get('https://api.ipify.org?format=json', proxies={'http': p_data['proxy'], 'https': p_data['proxy']}, timeout=5)
            if r.status_code == 200: working.append(p_data['proxy'])
        except: continue
    return working

WORKING_PROXIES = test_proxies()

def _get_proxies():
    if WORKING_PROXIES:
        proxy = WORKING_PROXIES[0]
        return {'http': proxy, 'https': proxy}
    return None

# ═══════════════════════════════════════════════════════════════
#  CRM VOSITALARI (TOOLS)
# ═══════════════════════════════════════════════════════════════

CRM_TOOLS = [{
    "function_declarations": [
        {
            "name": "search_leads",
            "description": "Leadlarni ismi, telefon, manzil yoki status bo'yicha qidirish.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name_input": {"type": "string"},
                    "phone_input": {"type": "string"},
                    "location_input": {"type": "string"},
                    "status_input": {"type": "string"},
                    "emotion_input": {"type": "string"},
                    "limit": {"type": "integer"}
                }
            }
        },
        {
            "name": "get_lead_detail",
            "description": "Bitta mijoz haqida to'liq ma'lumot olish.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lead_id": {"type": "integer"},
                    "name_input": {"type": "string"}
                }
            }
        },
        {
            "name": "get_leads_stats",
            "description": "CRM umumiy statistikasi.",
            "parameters": {
                "type": "object",
                "properties": {
                    "stat_type": {"type": "string", "enum": ["count", "sum", "status", "all"]}
                }
            }
        },
        {
            "name": "get_birthday_leads",
            "description": "Tug'ilgan kuni yaqinlashgan mijozlar.",
            "parameters": {
                "type": "object",
                "properties": {"days_ahead": {"type": "integer"}}
            }
        },
        {
            "name": "get_leads_by_status",
            "description": "Status bo'yicha leadlar ro'yxati.",
            "parameters": {
                "type": "object",
                "properties": {
                    "status_name": {"type": "string"},
                    "limit": {"type": "integer"}
                },
                "required": ["status_name"]
            }
        }
    ]
}]

SYSTEM_PROMPT = """Siz aqlli CRM yordamchisiz. O'zbek tilida muloqot qiling.
Foydalanuvchi so'raganda tegishli funksiyani chaqiring. Ma'lumot olgach, uni foydalanuvchiga chiroyli tushuntiring."""

# ═══════════════════════════════════════════════════════════════
#  AUDIO TAHLIL
# ═══════════════════════════════════════════════════════════════

@csrf_exempt
def analyze_audio_view(request):
    if request.method != "POST": return JsonResponse({"error": "Only POST allowed"}, status=405)
    audio_file = request.FILES.get("audio")
    if not audio_file: return JsonResponse({"error": "No audio file"}, status=400)
    
    mime_type = "audio/mpeg"
    audio_bytes = audio_file.read()
    try:
        result = _analyze_audio_with_requests(audio_bytes, mime_type)
        return JsonResponse({"status": "success", "result": result})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)

def _analyze_audio_with_requests(audio_bytes, mime_type):
    proxies = _get_proxies()
    # 1. Yuklash
    up_headers = {
        "X-Goog-Upload-Command": "start, upload, finalize",
        "X-Goog-Upload-Header-Content-Type": mime_type,
        "X-Goog-Upload-Header-Content-Length": str(len(audio_bytes)),
        "Content-Type": mime_type,
    }
    up_resp = requests.post(GEMINI_FILES_URL, headers=up_headers, data=audio_bytes, proxies=proxies, timeout=120)
    file_data = up_resp.json().get("file")
    file_uri, file_name = file_data["uri"], file_data["name"]

    # 2. Kutish
    check_url = f"https://generativelanguage.googleapis.com/v1beta/{file_name}?key={API_KEY}"
    state = "PROCESSING"
    while state == "PROCESSING":
        time.sleep(3)
        state = requests.get(check_url, proxies=proxies).json().get("state", "ACTIVE")

    # 3. Tahlil
    payload = {
        "contents": [{
            "parts": [
                {"text": "Ushbu audioni tahlil qil va hisobot ber."},
                {"file_data": {"mime_type": mime_type, "file_uri": file_uri}}
            ]
        }]
    }
    gen_resp = requests.post(GEMINI_GENERATE_URL, json=payload, proxies=proxies, timeout=120)
    
    # 4. Tozalash
    requests.delete(check_url, proxies=proxies)
    return gen_resp.json()["candidates"][0]["content"]["parts"][0]["text"]

# ═══════════════════════════════════════════════════════════════
#  CHAT STREAMING (CORE LOGIC)
# ═══════════════════════════════════════════════════════════════

def stream_ai_response(user_message, history):
    proxies = _get_proxies()
    contents = []
    for msg in history:
        contents.append({"role": "user" if msg['role'] == "user" else "model", "parts": [{"text": msg['content']}]})
    contents.append({"role": "user", "parts": [{"text": user_message}]})

    payload = {
        "contents": contents,
        "tools": CRM_TOOLS,
        "systemInstruction": {"parts": [{"text": SYSTEM_PROMPT}]}
    }

    try:
        # Birinchi qadam: Modelga yuborish
        response = requests.post(GEMINI_GENERATE_URL, json=payload, proxies=proxies, timeout=30)
        res_json = response.json()
        print(res_json)
        if "candidates" not in res_json:
            yield f"data: {json.dumps({'error': 'API Error'})}\n\n"
            return

        part = res_json['candidates'][0]['content']['parts'][0]

        # 1. Agar AI FUNKSIYA chaqirsa
        if "functionCall" in part:
            fn_call = part["functionCall"]
            fn_name = fn_call["name"]
            fn_args = fn_call.get("args", {})

            # Ma'lumotlar bazasidan qidirish
            db_results = call_function(fn_name, fn_args)
            
            # Modelga funksiya natijasini qaytarish (MUHIM QADAM)
            contents.append({"role": "model", "parts": [part]}) # Modelning functionCall qismi
            contents.append({
                "role": "function", # Ba'zi v1beta'larda bu rol 'function' yoki 'user' bo'lishi mumkin
                "parts": [{
                    "functionResponse": {
                        "name": fn_name,
                        "response": {"content": db_results}
                    }
                }]
            })

            # Endi yakuniy javobni olish uchun qayta stream qilamiz
            final_payload = {"contents": contents, "tools": CRM_TOOLS}
            final_res = requests.post(GEMINI_URL, json=final_payload, proxies=proxies, stream=True, timeout=30)
            
            for line in final_res.iter_lines():
                if not line: continue
                decoded = line.decode('utf-8')
                if decoded.startswith("data: "):
                    try:
                        chunk = json.loads(decoded[6:])
                        token = chunk['candidates'][0]['content']['parts'][0].get('text', '')
                        if token: yield f"data: {json.dumps({'token': token})}\n\n"
                    except: continue

        # 2. Agar AI to'g'ridan-to'g'ri MATN yuborsa
        elif "text" in part:
            yield f"data: {json.dumps({'token': part['text']})}\n\n"

    except Exception as e:
        yield f"data: {json.dumps({'error': str(e)})}\n\n"

    yield f"data: {json.dumps({'done': True})}\n\n"

# Django view lar o'zgarishsiz qoladi
@csrf_exempt
def chat_send(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        return StreamingHttpResponse(stream_ai_response(data.get('message', ''), data.get('history', [])), content_type='text/event-stream')
    return JsonResponse({'error': 'Method not allowed'}, status=405)

def chat_view(request):
    return render(request, 'chat/chat_interface.html')