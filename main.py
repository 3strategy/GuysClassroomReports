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
import datetime
# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/classroom.courses.readonly',
     'https://www.googleapis.com/auth/classroom.rosters.readonly',
     'https://www.googleapis.com/auth/classroom.profile.emails',
     'https://www.googleapis.com/auth/classroom.student-submissions.students.readonly']
class CourseWork():
    def __init__(self,id,name,date):
      self.id=id
      self.name=name
      self.date=date
    def __repr__(self):
        return f'{self.id}, {self.name[:10]}, {self.date}'

class Student():
    def __init__(self,id,name,nickName):
      self.id=id
      self.name=name
      self.nickName=nickName
    def __repr__(self):
        return f'{self.id}, {self.name}, {self.nickName}'

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
    print('gs13',course['name'])
    res = service.courses().courseWork().list(courseId=319934191831).execute()
    courseWorkDict = dict()

    # go through works, and collect them to a dictionary with names and dates.
    for c in res['courseWork']: # הדפסת רשימת המטלות
        #print(c['id'], c['title']) # הדפסת רשימת המטלות
        id = c['id']
        if 'dueDate' in c:  # checks if "item" is a *key* in the dict "functionTable"
            date = datetime.datetime(c['dueDate']['year'], c['dueDate']['month'], c['dueDate']['day'])   # store the *value* for the *key* "item"
        else:
            d = c['creationTime'][:10].split('-')
            date = datetime.datetime(int(d[0]),int(d[1]),int(d[2]))
        if date>datetime.datetime(2022,1,20):
            wrk = CourseWork(id, c['title'], date)
            courseWorkDict[id]=wrk
    print('\nCounted works in dict:',len(courseWorkDict))

    #test 30/9: '400863422243' #looking at specific submission of a work by a student
    for hagasha in []:#[448006770517 ,467869743253]:# these are 1430, 1520, 468340104676]:
        res2 = cs.list_submissions(319934191831,hagasha) #using the functions in the snippets.
        print('gilads submissions for specific hagashot')
        for r in res2:
            if r['userId'] == '109281564654077610155': # gilad
                print(len(r['assignmentSubmission']['attachments']))
                print(r)
                print(r)
        print()

    for userid in ['109281564654077610155']:
        res4 = cs.list_all_submissions(319934191831,109281564654077610155,False)
        stdWorkSubs= {}
        for s in res4:
            id = s['courseWorkId']
            if id in courseWorkDict:
                stdWorkSubs[id]=s['state']
                #print('gilads',s)
        #print('\nworks submitted', len(stdWorkSubs))
        countStdSubmissions = 0
        for s in stdWorkSubs:
            state = stdWorkSubs[s]
            #print(courseWorkDict[s],'gilad:',state)
            if state != "CREATED":
                countStdSubmissions+=1

        print(f'Gilad submitions {countStdSubmissions}/{(len(stdWorkSubs)-3)}')
    # res3 = service.courses().courseWork().studentSubmissions().list(courseId=319934191831,courseWorkId=400863422243).execute()
    # #res3 will contain all grades but not rubric breakdown.
    # results = service.courses().list(pageSize=10).execute()
    # courses = results.get('courses', [])
    #
    # if not courses:
    #    print('No courses found.')
    # else:
    #    print('Courses:')
    #    for course in courses:
    #        print(course['name'], course['id'])

if __name__ == '__main__':
    main()
