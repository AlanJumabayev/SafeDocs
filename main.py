from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import pytesseract
from PIL import Image
import PyPDF2
import io
import os
from typing import Dict, List, Optional
from pydantic import BaseModel
import json
from datetime import datetime
import uuid
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Модели данных
class DocumentAnalysis(BaseModel):
    document_id: str
    filename: str
    text_content: str
    risks: List[Dict]
    benefits: List[Dict]
    unclear_terms: List[Dict]
    overall_rating: str  # "безопасен", "требует внимания", "рискован"
    summary: str
    processed_at: str

class ChatMessage(BaseModel):
    document_id: str
    question: str

class ChatResponse(BaseModel):
    answer: str
    document_id: str

# Инициализация FastAPI
app = FastAPI(
    title="SafeDocs - AI защита юридических документов",
    description="Анализ договоров с фокусом на казахстанское законодательство",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Создаем папки если их нет
os.makedirs("static", exist_ok=True)
os.makedirs("uploads", exist_ok=True)

# Подключаем статические файлы
app.mount("/static", StaticFiles(directory="static"), name="static")

# Временное хранилище (в продакшене будет БД)
documents_storage = {}
chat_history = {}

class FileProcessor:
    """Обработка различных типов файлов"""
    
    @staticmethod
    def extract_text_from_pdf(file_content: bytes) -> str:
        """Извлечение текста из PDF"""
        try:
            pdf_file = io.BytesIO(file_content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            
            for page_num, page in enumerate(pdf_reader.pages):
                try:
                    page_text = page.extract_text()
                    if page_text.strip():
                        text += f"\n--- Страница {page_num + 1} ---\n"
                        text += page_text + "\n"
                except Exception as e:
                    print(f"Ошибка на странице {page_num + 1}: {e}")
                    continue
            
            if not text.strip():
                raise Exception("PDF файл не содержит читаемого текста")
                
            return text.strip()
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Ошибка обработки PDF: {str(e)}")
    
    @staticmethod
    def extract_text_from_image(file_content: bytes) -> str:
        """OCR извлечение текста из изображения"""
        try:
            image = Image.open(io.BytesIO(file_content))
            
            # Оптимизируем изображение для OCR
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Увеличиваем изображение для лучшего распознавания
            width, height = image.size
            if width < 1000:
                scale = 1000 / width
                new_width = int(width * scale)
                new_height = int(height * scale)
                image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # OCR с поддержкой русского и казахского
            custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯабвгдеёжзийклмнопрстуфхцчшщъыьэюяABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,;:!?()-_"№%'
            text = pytesseract.image_to_string(image, lang='rus+eng', config=custom_config)
            
            if not text.strip():
                raise Exception("Не удалось распознать текст на изображении")
                
            return text.strip()
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Ошибка OCR: {str(e)}")

class AIAnalyzer:
    """AI анализ документов (пока простой, потом Gemini)"""
    
    @staticmethod
    def analyze_document(text: str, filename: str) -> DocumentAnalysis:
        """Анализ юридического документа"""
        
        text_lower = text.lower()
        
        # Поиск рисков
        risks = []
        risk_patterns = {
            "штрафные санкции": ["штраф", "пеня", "неустойка", "санкции"],
            "односторонние условия": ["односторонн", "в любое время", "по своему усмотрению", "вправе расторгнуть"],
            "высокая ответственность": ["полная ответственность", "возмещение всех", "солидарная ответственность"],
            "неопределенные сроки": ["разумный срок", "в кратчайшие сроки", "незамедлительно", "без промедления"],
            "финансовые риски": ["за свой счет", "без возмещения", "безвозмездно", "убытки покупателя"]
        }
        
        for risk_type, keywords in risk_patterns.items():
            for keyword in keywords:
                if keyword in text_lower:
                    # Находим контекст
                    start_pos = text_lower.find(keyword)
                    context_start = max(0, start_pos - 100)
                    context_end = min(len(text), start_pos + 200)
                    context = text[context_start:context_end].strip()
                    
                    risks.append({
                        "type": risk_type,
                        "keyword": keyword,
                        "context": context,
                        "severity": "высокий" if any(x in keyword for x in ["штраф", "полная ответственность"]) else "средний",
                        "recommendation": f"Рекомендуется пересмотреть условия, связанные с '{keyword}'"
                    })
                    break  # Один риск на тип
        
        # Поиск выгодных условий
        benefits = []
        benefit_patterns = {
            "гарантии": ["гарантия", "гарантирует", "обязуется"],
            "защита интересов": ["страхование", "компенсация", "возмещение"],
            "гибкие условия": ["по согласованию", "возможность изменения", "право выбора"],
            "возврат средств": ["возврат", "возмещение платежа", "компенсация расходов"]
        }
        
        for benefit_type, keywords in benefit_patterns.items():
            for keyword in keywords:
                if keyword in text_lower:
                    start_pos = text_lower.find(keyword)
                    context_start = max(0, start_pos - 100)
                    context_end = min(len(text), start_pos + 200)
                    context = text[context_start:context_end].strip()
                    
                    benefits.append({
                        "type": benefit_type,
                        "keyword": keyword,
                        "context": context,
                        "value": "высокая" if "гарантия" in keyword else "средняя"
                    })
                    break
        
        # Поиск неясных терминов
        unclear_terms = []
        unclear_patterns = [
            "в установленном порядке", "соответствующие меры", "надлежащим образом",
            "разумный срок", "существенные нарушения", "форс-мажорные обстоятельства",
            "иные обстоятельства", "по обоюдному согласию", "в исключительных случаях"
        ]
        
        for pattern in unclear_patterns:
            if pattern in text_lower:
                start_pos = text_lower.find(pattern)
                context_start = max(0, start_pos - 100)
                context_end = min(len(text), start_pos + 200)
                context = text[context_start:context_end].strip()
                
                unclear_terms.append({
                    "phrase": pattern,
                    "context": context,
                    "explanation": f"Фраза '{pattern}' требует уточнения конкретных условий",
                    "suggestion": "Рекомендуется запросить детализацию данного пункта"
                })
        
        # Общая оценка
        risk_count = len(risks)
        severe_risks = len([r for r in risks if r.get("severity") == "высокий"])
        
        if severe_risks > 0:
            overall_rating = "рискован"
        elif risk_count > 3:
            overall_rating = "требует внимания"
        elif risk_count > 0:
            overall_rating = "требует внимания"
        else:
            overall_rating = "безопасен"
        
        # Краткое резюме
        summary = f"""
Документ '{filename}' проанализирован:

🔍 ОСНОВНЫЕ НАХОДКИ:
• Рисков найдено: {len(risks)}
• Выгодных условий: {len(benefits)}
• Неясных формулировок: {len(unclear_terms)}

⚖️ ОБЩАЯ ОЦЕНКА: {overall_rating.upper()}

💡 РЕКОМЕНДАЦИИ:
{"• Обратите особое внимание на штрафные санкции" if any("штраф" in r["keyword"] for r in risks) else ""}
{"• Уточните неопределенные формулировки" if unclear_terms else ""}
{"• Используйте найденные гарантии в свою пользу" if benefits else ""}

📋 Этот анализ основан на базовых правилах. Для детального изучения рекомендуется консультация с юристом.
        """.strip()
        
        return DocumentAnalysis(
            document_id=str(uuid.uuid4()),
            filename=filename,
            text_content=text[:2000] + "..." if len(text) > 2000 else text,
            risks=risks,
            benefits=benefits,
            unclear_terms=unclear_terms,
            overall_rating=overall_rating,
            summary=summary,
            processed_at=datetime.now().isoformat()
        )

# API Routes
@app.get("/")
async def get_main_page():
    """Главная страница приложения"""
    try:
        return FileResponse('static/index.html')
    except FileNotFoundError:
        # Если файла нет, возвращаем базовую страницу
        return {"message": "SafeDocs API работает. Создайте файл static/index.html для веб-интерфейса."}

@app.post("/api/analyze", response_model=DocumentAnalysis)
async def analyze_document(file: UploadFile = File(...)):
    """Анализ загруженного документа"""
    
    # Проверяем тип файла
    allowed_types = {
        'application/pdf': 'pdf',
        'image/jpeg': 'image',
        'image/jpg': 'image', 
        'image/png': 'image',
        'text/plain': 'text'
    }
    
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400, 
            detail=f"Неподдерживаемый тип файла. Поддерживаются: PDF, JPG, PNG, TXT"
        )
    
    # Проверяем размер файла (макс 10MB)
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    file_content = await file.read()
    
    if len(file_content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="Файл слишком большой (макс 10MB)")
    
    if len(file_content) == 0:
        raise HTTPException(status_code=400, detail="Файл пустой")
    
    # Сохраняем файл
    file_path = f"uploads/{uuid.uuid4()}_{file.filename}"
    with open(file_path, "wb") as f:
        f.write(file_content)
    
    file_type = allowed_types[file.content_type]
    
    # Извлекаем текст
    try:
        if file_type == 'pdf':
            text = FileProcessor.extract_text_from_pdf(file_content)
        elif file_type == 'image':
            text = FileProcessor.extract_text_from_image(file_content)
        elif file_type == 'text':
            text = file_content.decode('utf-8')
        
        if len(text.strip()) < 50:
            raise HTTPException(
                status_code=400, 
                detail="Слишком мало текста для анализа (минимум 50 символов)"
            )
        
        # Анализируем документ
        analysis = AIAnalyzer.analyze_document(text, file.filename)
        
        # Сохраняем результат
        documents_storage[analysis.document_id] = analysis
        
        return analysis
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка анализа: {str(e)}")

@app.post("/api/chat", response_model=ChatResponse)
async def chat_with_document(message: ChatMessage):
    """Чат с AI по документу"""
    
    if message.document_id not in documents_storage:
        raise HTTPException(status_code=404, detail="Документ не найден")
    
    document = documents_storage[message.document_id]
    
    # Простой чат (позже заменим на Gemini)
    question_lower = message.question.lower()
    
    # Готовые ответы на частые вопросы
    if any(word in question_lower for word in ["риск", "опасн", "штраф"]):
        risks_text = "\n".join([f"• {r['type']}: {r['recommendation']}" for r in document.risks])
        answer = f"🚨 В документе найдены следующие риски:\n\n{risks_text}" if risks_text else "В документе не найдено серьезных рисков."
    
    elif any(word in question_lower for word in ["выгод", "плюс", "хорош"]):
        benefits_text = "\n".join([f"• {b['type']}: {b['keyword']}" for b in document.benefits])
        answer = f"✅ Выгодные условия в документе:\n\n{benefits_text}" if benefits_text else "Явных выгодных условий не найдено."
    
    elif any(word in question_lower for word in ["непонятн", "неясн", "что означает"]):
        unclear_text = "\n".join([f"• {u['phrase']}: {u['explanation']}" for u in document.unclear_terms])
        answer = f"❓ Неясные формулировки:\n\n{unclear_text}" if unclear_text else "Все формулировки достаточно понятны."
    
    elif any(word in question_lower for word in ["подписывать", "согласиться", "стоит ли"]):
        answer = f"""
🤔 Рекомендация по документу:

Общая оценка: {document.overall_rating}

{"⚠️ Рекомендую внимательно изучить риски перед подписанием." if document.overall_rating != "безопасен" else "✅ Документ выглядит относительно безопасным."}

💡 Советую:
1. Проконсультироваться с юристом
2. Обратить внимание на найденные риски
3. Уточнить неясные формулировки

Помните: это базовый анализ, окончательное решение за вами!
        """
    
    else:
        answer = f"""
💬 Спасибо за вопрос! 

Я проанализировал ваш документ "{document.filename}" и могу ответить на вопросы о:
• Рисках в договоре
• Выгодных условиях  
• Неясных формулировках
• Рекомендациях по подписанию

Попробуйте спросить: "Какие есть риски?" или "Стоит ли подписывать?"

🔬 В разработке: полноценный AI-помощник с детальным анализом каждого пункта.
        """
    
    # Сохраняем в историю чата
    if message.document_id not in chat_history:
        chat_history[message.document_id] = []
    
    chat_history[message.document_id].append({
        "question": message.question,
        "answer": answer,
        "timestamp": datetime.now().isoformat()
    })
    
    return ChatResponse(answer=answer, document_id=message.document_id)

@app.get("/api/documents")
async def get_documents():
    """Список проанализированных документов"""
    return {
        "documents": [
            {
                "id": doc_id,
                "filename": doc.filename,
                "overall_rating": doc.overall_rating,
                "processed_at": doc.processed_at,
                "risks_count": len(doc.risks),
                "benefits_count": len(doc.benefits)
            }
            for doc_id, doc in documents_storage.items()
        ]
    }

@app.get("/api/documents/{document_id}")
async def get_document(document_id: str):
    """Детали анализа документа"""
    if document_id not in documents_storage:
        raise HTTPException(status_code=404, detail="Документ не найден")
    
    return documents_storage[document_id]

@app.get("/api/health")
async def health_check():
    """Проверка работоспособности API"""
    return {
        "status": "healthy",
        "service": "SafeDocs",
        "version": "1.0.0",
        "documents_count": len(documents_storage)
    }

if __name__ == "__main__":
    import uvicorn
    
    print("🛡️  SafeDocs запускается...")
    print("🌐 Веб-приложение: http://localhost:8000")
    print("📚 API документация: http://localhost:8000/docs")
    print("🔬 Тестирование API: http://localhost:8000/redoc")
    
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)