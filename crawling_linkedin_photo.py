try:
    from HTMLParser import HTMLParser
except ImportError:
    from html.parser import HTMLParser
import pprint
import json
import sys
import urllib
import requests
import time
from bs4 import BeautifulSoup

user_email = "nganhvu.gon@gmail.com"
user_password = "Vunguyen@jvn"
HOMEPAGE_URL = 'https://www.linkedin.com'
LOGIN_URL = 'https://www.linkedin.com/uas/login-submit'
BASED_ULR = "https://media.licdn.com/mpr/mpr/shrinknp_400_400"
PHOTO_PATH = "photo/"


def photo_parse(response_text,link_id):
	h = HTMLParser()
	soup = BeautifulSoup(response_text, 'html.parser')

	logfile = open('Log/image_log.txt', 'w')
	profilepic_string = ""
	for code in soup.find_all('img'):
	    code_str = code.get_text()
	    code_str = h.unescape(code_str)
	    code_str_list = code_str.split("\n\n\n")
	    for string in code_str_list:
	        string = string.replace('\n', '')
	        string.strip()
	        if len(string) > 3 and string[2] == '{' and string[len(string)-1] == '}':
	            try:
	                json_data = json.loads(string)
	                if 'included' in json_data:
	                    result_temps = json_data['included']
	                    for resutl_temp in result_temps:
	                        if 'croppedImage' in resutl_temp:
	                            #print(resutl_temp['croppedImage'])
	                            profilepic_string = resutl_temp['croppedImage']
	                        else:
	                        	profilepic_string = "No Profile Pic"
	            except:
	                logfile.write("error at:%s \n" % repr(string))               
	#print(based_link+profilepic_string)
	logfile.close()

	if profilepic_string == "No Profile Pic":
		return "NaN"
	else:	
		photo_file_name = "profile_img_%s.jpg" % link_id
		pic_url = BASED_ULR + profilepic_string
		print("picture_link:",pic_url)


		r = requests.get(pic_url)
		with open(PHOTO_PATH + photo_file_name, "wb") as code:
		    code.write(r.content)

		#urllib.request.urlretrieve(pic_url, PHOTO_PATH + photo_file_name)

		return PHOTO_PATH + photo_file_name


def photo_parse_with_log(response_text,link_id,logfile):
	h = HTMLParser()
	soup = BeautifulSoup(response_text, 'html.parser')

	profilepic_string = "No Profile Pic"
	for code in soup.find_all('img'):
	    code_str = code.get_text()
	    code_str = h.unescape(code_str)
	    code_str_list = code_str.split("\n\n\n")
	    for string in code_str_list:
	        string = string.replace('\n', '')
	        string.strip()
	        if len(string) > 3 and string[2] == '{' and string[len(string)-1] == '}':
	            try:
	                json_data = json.loads(string)
	                if 'included' in json_data:
	                    result_temps = json_data['included']
	                    for resutl_temp in result_temps:
	                        if 'croppedImage' in resutl_temp:
	                            #print(resutl_temp['croppedImage'])
	                            profilepic_string = resutl_temp['croppedImage']
	                            
	            except:
	                logfile.write("error at:%s \n" % repr(string))               


	if profilepic_string == "No Profile Pic":
		logfile.write("No Profile Pic")
		print("No Profile Pic")
		return "NaN"
	else:	
		logfile.write("Profile picture: %s\n"%profilepic_string)
		print("Profile picture: %s\n"%profilepic_string)
		photo_file_name = "profile_img_%s.jpg" % link_id
		pic_url = BASED_ULR + profilepic_string
		print("picture_link:",pic_url)


		r = requests.get(pic_url)
		with open(PHOTO_PATH + photo_file_name, "wb") as code:
		    code.write(r.content)

		#urllib.request.urlretrieve(pic_url, PHOTO_PATH + photo_file_name)

		return PHOTO_PATH + photo_file_name


def get_linkedindata_from_url(linkedin_url,link_id):

	client = requests.Session()
	h = HTMLParser()

	html = client.get(HOMEPAGE_URL).content
	soup = BeautifulSoup(html)
	csrf = soup.find(id="loginCsrfParam-login")['value']

	login_information = {
	   'session_key':user_email,
	   'session_password':user_password,
	   'loginCsrfParam': csrf,
	}
	logfile = open('Log/image_log_%s.txt' % time.strftime("%Y%m%d%H%M"), 'w')
	client.post(LOGIN_URL, data=login_information)
	print("get picture",linkedin_url)
	response_result = client.get(linkedin_url)
	image_path = photo_parse_with_log(response_result.text,link_id,logfile)
	print(image_path)
	logfile.close()
	return image_path



def get_linkedindata_from_list_urls(linkedin_df):
	client = requests.Session()
	h = HTMLParser()

	html = client.get(HOMEPAGE_URL).content
	soup = BeautifulSoup(html)
	csrf = soup.find(id="loginCsrfParam-login")['value']

	login_information = {
	   'session_key':user_email,
	   'session_password':user_password,
	   'loginCsrfParam': csrf,
	}

	client.post(LOGIN_URL, data=login_information)

	logfile = open('Log/image_log_%s.txt' % time.strftime("%Y%m%d%H%M"), 'w')
	count = 0
	linkedin_df['image_path'] = ""
	print(linkedin_df.head())
	for index, item in linkedin_df.iterrows():
		count = count +1
		logfile.write("%s.)\n"%count)
		logfile.write("User: %s - %s\n"%(item["candidate_surname"], item["candidate_name"]))
		logfile.write("Linkedin Url: %s \n"%(item["url"]))


		response_result = client.get(item["url"])
		image_path = photo_parse_with_log(response_result.text,"%s_%s"%(item["candidate_surname"], item["candidate_name"]),logfile)
		print(image_path)
		linkedin_df['image_path'].loc[linkedin_df.url == item["url"]] = image_path

	print(linkedin_df.head())

	logfile.close()

def get_profile_information():
	h = HTMLParser()
	text = response_result.text
	soup = BeautifulSoup(text, 'html.parser')
	logfile = open('Log/profile_log_%s.txt' % time.strftime("%Y%m%d%H%M"), 'w')
	company_list = list()

	university_list = list()
	language_list = list()
	for code in soup.find_all('code'):
	    code_str = code.get_text()
	    code_str = h.unescape(code_str)
	    if 'companyName' in code_str and 'deletedFields' in code_str:
	        json_data = json.loads(code_str)
	        dataset = json_data['included']
	        for data in dataset:
	            if "firstName" in data and 'summary' in data:
	                userfirstname = data["firstName"].encode("utf-8")
	                userlastname = data["lastName"].encode("utf-8")
	                print("userfirstname ", userfirstname,"\n userlastname",userlastname )
	            if 'companyName' in data:
	                company_dict = dict()
	                company_dict['name'] = data["companyName"].encode("utf-8")
	                if 'locationName' in data:
	                    company_dict['locationName'] = data["locationName"].encode("utf-8")
	                if 'entityUrn' in data:
	                    company_dict['entityUrn'] = data['entityUrn'].encode("utf-8")
	                    for dt in dataset:
	                        if dt['$type'].encode("utf-8") == 'com.linkedin.common.Date' and dt['$id'].encode("utf-8") == "%s,timePeriod,startDate"%company_dict['entityUrn']:
	                            if 'month' in dt:
	                                company_dict['startMonth'] = dt['month']
	                            if 'year' in dt:
	                                company_dict['startYear'] = dt['year']
	                        if dt['$type'].encode("utf-8") == 'com.linkedin.common.Date' and dt['$id'].encode("utf-8") == "%s,timePeriod,endDate"%company_dict['entityUrn']:
	                            if 'month' in dt:
	                                company_dict['endMonth'] = dt['month']
	                            if 'year' in dt:
	                                company_dict['endYear'] = dt['year']
	                        
	                company_list.append(company_dict)
	            if 'schoolName' in data:
	                pprint.pprint(data,logfile)
	                university_dict = dict()
	                university_dict['name'] = data["schoolName"].encode("utf-8")
	                g = geocoder.google(university_dict['name'])
	                university_dict['country'] = g.country
	                if 'entityUrn' in data:
	                    university_dict['entityUrn'] = data['entityUrn'].encode("utf-8")
	                    for dt in dataset:
	                        if dt['$type'].encode("utf-8") == 'com.linkedin.common.Date' and dt['$id'].encode("utf-8") == "%s,timePeriod,startDate"%university_dict['entityUrn']:
	                            if 'month' in dt:
	                                university_dict['startMonth'] = dt['month']
	                            if 'year' in dt:
	                                university_dict['startYear'] = dt['year']
	                        if dt['$type'].encode("utf-8") == 'com.linkedin.common.Date' and dt['$id'].encode("utf-8") == "%s,timePeriod,endDate"%university_dict['entityUrn']:
	                            if 'month' in dt:
	                                university_dict['endMonth'] = dt['month']
	                            if 'year' in dt:
	                                university_dict['endYear'] = dt['year']
	                if 'locationName' in data:
	                    university_dict['locationName'] = data["locationName"].encode("utf-8")
	                university_list.append(university_dict)
	            if 'name' in data and 'proficiency' in data:
	                language_dict = dict()
	                language_dict['name'] = data['name'].encode("utf-8")
	                language_dict['proficiency'] = data['proficiency'].encode("utf-8")
	                language_list.append(language_dict)
	logfile.close()
	return company_list, language_list, university_list
	

	







