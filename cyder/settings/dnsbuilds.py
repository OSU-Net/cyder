# STAGE_DIR: Where test builds should go. This shouldn't be in an SVN repo
STAGE_DIR = "/tmp/dns_stage/"

# PROD_DIR: This is the directory where inventory will place it's DNS files.
# This should be an SVN repo
PROD_DIR = "/tmp/dns_prod/cyzones/"

# BIND_PREFIX: This is the path to where inventory zone files are built
# relative to the root of the SVN repo. This is usually a substring of
# PROD_DIR.
BIND_PREFIX = ""


LOCK_FILE = "/tmp/lock.file"
NAMED_CHECKZONE_OPTS = ""
MAX_ALLOWED_LINES_CHANGED = 500
NAMED_CHECKZONE = "/usr/sbin/named-checkzone"  # path to named-checkzone
NAMED_CHECKCONF = "/usr/sbin/named-checkconf"  # path to named-checkconf

# Only one zone at a time should be removed
MAX_ALLOWED_CONFIG_LINES_REMOVED = 10

STOP_UPDATE_FILE = "/tmp/stop.update"
LAST_RUN_FILE = "/tmp/last.run"
