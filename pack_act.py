#!/usr/bin/env python

import os
from ConfigParser import ConfigParser, ParsingError

# Parameters:
# a directory, where are the activty sources
# the distribution

# in this case will be
activity_sources_path = './sugarlabs-calculate'
distro = 'debian'

ACT_SECTION = 'Activity'
PKG_SECTION = 'Package'
MAINT_SECTION = 'Maintainer'

def read_activity_info():
    # read activity.info file
    activity_info_path = os.path.join(activity_sources_path,
                                      'activity/activity.info')
    if not os.path.exists(activity_info_path):
        print "FATAL ERROR: no activity.info file available on path '%s'" % \
            activity_info_path
        raise
    activity_info = ConfigParser()
    activity_info.readfp(open(activity_info_path))
    return activity_info


def read_distro_info():
# read $distro.info file
    distro_info_path = os.path.join(activity_sources_path,
                                      'activity/%s.info' % distro)
    if not os.path.exists(distro_info_path):
        print "FATAL ERROR: no %s.info file available on path '%s'" % \
            (distro, distro_info_path)
        exit()

    distro_info = ConfigParser()
    distro_info.readfp(open(distro_info_path))
    return distro_info


def write_debian_changelog(data_path, package_name, activity_version,
                           pkg_version):
    # TODO: change by run ch -vb activity_version~pkg_version
    with open(os.path.join(data_path, 'changelog'), 'w') as changelog_file:
        changelog_file.write('%s (%s-%s) UNRELEASED; urgency=low\n\n' %
                             (package_name, activity_version, pkg_version))
        changelog_file.write('  * Initial version for Debian.\n')


def write_debian_compat(data_path):
    # compat
    with open(os.path.join(data_path, 'compat'), 'w') as compat_file:
        compat_file.write('8\n')


def write_debian_gdb_conf(data_path):
    # gbp.conf
    gbp_content = """# Configuration file for git-buildpackage and friends

[DEFAULT]
pristine-tar = True
sign-tags = True

[git-buildpackage]
compression = bzip2
"""
    with open(os.path.join(data_path, 'gbp.conf'), 'w') as gbp_conf_file:
        gbp_conf_file.write(gbp_content)


def write_debian_readme_source(data_path):
    # README.source
    content = """CDBS+git-buildpackage
---------------------

This source package uses CDBS and git-buildpackage.  NMUs need not (but
are encouraged to) make special use of these tools.  In particular, the
debian/control.in file can be completely ignored.

More info here: http://wiki.debian.org/CDBS+git-buildpackage


 -- Jonas Smedegaard <dr@jones.dk>  Mon, 18 Feb 2013 12:55:37 +0100"""
    with open(os.path.join(data_path, 'README.source'), 'w') as readme_file:
        readme_file.write(content)


def write_debian_control_in(data_path, activity_info, distro_info):
    with open(os.path.join(data_path, 'control.in'), 'w') as control_in_file:
        control_in_file.write('Source: %s\n' %
                              distro_info.get(PKG_SECTION, 'name'))
        control_in_file.write('Section: x11\n')
        control_in_file.write('Priority: optional\n')
        control_in_file.write('Maintainer: %s <%s>\n' % (
            distro_info.get(MAINT_SECTION, 'name'),
            distro_info.get(MAINT_SECTION, 'email')))

        uploaders = distro_info.get(MAINT_SECTION, 'uploaders')
        if uploaders.find('\n') > -1:
            uploaders = uploaders.replace('\n', '\n ')
        control_in_file.write('Uploaders: %s\n' % uploaders)

        control_in_file.write('Build-Depends: @cdbs@\n')
        control_in_file.write('Standards-Version: 3.9.6\n')
        control_in_file.write('Vcs-Git: %s\n' %
                              distro_info.get(PKG_SECTION, 'vcs-git'))
        control_in_file.write('Vcs-Browser: %s\n' %
                              distro_info.get(PKG_SECTION, 'vcs-browser'))
        control_in_file.write('Homepage: %s\n' %
                              activity_info.get(ACT_SECTION, 'homepage'))
        control_in_file.write('XS-Python-Version: all\n\n')
        control_in_file.write('Package: %s\n' %
                              distro_info.get(PKG_SECTION, 'name'))
        control_in_file.write('Architecture: all\n')

        control_in_file.write('Depends: ${shlibs:Depends},\n'
                              ' ${python:Depends},\n'
                              ' ${cdbs:Depends},\n'
                              ' ${misc:Depends}\n')
        control_in_file.write('Recommends: ${cdbs:Recommends}\n')
        control_in_file.write('Provides: ${python:Provides},\n'
                              ' ${cdbs:Provides}\n')
        control_in_file.write('Conflicts: ${cdbs:Conflicts}\n')
        control_in_file.write('Replaces: ${cdbs:Replaces}\n')
        long_description = activity_info.get(ACT_SECTION,
                                             'long_description')
        if long_description.find('\n') > -1:
            long_description = long_description.replace('\n', '\n ')
        control_in_file.write('Description: %s\n' % long_description)


def write_debian_rules(data_path, activity_info, distro_info):
    with open(os.path.join(data_path, 'rules'), 'w') as rules_file:
        header = "#" * 83 + "\n" + \
"""#!/usr/bin/make -f
# -*- mode: makefile; coding: utf-8 -*-
# Copyright 2008-2012, 2015 Jonas Smedegaard <dr@jones.dk>
# Copyright 2015 Martin Abente Lahaye <tch@sugarlabs.org>
# Description: Main Debian packaging script for %s
# This file was generated by pack_act.py
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>."""
        rules_file.write(header % activity_info.get(ACT_SECTION, 'name'))

        rules_file.write(
            '\n\n# These need to be declared before CDBS includes\n')
        rules_file.write('pkg = $(DEB_SOURCE_PACKAGE)\n')
        rules_file.write('DEB_PYTHON_SUGAR_PACKAGES = $(pkg)\n\n')

        rules_file.write(
            'include /usr/share/cdbs/1/rules/upstream-tarball.mk\n')
        rules_file.write(
            'include /usr/share/cdbs/1/rules/utils.mk\n')
        rules_file.write(
            'include /usr/share/cdbs/1/class/python-sugar.mk\n')
        rules_file.write(
            'include /usr/share/cdbs/1/rules/debhelper.mk\n\n')

        rules_file.write('DEB_SUGAR_PRIMARY_BRANCH = %s\n' %
                         distro_info.get(PKG_SECTION, 'primary_branch'))
        rules_file.write('DEB_UPSTREAM_PACKAGE = %s\n' %
                         activity_info.get(ACT_SECTION, 'name'))
        rules_file.write('DEB_UPSTREAM_URL = %s$(DEB_UPSTREAM_PACKAGE)\n' %
                         activity_info.get(ACT_SECTION, 'sources_url'))
        rules_file.write('DEB_UPSTREAM_TARBALL_EXTENSION = %s\n\n' %
                         activity_info.get(ACT_SECTION, 'sources_format'))

        rules_file.write('# Suppress unneeded auto-resolved build-dependency '
                         'on python-dev\n')
        rules_file.write(
            'CDBS_BUILD_DEPENDS_class_python-sugar_python = python\n\n')

        rules_file.write('# Override Sugar toolkit to use\n')
        rules_file.write('CDBS_BUILD_DEPENDS_class_python-sugar_sugar = '
                         'python-sugar-0.98, python-sugar-toolkit-0.98, '
                         'unzip\n\n')

        rules_file.write('# Needed (always/often/seldom) at runtime\n')
        rules_file.write('CDBS_DEPENDS_$(pkg) = python, python-gobject-2, '
                         'python-gtk2, python-cairo, python-sugar-0.98, '
                         'python-sugar-toolkit-0.98\n')
        rules_file.write('CDBS_RECOMMENDS_$(pkg) +=, '
                         'sugar-$(DEB_SUGAR_PRIMARY_BRANCH)-icon-theme | '
                         'sugar-icon-theme\n')




activity_info = read_activity_info()
activity_version = activity_info.get(ACT_SECTION, 'activity_version')
print "Activity version", activity_version

distro_info = read_distro_info()
pkg_version = distro_info.get(PKG_SECTION, 'version')
package_name = distro_info.get(PKG_SECTION, 'name')
print "Package version", pkg_version

# create the directory to work
data_path = os.path.join(package_name, distro)
if not os.path.exists(data_path):
    os.makedirs(data_path)

if distro == 'debian':
    # changelog
    write_debian_changelog(data_path, package_name, activity_version,
                           pkg_version)
    # compat
    write_debian_compat(data_path)
    # gbp.conf
    write_debian_gdb_conf(data_path)
    # control.in
    write_debian_control_in(data_path, activity_info, distro_info)
    # README.source
    write_debian_readme_source(data_path)
    # rules
    write_debian_rules(data_path, activity_info, distro_info)
    # source

    # watch
else:
    print "Distribution '%s' unknown" % distro
