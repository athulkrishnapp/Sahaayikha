from datetime import datetime, date
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db

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
    status = db.Column(db.String(50), default="Active")  # Active / Blocked / Deactivated
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    fcm_token = db.Column(db.String(255), nullable=True) # <-- ADD THIS LINE



    # Relationships
    items = db.relationship("Item", backref="owner", lazy="dynamic")
    bookmarks = db.relationship("Bookmark", backref="user", lazy="dynamic")
    chat_sessions1 = db.relationship("ChatSession", foreign_keys="ChatSession.user1_id", backref="user1", lazy="dynamic")
    chat_sessions2 = db.relationship("ChatSession", foreign_keys="ChatSession.user2_id", backref="user2", lazy="dynamic")
    messages = db.relationship("ChatMessage", backref="sender", lazy="dynamic")
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


# ---------- ADMINS ----------
class Admin(UserMixin, db.Model):
    __tablename__ = "admins"
    admin_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(50), default="Active")  # Active / Inactive
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
    status = db.Column(db.String(50), default="Pending")  # Pending / Approved / Blocked
    registered_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    disaster_needs = db.relationship("DisasterNeed", backref="organization", lazy="dynamic")

    def set_password(self, raw_password):
        self.password = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password, raw_password)

    def get_id(self):
        return f"org:{self.org_id}"


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
    type = db.Column(db.String(50))  # Trade / Share / Disaster
    condition = db.Column(db.String(50))  # New / Used / Old
    urgency_level = db.Column(db.String(50))  # Urgent / Flexible
    expected_return = db.Column(db.String(255))
    location = db.Column(db.String(255))
    status = db.Column(db.String(50), default="Active")  # Active / Traded / Verified / Expired
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=True)
    deal_finalized_at = db.Column(db.DateTime, nullable=True)

    # Relationships
    histories = db.relationship("ItemHistory", backref="item", lazy="dynamic")
    chat_sessions = db.relationship("ChatSession", backref="item", lazy="dynamic")
    bookmarks = db.relationship("Bookmark", backref="item", lazy="dynamic")
    reports = db.relationship("Report", backref="item", lazy="dynamic")
    images = db.relationship("ItemImage", backref="item", lazy="dynamic")

class DealProposal(db.Model):
    __tablename__ = "deal_proposals"
    id = db.Column(db.Integer, primary_key=True)
    chat_session_id = db.Column(db.Integer, db.ForeignKey("chat_sessions.session_id"), nullable=False, unique=True)
    
    # Track the status of each participant
    # Status can be: 'pending', 'confirmed', 'rejected'
    proposer_status = db.Column(db.String(50), default='pending', nullable=False)
    owner_status = db.Column(db.String(50), default='pending', nullable=False)
    
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship back to the chat session
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
    action = db.Column(db.String(255))  # Reposted / Expired / Deleted
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


# ---------- CHAT ----------
class ChatSession(db.Model):
    __tablename__ = "chat_sessions"
    session_id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey("items.item_id"), nullable=False)
    user1_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    user2_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    status = db.Column(db.String(50), default="Active")  # Active / Blocked / Ended / Confirmed
    started_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    messages = db.relationship("ChatMessage", backref="session", lazy="dynamic")


class ChatMessage(db.Model):
    __tablename__ = "chat_messages"
    
    # ## ENSURE THIS LINE EXISTS AND IS CORRECT ##
    message_id = db.Column(db.Integer, primary_key=True)
    
    session_id = db.Column(db.Integer, db.ForeignKey("chat_sessions.session_id"), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    message = db.Column(db.Text, nullable=True)
    image_url = db.Column(db.String(255), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    deleted_at = db.Column(db.DateTime, nullable=True)


# ---------- DISASTER NEEDS ----------
class DisasterNeed(db.Model):
    __tablename__ = "disaster_needs"
    need_id = db.Column(db.Integer, primary_key=True)
    org_id = db.Column(db.Integer, db.ForeignKey("organizations.org_id"), nullable=False)
    title = db.Column(db.String(255), nullable=True) # <-- ADD THIS
    categories = db.Column(db.Text, nullable=True) # Will store comma-separated categories
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(255))
    posted_at = db.Column(db.DateTime, default=datetime.utcnow)


# ---------- DISASTER DONATIONS ----------
from datetime import datetime
from app import db

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
    pickup_retries = db.Column(db.Integer, default=0) # To track the one-time retry
    proof_image_url = db.Column(db.String(255), nullable=True) # For orgs to upload proof
    
    # Relationships
    user = db.relationship('User', backref='donation_offers')
    need = db.relationship('DisasterNeed', backref='donation_offers')
    organization = db.relationship('Organization', backref='donation_offers')
    offered_items = db.relationship('OfferedItem', backref='offer', lazy='dynamic', cascade="all, delete-orphan")

class OfferedItem(db.Model):
    __tablename__ = 'offered_items'
    offered_item_id = db.Column(db.Integer, primary_key=True)
    offer_id = db.Column(db.Integer, db.ForeignKey('donation_offers.offer_id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(255), nullable=True) # <-- ADD THIS LINE
    description = db.Column(db.Text, nullable=True)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    condition = db.Column(db.String(50)) # New / Used
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
    status = db.Column(db.String(50), default="Open")  # Open / Responded / Closed


# ---------- REPORT ----------
class Report(db.Model):
    __tablename__ = "reports"
    report_id = db.Column(db.Integer, primary_key=True)
    reported_by = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey("items.item_id"), nullable=True)
    chat_session_id = db.Column(db.Integer, db.ForeignKey("chat_sessions.session_id"), nullable=True)
    
    # --- ADD THESE TWO LINES for reporting an organization regarding a donation ---
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
    status = db.Column(db.String(50), default="Unread")  # Read / Unread


# ---------- SYSTEM SETTINGS ----------
class SystemSetting(db.Model):
    __tablename__ = "system_settings"
    setting_id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(255), unique=True, nullable=False)
    value = db.Column(db.String(255))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)