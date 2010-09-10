
"""
Copyright (C) Sarah Mount, 2010.

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have rceeived a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

__author__ = 'Sarah Mount'
__date__ = 'September 2010'

from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

from urllib2 import urlopen
from urllib import urlencode

from django.utils import simplejson as json

import cgi
import logging
import os.path


kmurl = "http://www.knowmore.org/wiki/api/api.php?"


class CompanyInfo(db.Model):
    """Model for information about a particular company.
    
    This information is taken directly from knowmore.org by the
    ScreenScrape class.
    """
    name = db.StringProperty()
    km_url = db.LinkProperty()
    summary = db.StringProperty()
    timestamp = db.StringProperty()
    worker = db.IntegerProperty(choices=set([1, 2, 3, 4, 5]))
    human = db.IntegerProperty(choices=set([1, 2, 3, 4, 5]))
    politics = db.IntegerProperty(choices=set([1, 2, 3, 4, 5]))
    environment = db.IntegerProperty(choices=set([1, 2, 3, 4, 5]))
    ethics = db.IntegerProperty(choices=set([1, 2, 3, 4, 5]))
    co_url = db.StringListProperty()
    def json(self):
        """Return object in JSON format."""
        formatted = {'name':self.name,
                     'km_url':str(self.km_url),
                     'issue_summary':self.summary,
                     'update_time':self.timestamp,
                     'co_url':list(self.co_url),
                     'r_worker':str(self.worker),
                     'r_human':str(self.human),
                     'r_politics':str(self.politics),
                     'r_enviro':str(self.environment),
                     'r_ethics':str(self.ethics),
                     }
        return json.dumps(formatted)
    def html(self):
        """Return object in HTML."""
        template_values = {'company':self}
        path = os.path.join(os.path.dirname(__file__), 'index.html')
        return template.render(path, template_values)


class ScreenScraper(webapp.RequestHandler):
    """Fetch the latest JSON feed from knowmore.org and store it in
    the datastore.
    """
    def get(self):
        logging.info('Started screen scraper.')
        url = kmurl + (urlencode((('request', 'profile'), ('flag', 'e'))))
        try:
            response = json.loads(urlopen(url).read())
            logging.info('Fetched down JSON feed.')
        except urllib2.URLError, e:
            logging.critical('Could not open JSON feed. Cannot continue.')
            return
        logging.info('Got %i company profiles.' % len(response['profiles']))
        for co_d in response['profiles']:
            if co_d['company_name'] == 'Target Corporation':
                continue
            company = CompanyInfo()
            company.name = co_d['company_name']
            if co_d['km_url'].startswith('http://'):
                company.km_url = co_d['km_url']
            else:
                company.km_url = 'http://' + co_d['km_url']
            company.summary = co_d['issue_summary']
            company.timestamp = co_d['update_time']
            company.worker = int(co_d['r_worker'])
            company.human = int(co_d['r_human'])
            company.politics = int(co_d['r_politics'])
            company.environment = int(co_d['r_enviro'])
            company.ethics = int(co_d['r_ethics'])
            company.co_url = co_d['company_url']
            # Store the thing
            company.put()
            # Ready for the next one...
            company = None
        logging.info('Screen scraping complete.')
        self.response.headers['Content-Type'] = 'text/html'
        self.response.out.write('Screen scraping complete.')


class MainPage(webapp.RequestHandler):
    def get(self):
        name = self.request.get('company')
        companies = CompanyInfo.gql('WHERE name = :1 LIMIT 1', name)
        if self.request.get('format') == 'json':
            self.response.headers['Content-Type'] = 'text/json'
            self.response.out.write(companies[0].json())
        else:
            self.response.headers['Content-Type'] = 'text/html'
            self.response.out.write(companies[0].html())



application = webapp.WSGIApplication(
    [('/', MainPage),
     ('/scrape/', ScreenScraper),
     ],
    debug=True)


def main():
    run_wsgi_app(application)


if __name__ == "__main__":
    main()
