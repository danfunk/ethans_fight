ethans_fight
===========

Facebook Group Archiver.  Downloads all content from a Facebook group's Feed into a moderately attractive local html/image archive.  

This is a simple tool in case you ever find that you have a ton of content in a Facebook group that you want to hold onto for some reason.  

Currently Facebook provides a similar feature for personal profiles, but it does not provide it for groups.  

Built using Python 2.7

Getting Started
---------------

### 1. Setup a virtual ENV for this project.

```bash
     $ virtualenv ENV --no-site-packages --unzip-setuptools 
     $ source ENV/bin/activate 
```

### 2. Install required libraries

```base
     $ pip install -r requirements.txt
```

### 3. Look up the facebook ID for the group you wish to archive.
A nice tool for this is http://wallflux.com/facebook_id/
   Just past the url for your group into the box, and out comes the id.
   All you want is that number highlighted in yellow on the resulting page.
   You don't need to register the page or anything.

### 4.  Get an OAuth Access Token
   There are two ways to get an access token.  Since this application runs
   relatively quickly, you can be find just generating a temporary token
   using the Graph API Exporer.  To do so, go to https://developers.facebook.com/tools/explorer
   click on the "Get Access Token" button. Copy this new token somewhere.
   You can also generate a more perminent access token by following the directions
   here: http://stackoverflow.com/questions/16054033/facebook-graphapi-oauth-how-to-get-access-token
   
   
### 5. Update the config.yml file
   Take the two values you gathered above, and paste them into your config file, replacing
   the defaults that are already there.
   
### 6. Run the script.

```bash
    $ python ethan.py
```

### 7. View the results.  
   Everything is written to a directory called "content"
   Just open up the index.html file there and you should
   start seeing the output as soon as the script starts.
   
   Content is paginated, at 25 results per page.  At the
   bottom of each page is a "Next" link that takes you
   to the next page.
   

Modifying
-----------

This uses the templating system "Quik".  The two templates used are for the main index pages, and for the larger photo pages.  You can edit these templates and in the html/ folder.  You can also adjust the CSS in the css folder.  If you make this better, please send it back to me as a pull request and I'll update things here.  


