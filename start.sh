#!/bin/bash
#

set -e

if [ ! -d env ]; then
  python3 -mvenv env
fi

. env/bin/activate

pip3 install -r requirements.txt

jupyter lab


