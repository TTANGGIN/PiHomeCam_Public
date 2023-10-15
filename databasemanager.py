from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey, DateTime
from sqlalchemy.sql import func
from models import db, User, ActivityLog

class DatabaseManager:
    
    @staticmethod
    def init_app(app):
        # Initialize SQLAlchemy with the Flask app
        db.init_app(app)
        print("init database")

    @staticmethod
    def add_user(username, password, ip_address):
        user = User(username=username, password=password, ip_address=ip_address)
        db.session.add(user)
        db.session.commit()

    @staticmethod
    def get_user_by_id(user_id):
        return User.query.get(user_id)
    
    @staticmethod
    def get_user_by_username(username):
        return User.query.filter_by(username=username).first()

    @staticmethod
    def get_all_users():
        return User.query.all()

    @staticmethod
    def update_user(user_id, username=None, password=None, ip_address=None):
        user = User.query.get(user_id)
        if username:
            user.username = username
        if password:
            user.password = password
        if ip_address:
            user.ip_address = ip_address
        db.session.commit()

    @staticmethod
    def delete_user(user_id):
        user = User.query.get(user_id)
        db.session.delete(user)
        db.session.commit()

    @staticmethod
    def add_activity(user_id, activity, remark=None, filePath=None):
        activity_log = ActivityLog(user_id=user_id, activity=activity, remark=remark, filePath=filePath)
        db.session.add(activity_log)
        db.session.commit()

    @staticmethod
    def get_activity(activity_id):
        return ActivityLog.query.get(activity_id)
    
    @staticmethod
    def get_activities_by_username(username):
        user = User.query.filter_by(username=username).first()
        if user:
            return user.activities
        return None

    @staticmethod
    def get_all_activities():
        return ActivityLog.query.all()

    @staticmethod
    def update_activity(activity_id, activity=None, remark=None, filePath=None):
        activity_log = ActivityLog.query.get(activity_id)
        if activity:
            activity_log.activity = activity
        if remark:
            activity_log.remark = remark
        if filePath:
            activity_log.filePath = filePath
        db.session.commit()

    @staticmethod
    def delete_activity(activity_id):
        activity_log = ActivityLog.query.get(activity_id)
        db.session.delete(activity_log)
        db.session.commit()