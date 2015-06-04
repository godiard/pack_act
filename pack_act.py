#!/usr/bin/env python

import sys
import os
from ConfigParser import ConfigParser, ParsingError
import subprocess
import datetime
import urllib

import licenses

# Parameters:
# a directory, where are the activty sources
# the distribution

ACT_SECTION = 'Activity'
PKG_SECTION = 'Package'
MAINT_SECTION = 'Maintainer'

def read_activity_info(activity_sources_path):
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


def read_distro_info(activity_sources_path, distro):
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


def write_debian_changelog(data_path, activity_info, distro_info):
    activity_version = activity_info.get(ACT_SECTION, 'activity_version')
    pkg_version = distro_info.get(PKG_SECTION, 'version')
    package_name = distro_info.get(PKG_SECTION, 'name')
    # TODO: change by run dch -vb activity_version~pkg_version
    # or a way to concatenate the information on newer versions

    with open(os.path.join(data_path, 'changelog'), 'w') as changelog_file:
        changelog_file.write('%s (%s~%s) UNRELEASED; urgency=low\n\n' %
                             (package_name, activity_version, pkg_version))
        changelog_file.write('  * Initial version for Debian.\n\n')

        now = datetime.datetime.now()
        changelog_file.write(' -- %s <%s>  %s\n' % (
            distro_info.get(MAINT_SECTION, 'name'),
            distro_info.get(MAINT_SECTION, 'email'),
            now.strftime('%a, %d %b %Y %H:%M:%S -0300')))
        # Format should be (TODO tz pending)
        # Tue, 19 May 2015 13:17:48 -0300

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


def write_debian_rules(data_path, activity_info, distro_info,
                       activity_sources_path):
    with open(os.path.join(data_path, 'rules'), 'w') as rules_file:
        header = """#!/usr/bin/make -f
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

        if os.path.exists(os.path.join(activity_sources_path, 'activity',
                                       'mimetypes.xml')):
            # TODO: replace with a better solution
            rules_file.write('# Exclude updated mime database files\n')
            rules_file.write('DEB_DH_ALWAYS_EXCLUDE=usr/share/mime\n')

        rules_file.write('# Suppress unneeded auto-resolved build-dependency '
                         'on python-dev\n')
        rules_file.write(
            'CDBS_BUILD_DEPENDS_class_python-sugar_python = python\n\n')

        activity_type = activity_info.get(ACT_SECTION, 'activity_type')
        if activity_type == 'gtk2':
            # gtk2
            rules_file.write('# Override Sugar toolkit to use\n')
            rules_file.write('CDBS_BUILD_DEPENDS_class_python-sugar_sugar = '
                             'python-sugar-0.98, python-sugar-toolkit-0.98, '
                             'unzip\n\n')

            rules_file.write('# Needed (always/often/seldom) at runtime\n')
            rules_file.write('CDBS_DEPENDS_$(pkg) = python, python-gobject-2, '
                             'python-gtk2, python-cairo, python-sugar-0.98, '
                             'python-sugar-toolkit-0.98\n')
        elif activity_type == 'gtk3':
            # gtk3
            rules_file.write('# Override Sugar toolkit to use\n')
            rules_file.write('CDBS_BUILD_DEPENDS_class_python-sugar_sugar = '
                             'python-sugar3, unzip\n\n')

            rules_file.write('# Needed (always/often/seldom) at runtime\n')
            rules_file.write('CDBS_DEPENDS_$(pkg) = python, python-sugar3, '
                             'python-gi, python-cairo\n')

            rules_file.write('CDBS_DEPENDS_$(pkg) +=, gir1.2-glib-2.0, '
                             'gir1.2-gtk-3.0, gir1.2-pango-1.0, '
                             'gir1.2-gdkpixbuf-2.0\n')
        else:
            print 'activity_type "%s" not supported' % activity_type

        if distro_info.has_option(PKG_SECTION, 'dependencies'):
            activity_dependencies = distro_info.get(PKG_SECTION,
                                                    'dependencies')
            dependency_list = activity_dependencies.split(',')

            # here we should add the dependencies common to the activities
            dependencies_map = {
                'gstreamer':
                    'gir1.2-gstreamer-1.0, gir1.2-gst-plugins-base-1.0, '
                    'gstreamer1.0-plugins-base, gstreamer1.0-plugins-good, '
                    'libgstreamer1.0-0',
                'pygame': 'python-pygame',
                'telepathy': 'python-telepathy',
                'webkit': 'gir1.2-webkit-3.0',
                'webkit2': 'gir1.2-webkit2-3.0',
                'espeak': 'gst-plugins-espeak'}

            # Verify every dependency included in the .info file
            # if is found in the map add the value, if not add as found
            for dependency in dependency_list:
                dependency = dependency.strip()
                if dependency in dependencies_map:
                    dependency = dependencies_map[dependency]
                rules_file.write('CDBS_DEPENDS_$(pkg) +=, %s\n' %
                                 dependency)


        rules_file.write('CDBS_RECOMMENDS_$(pkg) +=, '
                         'sugar-$(DEB_SUGAR_PRIMARY_BRANCH)-icon-theme | '
                         'sugar-icon-theme\n')

    # set +x permission
    os.chmod(os.path.join(data_path, 'rules'), 0755)


def write_debian_format(data_path):
    source_path = os.path.join(data_path, 'source')
    if not os.path.exists(source_path):
        os.makedirs(source_path)
    with open(os.path.join(source_path, 'format'), 'w') as format_file:
        format_file.write('3.0 (quilt)\n')


def write_debian_watch(data_path, activity_info):
    with open(os.path.join(data_path, 'watch'), 'w') as watch_file:
        watch_file.write(
            '# run the "uscan" command to check for upstream updates '
            'and more.\n')
        watch_file.write('version=3\n')
        watch_file.write('%s%s-(.*).%s\n' % (
            activity_info.get(ACT_SECTION, 'sources_url'),
            activity_info.get(ACT_SECTION, 'name'),
            activity_info.get(ACT_SECTION, 'sources_format')))


def write_debian_copyright(data_path, activity_info,
                           distro_info, activity_sources_path):
    # try create a copyright file so close as possible to
    # the packages used in sugar activities in debian
    # reference:
    # http://anonscm.debian.org/cgit/collab-maint/
    #   sugar-memorize-activity.git/tree/debian/copyright

    if not activity_info.has_option(ACT_SECTION, 'license'):
        print "FATAL: no option 'license' in activity.info"
        exit()

    if os.path.exists(os.path.join(
            activity_sources_path, 'LICENSE')):
        license_file_path = os.path.join(
            '/usr/share/sugar/activities/'
            '%s.activity' % activity_info.get(ACT_SECTION, 'name'),
            'LICENSE')
    else:
        license = activity_info.get(ACT_SECTION, 'license')

        # licenses in /usr/share/common-licenses/
        # valid for applications
        # Apache-2.0, BSD, GPL, GPL-1, GPL-2, GPL-3, Artistic
        if license.lower().find('apache') > -1:
            license_file = 'Apache-2.0'
        elif license.lower().find('bsd') > -1:
            license_file = 'BSD'
        elif license.lower().find('artistic') > -1:
            license_file = 'Artistic'
        elif license.lower().find('gpl') > -1:
            if license.find('1') > -1:
                license_file = 'GPL-1'
            elif license.find('2') > -1:
                license_file = 'GPL-2'
            elif license.find('3') > -1:
                license_file = 'GPL-3'
            else:
                license_file = 'GPL'
        else:
            # TODO: what do if can't recognize the license?
            license_file = 'GPL'
        license_file_path = os.path.join(
            '/usr/share/common-licenses/', license_file)

    # check licenses in the sources
    copyrights = {}
    _check_copyright_on_file(activity_sources_path, copyrights)

    # write the license file
    with open(os.path.join(data_path, 'copyright'), 'w') as copyright_file:
        copyright_file.write('Name: %s\n' % distro_info.get(
            PKG_SECTION, 'name'))
        copyright_file.write('Maintainer: %s <%s>\n' % (
            activity_info.get(MAINT_SECTION, 'name'),
            activity_info.get(MAINT_SECTION, 'email')))
        copyright_file.write(
            'Source: %s\n\n\n' % activity_info.get(ACT_SECTION, 'sources_url'))

        if copyrights:
            for file_name in copyrights.keys():
                rights_for_file = copyrights[file_name]
                file_name = file_name[file_name.find('/') + 1:]
                first_line = True
                copyright_file.write('Files: %s\n' % file_name)
                for right in rights_for_file:
                    right = right.strip()
                    if first_line:
                        copyright_file.write('Copyright: %s\n' %
                                             right[right.find('('):])
                    else:
                        copyright_file.write('           %s\n' %
                                             right[right.find('('):])
                    first_line = False
                copyright_file.write('License: %s\n\n' % license)

        # general license
        copyright_file.write('Files: *\n')
        copyright_file.write('Copyright: %s\n' % activity_info.get(
            MAINT_SECTION, 'name'))
        copyright_file.write('License: %s\n' % license)
        now = datetime.datetime.now()
        year = now.strftime('%Y')
        if license_file in ['GPL', 'GPL-1', 'GPL-2', 'GPL-3']:
            if license_file == 'GPL-1':
                gpl_version = 1
            elif license_file == 'GPL-2':
                gpl_version = 2
            else:
                gpl_version = 3
            license_summary = licenses.GPL % (
                year, activity_info.get(MAINT_SECTION, 'name'), gpl_version)
        elif license_file == 'BSD':
            license_summary = licenses.BSD
        elif  license_file == 'Apache-2.0':
            license_summary = licenses.APACHE % (
                year, activity_info.get(MAINT_SECTION, 'name'))
        else:
            license_summary = ''

        if license_summary:
            for line in license_summary.split('\n'):
                copyright_file.write(' %s\n' % line)

        copyright_file.write(' On Debian systems, the complete version of '
                             'the license can be found\n in the file "%s"\n' %
                             license_file_path)


def _check_copyright_on_file(path, copyrights):
     for name in os.listdir(path):
        new_path = os.path.join(path, name)
        if name in ['po', 'locale', 'screenshots', '.git']:
            continue
        if os.path.isdir(new_path):
             _check_copyright_on_file(new_path, copyrights)
        else:
            # read the file line by line
            with open(new_path) as source_file:
                for line in source_file:
                    if line.startswith('# Copyright'):
                        if new_path in copyrights:
                            copyrights[new_path].append(line)
                        else:
                            copyrights[new_path] = [line]


def prepare_debian(activity_info, distro_info):
    # download the sources
    download_url = activity_info.get(ACT_SECTION, 'sources_url') + \
        activity_info.get(ACT_SECTION, 'name') + "-" + \
        activity_info.get(ACT_SECTION, 'activity_version') + "."+ \
        activity_info.get(ACT_SECTION, 'sources_format')
    file_name = distro_info.get(PKG_SECTION, 'name') + "_" + \
        activity_info.get(ACT_SECTION, 'activity_version') + "~" + \
        distro_info.get(PKG_SECTION, 'version') + ".orig."+ \
        activity_info.get(ACT_SECTION, 'sources_format')
    if os.path.exists(file_name):
        print "Sources file %s already downloaded" % file_name
    else:
        print "Downloading %s ...." % download_url
        urllib.urlretrieve(download_url, file_name)

def main(argv):
    distro = 'debian'
    if len(argv) > 1:
        activity_sources_path = argv[1]
    else:
        print "Usage pack_act activity_sources_dir [distribution]"
        print "  distribution only debian right now"
        exit()

    if len(argv) > 2:
        distro = argv[2]

    activity_info = read_activity_info(activity_sources_path)
    activity_version = activity_info.get(ACT_SECTION, 'activity_version')
    print "Activity version", activity_version

    distro_info = read_distro_info(activity_sources_path, distro)
    pkg_version = distro_info.get(PKG_SECTION, 'version')
    package_name = distro_info.get(PKG_SECTION, 'name')
    print "Package version", pkg_version

    # create the directory to work
    data_path = os.path.join(package_name, distro)
    if not os.path.exists(data_path):
        os.makedirs(data_path)

    if distro == 'debian':
        prepare_debian(activity_info, distro_info)
        # copyright
        write_debian_copyright(data_path, activity_info,
                               distro_info, activity_sources_path)
        # changelog
        write_debian_changelog(data_path, activity_info, distro_info)
        # compat
        write_debian_compat(data_path)
        # gbp.conf
        write_debian_gdb_conf(data_path)
        # control.in
        write_debian_control_in(data_path, activity_info, distro_info)
        # README.source
        write_debian_readme_source(data_path)
        # rules
        write_debian_rules(data_path, activity_info, distro_info,
                           activity_sources_path)
        # source/format
        write_debian_format(data_path)
        # watch
        write_debian_watch(data_path, activity_info)

        command = ['debian/rules', 'pre-build', 'DEB_MAINTAINER_MODE=1']
        p = subprocess.Popen(command,cwd=package_name)
        command = ['debian/rules', 'clean', 'DEB_MAINTAINER_MODE=1']
        p = subprocess.Popen(command,cwd=package_name)

    else:
        print "Distribution '%s' unknown" % distro

main(sys.argv)
