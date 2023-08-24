from locust import HttpUser,SequentialTaskSet,task,constant,events
from locust.exception import StopUser
from client_end_script_helper import test_host,read_config
from credentials import *
from Answers import *
from CourseCode import coursecode
from TestName import quizid
from locust import HttpUser,SequentialTaskSet,task,constant,log
import re
import datetime
# from locust.exception import StopUser

test_id,num_user=read_config()
# url = "sys_perf_check/"+test_id+"/"+num_user+"/"
class PerfCheck(SequentialTaskSet):
    def __init__(self,parent):
        super().__init__(parent)
        self.codeid = quizid
        print("this test is being conducted for the quiz " + self.codeid)
        self.email,self.password=USER_CREDENTIALS.pop()

    @task
    def perf_check(self):
        url = "sys_perf_check/"+test_id+"/"+num_user+"/"
        print(url)
        # with self.client.get(url,name="perf_check",catch_response=True,verify=False) as response:
        with self.client.get(url,name="perf_check",catch_response=True,verify=False) as response:
            print("perf_check:",response.text)
            
            
    @task
    def login(self):
        #PasscodeBasedLogin
        #self.email,self.password=USER_CREDENTIALS.pop()
        self.client.cookies.clear()
        url="api/account/login/"
        data={
            "email_id":self.email,"passcode":self.password
        }
        with self.client.post(url,name="SignInAttempt",data=data,catch_response=True) as response:
            self.csrftoken = response.cookies['csrftoken']
            print("login:",response)

    @task
    def course_list(self):
        #CourseListView
        url ="api/course/"
        with self.client.get(url,name="course_list",catch_response=True) as response:
            print("course_list:",response)
            self.code = coursecode


    @task
    def quiz_list(self):
        #DownloadableQuizzesListView
        url = "api/quiz/"+ self.code + "/downloadable-quizzes/"
        with self.client.get(url,name="quiz_list",catch_response=True) as response:
            print("quiz_list:",response)

    @task
    def quiz_info(self):
        #DownloadQuizInfoView
        url = "api/quiz/"+ self.codeid + "/info/"
        with self.client.get(url,name="quiz_info",catch_response=True) as response:
            print(url)
            print(response.text)
            quiz_keystate = re.search(r"\"keystate\":(.*?)(,|})",response.text)
            self.quiz_keystate= quiz_keystate.group(1)[1:-1] #.encode('ascii')
            print("quiz_info:",response)
            print(response.text)
            
    @task
    def quiz_download(self):
        #QuizDownloadView
        url = "api/quiz/"+ self.codeid + "/download/"
        with self.client.get(url,name="quiz_download",catch_response=True) as response:
            print("quiz_download:",response)

    @task
    def quiz_authenticate(self):
        #QuizAuthenticateView
        url = "api/quiz/"+ self.codeid + "/authenticate/"
        with self.client.get(url,name="quiz_authenticate",catch_response=True) as response:
            print("quiz_authenticate:",response)
            print(response.text)
    # @task
    # def safe_image_upload(self):
    #     url = "api/quiz/uploadImage/"
    #     # attach = open('low.jpg', 'rb')
    #     attach = open('mid.jpg', 'rb')
    #     # attach = open('high.jpg', 'rb')
    #     with self.client.post(url, name="Image Upload", files=dict(ansimage=attach), headers={"X-CSRFToken": self.csrftoken}, catch_response=True) as response:
    #         print(url+"done")

    @task
    def quiz_submit(self):
            #QuestionSubmissionView
            datetime_format = "%Y-%m-%dT%H:%M:%S"
            url = "api/quiz/"+self.quiz_keystate + "/submit/"
            data ={
                "quizData":answers,"submissionTime":datetime.datetime.now().strftime(datetime_format),"seconds_since_mark":"0"
            }
            with self.client.post(url,name="Submit",json=data,headers={"X-CSRFToken": self.csrftoken},catch_response=True) as response:
                print("quiz_submit:",response)

    # @task
    # def on_stop(self):
    #     raise StopUser()


class MySeqTest(HttpUser):
    # fixed_count=1
    wait_time=constant(1)
    host =test_host
    tasks = [PerfCheck]

