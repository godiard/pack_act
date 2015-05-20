#!/usr/bin/env python

import os
from ConfigParser import ConfigParser, ParsingError

# Parameters:
# a directory, where are the activty sources
# the distribution
# the packge name

# in this case will be
activity_sources_path = './sugarlabs-calculate'
distribution = 'debian'
package_name = 'sugar-calculate-activity'

ACT_SECTION = 'Activity'

# read activity.info file
activity_info_path = os.path.join(activity_sources_path,
                                  'activity/activity.info')
if not os.path.exists(activity_info_path):
    print "FATAL ERROR: no activity.info file available on path '%s'" % \
        activity_info_path
    exit()

activity_info = ConfigParser()
activity_info.readfp(open(activity_info_path))
activity_version = activity_info.get(ACT_SECTION, 'activity_version')
print "Activity version", activity_version

# create the directory to work
data_path = os.path.join(package_name, distribution)
if not os.path.exists(data_path):
    os.makedirs(data_path)

if distribution == 'debian':
    # changelog

    # compat
    with open(os.path.join(data_path, 'compat'), 'w') as compat_file:
        compat_file.write('8\n')
    # control
    # control.in
    # gbp.conf
    # README.source
    # rules
    # source
    # watch
else:
    print "Distribution '%s' unknown" % distribution
