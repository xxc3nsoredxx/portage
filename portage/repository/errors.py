# Copyright: 2005 Gentoo Foundation
# License: GPL2
# $Id$

class TreeCorruption(Exception):
	def __init__(self, err):
		self.err = err
	def __str__(self):
		return "unexpected tree corruption: %s" % str(self.err)

class InitializationError(TreeCorruption):
	def __str__(self):
		return "initialization failed: %s" % str(self.err)
