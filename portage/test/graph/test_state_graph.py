# Copyright: 2006 Gentoo Foundation
# License: GPL2
# $Id:$

from twisted.trial import unittest
from portage.package.atom import atom
from portage.ebuild.conditionals import DepSet
from portage.graph.state_graph import combinations
if not hasattr(__builtins__, "set"):
	from sets import Set as set

class CombinationsTest(unittest.TestCase):

	test_input = {
		"|| ( a ( b c ) )":("a","b c"),
		"|| ( ( a b ) c ( d e ) )":("a b", "c", "d e"),
		"|| ( a ( b c ) ( d e ) )":("a", "b c", "d e") ,
		"|| ( a b ) ( c d )":("a c d", "b c d"),
		"a || ( b c )":("a b","a c")
	}

	def get_combinations(self, depstring):
		d = DepSet(depstring, atom)
		return combinations(d)

	def test_combinations(self):
		for depstring, comb_strings in self.test_input.iteritems():
			comb = self.get_combinations(depstring)
			comb_known_good = set()
			for comb_string in comb_strings:
				comb_known_good.update(self.get_combinations(comb_string))
			self.assertEquals(comb,comb_known_good)
