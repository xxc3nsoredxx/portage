# Copyright 2006 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Id: portage_const.py 3761 2006-07-02 19:40:56Z genone $

from transports.protocols import Protocol

protocol = Protocol("file")
Protocol.register(protocol)
