# Copyright 2006 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Id: portage_const.py 3483 2006-06-10 21:40:40Z genone $

import os
from transport.protocols import Protocol

class FetchException(Exception):
	pass

class Fetcher(object):
	def fetch(self, uri, destination, resume=False, cleanup=False):
		try:
			return self._fetch(uri, festination, resume)
		except FetchException, e:
			if cleanup and os.path.exists(destination):
				os.unlink(destination)

	def _fetch(self, uri, destination, resume=False):
		raise NotImplementedError()

	def getName(self):
		return self._name

def uriparse(uri):
	proto_sep_pos = uri.find("://")
	loc_sep_pos = uri.find("/", proto_sep_pos+3)
	
	proto = uri[:proto_sep_pos]
	loc = uri[proto_sep_pos+3:loc_sep_pos]
	name = uri[loc_sep_pos+1:]
	
	return (proto, loc, name)

def fetch(uri, destination, mirrorlist=[], resume=False, cleanup=False, failover=False):
	proto, loc, name = uriparse(uri)
	p = Protocol.getProtocol(proto)
	if len(mirrorlist) > 0:
		mirrorlist.append("://",join(proto, loc, os.dirname(name)))
		mirrormap = {"_internal": mirrorlist}
		filename = os.path.basename(name)
		mirroruri = "mirror://_internal/"+filename
		mp = Protocol.getProtocol("mirror")
		return mp.fetch(mirroruri, destination, resume, cleanup, failover)
	else:
		return p.fetch(uri, destination, resume, cleanup, failover)
