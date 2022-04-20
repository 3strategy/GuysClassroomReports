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
import jsonpickle
# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/classroom.courses.readonly',
     'https://www.googleapis.com/auth/classroom.rosters.readonly',
     'https://www.googleapis.com/auth/classroom.profile.emails',
     'https://www.googleapis.com/auth/classroom.student-submissions.students.readonly']

useNickNames = False # set to False if you don't want to manually define English nick Names

stdNames = dict([(107766054206145875440,'maayan'), (111172737869240566953,'nimrod'),(108168318660396843189,'guy'), \
                (112946615777025405797,'gal'),(110218538845151914929,'elad'),(109082288264554060697,'asaf'), \
                (106955666250273733477,'eden'),(112108709999563961515,'ilay'),(115710532509308023906,'lir'), \
                (112236029006376497710,'noam'),(109478865400455908580,'shani'),(118327441803103683622,'michal'), \
                (117889535936306448424,'rom'),(104580194319848892894,'tal'),(102005049826024063953,'itamar'), \
                (106552389423231110486,'naor'),(112690319777254745789,'yair'),(117090042331819769440,'mayaa'), \
                (106438875759955145463,'mayas'),(116461312202155079828,'yonatao'),(109281564654077610155,'gilad'), \
                (101718685423349384354,'yonatanal'),(102048010413141818326,'dana'),(109290410974718440223,'yonatanm')])

def nickFromId(id):
    if id in stdNames:
        return stdNames[id]
    return 'noNickForId'


def main():
    classID = 319934191831 # you need to find out what your class Id is.
    cutOffDate = (2022,1,20)   # count couseWork due after this date (or if no due date - work created after this date)
    global useNickNames
    # you must use the initial students console print to create a shortEnglish Name to ID mapping (as seen above)
    # without a shortname (english) it's impossible to use the outputs efficiently.
    # you may avoid this by setting useNickNames = False

    import pathlib
    p = pathlib.Path('studentsDict.json')
    if p.is_file():
        f = open('studentsDict.json', 'r')
        sdudentsDickFromBackup = jsonpickle.decode(f.read())  # later used to check for differnces (new submissions).
    else:
        print('\n********\nno backup file "studentsDict.json" available for comparison\n********')
        sdudentsDickFromBackup = None

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
    course = cs.get_course(classID) #using the functions in the snippets.
    print('gs13',course['name'])
    res = service.courses().courseWork().list(courseId=classID).execute()
    courseWorkDict = dict()

    stdtsRes= cs.list_students(classID,True)
    studentsDict={}
    studentsLst=[]
    for s in stdtsRes:
        id = int(s['userId'])
        if useNickNames:
            stdt= Student(id,s['profile']['name']['fullName'],s['profile']['name']['familyName'],nickFromId(id))
        else:
            stdt = Student(id, s['profile']['name']['fullName'], s['profile']['name']['familyName'])
        studentsDict[id]=(stdt)
        studentsLst.append(stdt)
    studentsLst.sort(key=lambda x: x.familyName)
    # go through works, and collect them to a dictionary with names and dates.
    for c in res['courseWork']: # הדפסת רשימת המטלות
        #print(c['id'], c['title']) # הדפסת רשימת המטלות
        id = c['id']
        if 'dueDate' in c:  # checks if "item" is a *key* in the dict "functionTable"
            date = datetime.datetime(c['dueDate']['year'], c['dueDate']['month'], c['dueDate']['day'])   # store the *value* for the *key* "item"
        else:
            d = c['creationTime'][:10].split('-')
            date = datetime.datetime(int(d[0]),int(d[1]),int(d[2]))
        if date>datetime.datetime(cutOffDate[0],cutOffDate[1],cutOffDate[2]):
            wrk = CourseWork(id, c['title'], date)
            courseWorkDict[id]=wrk
    print('\nCounted works in dict:',len(courseWorkDict))

    #test 30/9: '400863422243' #looking at specific submission of a work by a student
    # for hagasha in []:#[448006770517 ,467869743253]:# these are 1430, 1520, 468340104676]:
    #     res2 = cs.list_submissions(319934191831,hagasha) #using the functions in the snippets.
    #     print('gilads submissions for specific hagashot')
    #     for r in res2:
    #         if r['userId'] == '109281564654077610155': # gilad
    #             print(len(r['assignmentSubmission']['attachments']))
    #             print(r)
    #             print(r)
    #     print()

    for std in studentsLst: #['109281564654077610155']:
        res4 = cs.list_all_submissions(classID,std.id,False)
        stdWorkSubs= {}
        for s in res4:
            id = s['courseWorkId']
            if id in courseWorkDict:
                stdWorkSubs[id]=s['state']

        countStdSubmissions = 0
        for s in stdWorkSubs:
            state = stdWorkSubs[s]
            #print(courseWorkDict[s],'gilad:',state)
            if state != "CREATED":
                countStdSubmissions+=1
        std.studentHwAvg = int(round(100*countStdSubmissions / (len(stdWorkSubs) - 3)))
        print(f'{countStdSubmissions}/{(len(stdWorkSubs)-3)},\t{std}')

    # output sorted std list with HW submission rates to console
    print('\n\n Sorted averages:')
    for x in studentsLst:
      print (x)

    if sdudentsDickFromBackup != None:
        for x in studentsDict:
            oldAvg=sdudentsDickFromBackup[str(x)].studentHwAvg
            if studentsDict[x].studentHwAvg != oldAvg:
                print(studentsDict[x], f' ***changed*** from  {oldAvg} to {studentsDict[x].studentHwAvg}')

    # output JSON file for later comaprison between dates.
    jsonpickle.set_encoder_options('json', sort_keys=True, indent=2)
    with open(f"studentsDict.{datetime.date.today()}.json", "w") as outfile:
        outfile.write(jsonpickle.encode(studentsDict))
    with open(f"studentsDict.json", "w") as outfile:
        outfile.write(jsonpickle.encode(studentsDict))


if __name__ == '__main__':
    main()
