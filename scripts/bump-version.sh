#!/bin/sh
ver=$1
[ ! $ver ] && echo "reuqired version bumber" && exit
echo $ver > VERSION.txt
echo Files modified successfully, version bumped to $ver
git commit -a -m "Bumped version number to $ver"
