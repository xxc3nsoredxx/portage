# Copyright 2006 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Id: portage_const.py 3761 2006-07-02 19:40:56Z genone $

from transports import Fetcher, FetchException, uriparse, FETCH_OK, FETCH_FAILED
from transports.protocols.http import protocol as http_protocol
from transports.protocols.ftp import protocol as ftp_protocol

import os, sys
from urllib2 import urlopen

class UrlLibFetcher(Fetcher):
	_protos = ["http", "ftp"]
	_name = "UrlLib"

	def _fetch(self, uri, destination, resume=False, fd=sys.stdout):
		rval = FETCH_FAILED
		proto, loc, name = uriparse(uri)
		if os.path.isfile(destination):
			target = destination
		else:
			target = os.path.join(destination, name)
		fd.write("Fetching %s\nto %s\nusing internal urllib handler\n\n" % (uri, target))
		try:
			fd_r = urlopen(uri)
			fd_w = open(target, "w")
			fd_w.write(fd_r.read())
			fd_w.close()
			fd_r.close()
		except SystemExit:
			pass
		except Exception, e:
			raise FetchException(str(e))
		else:
			rval = FETCH_OK
		return rval

http_protocol.addFetcher(UrlLibFetcher())
ftp_protocol.addFetcher(UrlLibFetcher())
