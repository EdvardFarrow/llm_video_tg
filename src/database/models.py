from datetime import datetime
from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class Video(Base):
    __tablename__ = 'videos'

    id: Mapped[str] = mapped_column(String, primary_key=True)    
    creator_id: Mapped[str] = mapped_column(String, index=True)
    video_created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    
    # Итоговая статистика
    views_count: Mapped[int] = mapped_column(BigInteger, default=0)
    likes_count: Mapped[int] = mapped_column(BigInteger, default=0)
    comments_count: Mapped[int] = mapped_column(BigInteger, default=0)
    reports_count: Mapped[int] = mapped_column(BigInteger, default=0)
    
    # Служебные поля
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

class VideoSnapshot(Base):
    __tablename__ = 'video_snapshots'

    id: Mapped[str] = mapped_column(String, primary_key=True)
    video_id: Mapped[str] = mapped_column(ForeignKey('videos.id', ondelete='CASCADE'), index=True)
    
    # Значения на момент снимка
    views_count: Mapped[int] = mapped_column(BigInteger)
    likes_count: Mapped[int] = mapped_column(BigInteger)
    comments_count: Mapped[int] = mapped_column(BigInteger)
    reports_count: Mapped[int] = mapped_column(BigInteger)
    
    # Дельты могут быть отрицательными, поэтому Integer
    delta_views_count: Mapped[int] = mapped_column(Integer)
    delta_likes_count: Mapped[int] = mapped_column(Integer)
    delta_comments_count: Mapped[int] = mapped_column(Integer)
    delta_reports_count: Mapped[int] = mapped_column(Integer)
    
    # Индекс для аналитики по времени
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), onupdate=func.now(), nullable=True)