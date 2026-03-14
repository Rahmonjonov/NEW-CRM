import json
import requests
import random
from django.http import StreamingHttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from .functions import *
"AIzaSyDAh_VfuqrI8zoma7ZN0lGu33_u977GBEE"
"AIzaSyAn4TX1VqEliKOXgoMHGZykNtTH3WLIBYg"
API_KEY = "AIzaSyDAh_VfuqrI8zoma7ZN0lGu33_u977GBEE"
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:streamGenerateContent?alt=sse&key={API_KEY}"

# ============== HTTP PROXY LIST (SOCKS5 o'rniga) ==============
HTTP_PROXIES = [
    {'proxy': 'http://vdkddoct:2cqkbc4zn6oo@31.59.20.176:6754', 'country': 'UK'},
    {'proxy': 'http://vdkddoct:2cqkbc4zn6oo@23.95.150.145:6114', 'country': 'USA'},
    {'proxy': 'http://vdkddoct:2cqkbc4zn6oo@198.23.239.134:6540', 'country': 'USA'},
    # {'proxy': 'http://vdkddoct:2cqkbc4zn6oo@45.38.107.97:6014', 'country': 'UK'},
    # {'proxy': 'http://vdkddoct:2cqkbc4zn6oo@107.172.163.27:6543', 'country': 'USA'},
    # {'proxy': 'http://vdkddoct:2cqkbc4zn6oo@198.105.121.200:6462', 'country': 'UK'},
    # {'proxy': 'http://vdkddoct:2cqkbc4zn6oo@64.137.96.74:6641', 'country': 'Spain'},
    # {'proxy': 'http://vdkddoct:2cqkbc4zn6oo@216.10.27.159:6837', 'country': 'USA'},
    # {'proxy': 'http://vdkddoct:2cqkbc4zn6oo@142.111.67.146:5611', 'country': 'Japan'},
    # {'proxy': 'http://vdkddoct:2cqkbc4zn6oo@194.39.32.164:6461', 'country': 'Germany'},
]

# ============== PROXY TEST ==============
def test_proxies():
    """Proxylarni test qilish"""
    working_proxies = []
    
    print("🔄 Proxylar tekshirilmoqda...")
    for i, proxy_data in enumerate(HTTP_PROXIES, 1):
        proxy = proxy_data['proxy']
        country = proxy_data['country']
        try:
            response = requests.get(
                'https://api.ipify.org?format=json',
                proxies={'http': proxy, 'https': proxy},
                timeout=5
            )
            if response.status_code == 200:
                ip = response.json()['ip']
                print(f"✅ [{i}/{len(HTTP_PROXIES)}] {country} proxy ishlayapti: {proxy} -> IP: {ip}")
                working_proxies.append(proxy)
            else:
                print(f"❌ [{i}/{len(HTTP_PROXIES)}] {country} proxy ishlamayapti")
        except Exception as e:
            print(f"❌ [{i}/{len(HTTP_PROXIES)}] {country} proxy xatolik: {str(e)[:50]}")
    
    return working_proxies

# Proxylarni test qilish
WORKING_PROXIES = test_proxies()
print(f"\n🎯 Jami ishlaydigan proxylar: {len(WORKING_PROXIES)} ta")

# ============== SIZNING ASL KODINGIZ ==============
def chat_view(request):
    return render(request, 'chat/chat_interface.html')

@csrf_exempt
def chat_send(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '')
            history = data.get('history', [])

            if not user_message.strip():
                return JsonResponse({'error': 'Empty message'}, status=400)

            return StreamingHttpResponse(
                stream_ai_response(user_message, history),
                content_type='text/event-stream'
            )
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Method not allowed'}, status=405)


CRM_TOOLS = [
    {
        "function_declarations": [
            {
                "name": "search_leads", # Funksiyangizning nomi
                "description": "Leadlarni ismi, manzili, holati yoki emotsiyasi bo'yicha qidirish uchun ishlatiladi, parameters dan boshqa narsalarni funksiyaga berma.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        # Funksiyangiz qabul qiladigan argumentlar:
                        "name_input": {"type": "string", "description": "Mijozning ismi"},
                        "location_input": {"type": "string", "description": "Shahar, viloyat yoki tuman nomi"},
                        "status_input": {"type": "string", "description": "Leadning hozirgi holati"},
                        "emotion_input": {"type": "string", "description": "Mijozning kayfiyati yoki emotsiyasi"}
                    },
                    "required": [] # Majburiy bo'lmagan parametrlar
                }
            }
        ]
    }
]


def stream_ai_response(user_message, history):
    # 2. Avval payloadni tayyorlaymiz
    contents = []
    for msg in history:
        role = "user" if msg['role'] == "user" else "model"
        contents.append({"role": role, "parts": [{"text": msg['content']}]})
    
    contents.append({"role": "user", "parts": [{"text": user_message}]})

    payload = {
        "contents": contents,
        "tools": CRM_TOOLS,
        "systemInstruction": {
            "parts": [{"text": "Siz aqlli CRM yordamchisiz. Leadlarni qidirishda 'search_leads' funksiyasidan foydalaning."}]
        }
    }

    # 3. Response o'zgaruvchisini bo'sh holatda e'lon qilamiz
    response = None
    full_ai_response = ""
    function_call_data = None

    print(f"\n--- AI PROCESS START ---")

    try:
        # Proxy tanlash (Agar WORKING_PROXIES bo'lsa)
        proxy = WORKING_PROXIES[0] if 'WORKING_PROXIES' in globals() and WORKING_PROXIES else None
        proxies = {'http': proxy, 'https': proxy} if proxy else None

        # 4. Endi so'rov yuboramiz (Payload endi aniq bor)
        response = requests.post(
            GEMINI_URL, 
            json=payload, 
            stream=True, 
            timeout=30,
            proxies=proxies
        )

        if response.status_code != 200:
            print(f"❌ API Xato: {response.status_code} - {response.text}")
            yield f"data: {json.dumps({'error': f'API Error {response.status_code}'})}\n\n"
            return

        # 5. Javobni o'qish
        for line in response.iter_lines():
            if not line: continue
            decoded_line = line.decode('utf-8')
            
            if decoded_line.startswith("data: "):
                try:
                    chunk_json = json.loads(decoded_line[6:])
                    if 'candidates' not in chunk_json: continue
                    
                    part = chunk_json['candidates'][0]['content']['parts'][0]

                    # AI Funksiya chaqirsa
                    if "functionCall" in part:
                        function_call_data = part["functionCall"]
                        print(f"🔹 AI FUNKSIYA CHAQIRDI: {function_call_data['name']}")
                        print(f"🔹 ARGUMENTLAR: {json.dumps(function_call_data.get('args'), indent=2, ensure_ascii=False)}")
                        break 

                    # AI matn yuborsa
                    if "text" in part:
                        token = part["text"]
                        full_ai_response += token
                        yield f"data: {json.dumps({'token': token})}\n\n"
                except: continue

    except Exception as e:
        print(f"🔥 KRITIK XATOLIK: {str(e)}")
        yield f"data: {json.dumps({'error': str(e)})}\n\n"
        return

    # 6. Agar matnli javob bo'lsa, uni terminalda ko'ramiz
    if full_ai_response:
        print(f"📝 AI TO'LIQ JAVOBI: {full_ai_response}")

    # 7. Agar funksiya chaqirilgan bo'lsa, DB dan qidiramiz
    if function_call_data:
        args = function_call_data.get("args", {})
        db_results = search_leads(**args) # O'zingizning search_leads funksiyangiz
        
        if db_results['status'] == 'success':
            res_text = "\n\n🔍 **Topilgan natijalar:**\n"
            for lead in db_results['data']:
                res_text += f"👤 {lead['ism']} | 📍 {lead['manzil']}\n"
            print(f"📊 BAZA: {len(db_results['data'])} ta lead topildi.")
            yield f"data: {json.dumps({'token': res_text})}\n\n"
        else:
            print("⚠️ BAZA: Hech narsa topilmadi.")
            yield f"data: {json.dumps({'token': 'Ma’lumot topilmadi.'})}\n\n"

    print(f"--- AI PROCESS END ---\n")
    yield f"data: {json.dumps({'done': True})}\n\n"