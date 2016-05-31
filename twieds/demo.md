## Tweet Collection
- Show collection progress
- Show example tweet object in DB

## SLP Demo
- Show SLP method functioning: `slp_demo.py`

- Example: **434500083**
    -> My friend
    -> Location very accurate
    -> Theory holds up
    
- Example: **22749171**
    -> Uses full API requests when attempted
    -> Located near Washington
    -> Look on profile finds in San F ranisco

- Example: **2260536170**
    -> Random user from the flooding set
    -> Known location near Merseyside

- Example: **838509024**
    -> Hywel
    -> Example of failure to map
    -> Not enough activity / connections

- Doesnt work well for @MODIS_GeoBlink or @RiverLevelsUK etc

## MI Demo
- Show the MI method functioning `demos.py`
- Not using geotags

- Example: **567f185ded60b543ba53408b**
    -> UK tweeter
    -> Mainly uses location field

- Example: **5666fe8aed60b543ba437638**
    -> US Flood warning
    -> Bot account
    -> Latches onto 'Thurston County' in tweet text
    -> Does not have polygon so usespoint (small enough not to matter)
    
- Example: **56299bc2ed60b51fd4231679** 
    -> RiverLevelsUK flood warning
    -> Gets the UK from location field
    -> River was detected, but no location on the wiki (see output)
    
- Example: **Hywel tweet, shows MI advantage**
```{"created_at":"Mon Apr 25 15:11:55 +0000 2016","id":724616937792221184,"id_str":"724616937792221184","text":"Great opportunity: fully funded PhD studentship at U.Exeter studying online news-sharing networks and social media https:\/\/t.co\/89au6y2IQY","truncated":False,"entities":{"hashtags":[],"symbols":[],"user_mentions":[],"urls":[{"url":"https:\/\/t.co\/89au6y2IQY","expanded_url":"http:\/\/www.exeter.ac.uk\/studying\/funding\/award\/?id=2065","display_url":"exeter.ac.uk\/studying\/fundi\u2026","indices":[115,138]}]},"source":"\u003ca href=\"http:\/\/twitter.com\" rel=\"nofollow\"\u003eTwitter Web Client\u003c\/a\u003e","in_reply_to_status_id":None,"in_reply_to_status_id_str":None,"in_reply_to_user_id":None,"in_reply_to_user_id_str":None,"in_reply_to_screen_name":None,"user":{"id":838509024,"id_str":"838509024","name":"Hywel Williams","screen_name":"HywelTPWilliams","location":"University of Exeter, UK","description":"Scientist. Environment, ecology, evolution, complex systems.","url":None,"entities":{"description":{"urls":[]}},"protected":False,"followers_count":182,"friends_count":230,"listed_count":15,"created_at":"Fri Sep 21 20:27:21 +0000 2012","favourites_count":2,"utc_offset":None,"time_zone":None,"geo_enabled":False,"verified":False,"statuses_count":78,"lang":"en","contributors_enabled":False,"is_translator":False,"is_translation_enabled":False,"profile_background_color":"C0DEED","profile_background_image_url":"http:\/\/abs.twimg.com\/images\/themes\/theme1\/bg.png","profile_background_image_url_https":"https:\/\/abs.twimg.com\/images\/themes\/theme1\/bg.png","profile_background_tile":False,"profile_image_url":"http:\/\/pbs.twimg.com\/profile_images\/2634942495\/e73b01210b4b541594a240c797e37ca4_normal.png","profile_image_url_https":"https:\/\/pbs.twimg.com\/profile_images\/2634942495\/e73b01210b4b541594a240c797e37ca4_normal.png","profile_link_color":"0084B4","profile_sidebar_border_color":"C0DEED","profile_sidebar_fill_color":"DDEEF6","profile_text_color":"333333","profile_use_background_image":True,"has_extended_profile":False,"default_profile":True,"default_profile_image":False,"following":False,"follow_request_sent":False,"notifications":False},"geo":None,"coordinates":None,"place":None,"contributors":None,"is_quote_status":False,"retweet_count":2,"favorite_count":1,"favorited":False,"retweeted":False,"possibly_sensitive":False,"possibly_sensitive_appealable":False,"lang":"en","_id":'test'}```

## ED Demo

