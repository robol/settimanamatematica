#!/bin/bash
#

set -e

export PYTHON=python3

#Setup richiesto solo per i PC usati in laboratorio
if [[ -n "$WSL_DISTRO_NAME" && "$USER" = "studente" ]]; then
  export PYTHON=python3.10
  export BROWSER=wslview
  sudo apt-get -o Acquire::http::Proxy="http://131.114.4.69:3128" update
  sudo apt-get -y -o Acquire::http::Proxy="http://131.114.4.69:3128" install python3.10-venv wslu
fi

ENV_LOCATION="/tmp/$USER/env"

if [ ! -d "${ENV_LOCATION}" ]; then
  ${PYTHON} -mvenv "${ENV_LOCATION}"
fi

source "${ENV_LOCATION}/bin/activate"

pip3 install -r requirements.txt

jupyter lab


