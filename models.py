from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey, DateTime
from sqlalchemy.sql import func
from datetime import date, time

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'
    
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    ip_address = db.Column(db.String(15), nullable=False)

    activities = db.relationship('ActivityLog', backref='user', lazy=True, cascade='all, delete-orphan')


class ActivityLog(db.Model):
    __tablename__ = 'activity_log'
    
    activity_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, ForeignKey('user.user_id', ondelete='CASCADE'), nullable=True)
    date = db.Column(db.Date, nullable=False, default=func.current_date())
    time = db.Column(db.Time, nullable=False, default=func.current_time())
    activity = db.Column(db.String(200))
    remark = db.Column(db.String(100))
    filePath = db.Column(db.Text)

    def as_dict(self):
        result = {}
        for c in self.__table__.columns:
            value = getattr(self, c.name)
            if value is None and c.name == 'remark':
                result['remark'] = '-'
            elif isinstance(value, date):
                result[c.name] = value.strftime('%y/%m/%d')
            elif isinstance(value, time):
                result[c.name] = value.strftime('%H:%M:%S')
            else:
                result[c.name] = value
        return result