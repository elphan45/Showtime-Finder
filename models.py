from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import os

Base = declarative_base()

class Theater(Base):
    __tablename__ = 'theaters'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    url = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    showtimes = relationship('Showtime', back_populates='theater')

class Movie(Base):
    __tablename__ = 'movies'
    
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    language = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    showtimes = relationship('Showtime', back_populates='movie')

class Showtime(Base):
    __tablename__ = 'showtimes'
    
    id = Column(Integer, primary_key=True)
    theater_id = Column(Integer, ForeignKey('theaters.id'))
    movie_id = Column(Integer, ForeignKey('movies.id'))
    showtime = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    theater = relationship('Theater', back_populates='showtimes')
    movie = relationship('Movie', back_populates='showtimes')

# Create database tables
def init_db():
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        engine = create_engine(database_url)
        Base.metadata.create_all(engine)
