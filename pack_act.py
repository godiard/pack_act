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


def write_debian_compat():
    # compat
    with open(os.path.join(data_path, 'compat'), 'w') as compat_file:
        compat_file.write('8\n')


def write_debian_gdb_conf():
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



def write_debian_control_in(activity_info, distro_info):
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
    write_debian_compat()
    # gbp.conf
    write_debian_gdb_conf()
    # control
    # control.in
    write_debian_control_in(activity_info, distro_info)

    # README.source
    # rules
    # source
    # watch
else:
    print "Distribution '%s' unknown" % distro
