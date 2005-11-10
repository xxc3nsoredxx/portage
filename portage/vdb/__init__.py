# Copyright: 2005 Gentoo Foundation
# License: GPL2
# $Id$

from portage.repository import multiplex
from repository import tree as vdb_repository
from virtualrepository import tree as virtualrepository

def repository(*args, **kwargs):
	r = vdb_repository(*args, **kwargs)
	return multiplex.tree(r, virtualrepository(r))
