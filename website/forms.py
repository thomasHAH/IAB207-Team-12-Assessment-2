#Commented

#Importing Flaskform base class and all the different field types from
#WTForms - all necessary!
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms.fields import TextAreaField, SubmitField, StringField, PasswordField, DateField, TimeField, IntegerField, DecimalField, SelectField
from wtforms.validators import InputRequired, Length, Email, EqualTo, DataRequired, NumberRange


# ---------------Uni provided code for login and registration----------------------------------
# Form for user login
class LoginForm(FlaskForm):
    #Username field which must have input
    user_name=StringField("User Name", validators=[InputRequired('Enter user name')])
    #Password field input required as well
    password=PasswordField("Password", validators=[InputRequired('Enter user password')])
    #Submit button now
    submit = SubmitField("Login")

 #this is the registration form
class RegisterForm(FlaskForm):
    #Username field with input required
    user_name=StringField("User Name", validators=[InputRequired()])
    #Must have valid email format
    email = StringField("Email Address", validators=[Email("Please enter a valid email")])
    #linking two fields - password should be equal to data entered in confirm
    password=PasswordField("Password", validators=[InputRequired(), EqualTo('confirm', message="Passwords should match")])
    #used to check both passwords match
    confirm = PasswordField("Confirm Password")
    # submit button
    submit = SubmitField("Register")
#---------------------------------------------------------------------------------------------

#-------------------------NEW CODE-------------------------------------------------------------------------------
#This is a form for creatinv a new event
class EventForm(FlaskForm):
    #Title of the event, required
    title = StringField('Enter Your Event Name', validators=[DataRequired()])
    #optional event description
    description = TextAreaField('Event Description (optional)')
    #location of the event
    location = StringField('Location', validators=[DataRequired()])
    #cost of event
    cost = DecimalField('Cost of Tickets', places=2, default=0.0)
    #Capacity must be an integer and greater than 0 - MAY CHANGE THIS
    capacity = IntegerField('Capacity of Event', validators=[NumberRange(min=1, message="Capacity must be positive")], default=1)
    #Features stored similar to the event status as a selected feild that way there is multiple options
    features = SelectField('Pool Feature', choices=[('heated', 'Heated'), ('indoor', 'Indoor'), ('slide', 'Slide'), ('saltwater', 'Saltwater'), ('outdoor', 'Outdoor'), ('regular', 'Regular')], validators=[DataRequired()], default='regular')
    #Status of the event (NOTE should be Open, Inactive, Closed, Cancelled)
    status = SelectField('Event Status', choices=[('open', 'Open'), ('inactive', 'Inactive'), ('closed', 'Closed'), ('cancelled', 'Cancelled')], validators=[DataRequired()], default='open')
    #Date of the event (required, must match the format given) - could make this easier
    date = DateField('Date', format='%Y-%m-%d', validators=[DataRequired()])
    
    #Only allows images
    image = FileField('Event Image', validators=[FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')])
    #SUBMIT BUTTONN
    submit = SubmitField('Create Event')
    
    
#Adding comments to events - NEW
#Form class for creating and submitting comments
class CommentForm(FlaskForm):
    #A text area field where the user writes their comment
    #DataRequired ensures the field cannot be left empty
    text = TextAreaField("Write a comment", validators=[DataRequired()])
    submit = SubmitField("Post Comment")
       
#NEW 02/10/25
#This form is used whenever a logged-in user wants to book 
#tickets for an event. It provides a simple interface
#Form for booking tickets to an event
class BookingForm(FlaskForm):
    #IntegerField lets the user enter a number (how many tickets they want)
    #Label shown in the form: "Quantity of Tickets For The Pool Event"
    #Validators:
    # - DataRequired(): field cannot be left empty
    # - NumberRange(min=1): must be at least 1 (prevents 0 or negative ticket requests)
    quantity = IntegerField(
        "Quantity of Tickets For The Pool Event",
        validators=[DataRequired(), NumberRange(min=1)]
    )

    #submit button the user clicks to confirm booking
    #the button text will appear as "Book Now"
    submit = SubmitField("Book Now")
#-----------------------------------------------------------------------------------------------------------------