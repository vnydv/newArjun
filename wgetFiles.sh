
## change to util and get the required files
cd "/usr/sbin/camWIP/utils"

## clear existing files
rm __init__.py
rm api.py
rm camConnect.py
rm mergeCollate.py
rm options.py

wget "https://raw.githubusercontent.com/vnydv21/newArjun/main/utils/__init__.py"
wget "https://raw.githubusercontent.com/vnydv21/newArjun/main/utils/api.py"
wget "https://raw.githubusercontent.com/vnydv21/newArjun/main/utils/camConnect.py"
wget "https://raw.githubusercontent.com/vnydv21/newArjun/main/utils/mergeCollate.py"
wget "https://raw.githubusercontent.com/vnydv21/newArjun/main/utils/options.py"

cd "/usr/sbin/camWIP"
rm main.py

wget "https://raw.githubusercontent.com/vnydv21/newArjun/main/main.py"
