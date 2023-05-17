UTIL_DIR = "/usr/sbin/camWIP/utils"
MAIN_DIR = "/usr/sbin/camWIP"

## change to util and get the required files
cd $UTIL_DIR
wget "https://raw.githubusercontent.com/vnydv21/newArjun/main/utils/__init__.py"
wget "https://raw.githubusercontent.com/vnydv21/newArjun/main/utils/api.py"
wget "https://raw.githubusercontent.com/vnydv21/newArjun/main/utils/camConnect.py"
wget "https://raw.githubusercontent.com/vnydv21/newArjun/main/utils/mergeCollate.py"
wget "https://raw.githubusercontent.com/vnydv21/newArjun/main/utils/options.py"

cd $MAIN_DIR
wget "https://raw.githubusercontent.com/vnydv21/newArjun/main/main.py"
