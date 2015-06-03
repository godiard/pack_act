Introduction
============

This utility would be useful to make easier create packages
for different distributions.

The first version only create the files needed by debian

Would be possible integrate some of this changes in Sugar,
working in a feature based in http://wiki.sugarlabs.org/go/Features/Activity.info

Testing instructions:
--------------------

* Clone the activity. In the example I use the Calculate activity

git clone git@github.com:godiard/sugarlabs-calculate.git

* You don't need downoad the sources and rename.

* Add the following lines to activity.info file

```
homepage = http://wiki.sugarlabs.org/go/Activities/Calculate
long_description: Sugar Learning Platform - calculate activity
 Sugar Learning Platform promotes collaborative learning through Sugar
 Activities that encourage critical thinking, the heart of a quality
 education.  Designed from the ground up especially for children, Sugar
 offers an alternative to traditional “office-desktop” software.
 .
 Learner applications in Sugar are called Activities.  They are software
 packages that automatically save your work - producing specific
 instances of the Activity that can be resumed at a later time.  Many
 Activities support learner collaboration, where multiple learners may
 be invited to join a collective Activity session.
 .
 Calculate is a simple but powerfull calculator for the Sugar environment.

sources_url = http://download.sugarlabs.org/sources/sucrose/fructose/Calculate
sources_format = tar.bz2
activity_type = gtk2
license = GPLv2+

[Maintainer]
name = Gonzalo Odiard
email = godiard@gmail.com
```
The valid values for 'activity_type' are 'gtk2'and 'gtk3'.
For 'license' the accepted values are gpl[1/2/3], bsd, apache and artistic (the field is not case sensitive).
Multiline fields, as 'long description' are recognized becase the next lines
are indented.

In the activity directory add a file debian.info

```
[Package]
name = sugar-calculate-activity
version = 0godiard1
vcs-git = https://github.com/godiard/debian-sugar-calculate-activity.git
vcs-browser = https://github.com/godiard/debian-sugar-calculate-activity.git
primary_branch = 0.104

[Maintainer]
name = Debian Sugar Team
email = pkg-sugar-devel@lists.alioth.debian.org
uploaders = Jonas Smedegaard <dr@jones.dk>,
 Gonzalo Odiard <godiard@gmail.com>
```

All these fields are mandatory.

Is possible add a optional field 'dependencies' in the section 'Package'
This field is a list of string separated by ','. The strings can be from a list
of predefined groups of dependencies, or the packages itself.
The predefined dependencies are: [gstreamer, telepathy, pygame, webkit, webkit2]

* Run the utility, with the activity repository directory as parameter:

```
python pack_act.py ./sugarlabs-calculate
```
If needed, the sources file will be downloaded, and saved with the name needed by the distribution.

When finish, a directory with the package name will be created and all the files needed to create the package will be inside.

NOTE: Can show a error about copyright, press enter

* Create the package

For debian, you only need do:

```
cd sugar-calculate-activity
sudo pdebuild
```

Limitations
-----------

* Need modify to work as James proposed with a branch instead of in a separated directry.
* Activities with binary files (Paint).
