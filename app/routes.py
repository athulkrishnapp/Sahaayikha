import os
from datetime import datetime
from functools import wraps
from flask import (
    Blueprint, render_template, redirect, url_for,
    flash, request, abort
)
from flask_login import (
    login_user, logout_user, current_user,
    login_required
)
from werkzeug.utils import secure_filename

from app import db, login_manager
from app.models import (
    User, Admin, Organization, LoginLog,
    Item, ItemImage, ItemHistory,
    ChatSession, ChatMessage,
    DisasterNeed, DisasterDonation,
    Feedback, Report, Bookmark,
    CategoryFollow, Notification
)
from app.forms import (
    RegistrationForm, OrganizationRegistrationForm, LoginForm,
    ItemForm, FeedbackForm, ReportForm,
    CategoryFollowForm, DisasterNeedForm,
    DisasterDonationForm, ChatForm
)

main = Blueprint("main", __name__)

# -------------------------
# UPLOAD FOLDERS
# -------------------------
USER_UPLOAD_FOLDER = os.path.join("app", "static", "images", "profiles", "users")
ORG_UPLOAD_FOLDER = os.path.join("app", "static", "images", "profiles", "orgs")
ITEM_UPLOAD_FOLDER = os.path.join("app", "static", "images", "items")
os.makedirs(USER_UPLOAD_FOLDER, exist_ok=True)
os.makedirs(ORG_UPLOAD_FOLDER, exist_ok=True)
os.makedirs(ITEM_UPLOAD_FOLDER, exist_ok=True)

# -------------------------
# LOGIN MANAGER LOADER
# -------------------------
@login_manager.user_loader
def load_user(user_id):
    try:
        prefix, id_str = user_id.split(":")
        id_val = int(id_str)
    except Exception:
        return None
    if prefix == "user":
        return User.query.get(id_val)
    if prefix == "admin":
        return Admin.query.get(id_val)
    if prefix == "org":
        return Organization.query.get(id_val)
    return None

# -------------------------
# ROLE CHECK DECORATOR
# -------------------------
def role_required(role):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated:
                return login_manager.unauthorized()
            obj = current_user._get_current_object()
            if role == "admin" and not isinstance(obj, Admin):
                abort(403)
            if role == "org" and not isinstance(obj, Organization):
                abort(403)
            if role == "user" and not isinstance(obj, User):
                abort(403)
            return f(*args, **kwargs)
        return wrapped
    return decorator

# -------------------------
# HOME
# -------------------------
@main.route("/")
def home():
    items = Item.query.filter_by(status="Active").order_by(Item.created_at.desc()).limit(8).all()
    return render_template("home.html", title="Home", items=items)

# =========================
# AUTH ROUTES
# =========================
@main.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    form = RegistrationForm()
    if form.validate_on_submit():
        # Check for duplicate email
        if User.query.filter_by(email=form.email.data).first() or \
           Organization.query.filter_by(email=form.email.data).first() or \
           Admin.query.filter_by(email=form.email.data).first():
            flash("Email already registered.", "danger")
            return render_template("auth/user_register.html", form=form)

        # Save profile picture if uploaded
        filename = None
        if form.profile_picture.data:
            filename = secure_filename(form.profile_picture.data.filename)
            form.profile_picture.data.save(os.path.join(USER_UPLOAD_FOLDER, filename))
            filename = f"images/profiles/users/{filename}"

        # Create user
        user = User(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data,
            phone=form.phone.data,
            location=form.location.data,
            profile_picture=filename,
            status="Active",
            created_at=datetime.utcnow()
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Account created successfully! Please login.", "success")
        return redirect(url_for("main.login"))
    else:
        # WTForms validation errors
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{getattr(form, field).label.text}: {error}", "danger")

    return render_template("auth/user_register.html", form=form)



@main.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        obj = current_user._get_current_object()
        if isinstance(obj, Admin):
            return redirect(url_for("main.admin_dashboard"))
        if isinstance(obj, Organization):
            return redirect(url_for("main.org_dashboard"))
        return redirect(url_for("main.dashboard"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            db.session.add(LoginLog(user_id=user.user_id, ip_address=request.remote_addr))
            db.session.commit()
            flash("Logged in successfully.", "success")
            return redirect(url_for("main.dashboard"))

        # Invalid credentials
        flash("Invalid email or password.", "danger")
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{getattr(form, field).label.text}: {error}", "danger")

    return render_template("auth/user_login.html", form=form)



@main.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("main.home"))


# -------------------------
# PROFILE UPDATE
# -------------------------
@main.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    user = current_user._get_current_object()
    if isinstance(user, User):
        template = "auth/user_profile.html"
        form = RegistrationForm(obj=user)
    elif isinstance(user, Organization):
        template = "auth/org_profile.html"
        form = OrganizationRegistrationForm()
    else:
        flash("Profile not editable.", "warning")
        return redirect(url_for("main.home"))

    if form.validate_on_submit():
        if isinstance(user, User):
            user.first_name = form.first_name.data
            user.last_name = form.last_name.data
        else:
            user.name = form.name.data
        user.phone = form.phone.data
        user.location = form.location.data
        if form.profile_picture.data:
            filename = secure_filename(form.profile_picture.data.filename)
            folder = USER_UPLOAD_FOLDER if isinstance(user, User) else ORG_UPLOAD_FOLDER
            form.profile_picture.data.save(os.path.join(folder, filename))
            user.profile_picture = f"images/profiles/{'users' if isinstance(user, User) else 'orgs'}/{filename}"
        db.session.commit()
        flash("Profile updated successfully.", "success")
        return redirect(url_for("main.profile"))
    return render_template(template, form=form)


# =========================
# ADMIN ROUTES
# =========================
@main.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if current_user.is_authenticated and isinstance(current_user._get_current_object(), Admin):
        return redirect(url_for("main.admin_dashboard"))
    form = LoginForm()
    if form.validate_on_submit():
        admin = Admin.query.filter_by(email=form.email.data).first()
        if admin and admin.check_password(form.password.data):
            login_user(admin, remember=form.remember.data)
            db.session.add(LoginLog(user_id=admin.admin_id, ip_address=request.remote_addr))
            db.session.commit()
            flash("Admin logged in.", "success")
            return redirect(url_for("main.admin_dashboard"))
        flash("Invalid admin credentials.", "danger")
    return render_template("auth/admin_login.html", title="Admin Login", form=form)


@main.route("/admin/dashboard")
@login_required
@role_required("admin")
def admin_dashboard():
    users_count = User.query.count()
    orgs_count = Organization.query.count()
    items_count = Item.query.count()
    feedback_count = Feedback.query.count()
    reports_count = Report.query.count()
    return render_template(
        "dashboard/admin_dashboard.html",
        users_count=users_count,
        orgs_count=orgs_count,
        items_count=items_count,
        feedback_count=feedback_count,
        reports_count=reports_count
    )
    


@main.route("/admin/feedbacks")
@login_required
@role_required("admin")
def admin_feedbacks():
    feedbacks = Feedback.query.order_by(Feedback.submitted_at.desc()).all()
    return render_template("admin/admin_feedback.html", feedbacks=feedbacks)


@main.route("/admin/reports")
@login_required
@role_required("admin")
def admin_reports():
    reports = Report.query.order_by(Report.reported_at.desc()).all()
    return render_template("admin/admin_reports.html", reports=reports)


@main.route("/admin/reports/<int:report_id>/resolve")
@login_required
@role_required("admin")
def resolve_report(report_id):
    report = Report.query.get_or_404(report_id)
    report.status = "Resolved"
    db.session.commit()
    flash("Report resolved.", "success")
    return redirect(url_for("main.admin_reports"))


# =========================
# ADMIN – ORG APPROVAL
# =========================
@main.route("/admin/org-approvals")
@login_required
@role_required("admin")
def admin_org_approvals():
    pending_orgs = Organization.query.filter_by(status="Pending").all()
    return render_template("admin/admin_org_approval.html", pending=pending_orgs)


@main.route("/admin/org-approve/<int:org_id>", methods=["POST"])
@login_required
@role_required("admin")
def approve_org(org_id):
    org = Organization.query.get_or_404(org_id)
    org.status = "Approved"
    db.session.commit()
    flash(f"Organization '{org.name}' approved.", "success")
    return redirect(url_for("main.admin_org_approvals"))


@main.route("/admin/org-reject/<int:org_id>", methods=["POST"])
@login_required
@role_required("admin")
def reject_org(org_id):
    org = Organization.query.get_or_404(org_id)
    org.status = "Rejected"
    db.session.commit()
    flash(f"Organization '{org.name}' rejected.", "danger")
    return redirect(url_for("main.admin_org_approvals"))


# =========================
# ADMIN – SYSTEM SETTINGS
# =========================
@main.route("/admin/settings")
@login_required
@role_required("admin")
def system_settings():
    from app.models import SystemSetting
    settings = SystemSetting.query.order_by(SystemSetting.key).all()
    return render_template("admin/system_settings.html", settings=settings)


@main.route("/admin/settings/update/<int:setting_id>", methods=["POST"])
@login_required
@role_required("admin")
def update_setting(setting_id):
    from app.models import SystemSetting
    setting = SystemSetting.query.get_or_404(setting_id)
    new_value = request.form.get("value")
    if new_value:
        setting.value = new_value
        db.session.commit()
        flash(f"Updated setting '{setting.key}'", "success")
    else:
        flash("Value cannot be empty.", "danger")
    return redirect(url_for("main.system_settings"))


# =========================
# ORGANIZATION ROUTES
# =========================
@main.route("/org/register", methods=["GET", "POST"])
def org_register():
    if current_user.is_authenticated and isinstance(current_user._get_current_object(), Organization):
        return redirect(url_for("main.org_dashboard"))

    form = OrganizationRegistrationForm()
    if form.validate_on_submit():
        # Check for duplicate email
        if Organization.query.filter_by(email=form.email.data).first() or \
           User.query.filter_by(email=form.email.data).first() or \
           Admin.query.filter_by(email=form.email.data).first():
            flash("Email already registered.", "danger")
            return render_template("auth/org_register.html", form=form)

        # Save profile picture if uploaded
        filename = None
        if form.profile_picture.data:
            filename = secure_filename(form.profile_picture.data.filename)
            form.profile_picture.data.save(os.path.join(ORG_UPLOAD_FOLDER, filename))
            filename = f"images/profiles/orgs/{filename}"

        # Create organization
        org = Organization(
            name=form.name.data,
            email=form.email.data,
            phone=form.phone.data,
            location=form.location.data,
            profile_picture=filename,
            status="Pending",
            registered_at=datetime.utcnow()
        )
        org.set_password(form.password.data)
        db.session.add(org)
        db.session.commit()
        flash("Organization registered successfully! Pending approval.", "success")
        return redirect(url_for("main.org_login"))
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{getattr(form, field).label.text}: {error}", "danger")

    return render_template("auth/org_register.html", form=form)



@main.route("/org/login", methods=["GET", "POST"])
def org_login():
    if current_user.is_authenticated and isinstance(current_user._get_current_object(), Organization):
        return redirect(url_for("main.org_dashboard"))

    form = LoginForm()
    if form.validate_on_submit():
        org = Organization.query.filter_by(email=form.email.data).first()
        if org and org.check_password(form.password.data):
            if org.status != "Approved":
                flash("Organization not yet approved.", "warning")
                return render_template("auth/org_login.html", form=form)
            login_user(org, remember=form.remember.data)
            db.session.add(LoginLog(user_id=org.org_id, ip_address=request.remote_addr))
            db.session.commit()
            flash("Organization logged in successfully.", "success")
            return redirect(url_for("main.org_dashboard"))

        flash("Invalid email or password.", "danger")
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{getattr(form, field).label.text}: {error}", "danger")

    return render_template("auth/org_login.html", form=form)



@main.route("/org/dashboard")
@login_required
@role_required("org")
def org_dashboard():
    org = current_user._get_current_object()
    
    # Organization shouldn't query Item (they don't post items)
    needs = DisasterNeed.query.filter_by(org_id=org.org_id).all()
    donations = DisasterDonation.query.filter_by(org_id=org.org_id).all()
    
    return render_template(
        "dashboard/org_dashboard.html",
        org=org,
        needs=needs,
        donations=donations
    )


# =========================
# USER DASHBOARD
# =========================
@main.route("/dashboard")
@login_required
@role_required("user")
def dashboard():
    filter_type = request.args.get("filter")

    query = Item.query.filter_by(user_id=current_user.user_id)

    if filter_type == "Trade":
        query = query.filter_by(type="Trade")
    elif filter_type == "Disaster":
        query = query.filter_by(type="Disaster")
    elif filter_type == "Donation":
        # donations are in a separate table
        donations = DisasterDonation.query.filter_by(user_id=current_user.user_id).all()
        return render_template("dashboard/user_dashboard.html", items=[], donations=donations)

    items = query.all()
    donations = DisasterDonation.query.filter_by(user_id=current_user.user_id).all()

    return render_template(
        "dashboard/user_dashboard.html",
        items=items,
        donations=donations
    )



# =========================
# ITEM ROUTES
# =========================
@main.route("/item/new", methods=["GET", "POST"])
@login_required
def new_item():
    form = ItemForm()
    if form.validate_on_submit():
        item = Item(
            title=form.title.data,
            description=form.description.data,
            category=form.category.data,
            type=form.type.data,
            condition=form.condition.data,
            urgency_level=form.urgency_level.data,
            expected_return=form.expected_return.data,
            location=getattr(current_user, "location", None),
            status="Active",
            created_at=datetime.utcnow(),
            user_id=getattr(current_user, "user_id", None),
            expires_at=None  # Optional field
        )
        db.session.add(item)
        db.session.commit()

        if form.images.data:
            files = form.images.data if isinstance(form.images.data, list) else [form.images.data]
            for f in files:
                filename = secure_filename(f.filename)
                f.save(os.path.join(ITEM_UPLOAD_FOLDER, filename))
                db.session.add(ItemImage(item_id=item.item_id, image_url=f"images/items/{filename}"))
            db.session.commit()

        db.session.add(ItemHistory(
            item_id=item.item_id,
            user_id=getattr(current_user, "user_id", None),
            action="Created",
            timestamp=datetime.utcnow()
        ))
        db.session.commit()

        flash("Item posted successfully.", "success")
        return redirect(url_for("main.dashboard"))
    return render_template("items/post_item.html", form=form)


@main.route("/item/<int:item_id>")
def view_item(item_id):
    item = Item.query.get_or_404(item_id)
    return render_template("items/view_item.html", item=item)


@main.route("/item/<int:item_id>/history")
@login_required
def item_history(item_id):
    history = ItemHistory.query.filter_by(item_id=item_id).order_by(ItemHistory.timestamp.desc()).all()
    return render_template("items/item_history.html", history=history, item_id=item_id)


# =========================
# BOOKMARKS
# =========================
@main.route("/bookmark/<int:item_id>")
@login_required
def add_bookmark(item_id):
    bookmark = Bookmark.query.filter_by(user_id=getattr(current_user, "user_id", None), item_id=item_id).first()
    if bookmark:
        db.session.delete(bookmark)
        db.session.commit()
        flash("Bookmark removed.", "info")
    else:
        db.session.add(Bookmark(
            user_id=getattr(current_user, "user_id", None),
            item_id=item_id,
            saved_at=datetime.utcnow()
        ))
        db.session.commit()
        flash("Item bookmarked.", "success")
    return redirect(request.referrer or url_for("main.dashboard"))


@main.route("/bookmarks")
@login_required
def bookmarks():
    user_bookmarks = Bookmark.query.filter_by(user_id=getattr(current_user, "user_id", None)).all()
    return render_template("features/bookmarks.html", bookmarks=user_bookmarks)


# =========================
# CATEGORY FOLLOW
# =========================
@main.route("/category/follow/<string:category>")
@login_required
def follow_category(category):
    follow = CategoryFollow.query.filter_by(user_id=getattr(current_user, "user_id", None), category=category).first()
    if follow:
        db.session.delete(follow)
        db.session.commit()
        flash(f"Unfollowed category: {category}", "info")
    else:
        db.session.add(CategoryFollow(
            user_id=getattr(current_user, "user_id", None),
            category=category,
            followed_at=datetime.utcnow()
        ))
        db.session.commit()
        flash(f"Followed category: {category}", "success")
    return redirect(request.referrer or url_for("main.dashboard"))


# =========================
# DISASTER NEEDS & DONATIONS
# =========================
@main.route("/disaster/needs", methods=["GET", "POST"])
@login_required
def disaster_needs():
    form = DisasterNeedForm()
    if form.validate_on_submit():
        db.session.add(DisasterNeed(
            category=form.category.data,
            description=form.description.data,
            location=form.location.data,
            org_id=getattr(current_user, "org_id", None),
            posted_at=datetime.utcnow()
        ))
        db.session.commit()
        flash("Disaster need posted.", "success")
        return redirect(url_for("main.disaster_needs"))

    needs = DisasterNeed.query.order_by(DisasterNeed.posted_at.desc()).all()
    return render_template("features/disaster_needs.html", form=form, needs=needs)


@main.route("/disaster/donate/<int:need_id>", methods=["GET", "POST"])
@login_required
def disaster_donate(need_id):
    form = DisasterDonationForm()
    need = DisasterNeed.query.get_or_404(need_id)
    if form.validate_on_submit():
        db.session.add(DisasterDonation(
            user_id=getattr(current_user, "user_id", None),
            org_id=getattr(current_user, "org_id", None),
            item_id=None,
            expiry_date=form.expiry_date.data,
            manufacture_date=form.manufacture_date.data,
            status="Pending"
        ))
        db.session.commit()
        flash("Donation submitted successfully.", "success")
        return redirect(url_for("main.disaster_needs"))
    return render_template("features/disaster_donation.html", need=need, form=form)


# =========================
# FEEDBACK & REPORTS
# =========================
@main.route("/feedback", methods=["GET", "POST"])
@login_required
def feedback():
    form = FeedbackForm()
    if form.validate_on_submit():
        db.session.add(Feedback(
            user_id=getattr(current_user, "user_id", None),
            message=form.message.data,
            submitted_at=datetime.utcnow()
        ))
        db.session.commit()
        flash("Feedback submitted.", "success")
        return redirect(url_for("main.dashboard"))
    return render_template("features/feedback.html", form=form)


@main.route("/report", methods=["GET", "POST"])
@login_required
def report():
    form = ReportForm()
    if form.validate_on_submit():
        db.session.add(Report(
            reported_by=getattr(current_user, "user_id", None),
            reason=form.reason.data,
            reported_at=datetime.utcnow()
        ))
        db.session.commit()
        flash("Report submitted.", "success")
        return redirect(url_for("main.dashboard"))
    return render_template("features/report.html", form=form)


# =========================
# NOTIFICATIONS
# =========================
@main.route("/notifications")
@login_required
def notifications():
    notes = Notification.query.filter_by(user_id=getattr(current_user, "user_id", None)).order_by(Notification.sent_at.desc()).all()
    return render_template("features/notifications.html", notifications=notes)


# =========================
# CHAT
# =========================
@main.route("/chat/<int:session_id>", methods=["GET", "POST"])
@login_required
def chat(session_id):
    chat_session = ChatSession.query.get_or_404(session_id)
    form = ChatForm()
    if form.validate_on_submit():
        sender_id = getattr(current_user, "user_id", None) or getattr(current_user, "org_id", None)
        db.session.add(ChatMessage(
            session_id=chat_session.session_id,
            sender_id=sender_id,
            message=form.message.data,
            timestamp=datetime.utcnow()
        ))

        # notify other participant
        other_id = chat_session.user_id if sender_id != chat_session.user_id else chat_session.org_id
        db.session.add(Notification(
            user_id=other_id,
            message=f"New message in chat {chat_session.session_id}",
            sent_at=datetime.utcnow()
        ))
        db.session.commit()
        flash("Message sent.", "success")
        return redirect(url_for("main.chat", session_id=session_id))

    messages = ChatMessage.query.filter_by(session_id=session_id).order_by(ChatMessage.timestamp.asc()).all()
    return render_template("features/chat.html", messages=messages, form=form, session=chat_session)


# =========================
# ITEM SEARCH / FILTER
# =========================
@main.route("/items")
def items_list():
    query = Item.query.filter_by(status="Active")
    category = request.args.get("category")
    if category:
        query = query.filter_by(category=category)
    search = request.args.get("search")
    if search:
        query = query.filter(Item.title.ilike(f"%{search}%"))
    items = query.order_by(Item.created_at.desc()).all()
    return render_template("items/search_results.html", items=items)


# =========================
# AUTO-EXPIRE ITEMS
# =========================
def auto_expire_items():
    now = datetime.utcnow()
    expired_items = Item.query.filter(Item.expiry_date <= now, Item.status=="Active").all()
    for item in expired_items:
        item.status = "Expired"
    db.session.commit()



# =========================
# ERROR HANDLERS
# =========================
@main.errorhandler(403)
def forbidden(e):
    return render_template("errors/403.html"), 403

@main.errorhandler(404)
def not_found(e):
    return render_template("errors/404.html"), 404

@main.errorhandler(405)
def method_not_allowed(e):
    return render_template("errors/405.html"), 405

@main.errorhandler(500)
def server_error(e):
    return render_template("errors/500.html"), 500
