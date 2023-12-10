cd ..

# Update package lists
sudo apt update

# Install dependent libraries:
sudo apt install build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libsqlite3-dev libreadline-dev libffi-dev curl libbz2-dev tk-dev

# Download Python binary package:
wget https://www.python.org/ftp/python/3.10.13/Python-3.10.13.tgz

# Unzip the package:
tar -xzf Python-3.10.13.tgz

# Execute configure script
cd Python-3.10.13
./configure --enable-optimizations --enable-shared

# Build Python 3.10
make -j 2

# Install Python 3.10
sudo make install

# Verify the installation
python3.10 -V

echo "If Python version did not print, you may need to stop active processes"
