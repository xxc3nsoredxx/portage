# Copyright 1999-2012 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2

from __future__ import print_function

import platform
import sys

import portage
portage.proxy.lazyimport.lazyimport(globals(),
	'logging',
	'portage.util:writemsg_level',
	'textwrap',
	'_emerge.actions:load_emerge_config,run_action,' + \
		'validate_ebuild_environment',
	'_emerge.help:help@emerge_help',
)
from portage import os

if sys.hexversion >= 0x3000000:
	long = int

options=[
"--alphabetical",
"--ask-enter-invalid",
"--buildpkgonly",
"--changed-use",
"--changelog",    "--columns",
"--debug",
"--digest",
"--emptytree",
"--fetchonly",    "--fetch-all-uri",
"--ignore-default-opts",
"--noconfmem",
"--newuse",
"--nodeps",       "--noreplace",
"--nospinner",    "--oneshot",
"--onlydeps",     "--pretend",
"--quiet-repo-display",
"--quiet-unmerge-warn",
"--resume",
"--searchdesc",
"--skipfirst",
"--tree",
"--unordered-display",
"--update",
"--verbose",
"--verbose-main-repo-display",
]

shortmapping={
"1":"--oneshot",
"B":"--buildpkgonly",
"c":"--depclean",
"C":"--unmerge",
"d":"--debug",
"e":"--emptytree",
"f":"--fetchonly", "F":"--fetch-all-uri",
"h":"--help",
"l":"--changelog",
"n":"--noreplace", "N":"--newuse",
"o":"--onlydeps",  "O":"--nodeps",
"p":"--pretend",   "P":"--prune",
"r":"--resume",
"s":"--search",    "S":"--searchdesc",
"t":"--tree",
"u":"--update",
"v":"--verbose",   "V":"--version"
}

COWSAY_MOO = """

  Larry loves Gentoo (%s)

 _______________________
< Have you mooed today? >
 -----------------------
        \   ^__^
         \  (oo)\_______
            (__)\       )\/\ 
                ||----w |
                ||     ||

"""

def multiple_actions(action1, action2):
	sys.stderr.write("\n!!! Multiple actions requested... Please choose one only.\n")
	sys.stderr.write("!!! '%s' or '%s'\n\n" % (action1, action2))
	sys.exit(1)

def insert_optional_args(args):
	"""
	Parse optional arguments and insert a value if one has
	not been provided. This is done before feeding the args
	to the optparse parser since that parser does not support
	this feature natively.
	"""

	class valid_integers(object):
		def __contains__(self, s):
			try:
				return int(s) >= 0
			except (ValueError, OverflowError):
				return False

	valid_integers = valid_integers()

	class valid_floats(object):
		def __contains__(self, s):
			try:
				return float(s) >= 0
			except (ValueError, OverflowError):
				return False

	valid_floats = valid_floats()

	y_or_n = ('y', 'n',)

	new_args = []

	default_arg_opts = {
		'--ask'                  : y_or_n,
		'--autounmask'           : y_or_n,
		'--autounmask-keep-masks': y_or_n,
		'--autounmask-unrestricted-atoms' : y_or_n,
		'--autounmask-write'     : y_or_n,
		'--buildpkg'             : y_or_n,
		'--complete-graph'       : y_or_n,
		'--deep'       : valid_integers,
		'--depclean-lib-check'   : y_or_n,
		'--deselect'             : y_or_n,
		'--binpkg-respect-use'   : y_or_n,
		'--fail-clean'           : y_or_n,
		'--getbinpkg'            : y_or_n,
		'--getbinpkgonly'        : y_or_n,
		'--jobs'       : valid_integers,
		'--keep-going'           : y_or_n,
		'--load-average'         : valid_floats,
		'--package-moves'        : y_or_n,
		'--quiet'                : y_or_n,
		'--quiet-build'          : y_or_n,
		'--rebuild-if-new-slot': y_or_n,
		'--rebuild-if-new-rev'   : y_or_n,
		'--rebuild-if-new-ver'   : y_or_n,
		'--rebuild-if-unbuilt'   : y_or_n,
		'--rebuilt-binaries'     : y_or_n,
		'--root-deps'  : ('rdeps',),
		'--select'               : y_or_n,
		'--selective'            : y_or_n,
		"--use-ebuild-visibility": y_or_n,
		'--usepkg'               : y_or_n,
		'--usepkgonly'           : y_or_n,
	}

	short_arg_opts = {
		'D' : valid_integers,
		'j' : valid_integers,
	}

	# Don't make things like "-kn" expand to "-k n"
	# since existence of -n makes it too ambiguous.
	short_arg_opts_n = {
		'a' : y_or_n,
		'b' : y_or_n,
		'g' : y_or_n,
		'G' : y_or_n,
		'k' : y_or_n,
		'K' : y_or_n,
		'q' : y_or_n,
	}

	arg_stack = args[:]
	arg_stack.reverse()
	while arg_stack:
		arg = arg_stack.pop()

		default_arg_choices = default_arg_opts.get(arg)
		if default_arg_choices is not None:
			new_args.append(arg)
			if arg_stack and arg_stack[-1] in default_arg_choices:
				new_args.append(arg_stack.pop())
			else:
				# insert default argument
				new_args.append('True')
			continue

		if arg[:1] != "-" or arg[:2] == "--":
			new_args.append(arg)
			continue

		match = None
		for k, arg_choices in short_arg_opts.items():
			if k in arg:
				match = k
				break

		if match is None:
			for k, arg_choices in short_arg_opts_n.items():
				if k in arg:
					match = k
					break

		if match is None:
			new_args.append(arg)
			continue

		if len(arg) == 2:
			new_args.append(arg)
			if arg_stack and arg_stack[-1] in arg_choices:
				new_args.append(arg_stack.pop())
			else:
				# insert default argument
				new_args.append('True')
			continue

		# Insert an empty placeholder in order to
		# satisfy the requirements of optparse.

		new_args.append("-" + match)
		opt_arg = None
		saved_opts = None

		if arg[1:2] == match:
			if match not in short_arg_opts_n and arg[2:] in arg_choices:
				opt_arg = arg[2:]
			else:
				saved_opts = arg[2:]
				opt_arg = "True"
		else:
			saved_opts = arg[1:].replace(match, "")
			opt_arg = "True"

		if opt_arg is None and arg_stack and \
			arg_stack[-1] in arg_choices:
			opt_arg = arg_stack.pop()

		if opt_arg is None:
			new_args.append("True")
		else:
			new_args.append(opt_arg)

		if saved_opts is not None:
			# Recycle these on arg_stack since they
			# might contain another match.
			arg_stack.append("-" + saved_opts)

	return new_args

def _find_bad_atoms(atoms, less_strict=False):
	"""
	Declares all atoms as invalid that have an operator,
	a use dependency, a blocker or a repo spec.
	It accepts atoms with wildcards.
	In less_strict mode it accepts operators and repo specs.
	"""
	bad_atoms = []
	for x in ' '.join(atoms).split():
		bad_atom = False
		try:
			atom = portage.dep.Atom(x, allow_wildcard=True, allow_repo=less_strict)
		except portage.exception.InvalidAtom:
			try:
				atom = portage.dep.Atom("*/"+x, allow_wildcard=True, allow_repo=less_strict)
			except portage.exception.InvalidAtom:
				bad_atom = True

		if bad_atom or (atom.operator and not less_strict) or atom.blocker or atom.use:
			bad_atoms.append(x)
	return bad_atoms


def parse_opts(tmpcmdline, silent=False):
	myaction=None
	myopts = {}
	myfiles=[]

	actions = frozenset([
		"clean", "check-news", "config", "depclean", "help",
		"info", "list-sets", "metadata", "moo",
		"prune", "regen",  "search",
		"sync",  "unmerge", "version",
	])

	longopt_aliases = {"--cols":"--columns", "--skip-first":"--skipfirst"}
	y_or_n = ("y", "n")
	true_y_or_n = ("True", "y", "n")
	true_y = ("True", "y")
	argument_options = {

		"--ask": {
			"shortopt" : "-a",
			"help"    : "prompt before performing any actions",
			"type"    : "choice",
			"choices" : true_y_or_n
		},

		"--autounmask": {
			"help"    : "automatically unmask packages",
			"type"    : "choice",
			"choices" : true_y_or_n
		},

		"--autounmask-unrestricted-atoms": {
			"help"    : "write autounmask changes with >= atoms if possible",
			"type"    : "choice",
			"choices" : true_y_or_n
		},

		"--autounmask-keep-masks": {
			"help"    : "don't add package.unmask entries",
			"type"    : "choice",
			"choices" : true_y_or_n
		},

		"--autounmask-write": {
			"help"    : "write changes made by --autounmask to disk",
			"type"    : "choice",
			"choices" : true_y_or_n
		},

		"--accept-properties": {
			"help":"temporarily override ACCEPT_PROPERTIES",
			"action":"store"
		},

		"--backtrack": {

			"help"   : "Specifies how many times to backtrack if dependency " + \
				"calculation fails ",

			"action" : "store"
		},

		"--buildpkg": {
			"shortopt" : "-b",
			"help"     : "build binary packages",
			"type"     : "choice",
			"choices"  : true_y_or_n
		},

		"--buildpkg-exclude": {
			"help"   :"A space separated list of package atoms for which " + \
				"no binary packages should be built. This option overrides all " + \
				"possible ways to enable building of binary packages.",

			"action" : "append"
		},

		"--config-root": {
			"help":"specify the location for portage configuration files",
			"action":"store"
		},
		"--color": {
			"help":"enable or disable color output",
			"type":"choice",
			"choices":("y", "n")
		},

		"--complete-graph": {
			"help"    : "completely account for all known dependencies",
			"type"    : "choice",
			"choices" : true_y_or_n
		},

		"--complete-graph-if-new-use": {
			"help"    : "trigger --complete-graph behavior if USE or IUSE will change for an installed package",
			"type"    : "choice",
			"choices" : y_or_n
		},

		"--complete-graph-if-new-ver": {
			"help"    : "trigger --complete-graph behavior if an installed package version will change (upgrade or downgrade)",
			"type"    : "choice",
			"choices" : y_or_n
		},

		"--deep": {

			"shortopt" : "-D",

			"help"   : "Specifies how deep to recurse into dependencies " + \
				"of packages given as arguments. If no argument is given, " + \
				"depth is unlimited. Default behavior is to skip " + \
				"dependencies of installed packages.",

			"action" : "store"
		},

		"--depclean-lib-check": {
			"help"    : "check for consumers of libraries before removing them",
			"type"    : "choice",
			"choices" : true_y_or_n
		},

		"--deselect": {
			"help"    : "remove atoms/sets from the world file",
			"type"    : "choice",
			"choices" : true_y_or_n
		},

		"--dynamic-deps": {
			"help": "substitute the dependencies of installed packages with the dependencies of unbuilt ebuilds",
			"type": "choice",
			"choices": y_or_n
		},

		"--exclude": {
			"help"   :"A space separated list of package names or slot atoms. " + \
				"Emerge won't  install any ebuild or binary package that " + \
				"matches any of the given package atoms.",

			"action" : "append"
		},

		"--fail-clean": {
			"help"    : "clean temp files after build failure",
			"type"    : "choice",
			"choices" : true_y_or_n
		},

		"--ignore-built-slot-operator-deps": {
			"help": "Ignore the slot/sub-slot := operator parts of dependencies that have "
				"been recorded when packages where built. This option is intended "
				"only for debugging purposes, and it only affects built packages "
				"that specify slot/sub-slot := operator dependencies using the "
				"experimental \"4-slot-abi\" EAPI.",
			"type": "choice",
			"choices": y_or_n
		},

		"--jobs": {

			"shortopt" : "-j",

			"help"   : "Specifies the number of packages to build " + \
				"simultaneously.",

			"action" : "store"
		},

		"--keep-going": {
			"help"    : "continue as much as possible after an error",
			"type"    : "choice",
			"choices" : true_y_or_n
		},

		"--load-average": {

			"help"   :"Specifies that no new builds should be started " + \
				"if there are other builds running and the load average " + \
				"is at least LOAD (a floating-point number).",

			"action" : "store"
		},

		"--misspell-suggestions": {
			"help"    : "enable package name misspell suggestions",
			"type"    : "choice",
			"choices" : ("y", "n")
		},

		"--with-bdeps": {
			"help":"include unnecessary build time dependencies",
			"type":"choice",
			"choices":("y", "n")
		},
		"--reinstall": {
			"help":"specify conditions to trigger package reinstallation",
			"type":"choice",
			"choices":["changed-use"]
		},

		"--reinstall-atoms": {
			"help"   :"A space separated list of package names or slot atoms. " + \
				"Emerge will treat matching packages as if they are not " + \
				"installed, and reinstall them if necessary. Implies --deep.",

			"action" : "append",
		},

		"--binpkg-respect-use": {
			"help"    : "discard binary packages if their use flags \
				don't match the current configuration",
			"type"    : "choice",
			"choices" : true_y_or_n
		},

		"--getbinpkg": {
			"shortopt" : "-g",
			"help"     : "fetch binary packages",
			"type"     : "choice",
			"choices"  : true_y_or_n
		},

		"--getbinpkgonly": {
			"shortopt" : "-G",
			"help"     : "fetch binary packages only",
			"type"     : "choice",
			"choices"  : true_y_or_n
		},

		"--usepkg-exclude": {
			"help"   :"A space separated list of package names or slot atoms. " + \
				"Emerge will ignore matching binary packages. ",

			"action" : "append",
		},

		"--rebuild-exclude": {
			"help"   :"A space separated list of package names or slot atoms. " + \
				"Emerge will not rebuild these packages due to the " + \
				"--rebuild flag. ",

			"action" : "append",
		},

		"--rebuild-ignore": {
			"help"   :"A space separated list of package names or slot atoms. " + \
				"Emerge will not rebuild packages that depend on matching " + \
				"packages due to the --rebuild flag. ",

			"action" : "append",
		},

		"--package-moves": {
			"help"     : "perform package moves when necessary",
			"type"     : "choice",
			"choices"  : true_y_or_n
		},

		"--quiet": {
			"shortopt" : "-q",
			"help"     : "reduced or condensed output",
			"type"     : "choice",
			"choices"  : true_y_or_n
		},

		"--quiet-build": {
			"help"     : "redirect build output to logs",
			"type"     : "choice",
			"choices"  : true_y_or_n,
		},

		"--rebuild-if-new-slot": {
			"help"     : ("Automatically rebuild or reinstall packages when slot/sub-slot := "
				"operator dependencies can be satisfied by a newer slot, so that "
				"older packages slots will become eligible for removal by the "
				"--depclean action as soon as possible."),
			"type"     : "choice",
			"choices"  : true_y_or_n
		},

		"--rebuild-if-new-rev": {
			"help"     : "Rebuild packages when dependencies that are " + \
				"used at both build-time and run-time are built, " + \
				"if the dependency is not already installed with the " + \
				"same version and revision.",
			"type"     : "choice",
			"choices"  : true_y_or_n
		},

		"--rebuild-if-new-ver": {
			"help"     : "Rebuild packages when dependencies that are " + \
				"used at both build-time and run-time are built, " + \
				"if the dependency is not already installed with the " + \
				"same version. Revision numbers are ignored.",
			"type"     : "choice",
			"choices"  : true_y_or_n
		},

		"--rebuild-if-unbuilt": {
			"help"     : "Rebuild packages when dependencies that are " + \
				"used at both build-time and run-time are built.",
			"type"     : "choice",
			"choices"  : true_y_or_n
		},

		"--rebuilt-binaries": {
			"help"     : "replace installed packages with binary " + \
			             "packages that have been rebuilt",
			"type"     : "choice",
			"choices"  : true_y_or_n
		},
		
		"--rebuilt-binaries-timestamp": {
			"help"   : "use only binaries that are newer than this " + \
			           "timestamp for --rebuilt-binaries",
			"action" : "store"
		},

		"--root": {
		 "help"   : "specify the target root filesystem for merging packages",
		 "action" : "store"
		},

		"--root-deps": {
			"help"    : "modify interpretation of depedencies",
			"type"    : "choice",
			"choices" :("True", "rdeps")
		},

		"--select": {
			"help"    : "add specified packages to the world set " + \
			            "(inverse of --oneshot)",
			"type"    : "choice",
			"choices" : true_y_or_n
		},

		"--selective": {
			"help"    : "identical to --noreplace",
			"type"    : "choice",
			"choices" : true_y_or_n
		},

		"--use-ebuild-visibility": {
			"help"     : "use unbuilt ebuild metadata for visibility checks on built packages",
			"type"     : "choice",
			"choices"  : true_y_or_n
		},

		"--useoldpkg-atoms": {
			"help"   :"A space separated list of package names or slot atoms. " + \
				"Emerge will prefer matching binary packages over newer unbuilt packages. ",

			"action" : "append",
		},

		"--usepkg": {
			"shortopt" : "-k",
			"help"     : "use binary packages",
			"type"     : "choice",
			"choices"  : true_y_or_n
		},

		"--usepkgonly": {
			"shortopt" : "-K",
			"help"     : "use only binary packages",
			"type"     : "choice",
			"choices"  : true_y_or_n
		},
	}

	from optparse import OptionParser
	parser = OptionParser()
	if parser.has_option("--help"):
		parser.remove_option("--help")

	for action_opt in actions:
		parser.add_option("--" + action_opt, action="store_true",
			dest=action_opt.replace("-", "_"), default=False)
	for myopt in options:
		parser.add_option(myopt, action="store_true",
			dest=myopt.lstrip("--").replace("-", "_"), default=False)
	for shortopt, longopt in shortmapping.items():
		parser.add_option("-" + shortopt, action="store_true",
			dest=longopt.lstrip("--").replace("-", "_"), default=False)
	for myalias, myopt in longopt_aliases.items():
		parser.add_option(myalias, action="store_true",
			dest=myopt.lstrip("--").replace("-", "_"), default=False)

	for myopt, kwargs in argument_options.items():
		shortopt = kwargs.pop("shortopt", None)
		args = [myopt]
		if shortopt is not None:
			args.append(shortopt)
		parser.add_option(dest=myopt.lstrip("--").replace("-", "_"),
			*args, **kwargs)

	tmpcmdline = insert_optional_args(tmpcmdline)

	myoptions, myargs = parser.parse_args(args=tmpcmdline)

	if myoptions.ask in true_y:
		myoptions.ask = True
	else:
		myoptions.ask = None

	if myoptions.autounmask in true_y:
		myoptions.autounmask = True

	if myoptions.autounmask_unrestricted_atoms in true_y:
		myoptions.autounmask_unrestricted_atoms = True

	if myoptions.autounmask_keep_masks in true_y:
		myoptions.autounmask_keep_masks = True

	if myoptions.autounmask_write in true_y:
		myoptions.autounmask_write = True

	if myoptions.buildpkg in true_y:
		myoptions.buildpkg = True

	if myoptions.buildpkg_exclude:
		bad_atoms = _find_bad_atoms(myoptions.buildpkg_exclude, less_strict=True)
		if bad_atoms and not silent:
			parser.error("Invalid Atom(s) in --buildpkg-exclude parameter: '%s'\n" % \
				(",".join(bad_atoms),))

	if myoptions.changed_use is not False:
		myoptions.reinstall = "changed-use"
		myoptions.changed_use = False

	if myoptions.deselect in true_y:
		myoptions.deselect = True

	if myoptions.binpkg_respect_use is not None:
		if myoptions.binpkg_respect_use in true_y:
			myoptions.binpkg_respect_use = 'y'
		else:
			myoptions.binpkg_respect_use = 'n'

	if myoptions.complete_graph in true_y:
		myoptions.complete_graph = True
	else:
		myoptions.complete_graph = None

	if myoptions.depclean_lib_check in true_y:
		myoptions.depclean_lib_check = True

	if myoptions.exclude:
		bad_atoms = _find_bad_atoms(myoptions.exclude)
		if bad_atoms and not silent:
			parser.error("Invalid Atom(s) in --exclude parameter: '%s' (only package names and slot atoms (with wildcards) allowed)\n" % \
				(",".join(bad_atoms),))

	if myoptions.reinstall_atoms:
		bad_atoms = _find_bad_atoms(myoptions.reinstall_atoms)
		if bad_atoms and not silent:
			parser.error("Invalid Atom(s) in --reinstall-atoms parameter: '%s' (only package names and slot atoms (with wildcards) allowed)\n" % \
				(",".join(bad_atoms),))

	if myoptions.rebuild_exclude:
		bad_atoms = _find_bad_atoms(myoptions.rebuild_exclude)
		if bad_atoms and not silent:
			parser.error("Invalid Atom(s) in --rebuild-exclude parameter: '%s' (only package names and slot atoms (with wildcards) allowed)\n" % \
				(",".join(bad_atoms),))

	if myoptions.rebuild_ignore:
		bad_atoms = _find_bad_atoms(myoptions.rebuild_ignore)
		if bad_atoms and not silent:
			parser.error("Invalid Atom(s) in --rebuild-ignore parameter: '%s' (only package names and slot atoms (with wildcards) allowed)\n" % \
				(",".join(bad_atoms),))

	if myoptions.usepkg_exclude:
		bad_atoms = _find_bad_atoms(myoptions.usepkg_exclude)
		if bad_atoms and not silent:
			parser.error("Invalid Atom(s) in --usepkg-exclude parameter: '%s' (only package names and slot atoms (with wildcards) allowed)\n" % \
				(",".join(bad_atoms),))

	if myoptions.useoldpkg_atoms:
		bad_atoms = _find_bad_atoms(myoptions.useoldpkg_atoms)
		if bad_atoms and not silent:
			parser.error("Invalid Atom(s) in --useoldpkg-atoms parameter: '%s' (only package names and slot atoms (with wildcards) allowed)\n" % \
				(",".join(bad_atoms),))

	if myoptions.fail_clean in true_y:
		myoptions.fail_clean = True

	if myoptions.getbinpkg in true_y:
		myoptions.getbinpkg = True
	else:
		myoptions.getbinpkg = None

	if myoptions.getbinpkgonly in true_y:
		myoptions.getbinpkgonly = True
	else:
		myoptions.getbinpkgonly = None

	if myoptions.keep_going in true_y:
		myoptions.keep_going = True
	else:
		myoptions.keep_going = None

	if myoptions.package_moves in true_y:
		myoptions.package_moves = True

	if myoptions.quiet in true_y:
		myoptions.quiet = True
	else:
		myoptions.quiet = None

	if myoptions.quiet_build in true_y:
		myoptions.quiet_build = 'y'

	if myoptions.rebuild_if_new_slot in true_y:
		myoptions.rebuild_if_new_slot = 'y'

	if myoptions.rebuild_if_new_ver in true_y:
		myoptions.rebuild_if_new_ver = True
	else:
		myoptions.rebuild_if_new_ver = None

	if myoptions.rebuild_if_new_rev in true_y:
		myoptions.rebuild_if_new_rev = True
		myoptions.rebuild_if_new_ver = None
	else:
		myoptions.rebuild_if_new_rev = None

	if myoptions.rebuild_if_unbuilt in true_y:
		myoptions.rebuild_if_unbuilt = True
		myoptions.rebuild_if_new_rev = None
		myoptions.rebuild_if_new_ver = None
	else:
		myoptions.rebuild_if_unbuilt = None

	if myoptions.rebuilt_binaries in true_y:
		myoptions.rebuilt_binaries = True

	if myoptions.root_deps in true_y:
		myoptions.root_deps = True

	if myoptions.select in true_y:
		myoptions.select = True
		myoptions.oneshot = False
	elif myoptions.select == "n":
		myoptions.oneshot = True

	if myoptions.selective in true_y:
		myoptions.selective = True

	if myoptions.backtrack is not None:

		try:
			backtrack = int(myoptions.backtrack)
		except (OverflowError, ValueError):
			backtrack = -1

		if backtrack < 0:
			backtrack = None
			if not silent:
				parser.error("Invalid --backtrack parameter: '%s'\n" % \
					(myoptions.backtrack,))

		myoptions.backtrack = backtrack

	if myoptions.deep is not None:
		deep = None
		if myoptions.deep == "True":
			deep = True
		else:
			try:
				deep = int(myoptions.deep)
			except (OverflowError, ValueError):
				deep = -1

		if deep is not True and deep < 0:
			deep = None
			if not silent:
				parser.error("Invalid --deep parameter: '%s'\n" % \
					(myoptions.deep,))

		myoptions.deep = deep

	if myoptions.jobs:
		jobs = None
		if myoptions.jobs == "True":
			jobs = True
		else:
			try:
				jobs = int(myoptions.jobs)
			except ValueError:
				jobs = -1

		if jobs is not True and \
			jobs < 1:
			jobs = None
			if not silent:
				parser.error("Invalid --jobs parameter: '%s'\n" % \
					(myoptions.jobs,))

		myoptions.jobs = jobs

	if myoptions.load_average == "True":
		myoptions.load_average = None

	if myoptions.load_average:
		try:
			load_average = float(myoptions.load_average)
		except ValueError:
			load_average = 0.0

		if load_average <= 0.0:
			load_average = None
			if not silent:
				parser.error("Invalid --load-average parameter: '%s'\n" % \
					(myoptions.load_average,))

		myoptions.load_average = load_average
	
	if myoptions.rebuilt_binaries_timestamp:
		try:
			rebuilt_binaries_timestamp = int(myoptions.rebuilt_binaries_timestamp)
		except ValueError:
			rebuilt_binaries_timestamp = -1

		if rebuilt_binaries_timestamp < 0:
			rebuilt_binaries_timestamp = 0
			if not silent:
				parser.error("Invalid --rebuilt-binaries-timestamp parameter: '%s'\n" % \
					(myoptions.rebuilt_binaries_timestamp,))

		myoptions.rebuilt_binaries_timestamp = rebuilt_binaries_timestamp

	if myoptions.use_ebuild_visibility in true_y:
		myoptions.use_ebuild_visibility = True
	else:
		# None or "n"
		pass

	if myoptions.usepkg in true_y:
		myoptions.usepkg = True
	else:
		myoptions.usepkg = None

	if myoptions.usepkgonly in true_y:
		myoptions.usepkgonly = True
	else:
		myoptions.usepkgonly = None

	for myopt in options:
		v = getattr(myoptions, myopt.lstrip("--").replace("-", "_"))
		if v:
			myopts[myopt] = True

	for myopt in argument_options:
		v = getattr(myoptions, myopt.lstrip("--").replace("-", "_"), None)
		if v is not None:
			myopts[myopt] = v

	if myoptions.searchdesc:
		myoptions.search = True

	for action_opt in actions:
		v = getattr(myoptions, action_opt.replace("-", "_"))
		if v:
			if myaction:
				multiple_actions(myaction, action_opt)
				sys.exit(1)
			myaction = action_opt

	if myaction is None and myoptions.deselect is True:
		myaction = 'deselect'

	if myargs and isinstance(myargs[0], bytes):
		for i in range(len(myargs)):
			myargs[i] = portage._unicode_decode(myargs[i])

	myfiles += myargs

	return myaction, myopts, myfiles

def profile_check(trees, myaction):
	if myaction in ("help", "info", "search", "sync", "version"):
		return os.EX_OK
	for root_trees in trees.values():
		if root_trees["root_config"].settings.profiles:
			continue
		# generate some profile related warning messages
		validate_ebuild_environment(trees)
		msg = ("Your current profile is invalid. If you have just changed "
			"your profile configuration, you should revert back to the "
			"previous configuration. Allowed actions are limited to "
			"--help, --info, --search, --sync, and --version.")
		writemsg_level("".join("!!! %s\n" % l for l in textwrap.wrap(msg, 70)),
			level=logging.ERROR, noiselevel=-1)
		return 1
	return os.EX_OK

def emerge_main(args=None):
	"""
	@param args: command arguments (default: sys.argv[1:])
	@type args: list
	"""
	if args is None:
		args = sys.argv[1:]

	portage._disable_legacy_globals()
	portage._internal_warnings = True
	# Disable color until we're sure that it should be enabled (after
	# EMERGE_DEFAULT_OPTS has been parsed).
	portage.output.havecolor = 0

	# This first pass is just for options that need to be known as early as
	# possible, such as --config-root.  They will be parsed again later,
	# together with EMERGE_DEFAULT_OPTS (which may vary depending on the
	# the value of --config-root).
	myaction, myopts, myfiles = parse_opts(args, silent=True)
	if "--debug" in myopts:
		os.environ["PORTAGE_DEBUG"] = "1"
	if "--config-root" in myopts:
		os.environ["PORTAGE_CONFIGROOT"] = myopts["--config-root"]
	if "--root" in myopts:
		os.environ["ROOT"] = myopts["--root"]
	if "--accept-properties" in myopts:
		os.environ["ACCEPT_PROPERTIES"] = myopts["--accept-properties"]

	# optimize --help (no need to load config / EMERGE_DEFAULT_OPTS)
	if myaction == "help":
		emerge_help()
		return os.EX_OK
	elif myaction == "moo":
		print(COWSAY_MOO % platform.system())
		return os.EX_OK

	# Portage needs to ensure a sane umask for the files it creates.
	os.umask(0o22)
	if myaction == "sync":
		portage._sync_disabled_warnings = True
	settings, trees, mtimedb = load_emerge_config()
	rval = profile_check(trees, myaction)
	if rval != os.EX_OK:
		return rval

	tmpcmdline = []
	if "--ignore-default-opts" not in myopts:
		tmpcmdline.extend(settings["EMERGE_DEFAULT_OPTS"].split())
	tmpcmdline.extend(args)
	myaction, myopts, myfiles = parse_opts(tmpcmdline)

	# skip global updates prior to sync, since it's called after sync
	if myaction not in ('help', 'info', 'sync', 'version') and \
		myopts.get('--package-moves') != 'n' and \
		_global_updates(trees, mtimedb["updates"], quiet=("--quiet" in myopts)):
		mtimedb.commit()
		# Reload the whole config from scratch.
		settings, trees, mtimedb = load_emerge_config(trees=trees)
		portdb = trees[settings['EROOT']]['porttree'].dbapi

	xterm_titles = "notitles" not in settings.features
	if xterm_titles:
		xtermTitle("emerge")

	if "--digest" in myopts:
		os.environ["FEATURES"] = os.environ.get("FEATURES","") + " digest"
		# Reload the whole config from scratch so that the portdbapi internal
		# config is updated with new FEATURES.
		settings, trees, mtimedb = load_emerge_config(trees=trees)
		portdb = trees[settings['EROOT']]['porttree'].dbapi

	# NOTE: adjust_configs() can map options to FEATURES, so any relevant
	# options adjustments should be made prior to calling adjust_configs().
	if "--buildpkgonly" in myopts:
		myopts["--buildpkg"] = True

	adjust_configs(myopts, trees)
	apply_priorities(settings)

	if 'force-multilib' in settings.features:
		if settings.get("NO_AUTO_FLAG", "") is "":
			writemsg_level(bad("!!! Failed to find vars from extra profile") + "\n",level=logging.ERROR, noiselevel=-1)
			writemsg_level(bad("!!! Please make sure that you did follow the instructions and included the extra profile\n"),level=logging.ERROR, noiselevel=-1)
			writemsg_level(bad("!!! http://git.overlays.gentoo.org/gitweb/?p=proj/multilib-portage.git;a=blob;f=doc/portage-multilib-instructions\n"),level=logging.ERROR, noiselevel=-1)
			writemsg_level(bad("!!! has some basic instructions for the setup\n"),level=logging.ERROR, noiselevel=-1)
			return 1

	if myaction == 'version':
		writemsg_stdout(getportageversion(
			settings["PORTDIR"], None,
			settings.profile_path, settings["CHOST"],
			trees[settings['EROOT']]['vartree'].dbapi) + '\n', noiselevel=-1)
		return 0
	elif myaction == 'help':
		_emerge.help.help()
		return 0

	spinner = stdout_spinner()
	if "candy" in settings.features:
		spinner.update = spinner.update_scroll

	if "--quiet" not in myopts:
		portage.deprecated_profile_check(settings=settings)
		if portage.const._ENABLE_REPO_NAME_WARN:
			# Bug #248603 - Disable warnings about missing
			# repo_name entries for stable branch.
			repo_name_check(trees)
		repo_name_duplicate_check(trees)
		config_protect_check(trees)
	check_procfs()

	if "getbinpkg" in settings.features:
		myopts["--getbinpkg"] = True

	if "--getbinpkgonly" in myopts:
		myopts["--getbinpkg"] = True

	if "--getbinpkgonly" in myopts:
		myopts["--usepkgonly"] = True

	if "--getbinpkg" in myopts:
		myopts["--usepkg"] = True

	if "--usepkgonly" in myopts:
		myopts["--usepkg"] = True

	if "--buildpkgonly" in myopts:
		# --buildpkgonly will not merge anything, so
		# it cancels all binary package options.
		for opt in ("--getbinpkg", "--getbinpkgonly",
			"--usepkg", "--usepkgonly"):
			myopts.pop(opt, None)

	for mytrees in trees.values():
		mydb = mytrees["porttree"].dbapi
		# Freeze the portdbapi for performance (memoize all xmatch results).
		mydb.freeze()

		if myaction in ('search', None) and \
			"--usepkg" in myopts:
			# Populate the bintree with current --getbinpkg setting.
			# This needs to happen before expand_set_arguments(), in case
			# any sets use the bintree.
			mytrees["bintree"].populate(
				getbinpkgs="--getbinpkg" in myopts)

	del mytrees, mydb

	if "moo" in myfiles:
		print(COWSAY_MOO % platform.system())
		msg = ("The above `emerge moo` display is deprecated. "
			"Please use `emerge --moo` instead.")
		for line in textwrap.wrap(msg, 50):
			print(" %s %s" % (colorize("WARN", "*"), line))

	for x in myfiles:
		ext = os.path.splitext(x)[1]
		if (ext == ".ebuild" or ext == ".tbz2") and os.path.exists(os.path.abspath(x)):
			print(colorize("BAD", "\n*** emerging by path is broken and may not always work!!!\n"))
			break

	root_config = trees[settings['EROOT']]['root_config']
	if myaction == "moo":
		print(COWSAY_MOO % platform.system())
		return os.EX_OK
	elif myaction == "list-sets":
		writemsg_stdout("".join("%s\n" % s for s in sorted(root_config.sets)))
		return os.EX_OK
	elif myaction == "check-news":
		news_counts = count_unread_news(
			root_config.trees["porttree"].dbapi,
			root_config.trees["vartree"].dbapi)
		if any(news_counts.values()):
			display_news_notifications(news_counts)
		elif "--quiet" not in myopts:
			print("", colorize("GOOD", "*"), "No news items were found.")
		return os.EX_OK

	ensure_required_sets(trees)

	# only expand sets for actions taking package arguments
	oldargs = myfiles[:]
	if myaction in ("clean", "config", "depclean", "info", "prune", "unmerge", None):
		myfiles, retval = expand_set_arguments(myfiles, myaction, root_config)
		if retval != os.EX_OK:
			return retval

		# Need to handle empty sets specially, otherwise emerge will react 
		# with the help message for empty argument lists
		if oldargs and not myfiles:
			print("emerge: no targets left after set expansion")
			return 0

	if ("--tree" in myopts) and ("--columns" in myopts):
		print("emerge: can't specify both of \"--tree\" and \"--columns\".")
		return 1

	if '--emptytree' in myopts and '--noreplace' in myopts:
		writemsg_level("emerge: can't specify both of " + \
			"\"--emptytree\" and \"--noreplace\".\n",
			level=logging.ERROR, noiselevel=-1)
		return 1

	if ("--quiet" in myopts):
		spinner.update = spinner.update_quiet
		portage.util.noiselimit = -1

	if "--fetch-all-uri" in myopts:
		myopts["--fetchonly"] = True

	if "--skipfirst" in myopts and "--resume" not in myopts:
		myopts["--resume"] = True

	# Allow -p to remove --ask
	if "--pretend" in myopts:
		myopts.pop("--ask", None)

	# forbid --ask when not in a terminal
	# note: this breaks `emerge --ask | tee logfile`, but that doesn't work anyway.
	if ("--ask" in myopts) and (not sys.stdin.isatty()):
		portage.writemsg("!!! \"--ask\" should only be used in a terminal. Exiting.\n",
			noiselevel=-1)
		return 1

	if settings.get("PORTAGE_DEBUG", "") == "1":
		spinner.update = spinner.update_quiet
		portage.util.noiselimit = 0
		if "python-trace" in settings.features:
			import portage.debug as portage_debug
			portage_debug.set_trace(True)

	if not ("--quiet" in myopts):
		if '--nospinner' in myopts or \
			settings.get('TERM') == 'dumb' or \
			not sys.stdout.isatty():
			spinner.update = spinner.update_basic

	if "--debug" in myopts:
		print("myaction", myaction)
		print("myopts", myopts)

	if not myaction and not myfiles and "--resume" not in myopts:
		_emerge.help.help()
		return 1

	pretend = "--pretend" in myopts
	fetchonly = "--fetchonly" in myopts or "--fetch-all-uri" in myopts
	buildpkgonly = "--buildpkgonly" in myopts

	# check if root user is the current user for the actions where emerge needs this
	if portage.secpass < 2:
		# We've already allowed "--version" and "--help" above.
		if "--pretend" not in myopts and myaction not in ("search","info"):
			need_superuser = myaction in ('clean', 'depclean', 'deselect',
				'prune', 'unmerge') or not \
				(fetchonly or \
				(buildpkgonly and secpass >= 1) or \
				myaction in ("metadata", "regen", "sync"))
			if portage.secpass < 1 or \
				need_superuser:
				if need_superuser:
					access_desc = "superuser"
				else:
					access_desc = "portage group"
				# Always show portage_group_warning() when only portage group
				# access is required but the user is not in the portage group.
				from portage.data import portage_group_warning
				if "--ask" in myopts:
					writemsg_stdout("This action requires %s access...\n" % \
						(access_desc,), noiselevel=-1)
					if portage.secpass < 1 and not need_superuser:
						portage_group_warning()
					if userquery("Would you like to add --pretend to options?",
						"--ask-enter-invalid" in myopts) == "No":
						return 128 + signal.SIGINT
					myopts["--pretend"] = True
					del myopts["--ask"]
				else:
					sys.stderr.write(("emerge: %s access is required\n") \
						% access_desc)
					if portage.secpass < 1 and not need_superuser:
						portage_group_warning()
					return 1

	# Disable emergelog for everything except build or unmerge operations.
	# This helps minimize parallel emerge.log entries that can confuse log
	# parsers like genlop.
	disable_emergelog = False
	for x in ("--pretend", "--fetchonly", "--fetch-all-uri"):
		if x in myopts:
			disable_emergelog = True
			break
	if disable_emergelog:
		pass
	elif myaction in ("search", "info"):
		disable_emergelog = True
	elif portage.data.secpass < 1:
		disable_emergelog = True

	_emerge.emergelog._disable = disable_emergelog

	if not disable_emergelog:
		if 'EMERGE_LOG_DIR' in settings:
			try:
				# At least the parent needs to exist for the lock file.
				portage.util.ensure_dirs(settings['EMERGE_LOG_DIR'])
			except portage.exception.PortageException as e:
				writemsg_level("!!! Error creating directory for " + \
					"EMERGE_LOG_DIR='%s':\n!!! %s\n" % \
					(settings['EMERGE_LOG_DIR'], e),
					noiselevel=-1, level=logging.ERROR)
				portage.util.ensure_dirs(_emerge.emergelog._emerge_log_dir)
			else:
				_emerge.emergelog._emerge_log_dir = settings["EMERGE_LOG_DIR"]
		else:
			_emerge.emergelog._emerge_log_dir = os.path.join(os.sep,
				settings["EPREFIX"].lstrip(os.sep), "var", "log")
			portage.util.ensure_dirs(_emerge.emergelog._emerge_log_dir)

	if not "--pretend" in myopts:
		emergelog(xterm_titles, "Started emerge on: "+\
			_unicode_decode(
				time.strftime("%b %d, %Y %H:%M:%S", time.localtime()),
				encoding=_encodings['content'], errors='replace'))
		myelogstr=""
		if myopts:
			opt_list = []
			for opt, arg in myopts.items():
				if arg is True:
					opt_list.append(opt)
				elif isinstance(arg, list):
					# arguments like --exclude that use 'append' action
					for x in arg:
						opt_list.append("%s=%s" % (opt, x))
				else:
					opt_list.append("%s=%s" % (opt, arg))
			myelogstr=" ".join(opt_list)
		if myaction:
			myelogstr += " --" + myaction
		if myfiles:
			myelogstr += " " + " ".join(oldargs)
		emergelog(xterm_titles, " *** emerge " + myelogstr)
	del oldargs

	def emergeexitsig(signum, frame):
		signal.signal(signal.SIGINT, signal.SIG_IGN)
		signal.signal(signal.SIGTERM, signal.SIG_IGN)
		portage.util.writemsg("\n\nExiting on signal %(signal)s\n" % {"signal":signum})
		sys.exit(128 + signum)
	signal.signal(signal.SIGINT, emergeexitsig)
	signal.signal(signal.SIGTERM, emergeexitsig)

	def emergeexit():
		"""This gets out final log message in before we quit."""
		if "--pretend" not in myopts:
			emergelog(xterm_titles, " *** terminating.")
		if xterm_titles:
			xtermTitleReset()
	portage.atexit_register(emergeexit)

	if myaction in ("config", "metadata", "regen", "sync"):
		if "--pretend" in myopts:
			sys.stderr.write(("emerge: The '%s' action does " + \
				"not support '--pretend'.\n") % myaction)
			return 1

	if "sync" == myaction:
		return action_sync(settings, trees, mtimedb, myopts, myaction)
	elif "metadata" == myaction:
		action_metadata(settings, portdb, myopts)
	elif myaction=="regen":
		validate_ebuild_environment(trees)
		return action_regen(settings, portdb, myopts.get("--jobs"),
			myopts.get("--load-average"))
	# HELP action
	elif "config"==myaction:
		validate_ebuild_environment(trees)
		action_config(settings, trees, myopts, myfiles)

	# SEARCH action
	elif "search"==myaction:
		validate_ebuild_environment(trees)
		action_search(trees[settings['EROOT']]['root_config'],
			myopts, myfiles, spinner)

	elif myaction in ('clean', 'depclean', 'deselect', 'prune', 'unmerge'):
		validate_ebuild_environment(trees)
		rval = action_uninstall(settings, trees, mtimedb["ldpath"],
			myopts, myaction, myfiles, spinner)
		if not (myaction == 'deselect' or buildpkgonly or fetchonly or pretend):
			post_emerge(myaction, myopts, myfiles, settings['EROOT'],
				trees, mtimedb, rval)
		return rval

	elif myaction == 'info':

		# Ensure atoms are valid before calling unmerge().
		vardb = trees[settings['EROOT']]['vartree'].dbapi
		portdb = trees[settings['EROOT']]['porttree'].dbapi
		bindb = trees[settings['EROOT']]["bintree"].dbapi
		valid_atoms = []
		for x in myfiles:
			if is_valid_package_atom(x, allow_repo=True):
				try:
					#look at the installed files first, if there is no match
					#look at the ebuilds, since EAPI 4 allows running pkg_info
					#on non-installed packages
					valid_atom = dep_expand(x, mydb=vardb, settings=settings)
					if valid_atom.cp.split("/")[0] == "null":
						valid_atom = dep_expand(x, mydb=portdb, settings=settings)
					if valid_atom.cp.split("/")[0] == "null" and "--usepkg" in myopts:
						valid_atom = dep_expand(x, mydb=bindb, settings=settings)
					valid_atoms.append(valid_atom)
				except portage.exception.AmbiguousPackageName as e:
					msg = "The short ebuild name \"" + x + \
						"\" is ambiguous.  Please specify " + \
						"one of the following " + \
						"fully-qualified ebuild names instead:"
					for line in textwrap.wrap(msg, 70):
						writemsg_level("!!! %s\n" % (line,),
							level=logging.ERROR, noiselevel=-1)
					for i in e.args[0]:
						writemsg_level("    %s\n" % colorize("INFORM", i),
							level=logging.ERROR, noiselevel=-1)
					writemsg_level("\n", level=logging.ERROR, noiselevel=-1)
					return 1
				continue
			msg = []
			msg.append("'%s' is not a valid package atom." % (x,))
			msg.append("Please check ebuild(5) for full details.")
			writemsg_level("".join("!!! %s\n" % line for line in msg),
				level=logging.ERROR, noiselevel=-1)
			return 1

		return action_info(settings, trees, myopts, valid_atoms)

	# "update", "system", or just process files:
	else:
		validate_ebuild_environment(trees)

		for x in myfiles:
			if x.startswith(SETPREFIX) or \
				is_valid_package_atom(x, allow_repo=True):
				continue
			if x[:1] == os.sep:
				continue
			try:
				os.lstat(x)
				continue
			except OSError:
				pass
			msg = []
			msg.append("'%s' is not a valid package atom." % (x,))
			msg.append("Please check ebuild(5) for full details.")
			writemsg_level("".join("!!! %s\n" % line for line in msg),
				level=logging.ERROR, noiselevel=-1)
			return 1

		# GLEP 42 says to display news *after* an emerge --pretend
		if "--pretend" not in myopts:
			display_news_notification(root_config, myopts)
		retval = action_build(settings, trees, mtimedb,
			myopts, myaction, myfiles, spinner)
		post_emerge(myaction, myopts, myfiles, settings['EROOT'],
			trees, mtimedb, retval)

		return retval
