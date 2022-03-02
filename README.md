# University Complaint Website
## Introduction/Objective 
University Complaint is a website for teachers and students of the same univeristy where students can write complaints regarding their ongoing academic sessions and classes
and teachers can control, manage and give response(feedback) to students' complaints. 
The goal is to remove any barrier between a student and a teacher by which students can share their grievance to the teacher without any hesitation. 

## Sections/Elements

This project is divided into three parts. 
Mainly there are three types of user in the database and that is what I am calling sections here

##### Type of User:
1. Staff
2. Teacher
3. Student

``` Different functions of different Users :```

#### Staff

A staff is a role which works on feeding of the records of students and teachers. And assigns teacher on every student


1. Staff-records the details of a new teacher.
2. Staff-records the details of a student after taking admission in the college.
3. Staff-assigns teacher on every student and feeds it in the database.

#### Student

1. A student can write a complaint, edit a complaint, and can delete a complaint. [ Complete CRUD Functionality applies here]
2. Student can view the responses given by their teacher on the complaints.
3. Student can view notices, if any, published by any teacher.

#### Teacher

1. A teacher can view the complaints of only those students which are assigned to them.
2. Teacher can respond to complaints
3. Teacher can publish notices (here students can see every teacher's notices, keeping in mind that some notices might be important that must be seen by every student)

## Default User details for login ( for sake of testing)

|  NAME | ENROLLMENT ID | PASSWORD  |
| ------------- |:-------------:| -----:|
| Staff     |staff1         |  staff1   |
| Student 1 |student1       |  student1 |
| Student 2 |student2       |  student2 |
| Teacher 1 |Teacher1       |  Teacher1 |
| Teacher 2 |Teacher2       |  Teacher2 |


You can make more accounts by logging into staff portal and assigning roles to each user

## Technology Stack

```
Back-end:     Python - Flask Framework 
Front-end:    HTML, CSS, Bootstrap 
DataBase:     SQLAlchemy 
```

Some key features of back-end:

1. Password Hashing
2. Role based authorization
3. User Authentication


Interested in interacting with the GUI ?
Give it a try - https://iul-complaints.herokuapp.com/


As my main focus was on the back-end, I havn't applied my skills on front-end much. Some html and css templates 
I got from the internet which were free and legal to use, and did some modifications in them.


Sources :

[Registration Form HTML Template](https://www.codehim.com/demo/sign-in-and-sign-up-form-template/?)


[Registration Form CSS code](https://www.codehim.com/demo/sign-in-and-sign-up-form-template/style.css)

[Complaint and Notice Form](https://preview.colorlib.com/theme/bootstrap/contact-form-20/)

[About Page](https://fantacydesigns.com/about-us-page-design-in-html-and-css/)
