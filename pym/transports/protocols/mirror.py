# Copyright 2006 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Id: portage_const.py 3761 2006-07-02 19:40:56Z genone $

from transports.protocols import Protocol
import os, sys
from random import shuffle

class MirrorProtocol(Protocol):
	def __init__(self, mirrormap):
		self._name = "mirror"
		self._mirrormap = mirrormap

	def fetch(self, uri, destination, resume=False, cleanup=False, failover=False, fd=sys.stdout):
		from transports import fetch, FetchException
		uris = self.expandURI(uri)
		
		for myuri in uris:
			print uris
			try:
				rval = fetch(myuri, destination, mirrorlist=[], resume=resume, cleanup=cleanup, failover=failover, fd=fd)
				return rval
			except FetchException, e:
				continue
		
	def expandURI(self, uri):
		from transports import uriparse, expand_uri
		# name and loc are different than when used inside uriparse()
		proto, name, loc = uriparse(uri)
		if proto != "mirror":
			raise Exception("URI %s is not a mirrored URI." % uri)
		mirrors = []
		if self._mirrormap.has_key("local"):
			mirrors += self._mirrormap["local"]
		if name != "local":
			x = self._mirrormap[name]
			shuffle(x)
			mirrors += x
		
		rval = []
		for x in mirrors:
			rval += expand_uri(x+"/"+loc)
		return rval

protocol = None

def init(settings):
	global protocol

	from portage_const import CUSTOM_MIRRORS_FILE
	from portage_util import grabdict

	thirdpartymirrors = grabdict(os.path.join(settings["PORTDIR"], "profiles", "thirdpartymirrors"))
	custommirrors = grabdict(CUSTOM_MIRRORS_FILE)
	
	allmirrors = {}
	allmirrors.update(thirdpartymirrors)
	for k in custommirrors.keys():
		if allmirrors.has_key(k):
			allmirrors[k] = custommirrors[k]+allmirrors[k]
		else:
			allmirrors[k] = custommirrors[k]

	protocol = MirrorProtocol(allmirrors)
	Protocol.register(protocol)
