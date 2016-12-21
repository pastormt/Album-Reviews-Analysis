import json
from datetime import datetime as dt
import copy
import utilities as ut

# reformat data structure
# was dictionary where keys were artist names, and values were lists of lists, where each sublist represented an album
# now, will simply be a list of lists, where each sublist represents an album (and artist name is now one of the fields of each sublist)
def simplify_datastore(artists_albums):
    new_artists_albums = []
    artist_id = 1 # in case two artists have the same name
    for artist, albums in artists_albums.items():
        count = 1
        for album in albums:
            album_list = copy.deepcopy(album)
            album_list.append(artist)
            album_list.append(artist_id)
            album_list.append(count)
            new_artists_albums.append(album_list)
            count += 1

        artist_id += 1

    return new_artists_albums

# combine all dictionaries in list_of_dicts into one, without any duplicates (so if a key is in 2 dicts, it only appears 1 time in returned copy)
def dictionary_union(list_of_dicts):
    dict_union = copy.deepcopy(list_of_dicts[0])
    for i in range(1, len(list_of_dicts)):
        dict_union.update(list_of_dicts[i])

    return dict_union
    '''
    dict = list_of_dicts[0]
    for i in range(1, len(list_of_dicts)):
        for key, val in list_of_dicts[i].items():
            if key not in dict:
                dict[key] = val
    return dict
    '''


# remove all artists from artists_albums dictionary that have released an album before or during the year specified
# params: artists_albums - the usual dictionary. note, the albums for each artist ARE ALREADY SORTED!!! from earliest to latest date
#         year - remove artists if have album during or before this year
# returns: copy of artists albums with artists removed described above
def artists_after(artists_albums, year):
    # print("Length before: ", len(artists_albums))
    artists_albums_copy = copy.deepcopy(artists_albums)
    artists_to_remove = set()
    for artist, albums in artists_albums_copy.items():
        try:
            album_year = int(albums[0][2][-4:])
            if album_year <= year:
                #print("Year: ", int(albums[0][2][-4:]), " Artist: ", artist)
                artists_to_remove.add(artist)
        except:
            pass
    for artist in artists_to_remove:
        #print("Removing artist: ", artist)
        del artists_albums_copy[artist]

    return artists_albums_copy
    # print("Length after: ", len(artists_albums))


# for a given genre, produce a dictionary keys = artists and values = list of lists of that artists albums, if that artist
# did not release an album before 2000 (which would not have been included in Metacritic's DB, so that whole artist must be scrapped)

# params: genres - a list of strings of genre names (each needs to be a genre on Metacritic)
#         file_name - name of the .json file (including extension) to which the artists_albums dictionary should be saved

def get_and_save_artists_albums(genres, file_name):
    artists = ut.get_artists_from_genres(genres)
    print(len(artists), " artists in this genre on metacritic")

    ut.earliest_album_date_allmusic(artists)
    print(len(artists), " after considering earliest album date")

    artists_albums = {}

    # for io progress tracking
    num_artists = len(artists)
    cur_artist = 1

    print("from get_and_save_artists_albums...")

    count_no_artist_page = 0
    count_le1_album = 0

    for artist, artist_url in artists.items():
        # for progress tracking ONLY...
        print(cur_artist, " of ", num_artists)
        cur_artist += 1

        this_artist_albums = ut.get_albums_from_artist_page(artist_url)
        # removing artists with only 1 album
        if this_artist_albums != None: #and len(this_artist_albums) > 1:
            artists_albums[artist] = this_artist_albums
        else:
            count_no_artist_page += 1
        '''
        elif this_artist_albums == None:
            count_no_artist_page += 1
        else: # len(this_artist_albums) <= 1
            count_le1_album += 1
        '''

    print(count_no_artist_page, " removed because could not find artist page on metacritic")
    print(count_le1_album, " removed because <= 1 album")

    ut.save_dict_json(artists_albums, file_name)
    #print(artists_albums)

def erroneous_scores(artists_albums):
    max_score = [0,""]
    min_score = [100,""]

    for artist, albums in artists_albums.items():
        scores = []
        for this_album in albums:
            scores.append(this_album[0])
            scores.append(this_album[4])
        for s in scores:
            if s != 'tbd':
                #try:
                int_s = int(s)
                if int_s < 0 or int_s > 100:
                    print("Issue artist: ", artist, "Score: ", int_s)

                if int_s < min_score[0]:
                    min_score[0] = int_s
                    min_score[1] = artist

                elif int_s > max_score[0]:
                    max_score[0] = int_s
                    max_score[1] = artist

    print("Max score: ", max_score[0], "Artist: ", max_score[1])
    print("Min score: ", min_score[0], "Artist: ", min_score[1])

# get artists_albums dictionary from .json file where it is saved
# params: filename (of the .json)
# returns: artstists_albums

def json_to_dict_artists_albums(filename):
    #print("Converting JSON file to dict...")
    with open(filename) as tf:
        return json.load(tf)

# for determining album order for a given artist
# helper function for field_preprocessing, below
# converts metacritic date string into a sortable date object
# param: date string from metacritic
# returns: sortable date object
def date_formatting(full_date):
    #print(full_date)
    space_loc = full_date.find(' ')
    comma_loc = full_date.find(',')
    day = full_date[space_loc + 1:comma_loc]
    #print(day)
    if len(day) == 1:
        day = '0' + day
    #print(day)
    newd = full_date[0:space_loc + 1] + day + full_date[comma_loc + 1:]
    #print(newd)
    return dt.strptime(newd, '%b %d %Y')

# 1) sortable dates (from the string Metacritic provides) to each album of each artist
# 2) convert user score and critic score for each album to ints (from strings)
# 3) convert user score to be on a 100-point (instead of 10-point) scale, to match critic score
# 4) remove any albums for which this artist is not a "Primary Artist" (Metacritic lingo)

# param: artists_albums - dictionary with keys = artist name, and values = list of lists, where
# each sublist is an album

def field_preprocessing(artists_albums):
    #print("Preprocessing fields...")
    #print("artist_albums length: ", len(artists_albums))

    removed_new_l2 = 0
    removed_all_tbd = 0
    removed_albums = 0

    #for io progress tracking
    num_artists = len(artists_albums)
    cur_artist = 0

    # if artist has any album that has no rating for both the user score and the critic score, then the artist will need to be removed entirely
    artists_to_remove = set()

    for artist, albums in artists_albums.items():
        #print(cur_artist, " out of ", num_artists)
        #print("Current artist: ", artist)
        cur_artist += 1 # for io progress tracking ONYL... can be deleted

        #if len(albums) <= 1: # if only one album, this artist cant be compared for which album in its career was highest rated
        if len(albums) <= 0: #  no longer need this... hacky way to remove it but its fine
            artists_to_remove.add(artist)
            #print("artist: ", artist, " being removed since only has 1 album")
        else:
            albums_to_remove = []
            for this_album in albums:
                # review scores formatting
                # note: if either is "tbd" (Metacritic has these values) then we do not want to remove the album -- and therefore the whole artist, yet
                # however, if both are "tbd," then we would have to remove the whole artist
                all_tbd = 0

                try:
                    this_album[0] = int(this_album[0])
                except:
                    all_tbd += 1
                try:
                    this_album[4] = int(float(this_album[4]) * 10) # from 10-pt scale w decimals to 100-pt scale
                except:
                    all_tbd += 1

                ''' # no longer removing artists that have an album where both user score and critic's score is 'tbd'
                if all_tbd == 2: # need to remove the whole artist, since both user score and critic score are 'tbd' for a given album
                    artists_to_remove.add(artist)
                    removed_all_tbd += 1
                    #print("artist: ", artist, " being removed since tbd for ", this_album)
                    break # leaves the for loop iterating through the rest of this artist's albums, since the artist will be removed
                '''

                # date formatting
                formatted_date = date_formatting(this_album[2])
                this_album.append(formatted_date)

                # remove albums for which this artist is not a "Primary Artist"
                if this_album[3].find("Primary Artist") == -1:
                    albums_to_remove.append(this_album)
                    #print("Album: ", this_album[1], " removed from artist: ", artist, " since artist was not a Primary Artist")


            # now that all albums for this artist have had the sortable date added to them, sort them
            # except if user score and reviewer score (all_tbd == 2) were not populated... then removing artist so no need to sort, etc

            # if all_tbd != 2:
            # no longer removing artists that have an album where both user and critic score is tbd

            # for tracking only...
            removed_albums += len(albums_to_remove)
            #print(albums_to_remove)

            albums = [this_album for this_album in albums if this_album not in albums_to_remove]
            # now need to re-check that none have 0 albums

            if len(albums) <= 0:
                artists_to_remove.add(artist)
                removed_new_l2 += 1
            else:
                artists_albums[artist] = albums
                artists_albums[artist].sort(key = lambda this_album : this_album[5])

    for artist in artists_to_remove:
        #print("removing", artist)
        del artists_albums[artist]

    #print("removed_new_l2: ", removed_new_l2)
    #print("removed_all_tbd: ", removed_all_tbd)
    #print("albums to remove cumulative: ", removed_albums)
    #print("artist_albums length: ", len(artists_albums))
    #print(artists_albums)


# creates a sample artists_albums dictionary to use from a portion of a dictionary from one of the genre files (that hold json dictionaries already)
# param: from_file_name - the existing json file to use
#        sample_file_name - name of sample file to save to
#        sample_file_size - how many keys from from_file_name to include in the outputted sample file
def create_sample_json(from_file_name, sample_file_name, sample_file_size):
    all_data = json_to_dict_artists_albums(from_file_name)
    sample_data = {}

    count = 0
    for key, value in all_data.items():
        sample_data[key] = value
        count += 1
        if count >= sample_file_size:
            break

    ut.save_dict_json(sample_data, sample_file_name)
