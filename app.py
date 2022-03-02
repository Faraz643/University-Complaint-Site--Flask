from flask import Flask, render_template, request, redirect, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, UserMixin, logout_user, current_user, login_required
from datetime import datetime
from flask_user import roles_required, roles_accepted, UserManager, UserMixin
from flask_bcrypt import Bcrypt, generate_password_hash, check_password_hash
from sqlalchemy import desc, nulls_last, asc


app = Flask(__name__)
bcrypt = Bcrypt(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///iulrecord.db'
app.secret_key = 'j2q908jhhgd334@1i!j#dwq'
login_manager = LoginManager()
login_manager.init_app(app)
db = SQLAlchemy(app)
app.config['USER_ENABLE_EMAIL'] = False

# Models Here:


# Primary table to store all Users
class User(db.Model, UserMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), unique=False)
    enrollment_id = db.Column(db.Integer(), unique=True, nullable=True)
    password = db.Column(db.String(50), unique=False, nullable=True)
    roles = db.relationship('Role', secondary='user_roles')
    teacher_notice = db.relationship('Notice', backref='teacher_notice', lazy=True)
    teacher_following_student = db.relationship('Student', backref='teacher_user', lazy=True)
    posts = db.relationship('Complaints', backref='student_complaint_main_id', lazy=True)


# Stores the name(or type) of Roles
class Role(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), unique=False)


# Association Table, Defines which User relates to which Role
class UserRoles(db.Model):
    __tablename__ = 'user_roles'

    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer(), db.ForeignKey('role.id', ondelete='CASCADE'))


# This is a special Student table, only to store the name and , which student relates to which teacher, in
# short , it stores Foreign Key of teacher
class Student(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    student_name = db.Column(db.String(80))
    enrollment_id = db.Column(db.Integer(), unique=True, nullable=True)
    teacher_id = db.Column(db.Integer(), db.ForeignKey('user.id'))
    teacher_name = db.Column(db.String(50), nullable=False)
    student_complaint = db.relationship('Complaints', backref='student_complaint', lazy=True)


# To store complaints of students
class Complaints(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    date = db.Column(db.DateTime(), default=datetime.utcnow)
    title = db.Column(db.String(80))
    description = db.Column(db.String(200))
    feedback = db.Column(db.String(500), unique=False)
    student_id = db.Column(db.Integer(), db.ForeignKey('student.id'))
    student_name = db.Column(db.String(50), nullable=False)
    student_main_id = db.Column(db.Integer(), db.ForeignKey('user.id'))


# To store Notice of teacher
class Notice(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    date = db.Column(db.DateTime(), default=datetime.utcnow)
    title = db.Column(db.String(80))
    description = db.Column(db.String(200))
    teacher_id = db.Column(db.Integer(), db.ForeignKey('user.id'))
    teacher_name = db.Column(db.String(50), nullable=False)


user_manager = UserManager(app, db, User)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/staff-login', methods=['GET', 'POST'])
def staff_login():
    if request.method == 'POST':
        staff_id = request.form.get('staff-id')
        staff_password = request.form.get('staff-password')
        user = User.query.filter_by(enrollment_id=staff_id).first()
        if user and bcrypt.check_password_hash(user.password, staff_password):
            login_user(user)
            return redirect('/staff-portal')
        else:
            flash('Invalid password', 'invalid-staff-details')
            return redirect('/staff-login')
    return render_template('staff-login-page.html')


# *
# These registration portals are used to enter user's data manually
# Only staff member is allowed to access these two routes to enter User details in record
@app.route('/staff-portal', methods=['POST', 'GET'])
def registration_portal():
    if current_user.is_anonymous:
        return render_template('index.html')
    if current_user.has_roles('Staff'):
        if request.method == 'POST':
            name = request.form.get('name')
            enrollment_id = request.form.get('enrollment_id')
            role = request.form.get('roletype')
            password = request.form.get('password')
            hashed = bcrypt.generate_password_hash(password).decode('utf-8')
            details = User(name=name, enrollment_id=enrollment_id, password=hashed)
            details.roles.append(Role(name=role))
            db.session.add(details)
            db.session.commit()
    else:
        logout_user()
        flash('Invalid details', 'invalid-staff-details')
        return redirect('/staff-login')
    return render_template('manual-registration.html')


# *
@app.route('/student-registration-portal', methods=['POST', 'GET'])
def student_portal():
    if current_user.has_roles('Staff'):
        if request.method == 'POST':
            student_name = request.form.get('name')
            enrollment_id = request.form.get('enrollment_id')
            teacher_id = request.form.get('teacher-id')
            teacher_name = request.form.get('teacher-name')
            user = User.query.filter_by(enrollment_id=teacher_id).first()
            user_id = user.id
            student = Student(student_name=student_name, enrollment_id=enrollment_id, teacher_id=user_id,
                              teacher_name=teacher_name)
            db.session.add(student)
            db.session.commit()
    else:
        return 'You Do Not Have Permission To Access This Page'
    return render_template('student-registration.html')


# Index page
@app.route('/')
def home():
    if current_user.is_anonymous:
        return render_template('index.html')
    if current_user.has_roles('Teacher'):
        return redirect('/teacher-dashboard')
    elif current_user.has_roles('Student'):
        return redirect('/student-dashboard')


# Student Functionality Starts From Here ->

# URL for student login
@app.route('/student-login', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect('/student-dashboard')
    if request.method == 'POST':
        student_enrollment_id = request.form.get('log_id')
        student_password = request.form.get('log_pass')
        student_user = User.query.filter_by(enrollment_id=student_enrollment_id).first()
        if student_user and bcrypt.check_password_hash(student_user.password, student_password):
            login_user(student_user)
            session['user'] = student_enrollment_id
            return redirect('/student-dashboard')
        else:
            flash('Invalid login details !', 'invalid-student-details')
            return redirect('/student-login')
    return render_template('student-login-page.html')


# URL for student dashboard
@app.route('/student-dashboard')
def admin():
    if current_user.is_anonymous:
        return render_template('index.html')
    if current_user.has_roles('Student'):
        complaints = current_user.posts
        return render_template('student-dashboard.html', complaints=complaints)
    else:
        logout_user()
        flash('Invalid login details !', 'invalid-student-details')
        return redirect('/student-login')


# URL for students to make complaints
@app.route('/write-complaint', methods=['GET', 'POST'])
def form():
    if current_user.is_anonymous:
        return render_template('index.html')
    if current_user.has_roles('Student'):
        if request.method == 'POST':
            complaint_title = request.form.get('Title')
            complaint_description = request.form.get('Description')
            c = current_user.enrollment_id
            b = Student.query.filter_by(enrollment_id=c).first()
            a = b.id
            complaint_data = Complaints(description=complaint_description, title=complaint_title, feedback=
                                        '𝘕𝘖 𝘙𝘌𝘚𝘗𝘖𝘕𝘚𝘌 𝘠𝘌𝘛 !', student_id=a, student_name=current_user.name,
                                        student_main_id=current_user.id)
            db.session.add(complaint_data)
            db.session.commit()
            flash('Complaint Posted !', 'complaint-success')
            return redirect('/student-dashboard')
    else:
        return 'You Do Not Have Permission To Access This Page'
    return render_template('student-complaint-form.html')


# URL to edit a complaint
@app.route('/edit-complaint/<int:id>', methods=['GET', 'POST'])
def edit_complaint(id):
    if current_user.is_anonymous:
        return render_template('index.html')
    edit_complaints = Complaints.query.get(id)
    if current_user.has_roles('Student'):
        if request.method == 'POST':
            edit_complaints.title = request.form.get('e-title')
            edit_complaints.description = request.form.get('e-description')
            db.session.commit()
            flash('Edited !', 'complaint-edit')
            return redirect('/student-dashboard')
    else:
        return 'You Do Not Have Permission To Access This Page'
    return render_template('edit-complaint.html', edit_complaints=edit_complaints)


# URL to delete a complaint
@app.route('/delete-complaint/<int:id>', methods=['GET', 'POST'])
def delete_complaint(id):
    if current_user.is_anonymous:
        return render_template('index.html')
    if current_user.has_roles('Student'):
        d_complaint = Complaints.query.get(id)
        db.session.delete(d_complaint)
        db.session.commit()
        flash('Complaint Deleted !', 'delete-success')
        return redirect('/student-dashboard')
    else:
        return 'You Do Not Have Permission To Access This Page'


# URL for Students to see teacher response
@app.route('/teacher-responses')
def response():
    if current_user.is_anonymous:
        return render_template('index.html')
    view_response = current_user.posts
    if current_user.has_roles('Student'):
        return render_template('view-response.html', view_response=view_response)
    else:
        return 'You Do Not Have Permission To Access This Page'


# URL for students to see notices
@app.route('/notice')
def view_notice_students():
    if current_user.is_anonymous:
        return render_template('index.html')
    show_notice_for_students = Notice.query.order_by(-Notice.id).all()
    if current_user.has_roles('Student'):
        return render_template('notice-for-students.html', show_notice_for_students=show_notice_for_students)
    else:
        return 'You Do Not Have Permission To Access This Page'


# Teacher Functionality Starts From Here ->

# URL for teacher login
@app.route('/teacher-login', methods=['POST', 'GET'])
def t_register():
    if current_user.is_authenticated:
        return redirect('/teacher-dashboard')
    if request.method == 'POST':
        teacher_enrollment_id = request.form.get('tlog_id')
        teacher_password = request.form.get('tlog_pass')
        teacher_user = User.query.filter_by(enrollment_id=teacher_enrollment_id).first()
        if teacher_user and bcrypt.check_password_hash(teacher_user.password, teacher_password):
            login_user(teacher_user)
            return redirect('/teacher-dashboard')
        else:
            flash('Invalid login details !', 'invalid-teacher-details')
            return redirect('/teacher-login')

    return render_template('teacher-login-page.html')


# URL for teacher dashboard
@app.route('/teacher-dashboard')
def t_admin():
    if current_user.is_anonymous:
        return render_template('index.html')
    if current_user.has_roles('Teacher'):
        # all_complaints = Complaints.query.all()
        extract = current_user.teacher_following_student
        complaint = Complaints
        uu = Complaints.query.order_by(Complaints.id)
        return render_template('teacher-dashboard.html', all_complaints=extract, complaint=complaint,
                               desc=desc(Complaints.date), uu=uu)
    else:
        logout_user()
        return redirect('/teacher-login')


# URL for teacher to give response and to view complaint
@app.route('/respond-to-complaint/<int:id>', methods=['GET', 'POST'])
def view_complaint(id):
    if current_user.is_anonymous:
        return render_template('index.html')
    complaint_data = Complaints.query.get(id)
    user_id = current_user.id
    if current_user.has_roles('Teacher'):
        if request.method == 'POST':
            teacher_response = request.form.get('teacherresponse')
            teacher_feedback = Complaints.query.filter_by(title=complaint_data.title).first()
            teacher_feedback.feedback = teacher_response
            db.session.commit()
            flash('!', 'category1')
            flash('Your response has been sent !', 'respond-complaint')
            return redirect('/teacher-dashboard')
    else:
        return 'You Do Not Have Permission To Access This Page'
    return render_template('view-complaints.html', complaint_data=complaint_data)


# URL for teacher to see their responses
@app.route('/your-responses')
def view_your_response():
    if current_user.is_anonymous:
        return render_template('index.html')
    # view_responses = Complaint.query.all()
    if current_user.has_roles('Teacher'):
        view_responses = Complaints.query.order_by(-Complaints.id).all()
        extract = current_user.teacher_following_student
        complaint = Complaints()
        return render_template('teacher-responses.html', complaint=complaint, all_complaints=extract,
                               view_responses=view_responses)
    elif current_user.has_roles('Student'):
        return 'You Do Not Have Permission To Access This Page'


# URL for teacher to make a notice
@app.route('/make-a-notice', methods=['GET', 'POST'])
def notice_form():
    if current_user.is_anonymous:
        return render_template('index.html')
    if current_user.has_roles('Teacher'):
        if request.method == 'POST':
            title_of_notice = request.form.get('Notice_title')
            description_of_notice = request.form.get('Notice_description')
            add_notice = Notice(title=title_of_notice, description=description_of_notice, teacher_id=current_user.id,
                                teacher_name=current_user.name)
            db.session.add(add_notice)
            db.session.commit()
            flash('!', 'category2')
            flash('Notice published !', 'notice-flash')
            return redirect('/teacher-dashboard')
    elif current_user.has_roles('Student'):
        return 'You Do Not Have Permission To Access This Page'
    return render_template('teacher-notice-form.html')


# URL for teacher to see their notices
@app.route('/your-notices')
def view_notice_teachers():
    if current_user.is_anonymous:
        return render_template('index.html')
    if current_user.has_roles('Teacher'):
        show_notice_for_teachers = Notice.query.order_by(-Notice.id).all()
        return render_template('teacher-notices.html', show_notice_for_teachers=show_notice_for_teachers)
    elif current_user.has_roles('Student'):
        return 'You Do Not Have Permission To Access This Page'


# Logout URL for users
@app.route('/logout')
def logout():
    logout_user()
    session.pop('user', None)
    return redirect('/')


@app.route('/about')
def about():
    return render_template('about.html')


if __name__ == '__main__':
    app.run(debug=True)