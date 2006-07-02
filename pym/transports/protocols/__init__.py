# Copyright 2006 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Id: portage_const.py 3483 2006-06-10 21:40:40Z genone $

from random import shuffle
import sys

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
		if proto.getName() in Protocol._protocols.keys():
			raise Exception("protocol %s is already registered" % proto.getName())
		Protocol._protocols[proto.getName()] = proto
	register = classmethod(register)
	
	def getProtocol(self, name):
		return Protocol._protocols[name.lower()]
	getProtocol = classmethod(getProtocol)
	
	def addFetcher(self, fetcher):
		self._fetchers[fetcher.getName()] = fetcher
		if self._preferred == None:
			self._preferred = fetcher.getName()
	
	def setPreferredFetcher(self, name):
		if not self._fetchers.has_key(name):
			raise Exception("Fetcher %s not associated with protocol %s" % (name, self._name))
		else:
			self._preferred = name

	def fetch(self, uri, destination, resume=False, cleanup=False, failover=False, fd=sys.stdout):
		from transports import fetch, uriparse
		if len(self._fetchers.keys()) == 0:
			raise Exception("No fetcher defined for protocol %s." % self._name)
		if uriparse(uri)[0].lower() != self._name:
			raise Exception("URI %s doesn't match protocol %s." % (uri, self._name))

		fetcher = self._fetchers[self._preferred]
		if failover:
			try:
				return fetcher.fetch(uri, destination, resume, cleanup, fd)
			except FetchException, e:
				for f in self._fetchers.keys():
					if f == self._preferred:
						continue
					try:
						return self._fetchers[f].fetch(uri, destination, resume, cleanup, fd)
					except FetchException, e:
						pass
				raise
		else:
			return fetcher.fetch(uri, destination, resume, cleanup)
