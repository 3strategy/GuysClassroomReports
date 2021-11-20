#started from https://github.com/googleworkspace/python-samples/tree/master/classroom/snippets
# https://issuetracker.google.com/issues/130443624?pli=1
# The issue above is about the missing feature (getting grades with rubric details).
from __future__ import print_function
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from classroomsnippets import *

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/classroom.courses.readonly',
     'https://www.googleapis.com/auth/classroom.rosters.readonly',
     'https://www.googleapis.com/auth/classroom.profile.emails',
     'https://www.googleapis.com/auth/classroom.student-submissions.students.readonly']

def main():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time. (stored in project's directory)
    if os.path.exists('token.json'):
        #x=os.path.realpath('token.json')
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())


    service = build('classroom', 'v1', credentials=creds)

    cs = ClassroomSnippets(service)
    course = cs.get_course(319934191831) #using the functions in the snippets.
    print(course['name'])
    #res = service.courses().courseWork().list(courseId=319934191831).execute()
    #test 30/9: '400863422243'
    res2 = cs.list_submissions(319934191831,400863422243) #using the functions in the snippets.
    res3 = service.courses().courseWork().studentSubmissions().list(courseId=319934191831,courseWorkId=400863422243).execute()
    #res3 will contain all grades but not rubric breakdown.
    results = service.courses().list(pageSize=10).execute()
    courses = results.get('courses', [])

    if not courses:
       print('No courses found.')
    else:
       print('Courses:')
       for course in courses:
           print(course['name'], course['id'])

if __name__ == '__main__':
    main()
