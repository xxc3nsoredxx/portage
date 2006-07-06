# Copyright 2006 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Id: portage_const.py 3761 2006-07-02 19:40:56Z genone $

from transports import Fetcher, FetchException, uriparse, FETCH_OK, FETCH_FAILED
from transports.protocols.file import protocol
import os, shutil, sys

class FileFetcher(Fetcher):
	_protos = ["file"]

	def __init__(self, name, func):
		self._name = name
		self._func = func

	def _fetch(self, uri, destination, resume=False, fd=sys.stdout):
		rval = FETCH_FAILED
		proto, loc, name = uriparse(uri)
		src = os.path.join(os.sep, loc, name)
		fd.write("%s file %s to %s ...\n" % (self._name, src, destination))
		rval = self._func(src, destination)
		return rval

copyfetcher = FileFetcher("Copy", shutil.copy2)
hardlinkfetcher = FileFetcher("Hardlink", os.link)
symlinkfetcher = FileFetcher("Symlink", os.symlink)

protocol.addFetcher(hardlinkfetcher)
protocol.addFetcher(symlinkfetcher)
protocol.addFetcher(copyfetcher)
protocol.setPreferredFetcher("Hardlink")
