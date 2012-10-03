#!/bin/bash

declare -a APPS=(api api_v2 api_v3 base build core dhcp mozdns mdns reports
systems truth user_systems, MozInvAuthorization)

for APP in "${APPS[@]}"
do
    find . -type f -name "*.py" -print0 | xargs -0 sed -i "s/from ${APP}/from cyder.${APP}/g";
    find . -type f -name "*.py" -print0 | xargs -0 sed -i "s/from inventory\./from cyder./g";
    find . -type f -name "*.py" -print0 | xargs -0 sed -i "s/from mozilla_inventory\./from cyder./g";
    find . -type f -name "urls.py" -print0 | xargs -0 sed -i "s/include('${APP}/include ('cyder.${APP}/g";
    find . -type f -name "urls.py" -print0 | xargs -0 sed -i "s/patterns('${APP}'/patterns('cyder.${APP}'/g";
done
