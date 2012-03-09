#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

# Author: Eni Mustafaj
# Example for CS249 - Web Mashups course


from google.appengine.ext import webapp
from google.appengine.ext.webapp import util

# IMPORTANT: In Python 2.5, the json library is called simplejson
import simplejson as json 

from google.appengine.ext import db

def write_radio_item(item, name):
    "Generate HTML code for a radio button."
    
    htmlText = '''
    <input type="radio" name="%s" value="%s" />
    <span>%s</span>
    <br/>''' % (name, item, item)
    return htmlText

def write_radio_list(radioList, name):
    "Generate HTML code for radio buttons list."
    
    htmlText = ''
    for item in radioList:
        htmlText += write_radio_item(item, name)
    return htmlText
        
def write_options_list(optList, name):
    "Generate HTML code for a list of options."
    
    htmlText = '<select name="%s">\n' % name
    htmlText += '<option>Choose from list</option>\n'
    for opt in optList:
        htmlText += '<option>%s</option>\n' % opt
    htmlText += '</select>\n' + '<br/>\n'
    return htmlText

def write_form(optList, optName, radioList, radioName):
    "Generate HTML code for a form."
    
    htmlText = '<form method="post" action="/survey">\n'
    htmlText += write_options_list(optList, optName)
    htmlText += write_radio_list(radioList, radioName)    
    htmlText += '<input type="submit" name="submit" value="Submit">\n</form>\n'
    return htmlText


class Answers(db.Model):
    answer1 = db.StringProperty()
    answer2 = db.StringProperty()

def save_results(choice1, choice2):
    submission = Answers()
    if choice1 != 'Choose from list':
        submission.answer1 = choice1
    if choice2:
        submission.answer2 = choice2
    # Save new entry only if there was some valid answer
    if submission.answer1 or submission.answer2:
        submission.put()    

              
class SurveyHandler(webapp.RequestHandler):
    def __init__(self):
        data = json.load(open('favorites.json'))
        optList = data['authors']
        radioList = data['books']
        htmlText = write_form(optList, 'authors', radioList, 'books')
        htmlText = '<p>Choose your favorites and submit:</p>\n' + htmlText
        self.surveyHTML = htmlText
        
    def get(self):
        self.response.out.write(self.surveyHTML)
        
    def post(self):
        IP = self.request.remote_addr
        choice1 = self.request.get('authors')
        choice2 = self.request.get('books')
        self.response.out.write("<p>Choices '%s' and '%s' were received from IP=%s." % \
                                (choice1, choice2, IP))
        self.response.out.write("<p><a href='/'>Return home</a></p>")
        
        db.run_in_transaction(save_results, choice1, choice2)

       
class ResultsHandler(webapp.RequestHandler):
    
    def create_image_URL(self, dataList):
        labels = set(dataList)
        counts = [dataList.count(el) for el in labels]
        counts = [str(el) for el in counts]
        data = ','.join(counts)
        labels = [el.replace(' ', '+') for el in labels if el]
        chl = '|'.join(labels)
        imgURL = 'http://chart.apis.google.com/chart?cht=p&chs=520x350&chma=25,25,25,25&chd=t:%s&chl=%s' % \
                 (data, chl)
        return imgURL
        
    def get(self):
        q = Answers.all()
        firstQuest = []
        secondQuest = []
        for answer in q:
            firstQuest.append(answer.answer1)
            secondQuest.append(answer.answer2)
        img1URL = self.create_image_URL(firstQuest)
        img2URL = self.create_image_URL(secondQuest)

        self.response.out.write("<p><img src='%s'></p>" % img1URL)
        self.response.out.write("<p><img src='%s'></p>" % img2URL)
        self.response.out.write("<p><a href='/'>Return home.</a></p>")
        

class MainHandler(webapp.RequestHandler):
    def get(self):
        self.response.out.write('<p><a href="/survey">Take survey</a></p>')
        self.response.out.write('<p><a href="/results">See results</a></p>')

def main():
    application = webapp.WSGIApplication([('/', MainHandler),
                                          ('/survey', SurveyHandler),
                                          ('/results', ResultsHandler)],
                                         debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
