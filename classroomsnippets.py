from __future__ import print_function
from googleapiclient import errors

class CourseWork():
    def __init__(self,id,name,date):
      self.id=id
      self.name=name
      self.date=date
    def __repr__(self):
        return f'{self.id}, {self.name[:10]}, {self.date}'


class Student():
    def __init__(self, id, name, familyName, sEnglishName='NA'):
      self.id=id
      self.name=name
      self.familyName = familyName
      self.sName=sEnglishName
      self.courseWork={}
      self.studentHwAvg=0
    def __repr__(self):
        if self.sName == 'NA':
            return f'{self.familyName}, {self.name}, HW: {self.studentHwAvg}%'
        else:
            return f'{self.familyName}, {self.sName}, {self.name}, HW: {self.studentHwAvg}%'


class ClassroomSnippets(object):
    def __init__(self, service):
        self.service = service

    def create_course(self):
        """ Creates a single Classroom course. """
        service = self.service
        # [START classroom_create_course]
        course = {
            'name': '10th Grade Biology',
            'section': 'Period 2',
            'descriptionHeading': 'Welcome to 10th Grade Biology',
            'description': """We'll be learning about about the
                         structure of living creatures from a
                         combination of textbooks, guest lectures,
                         and lab work. Expect to be excited!""",
            'room': '301',
            'ownerId': 'me',
            'courseState': 'PROVISIONED'
        }
        course = service.courses().create(body=course).execute()
        print('Course created: %s %s' % (course.get('name'), course.get('id')))
        # [END classroom_create_course]
        return course

    def get_course(self, course_id):
        """ Retrieves a classroom course by its id. """
        service = self.service
        # [START classroom_get_course]
        try:
            course = service.courses().get(id=course_id).execute()
            print('Course "{%s}" found.' % course.get('name'))
        except errors.HttpError as error:
            print('Course with ID "{%s}" not found.' % course_id)
        # [END classroom_get_course]
            return error
        return course

    def list_courses(self):
        """ Lists all classroom courses. """
        service = self.service
        # [START classroom_list_courses]
        courses = []
        page_token = None

        while True:
            response = service.courses().list(pageToken=page_token,
                                              pageSize=100).execute()
            courses.extend(response.get('courses', []))
            page_token = response.get('nextPageToken', None)
            if not page_token:
                break

        if not courses:
            print('No courses found.')
        else:
            print('Courses:')
            for course in courses:
                print(course.get('name'), course.get('id'))
        # [END classroom_list_courses]

    def update_course(self, course_id):
        """ Updates the section and room of Google Classroom. """
        service = self.service
        # [START classroom_update_course]
        course = service.courses().get(id=course_id).execute()
        course['section'] = 'Period 3'
        course['room'] = '302'
        course = service.courses().update(id=course_id, body=course).execute()
        print('Course %s updated.' % course.get('name'))
        # [END classroom_update_course]

    def patch_course(self, course_id):
        """ Creates a course with alias specification. """
        service = self.service
        # [START classroom_patch_course]
        course = {
            'section': 'Period 3',
            'room': '302'
        }
        course = service.courses().patch(id=course_id,
                                         updateMask='section,room',
                                         body=course).execute()
        print('Course "%s" updated.' % course.get('name'))
        # [END classroom_patch_course]

    def add_alias_new(self):
        """ Creates a course with alias specification. """
        service = self.service
        # [START classroom_new_alias]
        alias = 'd:school_math_101'
        course = {
            'id': alias,
            'name': 'Math 101',
            'section': 'Period 2',
            'description': 'Course Description',
            'room': '301',
            'ownerId': 'me'
        }
        try:
            course = service.courses().create(
                body=course).execute()
        except errors.HttpError:
            print('Course Creation Failed')
        # [END classroom_new_alias]

    def add_alias_existing(self, course_id):
        """ Adds alias to existing course. """
        service = self.service
        # [START classroom_existing_alias]
        alias = 'd:school_math_101'
        course_alias = {
            'alias': alias
        }
        try:
            course_alias = service.courses().aliases().create(
                courseId=course_id,
                body=course_alias).execute()
        except errors.HttpError:
            print('Alias Creation Failed')
        # [END classroom_existing_alias]

    def add_teacher(self, course_id):
        """ Adds a teacher to a course. """
        service = self.service
        # [START classroom_add_teacher]
        teacher_email = 'alice@example.edu'
        teacher = {
            'userId': teacher_email
        }
        try:
            teachers = service.courses().teachers()
            teacher = teachers.create(courseId=course_id,
                                      body=teacher).execute()
            print('User %s was added as a teacher to the course with ID %s'
                  % (teacher.get('profile').get('name').get('fullName'),
                     course_id))
        except errors.HttpError as error:
            print('User "{%s}" is already a member of this course.'
                  % teacher_email)
        # [END classroom_add_teacher]
            return error
        return teachers

    def add_student(self, course_id):
        """ Adds a student to a course. """
        service = self.service
        # [START classroom_add_student]
        enrollment_code = 'abcdef'
        student = {
            'userId': 'me'
        }
        try:
            student = service.courses().students().create(
                courseId=course_id,
                enrollmentCode=enrollment_code,
                body=student).execute()
            print(
                '''User {%s} was enrolled as a student in
                   the course with ID "{%s}"'''
                % (student.get('profile').get('name').get('fullName'),
                   course_id))
        except errors.HttpError as error:
            print('You are already a member of this course.')
        # [END classroom_add_student]
            return error
        return student

    def create_coursework(self, course_id):
        """ Creates a coursework. """
        service = self.service
        # [START classroom_create_coursework]
        coursework = {
            'title': 'Ant colonies',
            'description': '''Read the article about ant colonies
                              and complete the quiz.''',
            'materials': [
                {'link': {'url': 'http://example.com/ant-colonies'}},
                {'link': {'url': 'http://example.com/ant-quiz'}}
            ],
            'workType': 'ASSIGNMENT',
            'state': 'PUBLISHED',
        }
        coursework = service.courses().courseWork().create(
            courseId=course_id, body=coursework).execute()
        print('Assignment created with ID {%s}' % coursework.get('id'))
        # [END classroom_create_coursework]

    def list_submissions(self, course_id, coursework_id):
        """ Lists all student submissions for a given coursework. """
        service = self.service
        # [START classroom_list_submissions]
        submissions = []
        page_token = None

        while True:
            coursework = service.courses().courseWork()
            response = coursework.studentSubmissions().list(
                pageToken=page_token,
                courseId=course_id,
                courseWorkId=coursework_id,
                pageSize=10).execute()
            submissions.extend(response.get('studentSubmissions', []))
            page_token = response.get('nextPageToken', None)
            if not page_token:
                break

        if not submissions:
            print('No student submissions found.')
        else:
            print('Student Submissions:')
            for submission in submissions:
                print(f'{submission.get("id")}  at {submission.get("creationTime")} by {submission.get("userId")} : {submission.get("state")}  got {submission.get("draftGrade")}')
            return submissions
        # [END classroom_list_submissions]

    def list_student_submissions(self, course_id, coursework_id, user_id):
        """ Lists all coursework submissions for a given student. """
        service = self.service
        # [START classroom_list_student_submissions]
        submissions = []
        page_token = None

        while True:
            coursework = service.courses().courseWork()
            response = coursework.studentSubmissions().list(
                pageToken=page_token,
                courseId=course_id,
                courseWorkId=coursework_id,
                userId=user_id).execute()
            submissions.extend(response.get('studentSubmissions', []))
            page_token = response.get('nextPageToken', None)
            if not page_token:
                break

        if not submissions:
            print('No student submissions found.')
        else:
            print('Student Submissions:')
            for submission in submissions:
                print("%s was submitted at %s" %
                      (submission.get('id'),
                       submission.get('creationTime')))
            return submissions
        # [END classroom_list_student_submissions]


    def list_all_submissions(self, course_id, user_id, debug=False):
        """ Lists all coursework submissions for a given student. """
        service = self.service
        # [START classroom_list_submissions]
        submissions = []
        page_token = None

        while True:
            coursework = service.courses().courseWork()
            response = coursework.studentSubmissions().list(
                pageToken=page_token,
                courseId=course_id,
                courseWorkId="-",
                userId=user_id).execute()
            submissions.extend(response.get('studentSubmissions', []))
            page_token = response.get('nextPageToken', None)
            if not page_token:
                break

        if not submissions:
            print('No student submissions found.')
        else:
            if debug:
                print('Complete list of student Submissions:')
                for submission in submissions:
                    #print("%s was submitted at %s" %
                    #      (submission.get('id'),
                    #       submission.get('creationTime')))
                    print(
                        f'{submission.get("id")} {submission.get("courseWorkId")} at {submission.get("creationTime")} by {submission.get("userId")} : {submission.get("state")}  got {submission.get("draftGrade")}')
            return submissions
        # [END classroom_list_submissions]

    def add_attachment(self, course_id, coursework_id, submission_id):
        """ Adds an attachment to a student submission. """
        service = self.service
        # [START classroom_add_attachment]
        request = {
            'addAttachments': [
                {'link': {'url': 'http://example.com/quiz-results'}},
                {'link': {'url': 'http://example.com/quiz-reading'}}
            ]
        }
        coursework = service.courses().courseWork()
        coursework.studentSubmissions().modifyAttachments(
            courseId=course_id,
            courseWorkId=coursework_id,
            id=submission_id,
            body=request).execute()
        # [END classroom_add_attachment]

    def invite_guardian(self):
        """ Send an invite to a guardian. """
        service = self.service
        # [START classroom_add_attachment]
        guardian_invitation = {
            'invitedEmailAddress': 'guardian@gmail.com',
        }
        guardian_invitations = service.userProfiles().guardianInvitations()
        guardian_invitation = guardian_invitations.create(
            # You can use a user ID or an email address.
            studentId='student@mydomain.edu',
            body=guardian_invitation).execute()
        print("Invitation created with id: {%s}"
              % guardian_invitation.get('invitationId'))

    def list_students(self,course_id,debug=False):
        """ Lists all students in a course. """
        service = self.service
        # [START classroom_list_submissions]
        students = []
        page_token = None

        while True:
            courses = service.courses()
            response = courses.students().list(
                pageToken=page_token,
                courseId=course_id).execute()
            students.extend(response.get('students', []))
            page_token = response.get('nextPageToken', None)
            if not page_token:
                break
        if debug:
            for x in students:
                print(x)
        return students