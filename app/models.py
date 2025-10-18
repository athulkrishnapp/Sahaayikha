# app/models.py

from datetime import datetime, date
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db
from itsdangerous import URLSafeTimedSerializer as Serializer
from flask import current_app
from sqlalchemy import and_
from sqlalchemy.orm import foreign

# ---------- USERS ----------
class User(UserMixin, db.Model):
    __tablename__ = "users"
    user_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(255))
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(50))
    location = db.Column(db.String(255))
    profile_picture = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(50), default="Active")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    fcm_token = db.Column(db.String(255), nullable=True)
    otp = db.Column(db.String(6), nullable=True)
    otp_expiry = db.Column(db.DateTime, nullable=True)
    is_verified = db.Column(db.Boolean, default=False)
    # New fields for location-based search
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    search_radius = db.Column(db.Integer, default=20) # Default search radius of 20 km

    items = db.relationship("Item", backref="owner", lazy="dynamic")
    bookmarks = db.relationship("Bookmark", backref="user", lazy="dynamic")
    messages = db.relationship(
        "ChatMessage",
        primaryjoin="and_(User.user_id==foreign(ChatMessage.sender_id), ChatMessage.sender_type=='user')",
        lazy="dynamic",
        overlaps="org_sender"
    )
    feedbacks = db.relationship("Feedback", backref="user", lazy="dynamic")
    reports = db.relationship("Report", backref="reporter", lazy="dynamic")
    category_follows = db.relationship("CategoryFollow", backref="user", lazy="dynamic")
    notifications = db.relationship("Notification", backref="user", lazy="dynamic")
    login_logs = db.relationship("LoginLog", backref="user", lazy="dynamic")

    def set_password(self, raw_password):
        self.password = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password, raw_password)

    def get_id(self):
        return f"user:{self.user_id}"

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'])
        return s.dumps({'user_id': self.user_id})

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token, max_age=1800)['user_id']
        except:
            return None
        return User.query.get(user_id)


# ---------- ADMINS ----------
class Admin(UserMixin, db.Model):
    __tablename__ = "admins"
    admin_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(50), default="Active")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, raw_password):
        self.password = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password, raw_password)

    def get_id(self):
        return f"admin:{self.admin_id}"


# ---------- ORGANIZATIONS ----------
class Organization(UserMixin, db.Model):
    __tablename__ = "organizations"
    org_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(100))
    location = db.Column(db.String(255))
    profile_picture = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(50), default="Pending")
    registered_at = db.Column(db.DateTime, default=datetime.utcnow)
    description = db.Column(db.Text, nullable=True)  # <-- ADDED THIS LINE
    
    otp = db.Column(db.String(6), nullable=True)
    otp_expiry = db.Column(db.DateTime, nullable=True)
    is_verified = db.Column(db.Boolean, default=False)

    disaster_needs = db.relationship("DisasterNeed", backref="organization", lazy="dynamic")
    messages = db.relationship(
        "ChatMessage",
        primaryjoin="and_(Organization.org_id==foreign(ChatMessage.sender_id), ChatMessage.sender_type=='org')",
        lazy="dynamic",
        overlaps="messages,user_sender"
    )


    def set_password(self, raw_password):
        self.password = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password, raw_password)

    def get_id(self):
        return f"org:{self.org_id}"
    
    def get_reset_token(self, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'])
        return s.dumps({'org_id': self.org_id})

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            org_id = s.loads(token, max_age=1800)['org_id']
        except:
            return None
        return Organization.query.get(org_id)

# ---------- LOGIN LOG ----------
class LoginLog(db.Model):
    __tablename__ = "login_logs"
    log_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    login_time = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(100))


# ---------- ITEMS ----------
class Item(db.Model):
    __tablename__ = "items"
    item_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(255))
    type = db.Column(db.String(50))
    condition = db.Column(db.String(50))
    urgency_level = db.Column(db.String(50))
    expected_return = db.Column(db.String(255))
    location = db.Column(db.String(255))
    status = db.Column(db.String(50), default="Active")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=True)
    deal_finalized_at = db.Column(db.DateTime, nullable=True)
    # New fields for location-based search
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)

    histories = db.relationship("ItemHistory", backref="item", lazy="dynamic")
    bookmarks = db.relationship("Bookmark", backref="item", lazy="dynamic")
    reports = db.relationship("Report", backref="item", lazy="dynamic")
    images = db.relationship("ItemImage", backref="item", lazy="dynamic", cascade="all, delete-orphan")
    trade_requests_made = db.relationship('TradeRequest', foreign_keys='TradeRequest.item_offered_id', backref='offered_item', lazy='dynamic')
    trade_requests_received = db.relationship('TradeRequest', foreign_keys='TradeRequest.item_requested_id', backref='requested_item', lazy='dynamic')
    
    chat_sessions = db.relationship("ChatSession", back_populates="trade_item", foreign_keys="ChatSession.trade_item_id")


class TradeRequest(db.Model):
    __tablename__ = 'trade_requests'
    id = db.Column(db.Integer, primary_key=True)
    item_offered_id = db.Column(db.Integer, db.ForeignKey('items.item_id'), nullable=False)
    item_requested_id = db.Column(db.Integer, db.ForeignKey('items.item_id'), nullable=False)
    requester_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    status = db.Column(db.String(50), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    requester = db.relationship('User', foreign_keys=[requester_id])
    owner = db.relationship('User', foreign_keys=[owner_id])


class DealProposal(db.Model):
    __tablename__ = "deal_proposals"
    id = db.Column(db.Integer, primary_key=True)
    chat_session_id = db.Column(db.Integer, db.ForeignKey("chat_sessions.session_id"), nullable=False, unique=True)
    
    proposer_status = db.Column(db.String(50), default='pending', nullable=False)
    owner_status = db.Column(db.String(50), default='pending', nullable=False)
    
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    session = db.relationship("ChatSession", backref=db.backref("deal_proposal", uselist=False))


# ---------- ITEM IMAGES ----------
class ItemImage(db.Model):
    __tablename__ = "item_images"
    image_id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey("items.item_id"), nullable=False)
    image_url = db.Column(db.String(255), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)


# ---------- ITEM HISTORY ----------
class ItemHistory(db.Model):
    __tablename__ = "item_history"
    history_id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey("items.item_id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=True)
    action = db.Column(db.String(255))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


# ---------- CHAT ----------
class ChatSession(db.Model):
    __tablename__ = "chat_sessions"
    session_id = db.Column(db.Integer, primary_key=True)
    
    trade_item_id = db.Column(db.Integer, db.ForeignKey("items.item_id"), nullable=True)
    disaster_need_id = db.Column(db.Integer, db.ForeignKey("disaster_needs.need_id"), nullable=True)
    
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    org_id = db.Column(db.Integer, db.ForeignKey("organizations.org_id"), nullable=True)
    other_user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=True)

    status = db.Column(db.String(50), default="Active")
    started_at = db.Column(db.DateTime, default=datetime.utcnow)

    messages = db.relationship("ChatMessage", backref="session", lazy="dynamic", cascade="all, delete-orphan")
    user = db.relationship("User", foreign_keys=[user_id])
    other_user = db.relationship("User", foreign_keys=[other_user_id])
    organization = db.relationship("Organization", foreign_keys=[org_id])

    trade_item = db.relationship("Item", back_populates="chat_sessions", foreign_keys=[trade_item_id])
    disaster_need = db.relationship("DisasterNeed", back_populates="chat_sessions", foreign_keys=[disaster_need_id])

    __table_args__ = (
        db.CheckConstraint('(org_id IS NOT NULL AND other_user_id IS NULL) OR (org_id IS NULL AND other_user_id IS NOT NULL)', name='chk_participant'),
        db.CheckConstraint('(trade_item_id IS NOT NULL AND disaster_need_id IS NULL) OR (trade_item_id IS NULL AND disaster_need_id IS NOT NULL)', name='chk_chat_subject'),
    )

    @property
    def subject(self):
        return self.trade_item or self.disaster_need


class ChatMessage(db.Model):
    __tablename__ = "chat_messages"
    
    # THE FIX IS ON THE NEXT LINE
    message_id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey("chat_sessions.session_id"), nullable=False)
    sender_type = db.Column(db.String(50), nullable=False)
    sender_id = db.Column(db.Integer, nullable=False)
    message = db.Column(db.Text, nullable=True)
    image_url = db.Column(db.String(255), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)
    deleted_at = db.Column(db.DateTime, nullable=True)


# ---------- DISASTER NEEDS ----------
class DisasterNeed(db.Model):
    __tablename__ = "disaster_needs"
    need_id = db.Column(db.Integer, primary_key=True)
    org_id = db.Column(db.Integer, db.ForeignKey("organizations.org_id"), nullable=False)
    title = db.Column(db.String(255), nullable=True)
    categories = db.Column(db.Text, nullable=True)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(255))
    posted_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Corrected relationship
    chat_sessions = db.relationship("ChatSession", back_populates="disaster_need", foreign_keys="ChatSession.disaster_need_id")


# ---------- DISASTER DONATIONS ----------
class DonationOffer(db.Model):
    __tablename__ = 'donation_offers'
    offer_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    need_id = db.Column(db.Integer, db.ForeignKey('disaster_needs.need_id'), nullable=False)
    org_id = db.Column(db.Integer, db.ForeignKey('organizations.org_id'), nullable=False)
    status = db.Column(db.String(50), default='Pending Review')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    verified_at = db.Column(db.DateTime, nullable=True)
    picked_up_at = db.Column(db.DateTime, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    pickup_retries = db.Column(db.Integer, default=0)
    proof_image_url = db.Column(db.String(255), nullable=True)
    
    user = db.relationship('User', backref='donation_offers')
    need = db.relationship('DisasterNeed', backref='donation_offers')
    organization = db.relationship('Organization', backref='donation_offers')
    offered_items = db.relationship('OfferedItem', backref='offer', lazy='dynamic', cascade="all, delete-orphan")

class OfferedItem(db.Model):
    __tablename__ = 'offered_items'
    offered_item_id = db.Column(db.Integer, primary_key=True)
    offer_id = db.Column(db.Integer, db.ForeignKey('donation_offers.offer_id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(255), nullable=True)
    description = db.Column(db.Text, nullable=True)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    condition = db.Column(db.String(50))
    image_url = db.Column(db.String(255), nullable=True)
    manufacture_date = db.Column(db.Date, nullable=True)
    expiry_date = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(50), default='Pending')


# ---------- FEEDBACK ----------
class Feedback(db.Model):
    __tablename__ = "feedback"
    feedback_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    message = db.Column(db.Text, nullable=False)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50), default="Open")


# ---------- REPORT ----------
class Report(db.Model):
    __tablename__ = "reports"
    report_id = db.Column(db.Integer, primary_key=True)
    reported_by = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey("items.item_id"), nullable=True)
    chat_session_id = db.Column(db.Integer, db.ForeignKey("chat_sessions.session_id"), nullable=True)
    
    reported_org_id = db.Column(db.Integer, db.ForeignKey("organizations.org_id"), nullable=True)
    donation_offer_id = db.Column(db.Integer, db.ForeignKey("donation_offers.offer_id"), nullable=True)

    reason = db.Column(db.Text, nullable=False)
    reported_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50), default="Pending")


# ---------- BOOKMARK ----------
class Bookmark(db.Model):
    __tablename__ = "bookmarks"
    bookmark_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey("items.item_id"), nullable=False)
    saved_at = db.Column(db.DateTime, default=datetime.utcnow)


# ---------- CATEGORY FOLLOW ----------
class CategoryFollow(db.Model):
    __tablename__ = "category_follows"
    follow_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    category = db.Column(db.String(255))
    followed_at = db.Column(db.DateTime, default=datetime.utcnow)


# ---------- NOTIFICATION ----------
class Notification(db.Model):
    __tablename__ = "notifications"
    notification_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey("items.item_id"), nullable=True)
    message = db.Column(db.Text, nullable=False)
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50), default="Unread")
    item = db.relationship("Item", backref="notifications")


# ---------- SYSTEM SETTINGS ----------
class SystemSetting(db.Model):
    __tablename__ = "system_settings"
    setting_id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(255), unique=True, nullable=False)
    value = db.Column(db.String(255))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)