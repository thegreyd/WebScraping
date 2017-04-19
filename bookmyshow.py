from bs4 import BeautifulSoup
import urllib.request

url="https://in.bookmyshow.com/indore/movies/nowshowing"
req = urllib.request.Request(url,headers={'User-Agent': 'Mozilla'})
html = urllib.request.urlopen(req)

soup = BeautifulSoup(html, 'html.parser')

movie_db = {}

for div_tag in soup.find_all('div',"wow fadeIn movie-card-container"):
    if(div_tag.get("data-selector","")=="movies"):
        name = div_tag["data-search-filter"][7:]
        lang = div_tag["data-language-filter"][1:].split("|")
        genre = div_tag["data-genre-filter"][1:].split("|")
        dimension = div_tag["data-dimension-filter"][1:].split("|")
        movie_db[name] = (lang, genre, dimension) 

print("--------------Now showing Movies in Indore---------------")
column_format = " {:<40}{:<20}{:<30}{:<10}"
print(column_format.format("Name", "Language", "Genres", "Format"))
for key,value in movie_db.items():
	genres = ', '.join(value[1]) if value[1][0] else 'N/A'
	languages = ', '.join(value[0]) if value[0][0] else 'N/A'
	formats = ', '.join(value[2]) if value[2][0] else 'N/A'
	print(column_format.format(key, languages, genres, formats))