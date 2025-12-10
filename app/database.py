from sqlalchemy import create_engine, Column, String, JSON, Integer
from sqlalchemy.orm import sessionmaker, declarative_base


DATABASE_URL = "sqlite:///./workflow.db"


engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class RunModel(Base):
    """Stores the state and history of a workflow execution."""
    __tablename__ = "runs"

    run_id = Column(String, primary_key=True, index=True)
    graph_id = Column(String, index=True)
    status = Column(String, default="pending")  
    state = Column(JSON, default={})            
    history = Column(JSON, default=[])          

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


