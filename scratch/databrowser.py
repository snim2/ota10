#!/usr/bin/env python

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

import json
import os
import os.path
import sys

__author__ = 'Sarah Mount'
__date__ = 'September 2010'

# http://www.knowmore.org/wiki/api/api.php?request=profile&flag=e
db = 'knowmore.json'

def load_data():
    path = os.path.dirname(sys.argv[0])
    data = None
    with open(path + os.sep + db) as db_f:
        data = json.load(db_f)
    return data

def print_companies(data):
    for co_d in data['profiles']:
        print co_d['company_name']

    
if __name__ == '__main__':
    data = load_data()
    print_companies(data)
