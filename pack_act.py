#!/usr/bin/env python

import os

# Parameters:
# a directory, where are the activty sources
# the distribution
# the packge name

# in this case will be

activity_sources_path = './sugarlabs-calculate'
distribution = 'debian'
package_name = 'sugar-calculate-activity'

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
