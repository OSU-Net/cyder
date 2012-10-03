#!/bin/bash

declare -a ATTRS=(CORE_BASE_URL SCRIPT_URL FROM_EMAIL_ADDRESS
DHCP_CONFIG_OUTPUT_DIRECTORY DESKTOP_EMAIL_ADDRESS
MOZ_SITE_PATH BUG_URL MOZDNS_BASE_URL USER_SYSTEM_ALLOWED_DELETE
FIX_M_C_M_C MOZ_SITE_PATH REV_SITE_PATH ZONE_PATH RUN_SVN_STATS
ZONE_PATH DHCP_CONFIG_OUTPUT_DIRECTORY BUILD_PATH);

for ATTR in "${ATTRS[@]}"
do
    find . -type f -print0 | xargs -0 sed -i "s/from settings import ${ATTR}/from django.conf import settings/";
    find . -type f -print0 | xargs -0 sed -i "s/$ATTR/settings.${ATTR}/";
done
