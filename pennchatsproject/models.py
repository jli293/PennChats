from pennchatsproject import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Sequence


@login_manager.user_loader
def load_user(student_id):
    """Allows app the load the student based on the student_id that was passed in."""
    return Student.query.get(student_id)


class Student(db.Model, UserMixin):
    """Creates a model that represents a student.
    nullable=False means it will be compulsory to set the value for that column.
    index=True indicates that the column will be indexed.
    There is a many to many relationship between student and current courses,
    past courses, interests, and meetings."""

    __tablename__ = 'students'

    student_id = db.Column(db.Integer, primary_key=True,
                           unique=True, nullable=False)
    email = db.Column(db.String(64), index=True, unique=True, nullable=False)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    first_name = db.Column(db.Text)
    last_name = db.Column(db.Text)
    city = db.Column(db.Text)
    state = db.Column(db.Text)
    country = db.Column(db.Text)
    bio = db.Column(db.Text)
    linkedin = db.Column(db.Text)
    # profile_image = db.Column(
    #     db.String(64), nullable=False, default='default_profile.png')

    # many to many relationships - back references
    current_courses = db.relationship(
        'Course', secondary='current_courses_record', backref='current_students')
    past_courses = db.relationship(
        'Course', secondary='past_courses_record', backref='past_students')
    interests = db.relationship(
        'Interest', secondary='student_interest_record', backref='all_students')
    meetings = db.relationship(
        'Meeting', secondary='groupings', backref='students')

    # many to one relationships
    weekly_signups = db.relationship('WeeklySignUp', backref='student')
    # calling weekly_signups.student will refer to the student associated with the weekly signup form

    # one to many relatinoships
    cohort = db.Column(db.Text, db.ForeignKey('cohorts.cohort_name'))
    course_id_to_match = db.Column(db.Text, db.ForeignKey('courses.course_id'))
    interest_id_to_match = db.Column(
        db.Integer, db.ForeignKey('interests.interest_id'))

    # def __init__(self, email, username, student_id, password):
    #     self.email = email
    #     self.username = username
    #     self.student_id = student_id
    #     self.password_hash = generate_password_hash(password)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return self.student_id

    def __repr__(self):
        return f"Registered student: {self.username}, {self.student_id}, and {self.email}."


class WeeklySignUp(db.Model):
    """This table will store information of the matching preferences of a student on a given week.
    There is a one to many relationship between this table and the student table, the primetime table,
    the sectime table, primenetworkinggoal table, and the secnetworkinggoal table."""

    __tablename__ = 'weekly_signups'

    signup_id = db.Column(db.Integer, primary_key=True)

    # one to many relationships
    meeting_week_name = db.Column(db.Text, db.ForeignKey(
        'meeting_weeks.week_meet_name'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey(
        'students.student_id'), nullable=False)
    prime_time_id = db.Column(db.Integer, db.ForeignKey(
        'time_options.time_id'), nullable=False)
    sec_time_id = db.Column(db.Integer, db.ForeignKey(
        'time_options.time_id'), nullable=False)
    prime_networking_goal_id = db.Column(db.Integer, db.ForeignKey(
        'networking_goals.networking_goal_id'), nullable=False)
    sec_networking_goal_id = db.Column(db.Integer, db.ForeignKey(
        'networking_goals.networking_goal_id'), nullable=False)

    def __init__(self, signup_id, meeting_week_name, student_id, prime_time_id, sec_time_id, prime_networking_goal_id, sec_networking_goal_id):
        # need to figure out how to best time stamp WeeklySignUp Forms
        self.signup_id = signup_id
        self.meeting_week_name = meeting_week_name
        self.student_id = student_id
        self.prime_time_id = prime_time_id
        self.sec_time_id = sec_time_id
        self.prime_networking_goal_id = prime_networking_goal_id
        self.sec_networking_goal_id = sec_networking_goal_id

    def __repr__(self):
        return f"WeeklySignUp Form: time stamp: {self.meeting_week_name}, {self.student_id}, prime time pref ID: {self.prime_time_id}, the sec time pref ID: {self.sec_time_id}, prime goal ID: {self.prime_networking_goal_id}, sec goal ID: {self.sec_networking_goal_id}."


class WeekMeet(db.Model):
    """This table will store all the available weeks that students to sign up 
    for PennChats. The table will be queried to provide options for students to 
    fill out their WeeklySignUp forms.
    There is a many to one relationship between this table and the WeeklySignUp 
    table."""

    __tablename__ = 'meeting_weeks'

    week_meet_name = db.Column(db.Text, primary_key=True, nullable=False)

    # many to one relationship
    weekly_signups = db.relationship('WeeklySignUp', backref='week_meet')
    meetings = db.relationship('Meeting', backref='week_meet')
    unmatched_students = db.relationship(
        'UnmatchedStudents', backref='week_meet')

    def __init__(self, week_meet_name):
        self.week_meet_name = week_meet_name

    def __repr__(self):
        return f"This is the meeting week of {self.week_meet_name}."


class Course(db.Model):
    """This table is used to store all MCIT Online courses
    Course id is the actual MCIT online course ID number.
    There are several relationships between this table and the Student table."""
    # how do we input data to this table?

    __tablename__ = 'courses'

    course_id = db.Column(db.Text, primary_key=True,
                          unique=True, nullable=False)
    course_name = db.Column(db.Text, nullable=False)

    # many to one relationships
    students = db.relationship('Student', backref='course_to_match')
    # calling student.course_to_match will return the course this student prefers to be matched with

    def __init__(self, course_id, course_name):
        self.course_id = course_id
        self.course_name = course_name

    def __repr__(self):
        return f"{self.course_id} {self.course_name}"


# many to many relatinoship association tables
current_courses_record = db.Table('current_courses_record',
                                  db.Column('student_id', db.Integer, db.ForeignKey(
                                      'students.student_id'), primary_key=True),
                                  db.Column('course_id', db.Text, db.ForeignKey(
                                      'courses.course_id'), primary_key=True)
                                  )

past_courses_record = db.Table('past_courses_record',
                               db.Column('student_id', db.Integer, db.ForeignKey(
                                   'students.student_id'), primary_key=True),
                               db.Column('course_id', db.Text, db.ForeignKey(
                                   'courses.course_id'), primary_key=True)
                               )


class Interest(db.Model):
    """This table is used to store all interests we plan to provide as options for students to choose from
    when they fill out their user profile.
    There is a many to many relationship and a many to one relationship with 
    this table and the Student table."""

    __tablename__ = 'interests'

    interest_id = db.Column(db.Integer, primary_key=True)
    interest_name = db.Column(db.Text, nullable=False, unique=True)

    # many to one relationship
    students = db.relationship('Student', backref='interest_to_match')
    # calling student.interest_to_match will return all the interest this student prefers to be matched with

    def __init__(self, interest_name):
        self.interest_name = interest_name

    def __repr__(self):
        return f"This is the interest of {self.interest_name} with the interest ID of {self.interest_id}."


# many to many association table
student_interest_record = db.Table('student_interest_record',
                                   db.Column('student_id', db.Integer, db.ForeignKey(
                                       'students.student_id'), primary_key=True),
                                   db.Column('interest_id', db.Integer, db.ForeignKey(
                                       'interests.interest_id'), primary_key=True)
                                   )


class Cohort(db.Model):
    """This table is used to store all cohorts that exists in MCIT Online.
    The table will then be queried to provide options for students to fill out
    their personal profiles.
    There is a one to many relationship between this table and the student table."""

    __tablename__ = 'cohorts'

    cohort_name = db.Column(db.Text, primary_key=True, nullable=False)

    # many to one relationship
    students = db.relationship('Student', backref='belong_to_cohort')
    # calling student.belong_cohort will return the cohort object of this student

    def __init__(self, cohort_name):
        self.cohort_name = cohort_name

    def __repr__(self):
        return f"This is the cohort of {self.cohort_name}."


class TimeOption(db.Model):
    """This table is used to store all available time slots for
    students to choose from for their PennChats meetings.
    There are two many to one relationships between this table and the WeeklySignUp table."""
    # how do we input data to this table?

    __tablename__ = 'time_options'

    time_id = db.Column(db.Integer, primary_key=True)
    time_option = db.Column(db.Text, nullable=False, unique=True)

    # many to one relationships
    prim_time_signups = db.relationship(
        'WeeklySignUp', foreign_keys='WeeklySignUp.prime_time_id', backref='prime_time')
    sec_time_signups = db.relationship(
        'WeeklySignUp', foreign_keys='WeeklySignUp.sec_time_id', backref='sec_time')
    meetings = db.relationship('Meeting', backref='meet_time')

    def __init__(self, time_option):
        self.time_option = time_option

    def __repr__(self):
        return f"This is the time option of {self.time_option} with the time ID of {self.time_id}."


class NetworkingGoal(db.Model):
    """This table is used to store the all networking goals for
    students to choose from for their PennChats meetings.
    Currently contains only two goals: match by class, match by interest.
    There are two many to one relationships between this table and the WeeklySignUp table."""
    # how do we input data to this table?

    __tablename__ = 'networking_goals'

    networking_goal_id = db.Column(db.Integer, primary_key=True)
    networking_goal = db.Column(db.Text, nullable=False, unique=True)

    # many to one relationships
    # calling WeeklySignUp.prime_goal will refer to the primary goal associated with the form
    prim_goal_signups = db.relationship(
        'WeeklySignUp', foreign_keys='WeeklySignUp.prime_networking_goal_id', backref='prime_goal')
    # calling WeeklySignUp.sec_goal will refer to the secondary goal preference associated with the form
    sec_goal_signups = db.relationship(
        'WeeklySignUp', foreign_keys='WeeklySignUp.sec_networking_goal_id', backref='sec_goal')

    def __init__(self, networking_goal):
        self.networking_goal = networking_goal

    def __repr__(self):
        return f"This is the networking goal of {self.networking_goal} with the ID of {self.networking_goal_id}."


class Meeting(db.Model):
    """This table describes all the meetings that has been set up.
    A final output of the matching algorithm will be a list of Meeting objects.
    There is a many-to-many relationship between this table and the Student table."""
    # how do we input data to this table?

    __tablename__ = 'meetings'

    meeting_id = db.Column(db.Integer, primary_key=True)

    # one to many relationships
    meeting_week_name = db.Column(db.Text, db.ForeignKey(
        'meeting_weeks.week_meet_name'), nullable=False)
    time_id = db.Column(db.Integer, db.ForeignKey(
        'time_options.time_id'), nullable=False)

    # one to many relationships to be added
    course_id = db.Column(db.Integer)
    interest_id = db.Column(db.Integer)

    def __init__(self, meeting_week_name, time_id, course_id=None, interest_id=None):
        self.meeting_week_name = meeting_week_name
        self.time_id = time_id
        self.course_id = course_id
        self.interest_id = interest_id

    def __repr__(self):
        return f"Meeting instance. ID: {self.meeting_id}, meeting week: {self.meeting_week_name}, time_id: {self.time_id}, associated students: {self.students}."


# many to many association table
groupings = db.Table('groupings',
                     db.Column('student_id', db.Integer, db.ForeignKey(
                         'students.student_id'), primary_key=True),
                     db.Column('meeting_id', db.Integer, db.ForeignKey(
                         'meetings.meeting_id'), primary_key=True)
                     )


class UnmatchedStudents(db.Model):
    """This table records all the students who were not able to be matched.
    A final output of the matching algorithm will be a list of UnmatchedStudnets
    objects."""

    __tablename__ = 'unmatched_students'

    student_id = db.Column(db.Integer, primary_key=True, unique=True)
    
    # might be able to get rid of these three fields and replace with filter calls for student_id
    # email = db.Column(db.String(64), index=True, unique=True, nullable=False)
    # first_name = db.Column(db.Text)
    # last_name = db.Column(db.Text)

    # one to many relationship
    meeting_week_name = db.Column(db.Text, db.ForeignKey(
        'meeting_weeks.week_meet_name'), nullable=False)

    def __init__(self, meeting_week_name, student_id):
        self.meeting_week_name = meeting_week_name
        self.student_id = student_id

    def __repr__(self):
        return f"Unmatched student: {self.first_name} {self.last_name}, {self.student_id}, and {self.email}. Unmatched week: {self.meeting_week_name}"
