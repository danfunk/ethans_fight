import facebook
import os
import shutil
import requests
import simplejson
from datetime import datetime
from dateutil import parser
from quik import FileLoader

oauth_access_token="yourtoken"

group_id = "yourgroup"

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

# Cover over css files.
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

# Creates a page for a posting, along with all the comments.
def create_post_page(post):
    loader   = FileLoader('html')
    template = loader.load_template('post.html')
    date     = parser.parse(post["created_time"])

    has_pic   = False
    has_photo = False

    if(post.has_key("picture")) :
        download_picture(post["picture"], post["id"])
        has_pic   = True
        
    if(post.has_key("object_id")) :
        create_photo_page(post["object_id"])
        has_photo = True

    file_name = os.path.join("content", post["id"] + ".html")
    with open(file_name, 'wb') as f:
        f.write(template.render({'post': post, 'date' : date, 'has_pic': has_pic, 'has_photo': has_photo},
                                loader=loader).encode('utf-8'))
        
    # Download all the images.
    if post.has_key("comments") :
        for com in post["comments"]["data"]:
            download_fb_image(com["from"]["id"])                                

# Create an index page.
def index_page(posts, pg_count):
    index_name = os.path.join("content", "index" + str(pg_count) + ".html")
    with open(index_name, 'wb') as f:
        loader   = FileLoader('html')
        template = loader.load_template('index.html')
        f.write(template.render({'posts': posts},
                                loader=loader).encode('utf-8'))

def post_pages(posts):
    # Here is the main loop of the code, which calles the other methods and builds out all the pages.
    for post in iter(posts):
        create_post_page(post)

def process_feed(feed, pg_count):
    print("processing page #" + str(pg_count) )
    index_page(feed["data"], pg_count)
    post_pages(feed["data"])    
    if(feed.has_key("paging") & feed["paging"].has_key("next")):
        req    = requests.get(feed["paging"]["next"])
        process_feed(req.json(), pg_count + 1)


graph = facebook.GraphAPI(oauth_access_token)
profile = graph.get_object(group_id)
feed = graph.get_connections(group_id, "feed")

process_feed(feed, 0)


