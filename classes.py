from requests import post, get
from json import loads, dumps
from io import BytesIO
from pydub import AudioSegment
from functions import decoder
from ldap import initialize, OPT_REFERRALS, SCOPE_SUBTREE

class Asterix():
	def __init__(self):
		self.name = "XXXXX"
		self.password = "XXXXX"
		self.login = "XXXXX"
		self.headers = {'Content-type': 'application/json', 'charset': 'utf-8'}
		self.login_in()

	def login_in(self):
	    r = post(url="{}/api/v1.1.0/login".format(self.login),
	                      json={'username': self.name, 'password': self.password,
	                            'port': '8260'}, headers=self.headers)
	    connection = loads(r.text)
	    if "token" in connection:
	    	self.token = connection["token"]
	    else:
	    	self.token = False

	def logout(self):
	    r = post(url="{}/api/v1.1.0/logout?token={}".format(self.login,self.token),
	                      headers=self.headers)
	    if "Success" in r.text:
	        self.token = False
	    else:
	    	print("Logout failed")

	def get_string(self, times):
	    if(self.token):
	        r = post(url="{}/api/v1.1.0/cdr/get_random?token={}".format(self.login,self.token),
	                          json={
	                                    'extid': 'all',
	                                    'starttime': times[0],
	                                    'endtime': times[1]
	                                },
	                          headers=self.headers)
	        connection = loads(r.text)
	        if "random" in connection:
	            return self.download(connection["random"], times)
	    return False

	def download(self, random, times):
	    url = "{}/api/v1.1.0/cdr/download?extid=all&starttime={}&endtime={}&token={}&random={}".format(self.login, times[0], times[1], self.token, random)
	    myfile = get(url)
	    if "errno" not in myfile.text:
	    	return myfile.text

	def get_wav(self, name):
		r = post(url="{}/api/v1.1.0/recording/get_random?token={}".format(self.login, self.token), json={'recording': name}, headers=self.headers)
		connection = loads(r.text)
		url = "{}/api/v1.1.0/recording/download?recording={}&random={}&token={}".format(self.login, name, connection["random"], self.token)
		file_bytes = BytesIO(get(url).content)
		export = BytesIO()
		AudioSegment.from_file(file_bytes).export(export, format='mp3')
		return export

class OsTicket():
	def __init__(self):
		self.password = "XXXXX"
		self.login = "XXXXX"
	def post_ticket(self, data):
		header = {'X-API-Key': self.password}
		response = post(self.login, data=dumps(data), headers=header)
		return response.text

class LDAP():
	def __init__(self):
		self.server = "XXXXX"

	def search(self, number):
	    connect = initialize('ldap://' + self.server)
	    connect.set_option(OPT_REFERRALS, 0)
	    connect.simple_bind_s()
	    result = connect.search_s('dc=okall', SCOPE_SUBTREE,
	                              'mobile={}'.format(number), ['givenName', 'sn', 'mail'])
	    if not result:
	        result = connect.search_s('dc=okall', SCOPE_SUBTREE,
	                                     'mobile='+"+420"+number, ['givenName', 'sn', 'mail'])
	    if result:
	        return decoder(result[0][1]["sn"]) + " " + decoder(result[0][1]["givenName"]), decoder(result[0][1]["mail"])
	    return ("Neznámý volající", "nezami@kontakt.com")