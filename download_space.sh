#/bin/bash
# https://github.com/HoloArchivists/twspace-dl

set -x

cd $(dirname "$0")/downloads

# change this to run with $1 for the space URL
twspace_dl -i https://twitter.com/i/spaces/1lDxLndQAQyGm -m -u

# docker run --rm -v ${pwd}:/output ryu1845/twspace-dl -i space_url