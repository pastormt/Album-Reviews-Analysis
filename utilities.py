import requests
from lxml import html
from urllib.parse import quote
import json

# save dict to json file
# params: artists_albums - dictionary of keys = artist name, values = list of lists of album values
#         file_name - should end with .json
def save_dict_json(artists_albums, file_name):
    print("saving dictionary as ", file_name)
    with open(file_name,'w') as save_to:
        json.dump(artists_albums, save_to)

# param: genres - a list of genres viewable on http://www.metacritic.com/music under browse by genre
# returns: artists - a dictionary of unique artist names (keys) and their metacritic artist page urls (values) for the combined genres

def get_artists_from_genres(genres):
    print("getting artists from genres...")

    artists = {}

    for g in genres:
        print(g)
        # get number of pages
        page = requests.get('http://www.metacritic.com/browse/albums/genre/date/' + g, headers={'User-Agent': 'Mozilla/5.0'})
        tree = html.fromstring(page.content)
        last_page = int(tree.xpath("//li[contains(@class, 'last_page')]/a[@class='page_num']/text()")[0])

        # loop over all pages from 1 to last_page, and get artists (and artist pages on metacritic)
        for i in range(last_page):
            #print(i + 1, " out of ", last_page, " pages of artists")
            page = requests.get('http://www.metacritic.com/browse/albums/genre/date/' + g + '?page=' + str(i), headers={'User-Agent': 'Mozilla/5.0'})
            tree = html.fromstring(page.content)

            some_artists = tree.xpath("//li[contains(@class, 'product_artist')]/span[@class='data']/text()")
            some_artists_urls = tree.xpath("//div[contains(@class, 'product_title')]/a/@href")

            count = 0
            for this_url in some_artists_urls:
                if some_artists[count] not in artists:
                    print(some_artists[count])
                    try:
                        album_page = requests.get('http://www.metacritic.com' + this_url, headers={'User-Agent': 'Mozilla/5.0'})
                        album_tree = html.fromstring(album_page.content)

                        artist_url = album_tree.xpath("//div[contains(@class, 'product_artist')]/a/@href")[0]
                        artists[some_artists[count]] = artist_url
                    except: # The Script did not have a url link on their own page... causing artist_url list to be empty
                        pass
                count += 1

    return artists



# for each artist in artists, get the earliest album date the artist released, according to allmusic.com
# as metacritic.com only includes albums released after mid-1999
# param: artists - the set of artist names to check
# the function will remove artists will releases before 2000 from the set

def earliest_album_date_allmusic(artists):
    artists_to_remove = set()

    # for io progress tracking
    num_artists = len(artists)
    cur_artist = 1
    print("earliest album date check from allmusic...")
    for artist in artists.keys():
        # io progress tracking
        print(cur_artist, " out of ", num_artists)
        cur_artist += 1
        # end io progess tracking

        # search for the artist...
        artist_formatted = quote(artist)
        page = requests.get('http://www.allmusic.com/search/artists/' + artist_formatted, headers={'User-Agent': 'Mozilla/5.0'})
        tree = html.fromstring(page.content)

        #print(artist)

        # i'm assuming the first result returned by the search is the best match
        # the url of the artist page for the best match for the search term

        url_match_list = tree.xpath('//div[@class="info"]/div[@class="name"]/a/@href')

        if len(url_match_list) > 0:
            best_match_url = url_match_list[0]

            # go to that page's discography
            page = requests.get(best_match_url + '/discography', headers={'User-Agent': 'Mozilla/5.0'})
            tree = html.fromstring(page.content)

            albums_html = tree.xpath('//tbody/tr')
            years = []

            for album_html in albums_html:
                #print(album_html.xpath('td[@class="year"]/text()')[0].strip())
                try:
                    year = int(album_html.xpath('td[@class="year"]/text()')[0].strip())
                    years.append(year)
                except ValueError:
                    # need to remove the artist entirely, since that year could be before 2000! :(
                    # to do so, simply interpret the year as one before 2000
                    years.append(-1)

            years.sort()
            earliest_release = years[0] if len(years) > 0 else -1
            # if that is earlier than 2000, then must remove this artist from the set
            if earliest_release < 2000:
                artists_to_remove.add(artist)
        else: # no matches, so couldn't find the artist in allmusic.com, so must remove
            artists_to_remove.add(artist)

    for artist in artists_to_remove:
        del artists[artist]



# param: a single artist name
# returns: the url of that artist's page on metacritic

def get_artist_url_metacritic(artist):
    print(artist)
    artist = quote(artist)
    page = requests.get('http://www.metacritic.com/search/person/' + artist + '/results', headers={'User-Agent': 'Mozilla/5.0'})
    try:
        tree = html.fromstring(page.content)

        # assuming 1st result is best match for the artist name as the search term
        match_urls = tree.xpath('//ul[contains(@class, "search_results")]/li[contains(@class, "first_result")]//h3[contains(@class, "product_title")]/a/@href')

        if len(match_urls) > 0:
            return 'http://www.metacritic.com' + match_urls[0]
            # note: for one artist, not sure why, the search by the artist name did not bring up a page...
        else:
            return None
    except: # lxml.etree.XMLSyntaxError
        return None



# param: the url for a given artist's page on metacritic.com
# returns: a list of lists, each sub-list containing data on a single release of that artist

def get_albums_from_artist_page(artist_url):
    page = requests.get('http://www.metacritic.com' + artist_url + '?filter-options=music&sort_options=date&num_items=100', headers={'User-Agent': 'Mozilla/5.0'})
    try:
        tree = html.fromstring(page.content)
        it_over = tree.xpath("//table[contains(@class, 'credits')]/tbody/tr")

        all_albums = []

        for album_html in it_over:
            l = []
            l.append(album_html.xpath("td/span[contains(@class, 'metascore_w')]/text()"))
            l.append(album_html.xpath("td/a/text()"))
            l.append(album_html.xpath("td[contains(@class, 'year')]/text()"))
            l.append(album_html.xpath("td[contains(@class, 'role')]/text()"))
            l.append(album_html.xpath("td[contains(@class, 'score')]/span[contains(@class, 'textscore')]/text()"))

            for i in range(len(l)):
                l[i] = l[i][0].strip()

            all_albums.append(l)

        return all_albums

    except: # change this to specify the LXML XMLSyntaxError...
        return None
