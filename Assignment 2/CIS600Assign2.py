import twitter
import sys
import time
from urllib.error import URLError
from http.client import BadStatusLine
import json
import matplotlib.pyplot as plt
import networkx as nx
from sys import maxsize as maxint
from functools import partial

#from cookbook to authenticate login
def oauth_login():    
    CONSUMER_KEY = 'BRcoDxt2VHx4M7ZXeYZwoVeCZ'
    CONSUMER_SECRET = 'V7Y0mMnOD4LTuIXErSMDqO1LiWAMgzMSvLvSrQQAItW7OULb80'
    OAUTH_TOKEN = '264717372-j2cQ6tsjBClkEQWqbIuqgdhb4OFvtVj57ioBDwKL'
    OAUTH_TOKEN_SECRET = '1znzGflrF7tJbMXZ3o59tC6Kd2Zq1a89QobzR5KLtUuE3'
    
    auth = twitter.oauth.OAuth(OAUTH_TOKEN, OAUTH_TOKEN_SECRET,
                               CONSUMER_KEY, CONSUMER_SECRET)
    
    twitter_api = twitter.Twitter(auth=auth)
    return twitter_api

twitter_api = oauth_login()
#from cookbook to make twitter connection request
def make_twitter_request(twitter_api_func, max_errors=10, *args, **kw): 
    
    # A nested helper function that handles common HTTPErrors. Return an updated
    # value for wait_period if the problem is a 500 level error. Block until the
    # rate limit is reset if it's a rate limiting issue (429 error). Returns None
    # for 401 and 404 errors, which requires special handling by the caller.
    def handle_twitter_http_error(e, wait_period=2, sleep_when_rate_limited=True):
    
        if wait_period > 3600: # Seconds
            print('Too many retries. Quitting.', file=sys.stderr)
            raise e
    
        # See https://developer.twitter.com/en/docs/basics/response-codes
        # for common codes
    
        if e.e.code == 401:
            print('Encountered 401 Error (Not Authorized)', file=sys.stderr)
            return None
        elif e.e.code == 404:
            print('Encountered 404 Error (Not Found)', file=sys.stderr)
            return None
        elif e.e.code == 429: 
            print('Encountered 429 Error (Rate Limit Exceeded)', file=sys.stderr)
            if sleep_when_rate_limited:
                print("Retrying in 15 minutes...ZzZ...", file=sys.stderr)
                sys.stderr.flush()
                time.sleep(60*15 + 5)
                print('...ZzZ...Awake now and trying again.', file=sys.stderr)
                return 2
            else:
                raise e # Caller must handle the rate limiting issue
        elif e.e.code in (500, 502, 503, 504):
            print('Encountered {0} Error. Retrying in {1} seconds'.format(e.e.code, wait_period), file=sys.stderr)
            time.sleep(wait_period)
            wait_period *= 1.5
            return wait_period
        else:
            raise e

    # End of nested helper function
    
    wait_period = 2 
    error_count = 0 

    while True:
        try:
            return twitter_api_func(*args, **kw)
        except twitter.api.TwitterHTTPError as e:
            error_count = 0 
            wait_period = handle_twitter_http_error(e, wait_period)
            if wait_period is None:
                return
        except URLError as e:
            error_count += 1
            time.sleep(wait_period)
            wait_period *= 1.5
            print("URLError encountered. Continuing.", file=sys.stderr)
            if error_count > max_errors:
                print("Too many consecutive errors...bailing out.", file=sys.stderr)
                raise
        except BadStatusLine as e:
            error_count += 1
            time.sleep(wait_period)
            wait_period *= 1.5
            print("BadStatusLine encountered. Continuing.", file=sys.stderr)
            if error_count > max_errors:
                print("Too many consecutive errors...bailing out.", file=sys.stderr)
                raise

#from cookbook to get user profile
def get_user_profile(twitter_api, screen_names = None, user_ids = None):
    
    assert (screen_names != None) != (user_ids != None), "Must have screen_names or user_ids, but not both"

    items_to_info = {}

    items = screen_names or user_ids

    while len(items) > 0:

        items_str = ','.join([str(item) for item in items[:100]])
        items = items[100:]

        if screen_names:
            response = make_twitter_request(twitter_api.users.lookup, screen_name = items_str)
        else:  # user_ids
            response = make_twitter_request(twitter_api.users.lookup, user_id = items_str)

        for user_info in response:
            if screen_names:
                items_to_info[user_info['screen_name']] = user_info
            else:  # user_ids
                items_to_info[user_info['id']] = user_info

    return items_to_info

#from cookbook to get friend/follower ids
def get_friends_followers_ids(twitter_api, screen_name = None, user_id = None, friends_limit = maxint, followers_limit = maxint):
    # Must have either screen_name or user_id (logical xor)
    assert (screen_name != None) != (user_id != None), "Must have screen_name or user_id, but not both"

    get_friends_ids = partial(make_twitter_request, twitter_api.friends.ids, count = 5000)
    get_followers_ids = partial(make_twitter_request, twitter_api.followers.ids, count = 5000)

    friends_ids, followers_ids = [], []

    for twitter_api_func, limit, ids, label in [
        [get_friends_ids, friends_limit, friends_ids, "friends"],
        [get_followers_ids, followers_limit, followers_ids, "followers"]
    ]:

        if limit == 0: continue

        cursor = -1
        while cursor != 0:

            if screen_name:
                response = twitter_api_func(screen_name = screen_name, cursor = cursor)
            else:  # user_id
                response = twitter_api_func(user_id = user_id, cursor = cursor)

            if response is not None:
                ids += response['ids']
                cursor = response['next_cursor']

            print('Fetched {0} total {1} ids for {2}'.format(len(ids), label, (user_id or screen_name)), file = sys.stderr)

            if len(ids) >= limit or response is None:
                break

    return friends_ids[:friends_limit], followers_ids[:followers_limit]

#own code: return top 5 followers
def get_top_five_follower(old):
        new = {}
        for i in old:
            new[i] = old[i]['followers_count']

        return sorted(new, key = new.get, reverse = True)[:5]

#----------------own codes------------
#own code along with some modification from lecture notes
screen_name = 'KeithRunes'
user_id = 725424811154018306

#retrieve a list of friends and a list of followers and get reciprocal friends
follows, followers = get_friends_followers_ids(twitter_api, screen_name=screen_name, friends_limit=5000, followers_limit=5000)
reciprocalFriends = set(follows) & set (followers)

#get 5 most popular friends
iniProfileList = get_user_profile(twitter_api, user_ids = list(reciprocalFriends))
iniTopFive = get_top_five_follower(iniProfileList)

#own code: crawler modified from lecture notes
#initialize
maxNodes = 100
ids = []
ids.append(725424811154018306)
depth = 1
maxDepth = 8
nodeCount = 1
nodeToNode = {}
nodeToNode[725424811154018306] = iniTopFive

#run until depth exceed our set maximum depth(8) or number of nodes exceed our maximum number of nodes(100)
while depth < maxDepth:
    depth += 1
    (IDs, iniTopFive) = (iniTopFive, [])

    #for each id in IDs queue
    for id in IDs:

        #if id not in the ids list, add to list and store its edges
        if id in ids: continue
        ids.append(id)
        edges = []

        #for this current id, find its top 5 friends
        followID, followerID = get_friends_followers_ids(twitter_api, user_id=id, friends_limit=5000, followers_limit=5000)
        reciprocalID = set(followID) & (set (followerID))
        profileList = get_user_profile(twitter_api, user_ids = list(reciprocalID))
        TopFive = get_top_five_follower(profileList)

        #for each friend
        if followID or followerID:
            print("Got reciprocal_ids for {0}:{1}".format(id, TopFive))

            #if id is in TopFive and don't have edge and not in ids list, create its own node and update accordingly
            for i in TopFive:
                if (i not in edges): 
                    if (i not in ids):
                        nodeCount += 1
                    edges.append(i)
                    iniTopFive.append(i)
                else: 
                    continue

                    
        else:
            print(str(id) + 'is protected')
        
        #update a id's edges
        nodeToNode[id] = edges

        #if number of nodes exceed our maximum number of nodes(100), break
        if (nodeCount >= maxNodes): break
    
    if (nodeCount >= maxNodes): break

#own code: create graph
out=nx.Graph()
for k in nodeToNode:
    for v in nodeToNode[k]:
       out.add_edge(k, v)

#print number of nodes and edges       
print("# of Nodes = " + str(out.number_of_nodes())+"\n")
print("# of Edges = " + str(out.number_of_edges())+"\n")

#find diameter and average distance
diameter = nx.diameter(out)
averageDistance = nx.average_shortest_path_length(out)
print("average distance = " + str(averageDistance)+"\n")
print("diameter = " + str(diameter)+"\n" )

#display graph and save it
nx.draw(out)
plt.savefig("output.png")
plt.show()

