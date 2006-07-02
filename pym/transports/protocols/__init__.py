# Copyright 2006 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Id: portage_const.py 3483 2006-06-10 21:40:40Z genone $

from transports import fetch, uriparse

class Protocol(object):
	_protocols = {}
	
	def __init__(self, name):
		self._name = name.lower()
		self._fetchers = {}
		self._preferred = None
	
	def getName(self):
		return self._name
	
	def register(self, proto):
		if not isinstance(proto, Protocol):
			raise TypeError("argument isn't a Protocol instance")
		if proto.getName() in _protocols.keys():
			raise Exception("protocol %s is already registered" % proto.getName())
		_protocols[proto.getName()] = proto
	register = classmethod(register)
	
	def getProtocol(self, name):
		return _protocols[name.lower()]
	getProtocol = classmethod(getProtocol)
	
	def addFetcher(self, fetcher):
		self._fetchers[fetcher.getName()] = fetcher
		if self._preferred == None:
			self._preferred = name
	
	def setPreferredFetcher(self, name):
		if not self._fetchers.has_key(name):
			raise Exception("Fetcher %s not associated with protocol %s" % (name, self._name))
		else:
			self._preferred = name

	def fetch(self, uri, destination, resume=False, cleanup=False, failover=False):
		if len(self._fetchers.keys()) == 0:
			raise Exception("No fetcher defined for protocol %s." % self._name)
		if uriparse(uri)[0].lower() != self._name:
			raise Exception("URI %s doesn't match protocol %s." % (uri, self._name))

		fetcher = self._fetchers[self._preferred]
		if failover:
			try:
				return fetcher.fetch(uri, destination, resume, cleanup)
			except FetchException, e:
				for f in self._fetchers.keys():
					if f == self._preferred:
						continue
					try:
						return self._fetchers[f].fetch(uri, destination, resume, cleanup)
					except FetchException, e:
						pass
				raise
		else:
			return fetcher.fetch(uri, destination, resume, cleanup)

class MirrorProtocol(Protocol):
	def __init__(self, mirrormap)
		self._name = "mirror"
		self._mirrormap = mirrormap

	def fetch(self, uri, destination, resume=False, cleanup=False, failover=False):
		# name and loc are different than when used inside uriparse()
		proto, name, loc = uriparse(uri)
		if proto != "mirror":
			raise Exception("URI %s is not a mirrored URI." % uri)
		
		uris = self._getURIList(name, loc)
		
		for myuri in uris:
			try:
				return fetch(myuri, destination, resume, cleanup, failover)
			except FetchException, e:
				continue
		
	def _getURIList(self, name, loc):
		mirrors = []
		if self._mirrormap.has_key("local"):
			mirrors += self._mirrormap["local"]
		mirrors += self._mirrormap[name]
		
		return ["/".join(x, loc) for x in mirrors]
