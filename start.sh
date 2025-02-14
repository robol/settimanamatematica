#!/bin/bash
#

set -e

ENV_LOCATION="/tmp/$USER/env"
if [ "$TMP" != "" ]; then
  ENV_LOCATION="$TMP/$USER/env"
fi

if [ ! -d "${ENV_LOCATION}" ]; then
  python3 -mvenv "${ENV_LOCATION}"
fi

source "${ENV_LOCATION}/bin/activate"

pip3 install -r requirements.txt

jupyter lab


