import settings
import requests


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
        activities = self.get_activities()
        if len(activities) == 0:
            print("Creating an activity")
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
        # TODO need to figure out where we get this index from, possibly its the game session?
        url = self.get_api_url() + '/proxy/gleaner/kibana/visualization/list/dev/5bcedeb32a99fd008a9fedb1'
        headings = requests.get(url, headers={"Authorization": self.the_token, "kbn-xsrf": "reporting"}).json()

        # TODO this is currently fixed as '5bcedeb32a99fd008a9fedb2'; need to inject the real index values for the current game/class here
        with open('query.json') as json_data:
            query = json_data.read()
            json_data.close()

        url = self.get_api_url() + '/proxy/kibana/elasticsearch/_msearch'
        result = requests.post(url, data=query, headers={"Authorization": self.the_token, "kbn-xsrf": "reporting"}).json()
        responses = result["responses"]

        data = []
        for index in range(len(responses)):
            data_item = {}
            data_item["name"] = headings[index]
            aggregation = responses[index]["aggregations"]

            data_item["data"] = aggregation[list(aggregation.keys())[0]]
            data.append(data_item)

        return data
