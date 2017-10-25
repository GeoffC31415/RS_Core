#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  WriteRecords.py
#  
#  Copyright 2017  <pi@raspberrypi>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  

from datetime import datetime
import PullReading
import RS_Database


def main():
	RS_Database.connect_to_db()
	
	for x in range(0,10):
		RS_Database.write_reading(
								datetime.now(), 
								x, 
								PullReading.GetReading(x)
								 )
	
	RS_Database.commit_DB()
	
	return 0


if __name__ == '__main__':
	main()
