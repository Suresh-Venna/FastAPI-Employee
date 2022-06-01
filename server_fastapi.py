from fastapi import FastAPI, Depends, HTTPException
from typing import Optional, List
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy import Integer, String, Boolean, Float, Column
from pydantic import BaseModel
from fastapi.openapi.utils import get_openapi

app = FastAPI()


# Open API Documenation

def employee_schema():
    openapi_schema = get_openapi(
        title="Employee API Program",
        version="1.0",
        description="Coding Test for Interview",
        routes=app.routes
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = employee_schema

# sqlAlchemy

SQLALC_DB_URL = 'sqlite:///./sql_app.db'
engine = create_engine(SQLALC_DB_URL, echo=True, future=True)
Session_Local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = Session_Local()
    try:
        return db
    finally:
        db.close()


class DBEmployee(Base):
    __tablename__ = "employees"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50))


Base.metadata.create_all(bind=engine)


class Employee(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


def get_employee(db: Session, employee_id: int):
    return db.query(DBEmployee).where(DBEmployee.id == employee_id).first()


def get_employees(db: Session):
    return db.query(DBEmployee).all()


def create_employee(db: Session, employee: Employee):
    db_employee = DBEmployee(**employee.dict())
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)

    return db_employee


@app.post('/employees/employee', response_model=Employee)
def create_employees(employee: Employee, db: Session = Depends(get_db)):
    db_employee = create_employee(db, employee)
    return db_employee


@app.get('/employees/', response_model=List[Employee])
def get_employees_view(db: Session = Depends((get_db))):
    return get_employees(db)


@app.get('/employees/employee/{employee_id}')
def get_employees_view(employee_id: int, db: Session = Depends(get_db)):
    res = get_employee(db, employee_id)
    if res:
        return res
    else:
        raise HTTPException(status_code=404, detail="Item not found")
