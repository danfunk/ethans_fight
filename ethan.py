import facebook
import os
import shutil
import requests
import simplejson
import yaml
from datetime import datetime
from dateutil import parser
from quik import FileLoader

# Read in configuration
try:
    stram = open("config.yml")
    config = yaml.load(stram)
    print("Configuration:")
    print("====================")
    print("Group ID:" + config["group_id"])
    print("OAuth Token:" + config["oauth_access_token"])
    
    group_id = config["group_id"]
    oauth_access_token = config["oauth_access_token"]
except  (IOError, TypeError, KeyError, yaml.parser.ParserError)as e:
    print "There is a problem with the configuration file. Please see the readme for how to create this file."
    print "\n\nConfiguration error: {0}".format(e.message + "\n")
    quit()

# Set up directories.
icon_dir = os.path.join("content", "user_icons")
picture_dir = os.path.join("content", "pictures")
photo_dir = os.path.join("content", "photos")
css_dir = os.path.join("content", "css")
if not os.path.exists(icon_dir):
    os.makedirs(icon_dir)
if not os.path.exists(picture_dir):
    os.makedirs(picture_dir)
if not os.path.exists(photo_dir):
    os.makedirs(photo_dir)
if not os.path.exists(css_dir):
    os.makedirs(css_dir)

# Copy over css files.
src_files = os.listdir("css")
for file_name in src_files:
    full_file_name = os.path.join("css", file_name)
    if (os.path.isfile(full_file_name)):
        shutil.copy(full_file_name, css_dir)

# Downloads a users profile picture in small and medium sizes.    
def download_fb_image(fb_id):    
    file_name_sm = os.path.join("content", "user_icons", fb_id + ".jpg")
    file_name_lg = os.path.join("content", "user_icons", fb_id + "_lg.jpg")
    if not os.path.exists(file_name_sm):
        user = graph.get_connections(fb_id, "picture")
        with open(file_name_sm, 'wb') as f:
            f.write(user["data"])
    if not os.path.exists(file_name_lg):
        user = graph.request(fb_id + "/" + "picture", {"type" : "normal"})
        with open(file_name_lg, 'wb') as f:
            f.write(user["data"])

# Downloads a photo given a url.
def download_picture(path, id):
   r         = requests.get(path + "?type=large", stream=True)
   file_name = os.path.join("content", "pictures", id + ".jpg")

   if not os.path.exists(file_name):
       if r.status_code == 200:
           with open(file_name, 'wb') as f:
               for chunk in r.iter_content():
                   f.write(chunk)


# Creates a page for a large picture, including comments on that picture.
def create_photo_page(picture_id):

   try:
       post = graph.get_object(picture_id)
   
       loader   = FileLoader('html')
       template = loader.load_template('photo.html')
       date     = parser.parse(post["created_time"])
    
       download_picture(post["source"], picture_id)
       photo_url = os.path.join("..", "pictures", picture_id + ".jpg")

       file_name = os.path.join("content", "photos", post["id"] + ".html")
       with open(file_name, 'wb') as f:
           f.write(template.render({'post': post, 'date' : date, 'photo' : photo_url},
                                   loader=loader).encode('utf-8'))

       # Download all the images for the comments.
       if post.has_key("comments") :
           for com in post["comments"]["data"]:
               download_fb_image(com["from"]["id"])                                        

   except facebook.GraphAPIError:
       print "Oops!  failed to get this object:" + str(picture_id)


# Create an index page.
def index_page(posts, pg_count, more_pages):
    index_name = os.path.join("content", "index" + str(pg_count) + ".html")
    
    if(pg_count == 0):        
        index_name = os.path.join("content", "index" + ".html")

    with open(index_name, 'wb') as f:
        loader   = FileLoader('html')
        template = loader.load_template('index.html')
        f.write(template.render({'posts': posts, 'pg_count' : pg_count + 1, 'more_pages' : more_pages},
                                loader=loader).encode('utf-8'))


# RECURSIVE - work through the comments, recalling this method
# for subsequent pages of comments.  Download images, and return
# all comments as a single list.
def process_comments(comments):
    # print ("The comments is: " + str(comments))
    data = []
    for com in comments["data"]:
        download_fb_image(com["from"]["id"])                                                
        data.append(com)

    if(comments.has_key("paging") and comments["paging"].has_key("next")):
        print("THERE ARE MORE COMMENTS ON THIS ONE!!!!")
        req    = requests.get(comments["paging"]["next"])
        data.extend(process_comments(req.json()))
        
    return data

# Run through the posts individually and grab all the images
def prepare_post(post):

    # Turn the created time into a real date object.
    post["date"] = parser.parse(post["created_time"])

    # Create a phot page if a photo exists.
    if(post.has_key("object_id")) :
        create_photo_page(post["object_id"])

    # download any assoicated pictures.
    if(post.has_key("picture")) :
        download_picture(post["picture"], post["id"])

    # Download all the images in the comments.
    if post.has_key("comments") :
        post["all_comments"] = process_comments(post["comments"])
         
# RECURSIVE - work through the feed, page by page, creating
# an index page for each.
def process_feed(feed, pg_count):
    print("processing page #" + str(pg_count) )

    # create a parsed out time for each post
    # and make sure you have /all/ the comments (not just the first page.)
    for post in iter(feed["data"]):
        prepare_post(post)   

    more_pages=False
    if(feed.has_key("paging") and feed["paging"].has_key("next")):
        more_pages=True

    index_page(feed["data"], pg_count, more_pages)

    # Stop here while we test...
    # if(more_pages):
    #    req    = requests.get(feed["paging"]["next"])
    #    process_feed(req.json(), pg_count + 1)


# Here is where we kick it all off by grabbing the first page
# of the newsfeed for the group.
try:
    graph = facebook.GraphAPI(oauth_access_token)
    profile = graph.get_object(group_id)
    feed = graph.get_connections(group_id, "feed")


    if(len(feed) == 0):
        print("\n\nERROR: No feed found for the group id '" + group_id + "' in your config.\n")
        quit()
        
    process_feed(feed, 0)


except facebook.GraphAPIError as e:
    print "\n\nFacebook Graph API error({0}): {1}".format(e.type, e.message + "\n")


