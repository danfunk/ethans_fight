ethans_fight
===========

Facebook Group HTML Generator.  Downloads all content from a Facebook group into a moderately attractive local html/image archive. 

Built using Python 2.7

Getting Started
---------------

1. Setup a virtual ENV for this project.
 
     $ virtualenv ENV --no-site-packages --unzip-setuptools 
     $ source ENV/bin/activate 

2. Install required libraries

     $ pip install -r requirements.txt

4. Look up the facebook ID for the group you wish to archive.
   A nice tool for this is http://wallflux.com/facebook_id/
   Just past the url for your group into the box, and out comes the id.
   All you want is that number highlighted in yellow on the resulting page.
   You don't need to register the page or anything.

5. Get an OAuth Access Token
   There are two ways to get an access token.  Since this application runs
   relatively quickly, you can be find just generating a temporary token
   using the Graph API Exporer.  To do so, go to https://developers.facebook.com/tools/explorer
   click on the "Get Access Token" button. Copy this new token somewhere.
   You can also generate a more perminent access token by following the directions
   here: http://stackoverflow.com/questions/16054033/facebook-graphapi-oauth-how-to-get-access-token
   
   
6. Update the config.yml file
   Take the two values you gathered above, and paste them into your config file, replacing
   the defaults that are already there.
   
7. Run the script.

    $ python ethan.py
