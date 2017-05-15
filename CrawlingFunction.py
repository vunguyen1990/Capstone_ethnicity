#Import part
#-------------------------------------------------------------
# import linkedinCrawlling_refer
import crawling_linkedin_photo
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
import geocoder
import pandas as pd
from bs4 import BeautifulSoup
import crawling_linkedin_photo
#=============================================================

#set constant
#-------------------------------------------------------------
user_email = "nganhvu.gon@gmail.com"
user_password = "Vunguyen@jvn"
HOMEPAGE_URL = 'https://www.linkedin.com'
LOGIN_URL = 'https://www.linkedin.com/uas/login-submit'
BASED_ULR = "https://media.licdn.com/mpr/mpr/shrinknp_400_400"
PHOTO_PATH = "photo/"
LOG_PATH = "Log/"
#=============================================================
def get_user_information(cand_id,linkedin_url):
    user_dict = dict()
    user_dict["cand_id"] = cand_id
    link_valid = True
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
    logfile = open( LOG_PATH + 'profile_log_%s.txt' % cand_id, 'w')
    logfile.write("cand_id: %d \n"%int(cand_id))
    
    function_start_time =  time.time()
    client.post(LOGIN_URL, data=login_information)
    response_result = client.get(linkedin_url)
    pprint.pprint(response_result,logfile)
    # print(response_result.text)
    # try:
    #   client.post(LOGIN_URL, data=login_information)
    #   response_result = client.get(linkedin_url)
    #   link_valid = True
    # except:
    #   logfile.write("Url:%s  is not valid\n" % linkedin_url)
    #   return None

    if link_valid == True:
        text = response_result.text
        soup = BeautifulSoup(text, 'html.parser')
        

        company_list = list()
        university_list = list()
        language_list = list()
        userfirstname ="No name"
        userlastname ="No name"

        
        profile_pic_path = crawling_linkedin_photo.photo_parse_with_log(text,cand_id,logfile)
        for code in soup.find_all('code'):
            code_str = code.get_text()
            code_str = h.unescape(code_str)

            if 'companyName' in code_str and 'deletedFields' in code_str:
                try:
                    json_data = json.loads(code_str)
                    # pprint.pprint(json_data,logfile)
                    dataset = json_data['included']
                    for data in dataset:
                        pprint.pprint(data,logfile)
                        if "firstName" in data and 'headline' in data:
                            userfirstname = data["firstName"].encode("utf-8")
                            userlastname = data["lastName"].encode("utf-8")
                            logfile.write("userfirstname: %s - userlastname %s \n" %(userfirstname,userlastname))
                            print("userfirstname ", userfirstname,"\n userlastname",userlastname )
                        if 'companyName' in data:
                            company_dict = dict()
                            company_dict['name'] = data["companyName"].encode("utf-8")
                            if 'locationName' in data:
                                company_dict['locationName'] = data["locationName"].encode("utf-8")
                                g = geocoder.google(company_dict['locationName'])
                                company_dict['country'] = g.country
                            else:
                                g_name = geocoder.google(company_dict['name'])
                                company_dict['country'] = g_name.country
                            if 'entityUrn' in data:
                                company_entityUrn = data['entityUrn'].encode("utf-8")
                                for dt in dataset:
                                    if dt['$type'].encode("utf-8") == 'com.linkedin.common.Date' and dt['$id'].encode("utf-8") == "%s,timePeriod,startDate"%company_entityUrn:
                                        if 'month' in dt:
                                            company_dict['startMonth'] = dt['month']
                                        if 'year' in dt:
                                            company_dict['startYear'] = dt['year']
                                    if dt['$type'].encode("utf-8") == 'com.linkedin.common.Date' and dt['$id'].encode("utf-8") == "%s,timePeriod,endDate"%company_entityUrn:
                                        if 'month' in dt:
                                            company_dict['endMonth'] = dt['month']
                                        if 'year' in dt:
                                            company_dict['endYear'] = dt['year']
                                    
                            company_list.append(company_dict)
                        if 'schoolName' in data:
                            # pprint.pprint(data,logfile)
                            university_dict = dict()
                            university_dict['name'] = data["schoolName"].encode("utf-8")
                            g = geocoder.google(university_dict['name'])
                            university_dict['country'] = g.country
                            if 'entityUrn' in data:
                                university_entityUrn = data['entityUrn'].encode("utf-8")
                                for dt in dataset:
                                    if dt['$type'].encode("utf-8") == 'com.linkedin.common.Date' and dt['$id'].encode("utf-8") == "%s,timePeriod,startDate"%university_entityUrn:
                                        if 'month' in dt:
                                            university_dict['startMonth'] = dt['month']
                                        if 'year' in dt:
                                            university_dict['startYear'] = dt['year']
                                    if dt['$type'].encode("utf-8") == 'com.linkedin.common.Date' and dt['$id'].encode("utf-8") == "%s,timePeriod,endDate"%university_entityUrn:
                                        if 'month' in dt:
                                            university_dict['endMonth'] = dt['month']
                                        if 'year' in dt:
                                            university_dict['endYear'] = dt['year']
                            if 'locationName' in data:
                                university_dict['locationName'] = data["locationName"].encode("utf-8")
                            university_list.append(university_dict)
                except:
                    print('error1')

                if 'projectView' in code_str:
                    try:
                        json_data = json.loads(code_str)
                        profile_id = json_data['data']['profile']
                        profile_id =profile_id[len('urn:li:fs_profile:'):]
                        language_id = language_pattern+profile_id
                        dataset = json_data['included']
                        for data in dataset:
                            if 'entityUrn' in data and data['entityUrn'].find(language_id) != -1:
                                print('language name',data['name'])
                                language_dict['name'] = data['name']
                                if 'proficiency' in data:
                                    language_dict['proficiency'] = data['proficiency']
                                    print('language proficiency',data['proficiency'])
                                language_list.append(language_dict)
                    except:
                        print("error language")


        user_dict["user_firstname"] = userfirstname
        user_dict["user_last"] = userlastname
        user_dict["url"] = linkedin_url
        user_dict["profile_pic_path"] = profile_pic_path
        # pprint.pprint(company_list,logfile)
        # pprint.pprint(university_list,logfile)
        # pprint.pprint(language_list,logfile)
        user_dict["company"] = company_list
        user_dict["university"] = university_list
        user_dict["language"] = language_list
        function_end_time =  time.time()
        logfile.write("All function time spending: %d"%(function_end_time - function_start_time))
        print("All function time spending:",function_end_time - function_start_time)
        logfile.close()
        return user_dict

def cand_info_2DF(result):
    cand_dict = dict()
    cand_dict['cand_id'] = result['cand_id']
    cand_dict['firstname'] = result['user_firstname']
    cand_dict['lastname'] = result['user_last']
    cand_dict['img_path'] = result['profile_pic_path']
    cand_dict['url'] = result['url']
    cand_df = pd.DataFrame(cand_dict,index=[0])  
    return cand_df

def company_list_2DF(result):
    company_list =list()

    for company in result['company']:
    #     pprint.pprint(company)
        company_dict =dict()
        company_dict['cand_id'] = result['cand_id']
        if 'name' in company:
            company_dict['name'] = company['name']
        if 'startYear' in company:
            company_dict['startYear'] = company['startYear']
        if 'startMonth' in company:
            company_dict['startMonth'] = company['startMonth']
        if 'locationName' in company:
            company_dict['locationName'] = company['locationName']
        if 'country' in company:
            company_dict['country'] = company['country']
        if 'endMonth' in company:
            company_dict['endMonth'] = company['endMonth']
        else:
            company_dict['endMonth'] = 'Present'
        if 'endYear' in company:
            company_dict['endYear'] = company['endYear']
        else:
            company_dict['endYear'] = 'Present'
            
        company_list.append(company_dict)
    result_df = pd.DataFrame(company_list)
    return result_df

def university_list_2DF(result):
    university_list =list()

    for university in result['university']:
        # pprint.pprint(university)
        university_dict =dict()
        university_dict['cand_id'] = result['cand_id']
        if 'name' in university:
            university_dict['name'] = university['name']
        if 'startYear' in university:
            university_dict['startYear'] = university['startYear']
        if 'startMonth' in university:
            university_dict['startMonth'] = university['startMonth']
        if 'country' in university:
            university_dict['country'] = university['country']
        if 'endMonth' in university:
            university_dict['endMonth'] = university['endMonth']
        else:
            university_dict['endMonth'] = 'Present'
        if 'endYear' in university:
            university_dict['endYear'] = university['endYear']
        else:
            university_dict['endYear'] = 'Present'
            
        university_list.append(university_dict)
    result_U_df = pd.DataFrame(university_list)
    return result_U_df

def language_list_2DF(result):
    language_list =list()

    for language in result['language']:
    #     pprint.pprint(university)
        language_dict =dict()
        language_dict['cand_id'] = result['cand_id']
        if 'name' in language:
            language_dict['name'] = language['name']
        if 'proficiency' in language:
            language_dict['proficiency'] = language['proficiency']
            
        language_list.append(language_dict)
    result_Language_df = pd.DataFrame(language_list)  
    return result_Language_df
