# Copyright: 2005 Gentoo Foundation
# License: GPL2
# $Id$

from ConfigParser import ConfigParser

class CaseSensitiveConfigParser(ConfigParser):
	def optionxform(self, val):
		return val
