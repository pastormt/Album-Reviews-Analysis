import statistics as stats
import decimal
import math
import numpy as np
import matplotlib.pyplot as plt
import copy

import thinkstats2 as ts2
import thinkplot as tp
import hypothesis as hyp
import estimation as est

# One-sided correlation test
# building upon code from Downey's ThinkStats2
class CorrelationOneSidedPermute(hyp.CorrelationPermute):
    def TestStatistic(self, data):
        xs, ys = data
        test_stat = ts2.Corr(xs, ys)
        return test_stat

# wrapper for Downey's DiffMeansOneSided, to print pvalue and plot cdf of sampling distribution
def PrintDiffMeansOneSided(data, title="CDF of sampling distribution of null hypothesis", label="difference in mean album score"):
    ht = hyp.DiffMeansOneSided(data)
    pvalue = ht.PValue()
    ht.PlotCdf(label='CDF')
    tp.Config(loc=2)
    tp.Show(xlabel=label,ylabel='CDF', title=title)
    print("Calculated p-value:", pvalue)

# from Downey's ThinkStats2
# for investigating estimator bias
def estimate_mean_error(data, iters):
    # assuming the actual population mean was the sample mean
    data_mean = data.mean()
    sample_size = len(data)

    means = []
    medians = []
    for _ in range(iters):
        xs = np.random.choice(data.values, len(data), replace=True)
        xbar = np.mean(xs)
        median = np.median(xs)
        means.append(xbar)
        medians.append(median)

    print(iters, 'iterations')
    print('Mean Error xbar', est.MeanError(means, data_mean))
    print('Mean Error sample median', est.MeanError(medians, data_mean), '\n')


# Using sample mean & median as estimators
# Get sampling distribution, CI, standard error
# The code below is from Downey's ThinkStats2
def estimate_mean(data):
    # assuming the actual population mean was the sample mean
    data_mean = data.mean()
    sample_size = len(data)
    print("Sample size of first albums reviewed by users is", sample_size)

    means = []
    medians = []
    for _ in range(1000):
        xs = np.random.choice(data.values, len(data), replace=True)
        xbar = np.mean(xs)
        median = np.median(xs)
        means.append(xbar)
        medians.append(median)

    print('\nStandard Error xbar', "%.2f" % est.RMSE(means, data_mean))
    print('Standard Error median', "%.2f" % est.RMSE(medians, data_mean))
    return means, medians

# from Downey's ThinkStats2
def PlotSamplingDistribution(data):
    means, medians = estimate_mean(data)
    cdf = ts2.Cdf(means)
    ci = cdf.Percentile(5), cdf.Percentile(95)
    print("90% Confidence Interval:", "(", "%.2f" % ci[0], ",", "%.2f" % ci[1], ")")

    def VertLine(x, label=None, color='0.8'):
        """Draws a vertical line at x."""
        tp.Plot([x, x], [0, 1], color=color, label=label)

    VertLine(ci[0], label='5th percentile')
    VertLine(ci[1], label='95th percentile')
    tp.Config(loc=2)
    tp.Plot(cdf, label='CDF')
    tp.Show(ylabel="CDF", xlabel="Users' mean score", title="CDF of sampling distribution of Users' mean scores \n 90% confidence interval plotted in grey")

# boilerplate
def print_critics_users_diff(users_scores, critics_scores):
    users_scores_mean = users_scores.mean()
    critics_scores_mean = critics_scores.mean()

    print("Mean CRITIC score:", "%.2f" % critics_scores_mean)
    print("Mean USER score:", "%.2f" % users_scores_mean)
    print("\nUSER mean - CRITIC mean:", "%.2f" % (users_scores_mean - critics_scores_mean))
    print("Users rated albums", "%.2f" % ((users_scores_mean - critics_scores_mean) * 100 / critics_scores_mean), "percent higher than critics did.")
    print("\nEffect size (Cohen's D) of", "%.2f" % ts2.CohenEffectSize(users_scores, critics_scores))

    types = ("Users", "Critics")
    ypos = np.arange(len(types))
    scores = [users_scores_mean, critics_scores_mean]

    plt.bar(ypos, scores, align='center', alpha=0.5)
    plt.xticks(ypos, types)
    plt.ylabel('Mean score')
    plt.title('Mean album review score (out of 100)')
    plt.ylim(60,90)
    plt.show()

# boilerplate
def print_critics_first_albums_observed_effect(first_albums_critics, other_albums_critics):
    first_critics_mean = first_albums_critics.mean()
    others_critics_mean = other_albums_critics.mean()
    print("Mean CRITIC score for a FIRST album:", first_critics_mean)
    print("Mean CRITIC score for an OTHER album:", others_critics_mean)
    diff = first_critics_mean - others_critics_mean
    print("Difference:", diff)
    print("FIRST albums rated", "%.2f" % ((diff / others_critics_mean) * 100), "percent WORSE")

    types = ("First", "Others")
    ypos = np.arange(len(types))
    plt.bar(ypos, [first_critics_mean, others_critics_mean], align='center', alpha=0.5)
    plt.xticks(ypos, types)
    plt.xlabel('Album type')
    plt.ylim(65,75)
    plt.ylabel('Mean Critic Score')
    plt.title('Mean CRITIC Ratings of First and Other Albums')
    plt.show()

# boilerplate
def print_users_first_albums_observed_effect(first_albums_users, other_albums_users):
    first_users_mean = first_albums_users.mean()
    others_users_mean = other_albums_users.mean()
    print("Mean USER score for a FIRST album:", "%.2f" % first_users_mean)
    print("Mean USER score for an OTHER album:", "%.2f" % others_users_mean)
    diff = first_users_mean - others_users_mean
    print("Difference:", "%.2f" % diff)
    print("FIRST albums rated", "%.2f" % ((diff / others_users_mean) * 100), "percent BETTER")

    types = ("First", "Others")
    ypos = np.arange(len(types))
    plt.bar(ypos, [first_users_mean, others_users_mean], align='center', alpha=0.5)
    plt.xticks(ypos, types)
    plt.xlabel('Album type')
    plt.ylim(75,85)
    plt.ylabel('Mean User Score')
    plt.title('Mean USER Ratings of First and Other Albums')
    plt.show()

# plots and prints summary stats regarding the number of albums each artist released
def print_num_albums_per_artist(all_genres):
    num_albums_counts = {}
    num_albums_list = []
    for artist, albums in all_genres.items():
        num_albums = len(albums)
        num_albums_list.append(num_albums)

        if num_albums in num_albums_counts:
            num_albums_counts[num_albums] += 1
        else:
            num_albums_counts[num_albums] = 1

    num_artists = len(all_genres)
    num_albums = sum(num_albums_list)
    print("In total,", num_artists, "artists, producing", num_albums, "albums.")
    print("An average of", "%.2f" % (num_albums / num_artists), "albums per artist.")

    num_albums_hist = ts2.Hist(num_albums_counts)
    artists_more_than_6_albums = sum([v for k,v in num_albums_hist.Items() if k > 6])

    print(artists_more_than_6_albums, 'artists with more than 6 albums.')

    tp.Hist(num_albums_hist)
    tp.Show(xlabel='Number of albums', ylabel='Count of artists with this number of albums',
            title='Histogram of the number of albums per artist')

# plots and prints summary stats regarding the number of albums per genre
def print_num_artists_per_genre(rock_artists_albums, indie_artists_albums, alternative_artists_albums, pop_artists_albums):
    num_rock_artists = len(rock_artists_albums)
    print(num_rock_artists, "artists in the rock genre")

    num_indie_artists = len(indie_artists_albums)
    print(num_indie_artists, "artists in the indie genre")

    num_alternative_artists = len(alternative_artists_albums)
    print(num_alternative_artists, "artists in the alternative genre")

    num_pop_artists = len(pop_artists_albums)
    print(num_pop_artists, "artists in the pop genre")

    num_artists_per_genre = [num_rock_artists, num_indie_artists, num_alternative_artists, num_pop_artists]
    types = ("Rock", "Indie", "Alternative", "Pop")
    ypos = np.arange(len(types))

    plt.bar(ypos, num_artists_per_genre, align='center', alpha=0.5)
    plt.xticks(ypos, types)
    plt.ylabel('Number of artists')
    plt.xlabel('Genre')
    plt.title('Number of Artists Per Genre')
    plt.show()

    total_count = 0
    for l in num_artists_per_genre:
        total_count += l
    print("Summing the counts of artists per genre yields", total_count, "artists, nearly twice the count of unique artists")



# many artists belong to more than 1 genre
# function to quantify part of that overlap and plot the resulting info
def print_unique_artists_per_genre(rock_artists_albums, indie_artists_albums, alternative_artists_albums, pop_artists_albums):
    genre_artist_sets = [set(rock_artists_albums.keys()), set(indie_artists_albums.keys()),
                    set(alternative_artists_albums.keys()), set(pop_artists_albums.keys())]

    genre_unique = []
    for i in range(0, len(genre_artist_sets)):
        list_not_i = [k for k in range(0, len(genre_artist_sets))]
        list_not_i.remove(i)
        others = copy.deepcopy(genre_artist_sets[list_not_i[0]])

        for j in range(1, len(list_not_i)):
            others = others.union(genre_artist_sets[list_not_i[j]])

        genre_unique.append(len(genre_artist_sets[i] - others))

    print(genre_unique[0], "artists unique to the rock genre")
    print(genre_unique[1], "artists unique to the indie genre")
    print(genre_unique[2], "artists unique to the alternative genre")
    print(genre_unique[3], "artists unique to the pop genre")

    types = ("Rock", "Indie", "Alternative", "Pop")
    ypos = np.arange(len(types))
    plt.bar(ypos, genre_unique, align='center', alpha=0.5)
    plt.xticks(ypos, types)
    plt.ylabel('Number of artists')
    plt.xlabel('Genre')
    plt.title('Number of Artists Unique to a Given Genre')
    plt.show()

# param: histo - the histogram to bin
#        num_bins - how many equal-sized (range) bins do you want?
# returns: a copy of histogram binned into num_bins equal-size bins
def binned(histo, num_bins = 5):
    decimal.getcontext().prec = 3

    histo_binned = {}

    bin_incr = decimal.Decimal('1') / decimal.Decimal(num_bins)
    #print("bin_incr: ", bin_incr)
    #cur_bin = decimal.Decimal('0')
    cur_bin = bin_incr

    for val, freq in sorted(histo.items()):
        #print("cur_bin: ", cur_bin)
        #print("val: ", val)

        while val > cur_bin:
            cur_bin += bin_incr

        if cur_bin not in histo_binned:
            histo_binned[cur_bin] = []

        histo_binned[cur_bin] += freq

    #print(sorted(histo, key = lambda kv : kv[1]))
    #print(sorted(histo_binned, key = lambda kv : kv[1]))
    return histo_binned

# copied from Allen Downey's ThinkStats2... needed to implement slightly differently since list.mean() should be stats.mean(list), etc
def cohens_effect_size(list1, list2):
    diff = stats.mean(list1) - stats.mean(list2)
    var1 = stats.variance(list1)
    var2 = stats.variance(list2)

    n1 = len(list1)
    n2 = len(list2)

    pooled_var = (n1 * var1 + n2 * var2) / (n1 + n2)
    d = diff / math.sqrt(pooled_var)
    return d

# comparing users and critics scores (irrespective of album ID)
def users_vs_critics(artists_albums):
    users_scores = []
    critics_scores = []

    for artist, albums in artists_albums.items():
        c_scores = [this_album[0] for this_album in albums if this_album[0] != 'tbd']
        u_scores = [this_album[4] for this_album in albums if this_album[4] != 'tbd']

        for score in c_scores:
            try:
                critics_scores.append(int(score))
            except ValueError:
                pass

        for score in u_scores:
            try:
                users_scores.append(int(score))
            except ValueError:
                pass

    avg_user_score = stats.mean(users_scores)
    avg_critics_score = stats.mean(critics_scores)

    cohensD = cohens_effect_size(users_scores, critics_scores)

    print("User score avg: ", avg_user_score)
    print("Critics score avg: ", avg_critics_score)
    print("Effect size (Cohen's D): ", cohensD)

    return {"Users" : avg_user_score, "Critics" : avg_critics_score}


# params: artists_albums - main dictionary (albums are already sorted per artist)
#         which_scores - number indicating users or critics (position in album list)
#         num_bins - # of equal-sized bins
# returns: per each bin of album IDs, lists of scores for album IDs that fall into that bin
def get_scores(artists_albums, which_score, num_bins = 5):
    decimal.getcontext().prec = 3

    albums_scores = {}

    # dont remove all albums for artists that have 'tbd' scores

    for artist, albums in artists_albums.items():

        count = decimal.Decimal('0')
        adj_num_albums = decimal.Decimal(len(albums) - 1)

        for this_album in albums:
            if this_album[which_score] != 'tbd':
                try: # incase this_album[which_score] is another string, not 'tbd'
                    int_score = int(this_album[which_score])
                    this_index = count / adj_num_albums

                    if this_index in albums_scores:
                        albums_scores[this_index].append(int_score)
                    else:
                        albums_scores[this_index] = [int_score]
                except ValueError:
                    pass
            count += 1

    #return binned_avg(albums_scores, albums_scores_counts, num_bins)
    # bin
    albums_scores_binned = binned(albums_scores, num_bins)

    return albums_scores_binned


# params: artists_albums - main dictionary (albums are already sorted per artist)
#         which_scores - number indicating users or critics (position in album list)
#         num_bins - # of equal-sized bins
# returns: per each bin of album IDs, lists of ranks for album IDs that fall into that bin
def get_ranks(artists_albums, which_score, chance_weighting = False, num_bins = 5):
    decimal.getcontext().prec = 3

    IDs_ranks = {}

    for artist, albums in artists_albums.items():
        ratings = [this_album[which_score] for this_album in albums]
        if 'tbd' not in ratings:
            ratings_dict = {}

            int_count = 0
            count = decimal.Decimal('0')
            adj_num_albums = decimal.Decimal(len(albums) - 1)
            for this_album in albums:
                this_index = count / adj_num_albums
                ratings_dict[this_index] = ratings[int_count]
                count += 1
                int_count += 1

            #print(ratings)
            #print(sorted(ratings_dict.items()))
            num_albums = len(albums)
            rank = 1.0
            for albumID, score in sorted(ratings_dict.items(), key = lambda kv : kv[1], reverse=True):
                if albumID in IDs_ranks:
                    if chance_weighting:
                        IDs_ranks[albumID].append(rank / num_albums)
                    else:
                        IDs_ranks[albumID].append(rank)
                else:
                    if chance_weighting:
                        IDs_ranks[albumID] = [rank / num_albums]
                    else:
                        IDs_ranks[albumID] = [rank]
                rank += 1

    # bin
    IDs_ranks_binned = binned(IDs_ranks, num_bins)
    #for binID, binVal in IDs_ranks_binned.items():
    #    IDs_ranks_binned[binID] = float(binVal) / IDs_counts_binned[binID]
    #return binned_avg(IDs_ranks, IDs_counts, num_bins)
    return IDs_ranks_binned

# params: artists_albums - the main dictionary we're working with throughout the project (keys are artist names, values are lists of
#            lists, each sublist containing data about 1 album)
#         which_score - an index # within each sublist (for each album) referring to either the critic's score or the user's score
#         chance_weighting - since certain index values are more likely to come up in scenarios where they would be a higher rank just by chance
#                    (ie if there are only 2 albums, there is a 50% chance either one is the highest ranked, but if there are 4, there is a 25% chance for each)
#                    flag on whether this should be considered
#         std_dev_weighted - whether or not the weight of each instance should be changed based upon how many std_devs above the mean
#            rating for the artist that album is
# returns: a dictionary where keys are album ID bins, values are, for the album IDs in a given bin, the (weighted) % that they held the top-rated album
def get_max_indexes(artists_albums, which_score, std_dev_weighted = False, chance_weighting = True, num_bins = 5):

    decimal.getcontext().prec = 3

    # dictionary of the index position in each artist's albums list of the album with the highest rating (critic's)
    # keys are index pos, values are counts
    max_indexes = {}

    # dictionary of key = identifer of the album, value = how many of that identifier are in the data at all (for all artists)
    # ie to account for the fact that different artists will have different numbers of total albums, so the fractions each
    # artist will have as their album identifiers will be different
    indexes_count = {}
    for artist, albums in artists_albums.items():
        # these are the rating values...
        # the indexes assigned to each album in artists_albums for this artist ... ie with count (from 0) / (num_albums - 1)
        # will be the same as the indexes of this array... so no need to add them in here
        ratings_dict = [this_album[which_score] for this_album in albums]

        if 'tbd' not in ratings_dict:

            max_value = max(ratings_dict)
            if ratings_dict.count(max_value) == 1:

                # populate indexes count... of all albums, not just those with the max value rating
                count = decimal.Decimal('0')
                adj_num_albums = decimal.Decimal(len(albums) - 1)
                for this_album in albums:
                    this_index = count / adj_num_albums
                    if this_index not in indexes_count:
                        indexes_count[this_index] = [1]
                    else:
                        indexes_count[this_index].append(1)
                    count += 1

                index_max_value = decimal.Decimal(ratings_dict.index(max_value))
                num_albums_adj = decimal.Decimal(len(albums) - 1)
                top_album_index = index_max_value / num_albums_adj

                incr = 1.0
                if chance_weighting:
                    incr *= len(albums)

                if std_dev_weighted:
                    # std dev weighting
                    std_dev = stats.pstdev(ratings_dict) #population since we have all of the artist's albums...
                    mean = stats.mean(ratings_dict)
                    incr *= float(max_value - mean) / std_dev

                if top_album_index not in max_indexes:
                    max_indexes[top_album_index] = [incr]
                else:
                    max_indexes[top_album_index].append(incr)

                #print("Artist: ", artist, "Index: ", top_album_index)

        #else:
            #print("Artist: ", artist, "tbd in ratings_dict")

    # binning

    #print(sorted(max_indexes.items()))
    max_indexes_hist_binned = binned(max_indexes, num_bins)
    #print(sorted(max_indexes_hist_binned.items()))

    indexes_count_binned = binned(indexes_count, num_bins)
    #print(sorted(indexes_count_binned.items()))

    for binID, binVal in max_indexes_hist_binned.items():
        max_indexes_hist_binned[binID] = float(sum(binVal)) / sum(indexes_count_binned[binID])

    #print(sorted(max_indexes_hist_binned.items()))
    return max_indexes_hist_binned
