# Copyright: 2005 Gentoo Foundation
# Author(s): Jeff Oliver (kaiserfro@yahoo.com)
# License: GPL2
# $Id$
from portage.repository import multiplex
from repository import tree as vdb_repository
from virtualrepository import tree as virtualrepository

def repository(*args, **kwargs):
	r = vdb_repository(*args, **kwargs)
	return multiplex.tree(r, virtualrepository(r))
