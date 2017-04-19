from bs4 import BeautifulSoup
import urllib.request

codechef_url = "https://www.codechef.com/contests"
codechef_html = urllib.request.urlopen(codechef_url)
content = codechef_html.read().decode(codechef_html.headers.get_content_charset()) 
#to convert into string

present_contest_index = content.find("<h3>Present Contests</h3>")
past_contest_index = content.find("<h3>Past Contests</h3>")
contest_html = content[present_contest_index:past_contest_index]

soup = BeautifulSoup(contest_html, 'html.parser')

contest_db = {}

for tbody_tag in soup.find_all('tbody'):
    for tr_tag in tbody_tag.find_all('tr'): 
        td_tags = tr_tag.find_all('td')
        code = td_tags[0].text
        name = td_tags[1].a.text
        start_date = td_tags[2].text
        end_date = td_tags[3].text
        contest_db[code] = (name, start_date, end_date)

print("--------------Codechef contests---------------")
column_format = " {:<10}{:<40}{:<30}{:<30}"
print(column_format.format("ID", "Name", "Start Date", "End Date"))
for key,value in contest_db.items():	
	print(column_format.format(key, value[0],value[1],value[2]))