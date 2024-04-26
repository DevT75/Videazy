from sqlalchemy import Boolean,Column,Integer,String,DateTime,func,ForeignKey,Enum,Table
from datetime import datetime
from typing import List
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from core.db import Base
import enum

class UserModel(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    first_name = Column(String[100])
    last_name = Column(String[100])
    email = Column(String[100],unique=True,index=True)
    password = Column(String[100])
    is_active= Column(Boolean,default=False)
    is_verified= Column(Boolean,default=False)
    verified_at = Column(DateTime,nullable=True,default=None)
    registered_at = Column(DateTime,nullable=True,default=None)
    updated_at = Column(DateTime,nullable=True,default=None,onupdate=datetime.now())
    # server_default is giving error     raise exc.ArgumentError(
# sqlalchemy.exc.ArgumentError: Argument 'arg' is expected to be one of type '<class 'str'>' or '<class 'sqlalchemy.sql.elements.ClauseElement'>' or '<class 'sqlalchemy.sql.elements.TextClause'>', got '<class 'sqlalchemy.sql.functions._FunctionGenerator'>'
    created_at = Column(DateTime,nullable=False,default=func.now())
    files = relationship("MediaModel", back_populates="user")