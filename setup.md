These are all the required steps to setup the environment on the Steam Deck to run all the code in this repo.

# 1. Distrobox

``` bash
distrobox create -n <container_name> -i ubuntu:22.04 or newer
distrobox enter <container_name>
```

After the container exists, some basic software needs to be installed:

# 2. Git

Reference: https://www.digitalocean.com/community/tutorials/how-to-install-git-on-ubuntu

``` bash
sudo apt update
sudo apt install git -y
```

Test with:

``` bash
git --version
```

# 3. VS Code

Reference: https://code.visualstudio.com/docs/setup/linux

``` bash
sudo apt-get install wget gpg
wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > packages.microsoft.gpg
sudo install -D -o root -g root -m 644 packages.microsoft.gpg /etc/apt/keyrings/packages.microsoft.gpg
echo "deb [arch=amd64,arm64,armhf signed-by=/etc/apt/keyrings/packages.microsoft.gpg] https://packages.microsoft.com/repos/code stable main" |sudo tee /etc/apt/sources.list.d/vscode.list > /dev/null
rm -f packages.microsoft.gpg

sudo apt install apt-transport-https
sudo apt update
sudo apt install code -y
```

Test with:

``` bash
code --version
```

# 4. Python 3

Reference: ...



## 4.1. Venv creation

Reference: ...



## 4.2. Installing Arcade

Reference: ...



## 4.3. Installing additional graphical drivers

Reference: ...



