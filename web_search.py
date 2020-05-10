'''*****************************************************************************
   This program create a web interface with cherrypy and it can search something
   through mongodb and we can insert some records into the database.

   The function create two input areas, one for searching and the other for
   inserting. At the top of the web there're name ,ID and prompt. Besides there
   are two iframes to display some result.

   search() function can search records according to input message, we can
   input several messages separate with ',' when user clicked the button
   the results will appear in the iframe1 and each result just displayed it's
   restaurant name, the name is also a button. If we click the button the
   detail will display in the iframe2.

   addrest() function can insert a record in the database if the submit message
   is correct. The prompt message will dispaly in iframe2.

   choose() functiion will display the detail message in iframe2 when click the
   name in iframe1.
   
   *****************************************************************************
'''


import cherrypy
import os, os.path
import demjson
from datetime import datetime
from pymongo import MongoClient

client = MongoClient()
db = client.test

class WebSearch(object):
    
    @cherrypy.expose
    def index(self):
        return """<html>
          <head>
            <link href="/static/style.css" rel="stylesheet">
          </head>
          <body>
            <h1>Type message:</h1>
            
            <form method="get" action="search" target="iframe1">
              <input type="text" value="" name="message" style="width:300px" />
              <button type="submit">提交</button>
            </form>
            
            <form method="get" action="addrest" target="iframe2" />
              <textarea name="message" style="vertical-aligen:top;\
              outline:none;width:300px;height:200px">
              </textarea>
              <button type="submit">添加</button>
            </form>
            
            <iframe name="iframe1" ></iframe>
            <iframe name="iframe2" ></iframe>
          </body>
        </html>"""
    @cherrypy.expose
    def search(self, message):
        #deal with the input message
        m = message.split(',')
        fields = []
        s = []
        for x in m:
            fields.append(x.split(':')[0])
            s.append(x.split(':')[1])
        allstr = {}
        for i in range(len(m)):
            #case-insensitive
            allstr[fields[i]] = {'$regex':s[i],'$options': 'i'}
        cursor = db.restaurants.find(allstr)
        result = []
        #set the style of the iframe 
        doc = '''<html>
                 <head>
                   <style type="text/css">
                     body {background-color:lightgreen}
                   </style>
                 </head>
                 <body>
                   <h2>Restaurants Name</h2>
                 </body>
                 <html>'''
        result.append(doc)

        #make every search result into a doc and convert the list choose()      
        for r in cursor:
            rest_name = r['name']
            doc = """<html>
                    <head></head>
                    <body>
                      <form method="get" action="choose" target="iframe2">
                      
                        <input type="hidden" id="restname" \
                        name="restname" value="%s">
                        
                        <input type="hidden" id="restmsg" \
                        name="restmsg" value="%s">
                        
                        <button type="submit">%s</button>
                      </form>
                    </body>
                    </html>"""%(rest_name, r, rest_name) 
            result.append(doc)
        return result
        
    #add a record into database and it has a feedback
    @cherrypy.expose
    def addrest(self, message):
        msg = demjson.decode(message)
        if(db.restaurants.insert_one(msg)):
            return 'Insert Successfully!'
        else:
            return 'Insert Failed'

    #display one detail message 
    @cherrypy.expose
    def choose(self,restname,restmsg):
        #msg = json.loads(json_util.dumps(restmsg))
        doc = '''<html>
                <head></head>
                <body>
                  <h2>%s detail</h2>
                  <h3>%s</h3>
                </body>
                </html>'''%(restname, restmsg)
        return doc


if __name__ == '__main__':

    conf = {
        '/': {
            'tools.sessions.on': True,
            'tools.staticdir.root': os.path.abspath(os.getcwd())
        },
        '/static': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': './public'
        }
    }

    
    cherrypy.quickstart(WebSearch(),'/',conf)












