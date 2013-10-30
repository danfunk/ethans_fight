import facebook
import json
import os
import requests
from datetime import datetime
from dateutil import parser
from quik import FileLoader

oauth_access_token="CAACEdEose0cBAOEWEn2PODjHl1aOOhq0XaU1kf8VNmrQsfJzinhT8BHy5hEZAPLSz7A193xzsuw5OkEx1T17ZAQ1LrDZAGlJi3R2p8yPZCZBUPxnecIAZCsRQFw6qy1uuZAo0EH2T6fbeuqRk2KkTYLa7zoLnlnZBWuQhoNdnMZAPTw7wvPr8dQQ10Xqyrzr0ivIZD"

group_id = "172331119467578"

graph = facebook.GraphAPI(oauth_access_token)
profile = graph.get_object(group_id)
feed = graph.get_connections(group_id, "feed")


# Set up directories.
icon_dir = os.path.join("content", "user_icons")
picture_dir = os.path.join("content", "pictures")
photo_dir = os.path.join("content", "photos")
if not os.path.exists(icon_dir):
    os.makedirs(icon_dir)
if not os.path.exists(picture_dir):
    os.makedirs(picture_dir)
if not os.path.exists(photo_dir):
    os.makedirs(photo_dir)

    
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

def download_picture(path, id):
   print "getting that picture: " + path
   r         = requests.get(path + "?type=large", stream=True)
   file_name = os.path.join("content", "pictures", id + ".jpg")

   if not os.path.exists(file_name):
       if r.status_code == 200:
           with open(file_name, 'wb') as f:
               for chunk in r.iter_content():
                   f.write(chunk)

def create_photo_page(picture_id):

    post = graph.get_object(picture_id)

    loader   = FileLoader('html')
    template = loader.load_template('post.html')
    date     = parser.parse(post["created_time"])
    
    download_picture(post["source"], picture_id)
    photo_url = os.path.join("content", "pictures", picture_id + ".jpg")

    file_name = os.path.join("content", "photos", post["id"] + ".html")
    with open(file_name, 'wb') as f:
        f.write(template.render({'post': post, 'date' : date, 'photo' : photo_url},
                              loader=loader).encode('utf-8'))
    
count = 0
for post in iter(feed["data"]):
#   print i["picture"]
    #   print i["name"]
    loader   = FileLoader('html')
    template = loader.load_template('photo.html')
    date     = parser.parse(post["created_time"])
    has_pic  = False

    if(post.has_key("picture")) :
        download_picture(post["picture"], post["id"])
        has_pic = True

    if(post.has_key("object_id")) :
        create_photo_page(post["object_id"])
        has_pic = True

    if(post.has_key("link")) :
        print post["link"]

    file_name = os.path.join("content", post["id"] + ".html")
    with open(file_name, 'wb') as f:
        f.write(template.render({'post': post, 'date' : date, 'has_pic': has_pic},
                              loader=loader).encode('utf-8'))

    print ("==========================\n")
    print (post["type"])
    print (post["id"])
    print ("==========================\n")
    for x in iter(post):
            print("--" + x)

    # Download all the images.
    if post.has_key("comments") :
        for com in post["comments"]["data"]:
            download_fb_image(com["from"]["id"])                    

    count = count + 1
    if (count > 20):
        break 

"""
        d =
        
        f.write("\n" + i["message"])
        download_fb_image(i["from"]["id"])        

        # NOTE:  May be paginated.
        f.write("\n\n")


#   print i["comments"]
        for x in iter(i):
            print("--" + x)
    break
    
#    r = requests.get(settings.STATICMAP_URL.format(**data), stream=True)
#    if r.status_code == 200:
#    with open(path, 'wb') as f:
#        for chunk in r.iter_content():
#            f.write(chunk)
"""
