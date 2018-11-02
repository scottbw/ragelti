import settings
import requests
import json


class Rage:

    def __init__(self):
        pass

    the_token = None
    the_class = None
    the_student = None
    the_activity = None

    def setup_activity(self, class_name):
        self.get_or_create_class(class_name)
        self.get_or_create_activity()

    def get_api_url(self):
        return settings.RAGE_GAME_HOST.split('api')[0]+'api'

    def login(self, username, password):

        url = self.get_api_url() + '/login'
        data = {'username': username, 'password': password}
        result = requests.post(url, json=data).json()

        self.the_token = 'Bearer ' + result['user']['token']

    def get_or_create_class(self, class_name):
        """
        Using the given class name from LTI, see if a class exists already. If not, create it.
        :param class_name:
        :return: the class id
        """
        classes = self.get_classes()
        for aclass in classes:
            name = aclass['name']
            if name == class_name:
                self.the_class = aclass
                print('Class exists already')
                return False

        url = self.get_api_url() + '/proxy/gleaner/classes'
        data = {'name': class_name}
        result = requests.post(url, json=data, headers={"Authorization": self.the_token}).json()
        self.the_class = result
        print('Creating a new class')
        return True

    def get_classes(self):
        url = self.get_api_url() + '/proxy/gleaner/classes/my'
        result = requests.get(url, headers={"Authorization": self.the_token}).json()
        return result

    def get_or_create_activity(self):
        """Get the activities for the class; if we don't have one, add it"""

        # Request URL: /api/proxy/gleaner/activities?gameId=5bcedeb32a99fd008a9fedb1&versionId=5bcedeb32a99fd008a9fedb2
        activities = self.get_activities()
        if len(activities) == 0:
            print("Creating an activity")
            data = {
                "name": "Rage LTI activity",
                "versionId":settings.RAGE_GAME_VERSION_ID,
                "classId": self.the_class['_id'],
                "gameId": settings.RAGE_GAME_ID,
                "offline": False
            }
            params = {
                "versionId": settings.RAGE_GAME_VERSION_ID,
                "gameId": settings.RAGE_GAME_ID
            }
            url = self.get_api_url() + "/proxy/gleaner/activities"
            response = requests.post(url, json=data, params=params, headers={"Authorization": self.the_token}).json()
            self.the_activity = response

            # Start the activity
            print("Starting the activity")
            url = self.get_api_url() + "/proxy/gleaner/activities/"+self.the_activity["_id"]+'/event/start'
            response = requests.post(url, headers={"Authorization": self.the_token}).json()
        else:
            print("Activity exists already")
            self.the_activity = activities[0]

    def get_activities(self):
        """Get the activities for the class; if we don't have one, add it"""
        url = self.get_api_url() + '/proxy/gleaner/classes/' + self.the_class['_id'] + '/activities/my'
        return requests.get(url, headers={"Authorization": self.the_token}).json()

    def add_student(self, student_id, student_email_address):
        """Add the student to the activity"""
        for student in self.the_activity['students']:
            if student == student_id:
                print("student already added")
                return False

        """Create a student login"""
        print("Creating a student account")
        url = self.get_api_url()+'/signup/massive'
        data = {
            "users":
                [{"username": student_id, "password": settings.RAGE_DEFAULT_STUDENT_PASSWORD, "email": student_email_address}]
        }
        result = requests.post(url, json=data, headers={"Authorization": self.the_token}).json()
        print(result)

        """Add the student to the activity"""
        url = self.get_api_url() + '/proxy/gleaner/activities/'+self.the_activity['_id']
        data = {"students":student_id}
        requests.put(url, json=data, headers={"Authorization": self.the_token}).json()
        print("add student: "+student_id + ' to activity '+self.the_activity['_id'])

    def get_results(self):

        index = self.the_activity["versionId"]

        with open('elastic_templates/xapi_verbs.json') as json_data:
            xapi_verbs_query = json_data.read()
            json_data.close()

        with open('elastic_templates/completed.json') as json_data:
            completed_query = json_data.read()
            json_data.close()

        with open('elastic_templates/skip_cutscene.json') as json_data:
            cutscene_query = json_data.read()
            json_data.close()

        with open('elastic_templates/total_students.json') as json_data:
            total_students_query = json_data.read()
            json_data.close()

        xapi_verbs_query = xapi_verbs_query.replace("{{index}}", index)
        completed_query = completed_query.replace("{{index}}", index)
        cutscene_query = cutscene_query.replace("{{index}}", index)
        total_students_query = total_students_query.replace("{{index}}", index)

        url = self.get_api_url() + '/proxy/kibana/elasticsearch/_msearch'

        xapi_verbs = requests.post(url, data=xapi_verbs_query, headers={"Authorization": self.the_token, "kbn-xsrf": "reporting"})\
            .json()["responses"][0]["aggregations"]["xapi"]["buckets"]

        completed = requests.post(url, data=completed_query, headers={"Authorization": self.the_token, "kbn-xsrf": "reporting"})\
            .json()["responses"][0]["aggregations"]["completed_items"]["buckets"]

        cutscene = requests.post(url, data=cutscene_query, headers={"Authorization": self.the_token, "kbn-xsrf": "reporting"})\
            .json()["responses"][0]["aggregations"]["cutscene"]["buckets"]

        total_students = requests.post(url, data=total_students_query, headers={"Authorization": self.the_token, "kbn-xsrf": "reporting"})\
            .json()["responses"][0]["aggregations"]["all"]["value"]

        data = {'xapi_verbs': xapi_verbs, 'completed_items': completed, 'cutscene_seen_skipped': cutscene, 'total_students': total_students}

        return data
