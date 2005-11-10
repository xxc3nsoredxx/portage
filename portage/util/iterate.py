# Copyright: 2005 Gentoo Foundation
# License: GPL2
# $Id$

from itertools import islice

def enumerate(iter, start, end):
	count = start
	for r in islice(iter, start, end):
		yield count, r
		count+=1
