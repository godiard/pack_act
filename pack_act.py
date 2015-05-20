#!/usr/bin/env python

import os
from ConfigParser import ConfigParser, ParsingError

# Parameters:
# a directory, where are the activty sources
# the distribution
# the packge name

# in this case will be
activity_sources_path = './sugarlabs-calculate'
distro = 'debian'
package_name = 'sugar-calculate-activity'

ACT_SECTION = 'Activity'
PKG_SECTION = 'Package'

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
    # TODO: check previous changes
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


activity_info = read_activity_info()
activity_version = activity_info.get(ACT_SECTION, 'activity_version')
print "Activity version", activity_version

distro_info = read_distro_info()
pkg_version = distro_info.get(PKG_SECTION, 'version')
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


    # README.source
    # rules
    # source
    # watch
else:
    print "Distribution '%s' unknown" % distro
