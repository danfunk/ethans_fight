from quik import FileLoader
import os
from os import walk
import re


# Provides a list of files from the given directory that match the given regex.
def list_files(dir, regex):
    f = []
    for (dirpath, dirnames, filenames) in walk(dir):
        files =  [fn for fn in filenames if re.match(regex, fn)]
        f.extend(files)
        break
    return f

index_name = os.path.join("content", "index.html")    

# USER ICONS
# ----------
user_icons = list_files(os.path.join("content", "user_icons"), ".*[^_][^l][^g]\.jpg")
print len(user_icons)

# VIDEOS
# ----------
vid_files  = list_files(os.path.join("content", "videos"), ".*")
regex      = re.compile("(.*)\..{3}")
videos = []
# Work through the image files and create a dictionary of data for them.
for f in vid_files:
    v_id  = regex.search(f).group(1)
    image = os.path.join("pictures/" + v_id + ".jpg")
    videos.append({"id" : v_id, "file" : f, "image" : image})

# PICTURES
# ----------
pictures = list_files(os.path.join("content", "pictures"), "[^_]*\.jpg")

# POSTS
# ----------
post_files = list_files(os.path.join("content", "posts"), ".*\.html")
posts = []
# Work through the image files and create a dictionary of data for them.
for f in post_files:
    p_id  = regex.search(f).group(1)
    posts.append({"page" : p_id, "file" : f})

posts = sorted(posts, key=lambda p : int(p.get("page")))

with open(index_name, 'wb') as f:
    loader   = FileLoader('html')
    template = loader.load_template('index.html')
    f.write(template.render({'user_icons': user_icons, 'friend_count': len(user_icons),
                             'videos': videos, 'video_count': len(videos),
                             'pictures': pictures,
                             'posts': posts},
                             loader=loader).encode('utf-8'))
    
