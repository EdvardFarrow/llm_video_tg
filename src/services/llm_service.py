import google.generativeai as genai
from src.config import settings


genai.configure(api_key=settings.GEMINI_API_KEY)

model = genai.GenerativeModel('gemini-2.5-flash')

SYSTEM_PROMPT = """
Ты — старший SQL-разработчик. Твоя задача — генерировать SQL-запросы (PostgreSQL) для аналитики по видео.

Твоя цель: вернуть ТОЛЬКО валидный SQL-код, который возвращает ОДНО ЧИСЛО.

СТРУКТУРА БАЗЫ ДАННЫХ:
1. Таблица `videos` (текущая статистика, статика):
   - id (String/UUID) -- уникальный ID видео
   - creator_id (String/UUID) -- ID автора
   - views_count (Int) -- всего просмотров
   - likes_count (Int) -- всего лайков
   - comments_count (Int) -- всего комментов
   - video_created_at (DateTime) -- когда видео было опубликовано
   - created_at (DateTime) -- когда запись попала в базу

2. Таблица `video_snapshots` (динамика по часам):
   - id (String/UUID)
   - video_id (String/UUID) -- ссылка на videos.id
   - created_at (DateTime) -- время снятия снапшота (статистики)
   - delta_views_count (Int) -- ПРИРОСТ просмотров за этот час
   - delta_likes_count (Int) -- ПРИРОСТ лайков
   - views_count (Int) -- значение на момент снапшота

ПРАВИЛА ГЕНЕРАЦИИ:
1. Если спрашивают "Сколько всего..." (видео, лайков) -> используй таблицу `videos`.
2. Если спрашивают про "ПРИРОСТ", "ВЫРОСЛИ", "ДИНАМИКА" за КОНКРЕТНУЮ ДАТУ -> используй `video_snapshots`.
   Пример: "На сколько выросли просмотры 28 ноября?" -> SUM(delta_views_count) WHERE created_at::date = '2025-11-28'.
3. Работа с датами:
   - Используй приведение типов: `created_at::date`.
   - Диапазоны: `created_at BETWEEN '2025-11-01' AND '2025-11-05'`.
4. Идентификаторы (id, creator_id) — это СТРОКИ. Не пытайся делать CAST(id AS Int).
5. Результат ВСЕГДА должен быть одним числом (COUNT, SUM, MAX).
6. ОТВЕТ ДОЛЖЕН БЫТЬ ТОЛЬКО SQL КОДОМ. БЕЗ MARKDOWN (```sql ... ```), БЕЗ ПОЯСНЕНИЙ.
"""

async def generate_sql_query(user_text: str) -> str:
    prompt = f"{SYSTEM_PROMPT}\n\nВопрос пользователя: {user_text}\nSQL запрос:"
    
    try:
        response = await model.generate_content_async(prompt)
        
        # Чистим ответ от маркдауна, если модель его все-таки добавила
        sql = response.text.strip().replace("```sql", "").replace("```", "").strip()
        return sql
    except Exception as e:
        print(f"LLM Error: {e}")
        # Возвращаем заглушку, чтобы бот не падал, а писал ошибку
        return "SELECT -1"