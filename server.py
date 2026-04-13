"""
Dahua Product Finder - Backend Server
======================================
Claude API-тай холбогдож, AI шийдэл олгогч ажиллуулна.

Ажиллуулах:
  pip install anthropic flask
  python server.py

Дараа нь browser-аа нээгээд: http://localhost:5000
"""

import os
import json
import re
from pathlib import Path
from flask import Flask, request, jsonify, send_from_directory
import anthropic

app = Flask(__name__, static_folder='.', static_url_path='')

# Serve the HTML file
@app.route('/')
def index():
    return send_from_directory('.', 'dahua-product-finder.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    api_key = data.get('apiKey', '')
    message = data.get('message', '')
    product_context = data.get('productContext', '')

    if not api_key:
        return jsonify({'error': 'API key шаардлагатай'}), 400

    try:
        client = anthropic.Anthropic(api_key=api_key)

        system_prompt = """Та Dahua камер, хяналтын систем, аюулгүй байдлын тоног төхөөрөмжийн мэргэжлийн зөвлөх AI байна. ITZONE LLC компанийн дотоод систем дээр ажиллаж байна.

Таны үүрэг:
1. Хэрэглэгчийн шаардлагыг ойлгох (Монгол эсвэл Англи хэлээр)
2. Бүтээгдэхүүний жагсаалтаас хамгийн тохирох моделиудыг санал болгох
3. Яагаад тухайн моделийг сонгосноо товч тайлбарлах
4. Техникийн үзүүлэлтүүдийг Монгол хэлээр тайлбарлах

Хариулахдаа:
- Монгол хэлээр хариулна
- Хамгийн тохирох 3-5 моделийг санал болгоно
- Модел бүрийн давуу талыг товч тайлбарлана
- Үнийн мэдээлэл оруулна (CNY)
- Хэрэв тохирох бүтээгдэхүүн олдохгүй бол ойролцоо хувилбар санал болгоно

ЧУХАЛ: Хариултынхаа ТӨГСГӨЛД дараах JSON форматаар зөвлөсөн моделиудаа жагсаана уу:
###MODELS###["DH-IPC-XXX", "DH-IPC-YYY"]###END###

Энэ JSON нь frontend-д бүтээгдэхүүний карт харуулахад ашиглагдана."""

        user_message = f"""Хэрэглэгчийн хүсэлт: {message}

Боломжит бүтээгдэхүүнүүд (модел | ангилал | цуврал | хэлбэр | нягтрал | IR зай | хамгаалалт | үнэ):
{product_context}"""

        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}]
        )

        ai_text = response.content[0].text

        # Extract recommended models from the response
        recommended = []
        model_match = re.search(r'###MODELS###(.+?)###END###', ai_text)
        if model_match:
            try:
                recommended = json.loads(model_match.group(1))
            except:
                pass
            # Remove the JSON tag from displayed text
            ai_text = re.sub(r'###MODELS###.+?###END###', '', ai_text).strip()

        return jsonify({
            'response': ai_text,
            'recommendedModels': recommended
        })

    except anthropic.AuthenticationError:
        return jsonify({'error': 'API key буруу байна. Зөв Anthropic API key оруулна уу.'}), 401
    except anthropic.RateLimitError:
        return jsonify({'error': 'API хязгаарлалтанд орлоо. Түр хүлээгээд дахин оролдоно уу.'}), 429
    except Exception as e:
        return jsonify({'error': f'Алдаа: {str(e)}'}), 500


if __name__ == '__main__':
    print("""
╔══════════════════════════════════════════════════╗
║   DAHUA Шийдэл Олгогч — AI Powered              ║
║   ITZONE LLC                                     ║
╠══════════════════════════════════════════════════╣
║                                                  ║
║   Сервер ажиллаж байна: http://localhost:5000    ║
║                                                  ║
║   Browser-аа нээгээд дээрх хаягаар орно уу.     ║
║   Зогсоох: Ctrl+C                               ║
║                                                  ║
╚══════════════════════════════════════════════════╝
    """)
    app.run(host='0.0.0.0', port=5000, debug=True)
