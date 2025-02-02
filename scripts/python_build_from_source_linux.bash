cd ..

# Update package lists
sudo apt update

# Install dependent libraries:
sudo apt install build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libsqlite3-dev libreadline-dev libffi-dev curl libbz2-dev tk-dev

# Download Python binary package:
wget https://www.python.org/ftp/python/3.11.10/Python-3.11.10.tgz

# Unzip the package:
tar -xzf Python-3.11.10.tgz

# Execute configure script
cd Python-3.11.10
./configure --enable-optimizations --enable-shared

# Build Python 3.11
make -j 2

# Install Python 3.11
sudo make install

# Verify the installation
python3.11 -V

echo "If Python version did not print, you may need to stop active processes"
