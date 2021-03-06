import facebook
import os
import shutil
import requests
import simplejson
import yaml
from datetime import datetime
from dateutil import parser
from quik import FileLoader
import youtube_dl
import cgi

# This downloads all the content and build pages for all the posts.  
# A second file called "indexer.py" will generate an index page that
# provides an overview and navigation of the content.

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
    download_group_videos = config["download_group_videos"]
    download_other_sites_videos = config["download_other_sites_videos"]
    download_other_groups_videos = config["download_other_groups_videos"]
    max_pages = config["max_pages"]
    posts_per_page = config["posts_per_page"]

except  (IOError, TypeError, KeyError, yaml.parser.ParserError)as e:
    print "There is a problem with the configuration file. Please see the readme for how to create this file."
    print "\n\nConfiguration error: {0}".format(e.message + "\n")
    quit()


# Checks to see if a directory exists, and if not, creates it.
def assure_dir_exists(path):
    try: 
        os.makedirs(path)
        return path
    except OSError:
        if not os.path.isdir(path):
            raise
        return path

# Set up directories.
icons_dir  = assure_dir_exists(os.path.join("content", "user_icons"))
pics_dir   = assure_dir_exists(os.path.join("content", "pictures"))
photos_dir = assure_dir_exists(os.path.join("content", "photos"))
css_dir    = assure_dir_exists(os.path.join("content", "css"))
video_dir  = assure_dir_exists(os.path.join("content", "videos"))
posts_dir  = assure_dir_exists(os.path.join("content", "posts"))

# Copy over css files.
src_files = os.listdir("css")
for file_name in src_files:
    full_file_name = os.path.join("css", file_name)
    if (os.path.isfile(full_file_name)):
        shutil.copy(full_file_name, css_dir)

# Downloads a users profile picture in small and medium sizes.    
def download_fb_image(fb_id):    
    file_name_sm = os.path.join("content", "user_icons", fb_id + ".jpg")
    # disable since it is not used: reduce calls to graph api
    #file_name_lg = os.path.join("content", "user_icons", fb_id + "_lg.jpg")
    try:
        if not os.path.exists(file_name_sm):
            user = graph.get_connections(fb_id, "picture")
            with open(file_name_sm, 'wb') as f:
                f.write(user["data"])
        #if not os.path.exists(file_name_lg):
        #    user = graph.request(fb_id + "/" + "picture", {"type" : "normal"})
        #    with open(file_name_lg, 'wb') as f:
        #        f.write(user["data"])
    except simplejson.scanner.JSONDecodeError:
        print "Oops! Problem parsing JSON, this occurs when trying to download a facebook profile picture."

# Downloads a photo given a url.
def download_picture(path, id, overwrite=False):   
    file_name = os.path.join("content", "pictures", id + ".jpg")
    if overwrite or not os.path.exists(file_name):
        r  = requests.get(path, stream=True)
        if r.status_code == 200:
            with open(file_name, 'wb') as f:
                for chunk in r.iter_content():
                    f.write(chunk)

# Returns all comments for a given post.  If the comments are paginated
# just make a seperate call and download them all.
def process_comments(post):

    # let's get all comments but with extra data field such as attachment
    comments = graph.request(post["id"] + "/" + "comments", {'limit':'500', 'fields':'id,attachment,from,message'})["data"]

    for com in comments:
        download_fb_image(com["from"]["id"])
        com["message"] = cgi.escape(com["message"]).replace('\n','<br />')
        if 'attachment' in com and com["attachment"]["type"] == "photo":
            # this is needed because it is not uncommon for graph api to fail in such case
            # the template will use a link to the picture instead of the photo page
            # knowing that the picture is in high res
            if not create_photo_page(com["attachment"]["target"]["id"]) :
                com["photo_error"] = True
            download_picture(com["attachment"]["media"]["image"]["src"], com["id"])

    return comments

# Creates a page for a large picture, including comments on that picture.
# return false if there was a problem
def create_photo_page(picture_id):

   try:
       post = graph.get_object(picture_id)

       # for a reason I ignore the message from the post of this image
       # is in the name...
       if("name" in post):
           post["name"] = cgi.escape(post["name"]).replace('\n','<br />')
       if("message" in post):
           post["message"] = cgi.escape(post["message"]).replace('\n','<br />')

       loader   = FileLoader('html')
       template = loader.load_template('photo.html')
       date     = parser.parse(post["created_time"])

       # TODO verify that the extension is correct...
       download_picture(post["source"] + "?type=large", picture_id)
       photo_url = os.path.join("..", "pictures", picture_id + ".jpg")

       file_name = os.path.join("content", "photos", post["id"] + ".html")

       # Download all the images for the comments.
       if post.has_key("comments") :
           post["all_comments"] = process_comments(post)

       with open(file_name, 'wb') as f:
           f.write(template.render({'post': post, 'date' : date, 'photo' : photo_url},
                                   loader=loader).encode('utf-8'))
       return True
   except facebook.GraphAPIError as e:
       print "Oops!  failed to get this object:" + str(picture_id) + "\nError: "+e.message
       return False
   except KeyError as e:
       print "Oops! Failed to find information for this image:" + str(picture_id) + "\nError: "+e.message
       return False

# Creates a page for a video, including comments on that picture.
ydl = youtube_dl.YoutubeDL({'outtmpl': os.path.join('tmp', '%(id)s%(ext)s')})
ydl.add_default_info_extractors()
def create_video_page(post):

   try:   
       loader   = FileLoader('html')
       template = loader.load_template('video.html')
       date     = parser.parse(post["created_time"])
       video_id = post["id"]
       # TODO actually use the template to generate a page...

       src = ""
       if(post.has_key("object_id")):
           if not (download_other_groups_videos or download_group_videos): return
           src = "https://www.facebook.com/photo.php?v=" + post["object_id"]
       elif(post.has_key("source")):
           if not download_other_sites_videos: return
           src = post["source"] 
       elif(post.has_key("link")):
           if not download_other_sites_videos: return
           src = post["link"] 
       else:
           return
          
       # Download the video
       result = ydl.extract_info(src, download=False)       
       if 'entries' in result:
           # Can be a playlist or a list of videos
           video = result['entries'][0]
       else:
           # Just a video
           video = result

       #print("Downloading Thumbnail: " + video["thumbnail"])
       download_picture(video["thumbnail"], video_id, True)
       
       video_name =  video_id + "." + video["ext"]

       video_url  = os.path.join("content", "videos", video_name)
       if not os.path.exists(video_url):
           tempfile = video["id"] + video["ext"]
           print "downloading " + video_name
           result = ydl.extract_info(src, download=True)
           os.rename(tempfile, video_url)

       post["video"] = video_name

   except facebook.GraphAPIError as e :
       print "Download failed for :" + str(video_id) + "\nError: "+e.message
   except youtube_dl.utils.DownloadError as e :
       print "Download failed for :" + str(video_id) + "\nError: "+e.message
   except KeyError as e :
       print "Complex output for data on this video :" + str(video_id) + "\nError: "+e.message

# Create an index page.
def index_page(posts, pg_count, more_pages):
    index_name = os.path.join("content", "posts", str(pg_count) + ".html")
    
    with open(index_name, 'wb') as f:
        loader   = FileLoader('html')
        template = loader.load_template('post.html')
        f.write(template.render({'posts': posts, 'pg_count' : pg_count + 1, 'more_pages' : more_pages},
                                loader=loader).encode('utf-8'))

# Run through the posts individually and grab all the images
def prepare_post(post):

    # Turn the created time into a real date object.
    post["date"] = parser.parse(post["created_time"])

    if(post.has_key("message")): 
        post["message"] = cgi.escape(post["message"]).replace('\n','<br />')

    # Create a photo page if a photo exists.
    if(post["type"] == "photo") :
        create_photo_page(post["object_id"])

    # Create a video page if a video exists.
    if(post["type"] == "video") :
        create_video_page(post)
        
    # download any associated pictures.
    if(post.has_key("picture")) :
        download_picture(post["picture"], post["id"])

    # Download all the images in the comments.
    if post.has_key("comments") :
        post["all_comments"] = process_comments(post)
         
# RECURSIVE - work through the feed, page by page, creating
# an index page for each.
def process_feed(feed, pg_count):
    print("processing page #" + str(pg_count) + " (" + str(pg_count+1) + "/" + str(max_pages) + ")")

    # create a parsed out time for each post
    # and make sure you have /all/ the comments (not just the first page.)
    for post in iter(feed["data"]):
        prepare_post(post)   

    more_pages=False
    if(pg_count < max_pages-1 and "paging" in feed and "next" in feed["paging"]):
        more_pages=True

    index_page(feed["data"], pg_count, more_pages)

    if(more_pages):
        req    = requests.get(feed["paging"]["next"])
        process_feed(req.json(), pg_count + 1)


# Here is where we kick it all off by grabbing the first page
# of the newsfeed for the group.
try:
    graph = facebook.GraphAPI(oauth_access_token)
    profile = graph.get_object(group_id)
    feed = graph.get_connections(group_id, "feed", limit=posts_per_page)


    if(len(feed) == 0):
        print("\n\nERROR: No feed found for the group id '" + group_id + "' in your config.\n")
        quit()
        
    process_feed(feed, 0)


except facebook.GraphAPIError as e:
    print "\n\nFacebook Graph API error({0}): {1}".format(e.type, e.message + "\n")


