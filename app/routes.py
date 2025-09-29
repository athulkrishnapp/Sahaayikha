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

from sqlalchemy import or_

from app import db, login_manager
from app.models import (
    User, Admin, Organization, LoginLog,
    Item, ItemImage, ItemHistory,
    ChatSession, ChatMessage, DealProposal, # <-- Added here
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

from datetime import datetime
from flask import jsonify, abort

from datetime import datetime, timedelta

from flask import jsonify
# -------------------------
# UPLOAD FOLDERS
# -------------------------
USER_UPLOAD_FOLDER = os.path.join("app", "static", "images", "profiles", "users")
ORG_UPLOAD_FOLDER = os.path.join("app", "static", "images", "profiles", "orgs")
ITEM_UPLOAD_FOLDER = os.path.join("app", "static", "images", "items")
CHAT_UPLOAD_FOLDER = os.path.join("app", "static", "images", "chat_uploads") 
os.makedirs(USER_UPLOAD_FOLDER, exist_ok=True)
os.makedirs(ORG_UPLOAD_FOLDER, exist_ok=True)
os.makedirs(ITEM_UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CHAT_UPLOAD_FOLDER, exist_ok=True)

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
# Local Date
# -------------------------

@main.app_template_filter('localdatetime')
def localdatetime_filter(utc_dt):
    # Assuming your server and users are in IST (UTC+5:30)
    return utc_dt + timedelta(hours=5, minutes=30)

# =========================
# AUTH SELECTOR ROUTES
# =========================
@main.route("/auth/login")
def auth_login_selector():
    return render_template("auth_login.html")

@main.route("/auth/register")
def auth_register_selector():
    return render_template("auth_reg.html")

# =========================
# Shedular deletion
# =========================


def run_scheduled_deletions():
    """A simple task to simulate a cron job for deleting items."""
    now = datetime.utcnow()
    thirty_days_ago = now - timedelta(days=30)
    
    # Find items to be soft-deleted
    items_to_delete = Item.query.filter(
        Item.status == 'Active',
        or_(
            Item.deal_finalized_at <= now,
            Item.created_at <= thirty_days_ago
        )
    ).all()

    for item in items_to_delete:
        item.status = 'Deleted' # Soft delete
        db.session.add(ItemHistory(item_id=item.item_id, action="Item automatically deleted."))
    
    if items_to_delete:
        db.session.commit()


# -------------------------
# HOME
# -------------------------
@main.route("/")
def home():
    run_scheduled_deletions() # Check for deletions on each home page visit
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
    # Only redirect if already logged in as User
    if current_user.is_authenticated and isinstance(current_user._get_current_object(), User):
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

        flash("Invalid email or password.", "danger")

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
# In app/routes.py

@main.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    user = current_user._get_current_object()
    
    # ## NEW: Fetch blocked chat sessions ##
    blocked_chats = []
    if isinstance(user, User):
        # Find all sessions where the status is 'Blocked' and the current user was involved
        blocked_chats = ChatSession.query.filter(
            ChatSession.status == 'Blocked',
            or_(ChatSession.user1_id == user.user_id, ChatSession.user2_id == user.user_id)
        ).all()
    
    if isinstance(user, User):
        template = "auth/user_profile.html"
        form = RegistrationForm(obj=user)
    elif isinstance(user, Organization):
        template = "auth/org_profile.html"
        form = OrganizationRegistrationForm(obj=user)
    else:
        flash("Profile not editable.", "warning")
        return redirect(url_for("main.home"))

    form.password.validators = []
    form.confirm_password.validators = []

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
            if isinstance(user, User):
                user.profile_picture = f"images/profiles/users/{filename}"
            else:
                user.profile_picture = f"images/profiles/orgs/{filename}"
        db.session.commit()
        flash("Profile updated successfully.", "success")
        return redirect(url_for("main.profile"))
    
    # Pass the blocked_chats list to the template
    return render_template(template, form=form, blocked_chats=blocked_chats)

@main.route('/profile/picture/delete', methods=['POST'])
@login_required
def delete_profile_picture():
    """Deletes the user's or org's current profile picture."""
    user = current_user._get_current_object()

    if user.profile_picture:
        try:
            # Construct full path to the image and delete it
            if isinstance(user, User):
                folder = USER_UPLOAD_FOLDER
                # ## CORRECTED PATH ##
                placeholder = 'images/users_placeholder.png'
            else:
                folder = ORG_UPLOAD_FOLDER
                # ## CORRECTED PATH ##
                placeholder = 'images/orgs_placeholder.png'
            
            filename = os.path.basename(user.profile_picture)
            file_path = os.path.join(folder, filename)

            if os.path.exists(file_path):
                os.remove(file_path)

        except Exception as e:
            print(f"Error deleting file: {e}")

        user.profile_picture = None
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'placeholder_url': url_for('static', filename=placeholder)
        })

    return jsonify({'success': False, 'error': 'No profile picture to delete.'})


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
            # db.session.add(LoginLog(user_id=admin.admin_id, ip_address=request.remote_addr))
            # db.session.commit()
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
            # db.session.add(LoginLog(user_id=org.org_id, ip_address=request.remote_addr))
            # db.session.commit()
            flash("Organization logged in successfully.", "success")
            return redirect(url_for("main.org_dashboard"))


        flash("Invalid email or password.", "danger")

    return render_template("auth/org_login.html", form=form)



# -------------------------
# ORG DASHBOARD
# -------------------------
@main.route("/org/dashboard")
@login_required
@role_required("org")
def org_dashboard():
    org = current_user._get_current_object()
    filter_type = request.args.get("filter")

    # All active items EXCEPT this org’s own
    all_items_query = Item.query.filter(
        Item.status == "Active",
        Item.user_id != org.org_id  # assuming org_id is used for DisasterNeed posting
    )
    if filter_type in ["Trade", "Disaster"]:
        all_items_query = all_items_query.filter_by(type=filter_type)
    all_items = all_items_query.order_by(Item.created_at.desc()).all()

    # My posted disaster needs
    my_items_query = DisasterNeed.query.filter_by(org_id=org.org_id)
    if filter_type:
        my_items_query = my_items_query.filter_by(category=filter_type)
    my_items = my_items_query.order_by(DisasterNeed.posted_at.desc()).all()

    donations = DisasterDonation.query.filter_by(org_id=org.org_id).all()

    return render_template(
        "dashboard/org_dashboard.html",
        org=org,
        all_items=all_items,
        my_items=my_items,
        donations=donations
    )





# =========================
# USER DASHBOARD
# =========================
@main.route("/dashboard")
@login_required
@role_required("user")
def dashboard():
    view = request.args.get("view", "all")
    filter_type = request.args.get("filter")

    items = []
    donations = []
    chat_sessions = []

    if view == "mine":
        query = Item.query.filter_by(user_id=current_user.user_id)
        # ## FIX 1: Added 'Share' to this list ##
        if filter_type in ["Trade", "Disaster", "Share"]:
            query = query.filter_by(type=filter_type)
        items = query.order_by(Item.created_at.desc()).all()
        donations = DisasterDonation.query.filter_by(user_id=current_user.user_id).all()

    elif view == "bookmarks":
        user_bookmarks = Bookmark.query.filter_by(user_id=current_user.user_id).order_by(Bookmark.saved_at.desc()).all()
        items = [b.item for b in user_bookmarks]

    elif view == "chats":
        chat_sessions = db.session.query(ChatSession).filter(
            or_(ChatSession.user1_id == current_user.user_id, ChatSession.user2_id == current_user.user_id)
        ).join(Item).order_by(ChatSession.started_at.desc()).all()
        
    else:  # Default to "all"
        view = "all"
        query = Item.query.filter(Item.status == "Active", Item.user_id != current_user.user_id)
        # ## FIX 2: Added 'Share' to this list ##
        if filter_type in ["Trade", "Disaster", "Share"]:
            query = query.filter_by(type=filter_type)
        items = query.order_by(Item.created_at.desc()).all()
        donations = DisasterDonation.query.filter_by(status="Pending").all()

    return render_template(
        "dashboard/user_dashboard.html",
        items=items,
        donations=donations,
        chat_sessions=chat_sessions,
        view=view
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
                if f and f.filename:
                    filename = secure_filename(f.filename)  # ✅ define filename
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
    is_bookmarked = False
    session = None
    deal = None

    if current_user.is_authenticated:
        # Check bookmark status
        if Bookmark.query.filter_by(user_id=current_user.user_id, item_id=item.item_id).first():
            is_bookmarked = True
        
        # Find the chat session and deal proposal between the viewer and the owner
        if item.user_id != current_user.user_id:
            session = ChatSession.query.filter(
                or_(
                    (ChatSession.user1_id == current_user.user_id) & (ChatSession.user2_id == item.user_id),
                    (ChatSession.user1_id == item.user_id) & (ChatSession.user2_id == current_user.user_id)
                ),
                ChatSession.item_id == item.item_id
            ).first()

            if session:
                deal = DealProposal.query.filter_by(chat_session_id=session.session_id).first()

    return render_template("items/view_item.html", item=item, is_bookmarked=is_bookmarked, session=session, deal=deal)


@main.route('/deal/<int:session_id>/propose', methods=['POST'])
@login_required
def propose_deal(session_id):
    decision = request.form.get('decision') # will be 'confirmed' or 'rejected'
    session = ChatSession.query.get_or_404(session_id)
    item = session.item

    # Security check
    if session.user1_id != current_user.user_id and session.user2_id != current_user.user_id:
        abort(403)

    # Find or create the deal proposal
    deal = DealProposal.query.filter_by(chat_session_id=session_id).first()
    if not deal:
        deal = DealProposal(chat_session_id=session_id)
        db.session.add(deal)

    # Update the status for the current user
    if item.user_id == current_user.user_id: # Current user is the owner
        deal.owner_status = decision
    else: # Current user is the proposer
        deal.proposer_status = decision
    
    # Check if both have confirmed
    if deal.owner_status == 'confirmed' and deal.proposer_status == 'confirmed':
        item.deal_finalized_at = datetime.utcnow() + timedelta(hours=24)
        flash('Both parties have confirmed the deal! This item will be removed in 24 hours.', 'success')
    else:
        # If anyone rejects or changes their mind, cancel the finalization
        item.deal_finalized_at = None
        flash('Your decision has been recorded.', 'info')
        
    db.session.commit()
    return redirect(request.referrer or url_for('main.home'))


@main.route("/item/<int:item_id>/history")
@login_required
def item_history(item_id):
    history = ItemHistory.query.filter_by(item_id=item_id).order_by(ItemHistory.timestamp.desc()).all()
    return render_template("items/item_history.html", history=history, item_id=item_id)




@main.route("/item/image/<int:image_id>/delete", methods=["POST"])
@login_required
def delete_item_image(image_id):
    """Handles the AJAX request to delete an image."""
    image = ItemImage.query.get_or_404(image_id)
    item = image.item

    # Security check: Ensure the current user owns the item linked to the image
    if item.user_id != getattr(current_user, "user_id", None):
        abort(403) # Forbidden

    try:
        # Construct the full path to the image file
        file_path = os.path.join("app", "static", image.image_url)
        
        # Delete the physical file from your server
        if os.path.exists(file_path):
            os.remove(file_path)

        # Delete the image record from the database
        db.session.delete(image)
        db.session.commit()

        # Send a success response back to the JavaScript
        return jsonify({"success": True})

    except Exception as e:
        db.session.rollback()
        print(f"Error deleting image: {e}") # Log the error for debugging
        return jsonify({"success": False, "error": "Server error, please try again."}), 500

@main.route("/item/<int:item_id>/edit", methods=["GET", "POST"])
@login_required
def edit_item(item_id):
    item = Item.query.get_or_404(item_id)

    # Only owner can edit
    if item.user_id != getattr(current_user, "user_id", None):
        abort(403)

    form = ItemForm(obj=item)
    if form.validate_on_submit():
        item.title = form.title.data
        item.description = form.description.data
        item.category = form.category.data
        item.type = form.type.data
        item.condition = form.condition.data
        item.urgency_level = form.urgency_level.data
        item.expected_return = form.expected_return.data
        
        # Handle newly uploaded images
        if form.images.data:
            for file_storage in form.images.data:
                if file_storage and file_storage.filename:
                    # FIX: Correctly get filename for each file and save it
                    filename = secure_filename(file_storage.filename)
                    file_path = os.path.join(ITEM_UPLOAD_FOLDER, filename)
                    file_storage.save(file_path)
                    
                    # Create a new database record for the uploaded image
                    new_image = ItemImage(item_id=item.item_id, image_url=f"images/items/{filename}")
                    db.session.add(new_image)
        
        db.session.commit()
        flash("Item updated successfully.", "success")
        return redirect(url_for("main.view_item", item_id=item.item_id))

    return render_template("items/edit_item.html", form=form, item=item)


@main.route("/item/<int:item_id>/delete", methods=["POST"])
@login_required
def delete_item(item_id):
    item = Item.query.get_or_404(item_id)

    # Only owner can delete
    if item.user_id != getattr(current_user, "user_id", None):
        abort(403)

    # Delete associated images first
    for img in item.images:
        try:
            os.remove(os.path.join(ITEM_UPLOAD_FOLDER, os.path.basename(img.image_url)))
        except Exception:
            pass
        db.session.delete(img)

    # Delete the item itself
    db.session.delete(item)
    db.session.commit()

    flash("Item deleted successfully.", "success")
    return redirect(url_for("main.dashboard"))





# =========================
# BOOKMARKS
# =========================
@main.route("/bookmark/<int:item_id>", methods=['POST'])
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
    # Redirect back to the page the user was on
    return redirect(request.referrer or url_for("main.dashboard"))


# ADD THIS NEW ROUTE for deleting chats
@main.route('/chat/<int:session_id>/delete', methods=['POST'])
@login_required
def delete_chat_session(session_id):
    session = ChatSession.query.get_or_404(session_id)
    
    # Security check: ensure current user is part of the chat
    if session.user1_id != current_user.user_id and session.user2_id != current_user.user_id:
        abort(403)
        
    # Delete associated messages first
    ChatMessage.query.filter_by(session_id=session_id).delete()
    
    # Now delete the session itself
    db.session.delete(session)
    db.session.commit()
    
    flash("Chat session has been deleted.", "success")
    return redirect(url_for('main.dashboard', view='chats'))


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
def report_general():
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



@main.route("/report/<int:item_id>", methods=["GET", "POST"])
@login_required
def report_item(item_id):
    form = ReportForm()
    if form.validate_on_submit():
        db.session.add(Report(
            reported_by=getattr(current_user, "user_id", None),
            item_id=item_id,
            reason=form.reason.data,
            reported_at=datetime.utcnow()
        ))
        db.session.commit()
        flash("Report submitted.", "success")
        return redirect(url_for("main.dashboard"))
    return render_template("features/report.html", form=form, item_id=item_id)



# =========================
# NOTIFICATIONS
# =========================
@main.route("/notifications")
@login_required
def notifications():
    notes = Notification.query.filter_by(user_id=getattr(current_user, "user_id", None)).order_by(Notification.sent_at.desc()).all()
    return render_template("features/notifications.html", notifications=notes)



# =========================
# Public Profile
# =========================

@main.route('/user/<int:user_id>')
@login_required
def public_profile(user_id):
    # If a user tries to view their own public profile, redirect them to their editable one
    if user_id == current_user.user_id:
        return redirect(url_for('main.profile'))

    # Fetch the user whose profile is being viewed
    user = User.query.get_or_404(user_id)

    # Fetch only the 'Active' items posted by that user
    items = Item.query.filter_by(user_id=user.user_id, status='Active')\
                      .order_by(Item.created_at.desc()).all()

    return render_template("public_profile.html", user=user, items=items)



# =========================
# Start CHAT
# =========================

@main.route("/item/<int:item_id>/chat")
@login_required
def start_chat(item_id):
    item = Item.query.get_or_404(item_id)
    # Assuming you chat with the item owner
    other_user_id = item.user_id
    # Check if session already exists
    session = ChatSession.query.filter_by(item_id=item_id, user1_id=current_user.user_id, user2_id=other_user_id).first()
    if not session:
        session = ChatSession(item_id=item_id, user1_id=current_user.user_id, user2_id=other_user_id)
        db.session.add(session)
        db.session.commit()
    return redirect(url_for("main.chat", session_id=session.session_id))




# =========================
# CHAT
# =========================

@main.route('/message/<int:message_id>/delete', methods=['POST'])
@login_required
def delete_message(message_id):
    # 1. Find the message in the database
    msg = ChatMessage.query.get_or_404(message_id)

    # 2. Security Check: Ensure the current user is the sender of the message
    if msg.sender_id != current_user.user_id:
        abort(403) # Forbidden

    # 3. "Soft delete" the message by marking it as deleted
    msg.deleted_at = datetime.utcnow()
    # Optional: You can also clear the content if you wish
    # msg.message = None
    # msg.image_url = None
    
    db.session.commit()

    # 4. Return a success response to the JavaScript
    return jsonify({'success': True})

# ADD this new route to confirm a deal
@main.route('/chat/<int:session_id>/confirm_deal', methods=['POST'])
@login_required
def confirm_deal(session_id):
    session = ChatSession.query.get_or_404(session_id)
    if session.user1_id != current_user.user_id and session.user2_id != current_user.user_id:
        abort(403)

    session.status = 'Confirmed'
    session.item.status = 'Traded' # Update the item's status as well
    db.session.add(ItemHistory(item_id=session.item_id, user_id=current_user.user_id, action=f"Deal confirmed with user {session.user1_id if session.user2_id == current_user.user_id else session.user2_id}"))
    db.session.commit()
    flash('Deal successfully confirmed! The item is now marked as "Traded".', 'success')
    return redirect(url_for('main.chat', session_id=session_id))

# ADD this new route to block a user in a chat
@main.route('/chat/<int:session_id>/block', methods=['POST'])
@login_required
def block_chat(session_id):
    session = ChatSession.query.get_or_404(session_id)
    if session.user1_id != current_user.user_id and session.user2_id != current_user.user_id:
        abort(403)

    session.status = 'Blocked'
    db.session.commit()
    flash('This chat has been blocked. You can no longer send messages.', 'warning')
    return redirect(url_for('main.chat', session_id=session_id))



@main.route('/chat/<int:session_id>/unblock', methods=['POST'])
@login_required
def unblock_chat(session_id):
    session = ChatSession.query.get_or_404(session_id)
    # Security check: ensure the current user is part of the chat
    if session.user1_id != current_user.user_id and session.user2_id != current_user.user_id:
        abort(403)

    # Change status back to Active
    session.status = 'Active'
    db.session.commit()
    flash('Chat has been unblocked.', 'success')
    return redirect(url_for('main.profile'))



# REPLACE your entire old /chat/<session_id> route with this one
@main.route("/chat/<int:session_id>", methods=["GET", "POST"])
@login_required
def chat(session_id):
    chat_session = ChatSession.query.get_or_404(session_id)
    if chat_session.user1_id != current_user.user_id and chat_session.user2_id != current_user.user_id:
        abort(403)

    other_user = chat_session.user2 if chat_session.user1_id == current_user.user_id else chat_session.user1
    deal = DealProposal.query.filter_by(chat_session_id=session_id).first()
    
    form = ChatForm()
    if form.validate_on_submit():
        if chat_session.status != 'Active':
            flash("Cannot send messages in this chat.", "danger")
            return redirect(url_for("main.chat", session_id=session_id))

        if not form.message.data and not form.image.data:
            flash("Cannot send an empty message.", "warning")
            return redirect(url_for("main.chat", session_id=session_id))

        image_filename = None
        if form.image.data:
            image_file = form.image.data
            image_filename = secure_filename(f"{datetime.utcnow().timestamp()}_{image_file.filename}")
            image_file.save(os.path.join(CHAT_UPLOAD_FOLDER, image_filename))
            image_filename = f"images/chat_uploads/{image_filename}"

        # Audio handling logic is now removed
        msg = ChatMessage(
            session_id=chat_session.session_id,
            sender_id=current_user.user_id,
            message=form.message.data if form.message.data else None,
            image_url=image_filename
        )
        db.session.add(msg)
        db.session.commit()
        return redirect(url_for("main.chat", session_id=session_id))

    messages = ChatMessage.query.filter_by(session_id=session_id).order_by(ChatMessage.timestamp.asc()).all()
    
    return render_template(
        "features/chat.html", 
        messages=messages, form=form, session=chat_session, other_user=other_user, deal=deal
    )

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
