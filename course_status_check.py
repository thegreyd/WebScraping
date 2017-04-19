#author - Siddharth Sharma
#contact - sshar24@ncsu.edu
#version - 1.0
#
#DESCRIPTION
#Simple script to regularly check if anything changed in course catalogue @https://www.acs.ncsu.edu/php/coursecat/
#Prints the whole list initially, and then subsequently prints the changes that occur if any.
#Saves to file at change to resume next time.
#
#INSTALLATION
# - Requires Python3
# - Requires Firefox (or Chrome)
# - Requires packages BeautifulSoup and Selenium
#   - Run in Cmd or Terminal:
#       - pip3 -U install bs4 
#       - pip3 -U install selenium
#
#USAGE
# - Variables 
#   - driver - browser to use Firefox or Chrome. Default - Firefox
#   - course_subject - The course listings which you want to check. Default - CSC
#   - course_career_value - "Graduate" or "Undergraduate". Default - Graduate
#   - limit_to_500_courses - Only show courses starting with 5. Default - True
#   - limit_to_oncampus - Only show oncampus courses. Default - True
#   - time_interval - frequency of refreshing page. Default - 3min
#       
# - Runs indefinitely. To exit terminate cmd/terminal and browser.


from bs4 import BeautifulSoup
import time, collections, pickle
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

binary = FirefoxBinary("/usr/bin/firefox-trunk")
driver = webdriver.Firefox(firefox_binary=binary)

url="https://www.acs.ncsu.edu/php/coursecat/"
#driver = webdriver.Firefox()
#driver = webdriver.Chrome()
course_subject = "CSC"
course_career_value = "Graduate"
limit_to_500_courses = True
limit_to_oncampus = True
time_interval = 60*3 #3 min
global_list = []

first_run = True
last_save = 0

def load_file():
    global global_list
    global last_save
    
    try:
        with open("course_list.save", "rb") as f:
            global_list = pickle.load(f)
        print("Resuming from last save @ {}".format(str(global_list[-1][0])))
        pretty_print(global_list[-1])
        if len(global_list)>0:
            last_save = global_list[-1][0]
    except:
        print("No save found. Creating a new save")
        save_file()

def save_file():
    global last_save

    with open("course_list.save", "wb") as f:
        pickle.dump(global_list, f)
        if len(global_list)>0:
            last_save = global_list[-1][0]

def wait_for_js(By, value, seconds=5):
    try:    
        element = WebDriverWait(driver, seconds).until(     
            EC.presence_of_element_located((By, value))
        )
    except:
        print("Timeout. Check your Internet connection speed and Retry.")
        exit()


def fill_subject():
    wait_for_js(By.ID, "auto-subject")
    element = driver.find_element_by_id("auto-subject")
    element.clear()
    element.send_keys(course_subject)

def select_campusonly():
    wait_for_js(By.ID, "campus-only")
    driver.find_element_by_id("campus-only").click()
    
def select_coursecareer():
    wait_for_js(By.ID, 'course-career')
    select = Select(driver.find_element_by_id('course-career'))
    select.select_by_visible_text(course_career_value)

def press_searchbutton():
    wait_for_js(By.CLASS_NAME, "btn-success")
    driver.find_element_by_class_name("btn-success").click()
    
    try:
        wait_for_js(By.ID, "subject-err-msg")
        driver.find_element_by_id("subject-err-msg").click()
        fill_subject()
        press_searchbutton()
    except:
        pass

def dropdown_searchsection():
    driver.find_element_by_id("class-search").click()

def search_sequence():
    driver.get(url)
    fill_subject()
    if limit_to_oncampus:
        select_campusonly()
    select_coursecareer()
    press_searchbutton()

def check():
    search_sequence()
    wait_for_js(By.CLASS_NAME, "course", seconds=120)    
    parseAndsave()

def check_regular():
        global first_run
    #try
        while True:
            if not first_run:
                dropdown_searchsection()
                first_run = False

            check()
            time.sleep(time_interval)
    #except e:
    #    print("Exception occured. Check your internet connection or browser and Retry.")
    #    print(e.message())
    #    exit()

def parseAndsave():
    global no_change

    timestamp = datetime.now()
    local_dict = collections.OrderedDict()
    
    #Parse
    
    soup = BeautifulSoup(driver.page_source,'html.parser')
    
    for section_tag in soup.find_all("section",{"class":"course"}):
        all_classes = []
        course_code = section_tag["id"]
        course_name = section_tag.h1.small.text

        if limit_to_500_courses and course_code[4]!="5":
            break

        special = course_code[-2:]=="91"

        for tr_tags in section_tag.tbody.find_all("tr"):
            td_tags = tr_tags.find_all("td")
            status = td_tags[3].text
            
            if special:
                special_course_code = course_code +"-"+ td_tags[0].text
                course_name = td_tags[8].text
                local_dict[special_course_code] = [course_name, status]
            else:
                all_classes.append(status)
        
        if not special:
            status = " ".join(all_classes)
            local_dict[course_code] = [course_name, status]
    
    #Save
    
    if len(global_list)>0:
        if global_list[-1][1]!=local_dict:
            print("Change","@",str(timestamp))
            if len(global_list[-1][1])!=len(local_dict):
                print("Number of subjects changed!")
            pretty_change_print(local_dict, global_list[-1][1])
            global_list.append([timestamp, local_dict])
            save_file()
        else:
            print("NoChange","@",str(timestamp))
            global_list[-1][0] = timestamp
            
            interval = timestamp - last_save
            if interval.seconds >= (60*10): #10min
                save_file()
    else:
        global_list.append([timestamp, local_dict])
        pretty_print(global_list[-1])
        save_file()

def pretty_print(list_item):
    printline()
    print(list_item[0])
    
    for key,value in list_item[1].items():
        print("{:<15}{:<50}{}".format(key,value[0],value[1]))
    printline()
    

def gen_delta_file(new_dict, old_dict):
    for key,value in old_dict.items():
        value2 = new_dict.get(key,"n/a")
        if(value != value2):
            print(key,value[0])
            print("Old: {}".format(value[1]))
            print("New: {}".format(value2[1]))
    

def pretty_change_print(new_dict, old_dict):
    printline()
    print("These are the Changed Values: ")
    for key,value in old_dict.items():
        value2 = new_dict.get(key,"n/a")
        if(value != value2):
            print()
            print(key,value[0])
            print("Old: {}".format(value[1]))
            print("New: {}".format(value2[1]))
    printline()

def printline():
    print("--------------------------------------------------------------------------")

load_file()
check_regular()
driver.close()