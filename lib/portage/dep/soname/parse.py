# Copyright 2015 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2

from portage.exception import InvalidData
from portage.localization import _
from portage.dep.soname.SonameAtom import SonameAtom


def parse_soname_deps(s):
    """
    Parse a REQUIRES or PROVIDES dependency string, and raise
    InvalidData if necessary.

    @param s: REQUIRES or PROVIDES string
    @type s: str
    @rtype: iter
    @return: An iterator of SonameAtom instances
    """

    categories = set()
    category = None
    previous_soname = None
    for soname in s.split():
        if soname.endswith(":"):
            if category is not None and previous_soname is None:
                raise InvalidData(f"Multilib category empty: {category}")

            category = soname[:-1]
            previous_soname = None
            if category in categories:
                raise InvalidData(
                    f"Multilib category occurs more than once: {category}"
                )
            categories.add(category)

        elif category is None:
            raise InvalidData(f"Multilib category missing: {soname}")
        else:
            previous_soname = soname
            yield SonameAtom(category, soname)

    if category is not None and previous_soname is None:
        raise InvalidData(f"Multilib category empty: {category}")
