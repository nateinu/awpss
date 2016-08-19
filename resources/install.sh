#!/bin/bash

if [ -z "$1" ]; then
	prefix=$HOME
else
	prefix=$1
fi

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

cp -r $DIR/../../awpss $prefix/

sed -i "s#{install_path}#$prefix/awpss#" $prefix/awpss/resources/awpss.desktop
mkdir -p $HOME/.local/share/applications/
cp $prefix/awpss/resources/awpss.desktop $HOME/.local/share/applications/

