import asyncio
import ijson
from datetime import datetime
from sqlalchemy import insert
from src.database.db import AsyncSessionLocal, init_models
from src.database.models import Video, VideoSnapshot


BATCH_SIZE = 1000

def parse_date(date_str):
    if not date_str:
        return None
    try:
        return datetime.fromisoformat(date_str)
    except ValueError:
        return None

async def load_data_from_json(file_path: str):
    print(f"Начинаю потоковое чтение файла {file_path}...")
    
    videos_buffer = []
    snapshots_buffer = []
    
    total_videos = 0
    
    async with AsyncSessionLocal() as session:
        with open(file_path, 'rb') as f:
            for video_obj in ijson.items(f, 'videos.item'):
                
                v_dict = {
                    "id": video_obj["id"],
                    "creator_id": video_obj["creator_id"],
                    "video_created_at": parse_date(video_obj.get("video_created_at")),
                    "views_count": video_obj.get("views_count", 0),
                    "likes_count": video_obj.get("likes_count", 0),
                    "comments_count": video_obj.get("comments_count", 0),
                    "reports_count": video_obj.get("reports_count", 0),
                    "created_at": parse_date(video_obj.get("created_at")),
                    "updated_at": parse_date(video_obj.get("updated_at"))
                }
                videos_buffer.append(v_dict)
                total_videos += 1

                snapshots_list = video_obj.get("snapshots", [])
                for snap in snapshots_list:
                    s_dict = {
                        "id": snap["id"],
                        "video_id": video_obj["id"],
                        "views_count": snap.get("views_count", 0),
                        "likes_count": snap.get("likes_count", 0),
                        "comments_count": snap.get("comments_count", 0),
                        "reports_count": snap.get("reports_count", 0),
                        "delta_views_count": snap.get("delta_views_count", 0),
                        "delta_likes_count": snap.get("delta_likes_count", 0),
                        "delta_comments_count": snap.get("delta_comments_count", 0),
                        "delta_reports_count": snap.get("delta_reports_count", 0),
                        "created_at": parse_date(snap.get("created_at")),
                    }
                    snapshots_buffer.append(s_dict)

                if len(videos_buffer) >= BATCH_SIZE:
                    await session.execute(insert(Video), videos_buffer)
                    videos_buffer = [] 
                    
                    if snapshots_buffer:
                        await session.execute(insert(VideoSnapshot), snapshots_buffer)
                        snapshots_buffer = []
                    
                    await session.commit() 
                    print(f"Processed {total_videos} videos...")

        if videos_buffer:
            await session.execute(insert(Video), videos_buffer)
        if snapshots_buffer:
            await session.execute(insert(VideoSnapshot), snapshots_buffer)
        
        await session.commit()
    
    print(f"✅ Успешно загружено {total_videos} видео и куча снапшотов!")

if __name__ == "__main__":
    async def main():
        await init_models()
        await load_data_from_json("data/videos.json")
    
    asyncio.run(main())