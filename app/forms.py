# app/forms.py

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField, BooleanField, DateField, FileField, MultipleFileField, IntegerField, FormField, SelectMultipleField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional, NumberRange
from flask_wtf.file import FileAllowed

from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional, NumberRange
from flask_wtf.file import FileAllowed


from wtforms import StringField, SubmitField, FileField,FieldList
from wtforms.validators import DataRequired, Length, Optional
from flask_wtf.file import FileAllowed
# -------------------------
# Dropdown Choices
# -------------------------

KERALA_LOCATIONS = sorted([
    ('', 'Select Location'),
    ('Alappuzha', 'Alappuzha'),
    ('Alappuzha - Ambalapuzha', 'Alappuzha - Ambalapuzha'),
    ('Alappuzha - Cherthala', 'Alappuzha - Cherthala'),
    ('Alappuzha - Haripad', 'Alappuzha - Haripad'),
    ('Alappuzha - Kayamkulam', 'Alappuzha - Kayamkulam'),
    ('Alappuzha - Mavelikkara', 'Alappuzha - Mavelikkara'),
    ('Ernakulam', 'Ernakulam'),
    ('Ernakulam - Aluva', 'Ernakulam - Aluva'),
    ('Ernakulam - Kochi', 'Ernakulam - Kochi'),
    ('Ernakulam - Kothamangalam', 'Ernakulam - Kothamangalam'),
    ('Ernakulam - Perumbavoor', 'Ernakulam - Perumbavoor'),
    ('Ernakulam - Thrikkakara', 'Ernakulam - Thrikkakara'),
    ('Idukki', 'Idukki'),
    ('Idukki - Adimali', 'Idukki - Adimali'),
    ('Idukki - Thodupuzha', 'Idukki - Thodupuzha'),
    ('Idukki - Kattappana', 'Idukki - Kattappana'),
    ('Idukki - Munnar', 'Idukki - Munnar'),
    ('Kannur', 'Kannur'),
    ('Kannur - Kannur City', 'Kannur - Kannur City'),
    ('Kannur - Taliparamba', 'Kannur - Taliparamba'),
    ('Kannur - Payyanur', 'Kannur - Payyanur'),
    ('Kasargod', 'Kasargod'),
    ('Kasargod - Kasargod City', 'Kasargod - Kasargod City'),
    ('Kasargod - Kanhangad', 'Kasargod - Kanhangad'),
    ('Kollam', 'Kollam'),
    ('Kollam - Kollam City', 'Kollam - Kollam City'),
    ('Kollam - Punalur', 'Kollam - Punalur'),
    ('Kottayam', 'Kottayam'),
    ('Kottayam - Kottayam City', 'Kottayam - Kottayam City'),
    ('Kottayam - Changanassery', 'Kottayam - Changanassery'),
    ('Kozhikode', 'Kozhikode'),
    ('Kozhikode - Kozhikode City', 'Kozhikode - Kozhikode City'),
    ('Kozhikode - Vatakara', 'Kozhikode - Vatakara'),
    ('Malappuram', 'Malappuram'),
    ('Malappuram - Malappuram City', 'Malappuram - Malappuram City'),
    ('Malappuram - Manjeri', 'Malappuram - Manjeri'),
    ('Malappuram - Perinthalmanna', 'Malappuram - Perinthalmanna'),
    ('Palakkad', 'Palakkad'),
    ('Palakkad - Palakkad City', 'Palakkad - Palakkad City'),
    ('Palakkad - Ottapalam', 'Palakkad - Ottapalam'),
    ('Pathanamthitta', 'Pathanamthitta'),
    ('Pathanamthitta - Adoor', 'Pathanamthitta - Adoor'),
    ('Pathanamthitta - Pandalam', 'Pathanamthitta - Pandalam'),
    ('Pathanamthitta - Pathanamthitta City', 'Pathanamthitta - Pathanamthitta City'),
    ('Thiruvananthapuram', 'Thiruvananthapuram'),
    ('Thiruvananthapuram - Kowdiar', 'Thiruvananthapuram - Kowdiar'),
    ('Thiruvananthapuram - Kazhakoottam', 'Thiruvananthapuram - Kazhakoottam'),
    ('Thiruvananthapuram - Thiruvallam', 'Thiruvananthapuram - Thiruvallam'),
    ('Thrissur', 'Thrissur'),
    ('Thrissur - Thrissur City', 'Thrissur - Thrissur City'),
    ('Thrissur - Irinjalakuda', 'Thrissur - Irinjalakuda'),
    ('Thrissur - Guruvayur', 'Thrissur - Guruvayur'),
    ('Wayanad', 'Wayanad'),
    ('Wayanad - Kalpetta', 'Wayanad - Kalpetta'),
    ('Wayanad - Mananthavady', 'Wayanad - Mananthavady'),
    ('Wayanad - Sultan Bathery', 'Wayanad - Sultan Bathery'),
    # Add more villages/towns to reach 100+
    ('Alappuzha - Ambalappuzha Market', 'Alappuzha - Ambalappuzha Market'),
    ('Kollam - Karunagappally', 'Kollam - Karunagappally'),
    ('Kollam - Kottarakkara', 'Kollam - Kottarakkara'),
    ('Kottayam - Vaikom', 'Kottayam - Vaikom'),
    ('Kottayam - Pala', 'Kottayam - Pala'),
    ('Ernakulam - Fort Kochi', 'Ernakulam - Fort Kochi'),
    ('Ernakulam - Mattancherry', 'Ernakulam - Mattancherry'),
    ('Thrissur - Chalakudy', 'Thrissur - Chalakudy'),
    ('Thrissur - Kodungallur', 'Thrissur - Kodungallur'),
    ('Palakkad - Chittur', 'Palakkad - Chittur'),
    ('Palakkad - Mannarkkad', 'Palakkad - Mannarkkad'),
    ('Malappuram - Tirur', 'Malappuram - Tirur'),
    ('Malappuram - Nilambur', 'Malappuram - Nilambur'),
    ('Malappuram - Kondotty', 'Malappuram - Kondotty'),
    ('Kannur - Iritty', 'Kannur - Iritty'),
    ('Kannur - Payyannur Market', 'Kannur - Payyannur Market'),
    ('Idukki - Thodupuzha Town', 'Idukki - Thodupuzha Town'),
    ('Idukki - Devikulam', 'Idukki - Devikulam'),
    ('Kasaragod - Nileshwar', 'Kasaragod - Nileshwar'),
    ('Kasaragod - Poinachi', 'Kasaragod - Poinachi'),
    # You can continue adding villages/towns to reach 100+
], key=lambda x: x[1])


CATEGORIES = [
    ('', 'Select your Product Category'),
    ('Books', 'Books'),
    ('Clothes', 'Clothes'),
    ('Electronics', 'Electronics'),
    ('Food & Snacks', 'Food & Snacks'),
    ('Furniture', 'Furniture'),
    ('Gardening Items', 'Gardening Items'),
    ('Kitchen Items', 'Kitchen Items'),
    ('Medicines', 'Medicines'),
    ('Shoes & Footwear', 'Shoes & Footwear'),
    ('Sports Equipment', 'Sports Equipment'),
    ('Stationery', 'Stationery'),
    ('Toys', 'Toys'),
    ('Bags & Luggage', 'Bags & Luggage'),
    ('Tools & Hardware', 'Tools & Hardware'),
    ('Pet Supplies', 'Pet Supplies'),
    ('Art Supplies', 'Art Supplies'),
    ('Baby Products', 'Baby Products'),
    ('Beverages', 'Beverages'),
    ('Cameras & Photography', 'Cameras & Photography'),
    ('Cleaning Supplies', 'Cleaning Supplies'),
    ('Computers & Accessories', 'Computers & Accessories'),
    ('Cosmetics', 'Cosmetics'),
    ('Decor', 'Decor'),
    ('Fitness Equipment', 'Fitness Equipment'),
    ('Garden Tools', 'Garden Tools'),
    ('Health & Wellness', 'Health & Wellness'),
    ('Home Appliances', 'Home Appliances'),
    ('Jewelry', 'Jewelry'),
    ('Lamps & Lighting', 'Lamps & Lighting'),
    ('Musical Instruments', 'Musical Instruments'),
    ('Office Supplies', 'Office Supplies'),
    ('Outdoor Gear', 'Outdoor Gear'),
    ('Party Supplies', 'Party Supplies'),
    ('Personal Care', 'Personal Care'),
    ('Shoes', 'Shoes'),
    ('Stationery & Office', 'Stationery & Office'),
    ('Travel Accessories', 'Travel Accessories'),
    ('Vehicles & Accessories', 'Vehicles & Accessories'),
    ('Other', 'Other')
]

EXPECTED_RETURN_CHOICES = [
    ('', 'Select Expected Return'),
    ('Books', 'Books'),
    ('Clothes', 'Clothes'),
    ('Electronics', 'Electronics'),
    ('Food & Snacks', 'Food & Snacks'),
    ('Furniture', 'Furniture'),
    ('Gardening Items', 'Gardening Items'),
    ('Kitchen Items', 'Kitchen Items'),
    ('Medicines', 'Medicines'),
    ('Shoes & Footwear', 'Shoes & Footwear'),
    ('Sports Equipment', 'Sports Equipment'),
    ('Stationery', 'Stationery'),
    ('Toys', 'Toys'),
    ('Bags & Luggage', 'Bags & Luggage'),
    ('Tools & Hardware', 'Tools & Hardware'),
    ('Pet Supplies', 'Pet Supplies'),
    ('Art Supplies', 'Art Supplies'),
    ('Baby Products', 'Baby Products'),
    ('Beverages', 'Beverages'),
    ('Cameras & Photography', 'Cameras & Photography'),
    ('Cleaning Supplies', 'Cleaning Supplies'),
    ('Computers & Accessories', 'Computers & Accessories'),
    ('Cosmetics', 'Cosmetics'),
    ('Decor', 'Decor'),
    ('Fitness Equipment', 'Fitness Equipment'),
    ('Garden Tools', 'Garden Tools'),
    ('Health & Wellness', 'Health & Wellness'),
    ('Home Appliances', 'Home Appliances'),
    ('Jewelry', 'Jewelry'),
    ('Lamps & Lighting', 'Lamps & Lighting'),
    ('Money', 'Money'),
    ('Musical Instruments', 'Musical Instruments'),
    ('Office Supplies', 'Office Supplies'),
    ('Outdoor Gear', 'Outdoor Gear'),
    ('Party Supplies', 'Party Supplies'),
    ('Personal Care', 'Personal Care'),
    ('Shoes', 'Shoes'),
    ('Stationery & Office', 'Stationery & Office'),
    ('Travel Accessories', 'Travel Accessories'),
    ('Vehicles & Accessories', 'Vehicles & Accessories'),
    ('Other', 'Other')
]

# -------------------------
# Search and Filter Forms
# -------------------------
class SearchForm(FlaskForm):
    search = StringField('Search', validators=[Optional()])
    # MODIFICATION: Changed SelectField to SelectMultipleField
    location = SelectMultipleField('Location', choices=KERALA_LOCATIONS, validators=[Optional()])
    urgency = SelectField('Urgency', choices=[('', 'All Urgencies'), ('Urgent', 'Urgent'), ('Flexible', 'Flexible')], validators=[Optional()])
    condition = SelectField('Condition', choices=[('', 'All Conditions'), ('New', 'New'), ('Used', 'Used'), ('Old', 'Old')], validators=[Optional()])
    sort_by = SelectField('Sort by', choices=[('newest', 'Newest'), ('oldest', 'Oldest')], default='newest', validators=[Optional()])
    submit = SubmitField('Search')
# -------------------------
# User / Org / Admin Forms
# -------------------------

class RegistrationForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=255)])
    last_name = StringField('Last Name', validators=[Optional(), Length(max=255)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=255)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    phone = StringField('Phone', validators=[Optional(), Length(max=50)])
    location = SelectField('Location', choices=KERALA_LOCATIONS, validators=[DataRequired()])
    profile_picture = FileField('Profile Picture', validators=[Optional(), FileAllowed(['jpg', 'png', 'jpeg'])])
    submit = SubmitField('Register')


class OrganizationRegistrationForm(FlaskForm):
    name = StringField('Organization Name', validators=[DataRequired(), Length(max=255)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=255)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    phone = StringField('Phone', validators=[Optional(), Length(max=100)])
    location = SelectField('Location', choices=KERALA_LOCATIONS, validators=[DataRequired()])
    profile_picture = FileField('Organization Logo/Profile', validators=[Optional(), FileAllowed(['jpg', 'png', 'jpeg'])])
    submit = SubmitField('Register Organization')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=255)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')



# -------------------------
#otp verification & forget pass
# -------------------------


class OtpForm(FlaskForm):
    otp = StringField('OTP', validators=[DataRequired(), Length(min=6, max=6)])
    submit = SubmitField('Verify')

class ForgotPasswordForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('New Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm New Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')



# -------------------------
# Item & Trade Forms
# -------------------------

class ItemForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=255)])
    description = TextAreaField('Description', validators=[Optional()])
    category = SelectField('Category', choices=CATEGORIES, validators=[DataRequired()])
    # --- MODIFICATION START ---
    type = SelectField('Type', choices=[
        ('Trade', 'Trade'),
        ('Share', 'Share')
    ], validators=[DataRequired()])
    # --- MODIFICATION END ---
    condition = SelectField('Condition', choices=[
        ('New', 'New'),
        ('Used', 'Used'),
        ('Old', 'Old')
    ], validators=[Optional()])
    urgency_level = SelectField('Urgency', choices=[
        ('Urgent', 'Urgent'),
        ('Flexible', 'Flexible')
    ], validators=[Optional()])
    expected_return = SelectField('Expected Return', choices=EXPECTED_RETURN_CHOICES, validators=[Optional()])
    images = MultipleFileField('Upload Images (you can select multiple)', validators=[Optional(), FileAllowed(['jpg', 'png', 'jpeg'])])
    submit = SubmitField('Post Item')

# -------------------------
# Disaster Forms
# -------------------------

class DisasterNeedForm(FlaskForm):
    title = StringField('Need Title (e.g., "Kottayam Flood Relief")', validators=[DataRequired(), Length(max=255)]) # <-- ADD THIS
    categories = SelectMultipleField('Categories (select multiple)', choices=CATEGORIES, validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    location = SelectField('Location', choices=KERALA_LOCATIONS, validators=[DataRequired()])
    submit = SubmitField('Post Need')


class OfferedItemForm(FlaskForm):
    """Sub-form for a single item within a larger donation offer."""
    class Meta:  # <-- ADD THIS META CLASS
        csrf = False

    title = StringField('Item Name', validators=[DataRequired(), Length(max=255)])
    category = SelectField('Category', choices=CATEGORIES, validators=[DataRequired()])
    description = TextAreaField('Description', validators=[Optional(), Length(max=1000)])
    quantity = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=1)], default=1)
    condition = SelectField('Condition', choices=[('New', 'New'), ('Used', 'Used')], validators=[DataRequired()])
    image = FileField('Image', validators=[Optional(), FileAllowed(['jpg', 'png', 'jpeg'])])
    manufacture_date = DateField('Manufacture Date', validators=[Optional()])
    expiry_date = DateField('Expiry Date', validators=[Optional()])

class DonationOfferForm(FlaskForm):
    """Main form for a user to offer a list of items."""
    offered_items = FieldList(FormField(OfferedItemForm), min_entries=1)
    submit = SubmitField('Submit Donation Offer')

# -------------------------
# Interaction Forms
# -------------------------

class FeedbackForm(FlaskForm):
    message = TextAreaField('Message', validators=[DataRequired(), Length(max=2000)])
    submit = SubmitField('Submit')


class ReportForm(FlaskForm):
    reason = TextAreaField('Reason', validators=[DataRequired(), Length(max=1000)])
    submit = SubmitField('Report')


class CategoryFollowForm(FlaskForm):
    category = SelectField('Category', choices=CATEGORIES, validators=[DataRequired()])
    submit = SubmitField('Follow')


class ChatForm(FlaskForm):
    message = StringField('Message', validators=[Optional(), Length(max=1000)])
    image = FileField('Image', validators=[Optional(), FileAllowed(['jpg', 'png', 'jpeg', 'gif'])])
    submit = SubmitField('Send')

class OrganizationReportForm(FlaskForm):
    reason = TextAreaField('Reason for Reporting', validators=[DataRequired(), Length(min=10, max=1000)])
    submit = SubmitField('Submit Report')