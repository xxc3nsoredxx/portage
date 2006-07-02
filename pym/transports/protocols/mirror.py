# Copyright 1998-2004 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Id: portage_const.py 3761 2006-07-02 19:40:56Z genone $

from transports.protocols import Protocol
import os

class MirrorProtocol(Protocol):
	def __init__(self, mirrormap):
		self._name = "mirror"
		self._mirrormap = mirrormap

	def fetch(self, uri, destination, resume=False, cleanup=False, failover=False, fd=sys.stdout):
		# name and loc are different than when used inside uriparse()
		proto, name, loc = uriparse(uri)
		if proto != "mirror":
			raise Exception("URI %s is not a mirrored URI." % uri)
		
		uris = self._getURIList(name, loc)
		
		for myuri in uris:
			try:
				return fetch(myuri, destination, resume, cleanup, failover, fd)
			except FetchException, e:
				continue
		
	def _getURIList(self, name, loc):
		mirrors = []
		if self._mirrormap.has_key("local"):
			mirrors += self._mirrormap["local"]
		if name != "local":
			mirrors += shuffle(self._mirrormap[name])
		
		return ["/".join(x, loc) for x in mirrors]

def init(settings):
	from portage_const import CUSTOM_MIRRORS_FILE
	from portage_util import grabdict

	thirdpartymirrors = grabdict(os.path.join(settings["PORTDIR"], "profiles", "thirdpartymirrors"))
	custommirrors = grabdict(CUSTOM_MIRRORS_FILE)
	defaultmirrors = {"_internal": settings["GENTOO_MIRRORS"]}
	
	allmirrors = {}
	allmirrors.update(thirdpartymirrors)
	allmirrors.update(custommirrors)
	allmirrors.update(defaultmirrors)

	protocol = Mirrorprotocol(allmirrors)
	Protocol.register(protocol)
