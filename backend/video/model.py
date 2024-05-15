from sqlalchemy import Boolean,Column,Integer,String,DateTime,func,ForeignKey,Enum
from datetime import datetime
import enum
from core.db import Base
from sqlalchemy.orm import relationship

class MediaTypeEnum(enum.Enum):
    video = "video"
    image = "image"

class MediaModel(Base):
    __tablename__ = "media"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"),nullable=True)
    type = Column(Enum(MediaTypeEnum))
    url = Column(String[500])
    uploaded_at = Column(DateTime,nullable=False,default=func.now())
    modified_at = Column(DateTime,nullable=True,default=None,onupdate=datetime.now())
    user = relationship("UserModel", back_populates="files")