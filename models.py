from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class FileData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(100), nullable=False)
    data = db.Column(db.LargeBinary, nullable=False)




class EmployeeData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(100), nullable=False)
    hours_worked = db.Column(db.Float, nullable=False)
    employee_id = db.Column(db.Integer, nullable=False)
    job_group = db.Column(db.String(10), nullable=False)