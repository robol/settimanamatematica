#!/bin/bash
#

set -e

if [ ! -d /tmp/$USER/env ]; then
  python3 -mvenv /tmp/$USER/env
fi

. /tmp/$USER/env/bin/activate

pip3 install -r requirements.txt

jupyter lab


