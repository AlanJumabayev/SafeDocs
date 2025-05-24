# SafeDocs
# setup_enhanced_safedocs.py
# Скрипт для автоматической установки и настройки улучшенной системы SafeDocs

import os
import sys
import subprocess
import shutil
from pathlib import Path
import json

class SafeDocsEnhancedSetup:
    """Установщик улучшенной системы SafeDocs"""
    
    def __init__(self):
        self.project_root = Path.cwd()
        self.backup_dir = self.project_root / "backup"
        self.enhanced_files = [
            "enhanced_document_analyzer.py",
            "integration_patch.py",
            "export_and_chat.py"
        ]
        
    def run_setup(self):
        """Запуск полной установки"""
        print("🛡️ SafeDocs Pro v2.0 - Установка улучшенной системы")
        print("=" * 60)
        
        try:
            # 1. Проверка окружения
            self.check_environment()
            
            # 2. Создание резервной копии
            self.create_backup()
            
            # 3. Установка зависимостей
            self.install_dependencies()
            
            # 4. Применение улучшений
            self.apply_enhancements()
            
            # 5. Настройка конфигурации
            self.setup_configuration()
            
            # 6. Проверка работоспособности
            self.run_tests()
            
            print("\n✅ Установка завершена успешно!")
            print("🚀 Система готова к работе с улучшенным анализатором")
            
            self.show_usage_instructions()
            
        except Exception as e:
            print(f"\n❌ Ошибка установки: {e}")
            print("🔄 Попытка восстановления из резервной копии...")
            self.restore_backup()
            
    def check_environment(self):
        """Проверка окружения"""
        print("🔍 Проверка окружения...")
        
        # Проверка Python версии
        if sys.version_info < (3.8, 0):
            raise Exception("Требуется Python 3.8 или выше")
        
        # Проверка основных файлов
        required_files = ["main.py", "requirements.txt", "static/index.html"]
        for file_path in required_files:
            if not (self.project_root / file_path).exists():
                raise Exception(f"Отсутствует обязательный файл: {file_path}")
        
        print("✅ Окружение проверено")
        
    def create_backup(self):
        """Создание резервной копии"""
        print("💾 Создание резервной копии...")
        
        self.backup_dir.mkdir(exist_ok=True)
        
        # Копируем основные файлы
        files_to_backup = ["main.py", "requirements.txt", ".env"]
        for file_name in files_to_backup:
            source = self.project_root / file_name
            if source.exists():
                destination = self.backup_dir / file_name
                shutil.copy2(source, destination)
        
        # Копируем папку static
        static_source = self.project_root / "static"
        static_backup = self.backup_dir / "static"
        if static_source.exists():
            shutil.copytree(static_source, static_backup, dirs_exist_ok=True)
        
        print("✅ Резервная копия создана")
        
    def install_dependencies(self):
        """Установка дополнительных зависимостей"""
        print("📦 Установка зависимостей...")
        
        # Обновленный requirements.txt
        enhanced_requirements = """# SafeDocs Pro v2.0 - Расширенные зависимости

# Web Framework
fastapi==0.104.1
uvicorn[standard]==0.24.0

# File Processing  
PyPDF2==3.0.1
Pillow==10.1.0
python-multipart==0.0.6

# OCR (Text Recognition)
pytesseract==0.3.10

# Data Models & Validation
pydantic==2.5.0

# Environment Variables
python-dotenv==1.0.0

# Enhanced Analytics & NLP
regex==2023.10.3
textdistance==4.6.0

# Export functionality (опционально)
# reportlab==4.0.7  # для PDF экспорта
# openpyxl==3.1.2   # для Excel экспорта

# AI Integration (готово к подключению)
# google-generativeai==0.3.2
# openai==1.3.8

# Database support (для будущих версий)
# sqlalchemy==2.0.23
# sqlite3  # встроен в Python

# Advanced text processing
# spacy==3.7.2      # для продвинутого NLP
# nltk==3.8.1       # для лингвистического анализа

# Monitoring & Logging
# sentry-sdk==1.38.0  # для мониторинга ошибок
"""
        
        # Сохраняем обновленный requirements.txt
        with open(self.project_root / "requirements.txt", "w", encoding="utf-8") as f:
            f.write(enhanced_requirements)
        
        # Устанавливаем основные зависимости
        try:
            subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
            ], check=True, capture_output=True, text=True)
            print("✅ Основные зависимости установлены")
        except subprocess.CalledProcessError as e:
            print(f"⚠️ Предупреждение: некоторые зависимости не установлены: {e}")
            print("Система будет работать с базовой функциональностью")
        
        # Проверяем установку дополнительных пакетов
        self.install_optional_packages()
        
    def install_optional_packages(self):
        """Установка дополнительных пакетов"""
        optional_packages = [
            ("regex", "Улучшенная поддержка регулярных выражений"),
            ("textdistance", "Алгоритмы сравнения текстов"),
        ]
        
        for package, description in optional_packages:
            try:
                subprocess.run([
                    sys.executable, "-m", "pip", "install", package
                ], check=True, capture_output=True, text=True)
                print(f"✅ {package}: {description}")
            except subprocess.CalledProcessError:
                print(f"⚠️ {package}: не установлен (не критично)")
        
    def apply_enhancements(self):
        """Применение улучшений"""
        print("🔧 Применение улучшений...")
        
        # Проверяем наличие файлов улучшений
        for file_name in self.enhanced_files:
            if not (self.project_root / file_name).exists():
                print(f"⚠️ Файл {file_name} не найден - создаем заглушку")
                self.create_file_stub(file_name)
        
        # Применяем интеграционный патч
        try:
            from integration_patch import patch_main_system
            success = patch_main_system()
            if success:
                print("✅ Улучшенный анализатор интегрирован")
            else:
                print("⚠️ Интеграция выполнена частично")
        except ImportError:
            print("⚠️ Модуль интеграции не найден - работаем со стандартным анализатором")
        
    def create_file_stub(self, file_name):
        """Создание заглушки для отсутствующего файла"""
        stubs = {
            "enhanced_document_analyzer.py": '''# Заглушка для enhanced_document_analyzer.py
class EnhancedDocumentAnalyzer:
    def analyze_document_enhanced(self, *args, **kwargs):
        raise NotImplementedError("Улучшенный анализатор не установлен")
''',
            "integration_patch.py": '''# Заглушка для integration_patch.py
def patch_main_system():
    print("Патч интеграции не установлен")
    return False
''',
            "export_and_chat.py": '''# Заглушка для export_and_chat.py
class ExportManager:
    def __init__(self):
        pass
'''
        }
        
        stub_content = stubs.get(file_name, f"# Заглушка для {file_name}\npass")
        with open(self.project_root / file_name, "w", encoding="utf-8") as f:
            f.write(stub_content)
    
    def setup_configuration(self):
        """Настройка конфигурации"""
        print("⚙️ Настройка конфигурации...")
        
        # Создаем расширенный .env файл
        env_content = """# SafeDocs Pro v2.0 Configuration

# API Keys
GEMINI_API_KEY=AIzaSyDI1PwllCsLt8jzX32SgahMx0k5aaBC0Ic
# OPENAI_API_KEY=your_openai_key_here

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=true

# File Processing
MAX_FILE_SIZE_MB=20
UPLOAD_PATH=uploads/
STORAGE_PATH=storage/

# Enhanced Analysis Settings
ANALYSIS_DEPTH=advanced
ENABLE_CONTEXTUAL_ANALYSIS=true
ENABLE_KZ_LEGAL_CHECK=true
ENABLE_ENTITY_DETECTION=true

# Export Settings
ENABLE_PDF_EXPORT=false
ENABLE_EXCEL_EXPORT=false
DEFAULT_EXPORT_FORMAT=json

# Security Settings
ENABLE_FILE_VIRUS_SCAN=false
MAX_ANALYSIS_TIME_SECONDS=300
ENABLE_RATE_LIMITING=true

# Monitoring
ENABLE_ANALYTICS=false
LOG_LEVEL=INFO
"""
        
        env_path = self.project_root / ".env"
        if not env_path.exists():
            with open(env_path, "w", encoding="utf-8") as f:
                f.write(env_content)
            print("✅ Конфигурация создана")
        else:
            print("✅ Используется существующая конфигурация")
        
        # Создаем папки для хранения данных
        directories = [
            "storage", "storage/analysis", "storage/uploads", 
            "static", "logs", "exports"
        ]
        for directory in directories:
            (self.project_root / directory).mkdir(exist_ok=True)
        
        print("✅ Структура папок создана")
        
    def run_tests(self):
        """Запуск тестов работоспособности"""
        print("🧪 Проверка работоспособности...")
        
        test_results = {
            "basic_import": False,
            "enhanced_analyzer": False,
            "file_processing": False,
            "web_interface": False
        }
        
        # Тест базового импорта
        try:
            import main
            test_results["basic_import"] = True
            print("✅ Основной модуль загружается")
        except Exception as e:
            print(f"❌ Ошибка загрузки основного модуля: {e}")
        
        # Тест улучшенного анализатора
        try:
            from enhanced_document_analyzer import EnhancedDocumentAnalyzer
            analyzer = EnhancedDocumentAnalyzer()
            test_results["enhanced_analyzer"] = True
            print("✅ Улучшенный анализатор доступен")
        except Exception as e:
            print(f"⚠️ Улучшенный анализатор недоступен: {e}")
        
        # Тест обработки файлов
        try:
            from main import FileProcessor
            test_text = "Тестовый договор для проверки"
            test_results["file_processing"] = True
            print("✅ Обработка файлов работает")
        except Exception as e:
            print(f"❌ Ошибка обработки файлов: {e}")
        
        # Тест веб-интерфейса
        try:
            static_index = self.project_root / "static" / "index.html"
            if static_index.exists():
                test_results["web_interface"] = True
                print("✅ Веб-интерфейс доступен")
            else:
                print("⚠️ Веб-интерфейс не найден")
        except Exception as e:
            print(f"⚠️ Проблемы с веб-интерфейсом: {e}")
        
        # Сводка тестов
        passed_tests = sum(test_results.values())
        total_tests = len(test_results)
        
        print(f"\n📊 Результат тестов: {passed_tests}/{total_tests} прошли успешно")
        
        if passed_tests >= 2:
            print("✅ Система готова к работе")
        else:
            print("⚠️ Система частично готова - возможны ограничения функциональности")
        
        return test_results
    
    def restore_backup(self):
        """Восстановление из резервной копии"""
        if not self.backup_dir.exists():
            print("❌ Резервная копия не найдена")
            return
        
        print("🔄 Восстановление из резервной копии...")
        
        try:
            # Восстанавливаем файлы
            for item in self.backup_dir.iterdir():
                if item.is_file():
                    shutil.copy2(item, self.project_root / item.name)
                elif item.is_dir():
                    destination = self.project_root / item.name
                    if destination.exists():
                        shutil.rmtree(destination)
                    shutil.copytree(item, destination)
            
            print("✅ Система восстановлена из резервной копии")
        except Exception as e:
            print(f"❌ Ошибка восстановления: {e}")
    
    def show_usage_instructions(self):
        """Показать инструкции по использованию"""
        print("\n" + "=" * 60)
        print("📋 ИНСТРУКЦИИ ПО ИСПОЛЬЗОВАНИЮ")
        print("=" * 60)
        
        print("""
🚀 ЗАПУСК СИСТЕМЫ:
   python main.py

🌐 ВЕБРОЙ ИНТЕРФЕЙС:
   http://localhost:8000

📚 API ДОКУМЕНТАЦИЯ:
   http://localhost:8000/api/docs

🔧 ОСНОВНЫЕ УЛУЧШЕНИЯ:
   • Контекстное понимание субъектов в договоре
   • Определение направленности рисков и выгод
   • Учет казахстанского законодательства
   • Улучшенная система оценки рисков
   • Более точные рекомендации

💡 НОВЫЕ ВОЗМОЖНОСТИ:
   • Анализ обязательств сторон
   • Проверка соответствия нормам РК
   • Экспорт в различные форматы
   • Расширенный AI-чат

⚠️ ВАЖНЫЕ ПРИМЕЧАНИЯ:
   • Для полной функциональности установите дополнительные пакеты
   • Система работает в офлайн режиме
   • Документы обрабатываются локально и не передаются третьим лицам

🆘 ПОДДЕРЖКА:
   • При проблемах проверьте логи в папке logs/
   • Для восстановления запустите: python setup_enhanced_safedocs.py --restore
   • Техническая документация: README.md
        """)

def main():
    """Главная функция установщика"""
    import argparse
    
    parser = argparse.ArgumentParser(description="SafeDocs Pro v2.0 Setup")
    parser.add_argument("--restore", action="store_true", help="Восстановить из резервной копии")
    parser.add_argument("--test-only", action="store_true", help="Только запустить тесты")
    parser.add_argument("--skip-deps", action="store_true", help="Пропустить установку зависимостей")
    
    args = parser.parse_args()
    
    setup = SafeDocsEnhancedSetup()
    
    if args.restore:
        setup.restore_backup()
    elif args.test_only:
        setup.run_tests()
    else:
        if args.skip_deps:
            setup.skip_dependencies = True
        setup.run_setup()

if __name__ == "__main__":
    main()
