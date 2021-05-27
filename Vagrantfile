# -*- mode: ruby -*-
# vi: set ft=ruby :
# About: Vagrant file for the development environment

###############
#  Variables  #
###############

CPUS = 2
RAM = 4096

BOX = "bento/ubuntu-18.04"
VM_NAME = "ubuntu-18.04-pICA-emu"

######################
#  Provision Script  #
######################

# Common bootstrap
$bootstrap= <<-SCRIPT
# Install dependencies
apt-get update
DEBIAN_FRONTEND=noninteractive apt-get -y -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" upgrade

# Essential packages used by ./util/install.sh
apt-get install -y git make pkg-config sudo python3 libpython3-dev python3-dev python3-pip software-properties-common
# Test/Development utilities
apt-get install -y bash-completion htop dfc gdb tmux
apt-get install -y iperf iperf3
SCRIPT

$setup_x11_server= <<-SCRIPT
apt-get install -y xorg
apt-get install -y openbox
SCRIPT

# Use v5.4 LTS, EOL: Dec, 2025
# For eBPF, XDP, AF_XDP, EROFS etc.
$install_kernel= <<-SCRIPT
# Install libssl1.1 from https://packages.ubuntu.com/bionic/amd64/libssl1.1/download
echo "deb http://cz.archive.ubuntu.com/ubuntu bionic main" | tee -a /etc/apt/sources.list > /dev/null
apt update
apt install -y libssl1.1
cd /tmp || exit
wget -c https://kernel.ubuntu.com/~kernel-ppa/mainline/v5.4.70/amd64/linux-headers-5.4.70-050470_5.4.70-050470.202010070732_all.deb
wget -c https://kernel.ubuntu.com/~kernel-ppa/mainline/v5.4.70/amd64/linux-headers-5.4.70-050470-generic_5.4.70-050470.202010070732_amd64.deb
wget -c https://kernel.ubuntu.com/~kernel-ppa/mainline/v5.4.70/amd64/linux-image-unsigned-5.4.70-050470-generic_5.4.70-050470.202010070732_amd64.deb
wget -c https://kernel.ubuntu.com/~kernel-ppa/mainline/v5.4.70/amd64/linux-modules-5.4.70-050470-generic_5.4.70-050470.202010070732_amd64.deb
dpkg -i *.deb
update-initramfs -u -k 5.4.70-050470-generic
update-grub
SCRIPT

$post_installation= <<-SCRIPT
# Allow vagrant user to use Docker without sudo
usermod -aG docker vagrant
if [ -d /home/vagrant/.docker ]; then
  chown -R vagrant:vagrant /home/vagrant/.docker
fi
SCRIPT

$install_comnetsemu= <<-SCRIPT
cd /home/vagrant
git clone https://git.comnets.net/public-repo/comnetsemu.git

# Apply Xterm profile, looks nicer.
cp /home/vagrant/comnetsemu/util/Xresources /home/vagrant/.Xresources
# xrdb can not run directly during vagrant up. Auto-works after reboot.
xrdb -merge /home/vagrant/.Xresources

# Install comnetsemu. Docker in comnetsemu is now invalid.
cd /home/vagrant/comnetsemu/util || exit
PYTHON=python3 ./install.sh -a
# bash ./install.sh -v
# bash ./install.sh -c

cd /home/vagrant/comnetsemu/ || exit
# setup.py develop installs the package (typically just a source folder)
# in a way that allows you to conveniently edit your code after it is
# installed to the (virtual) environment, and have the changes take
# effect immediately. Convinient for development
sudo make develop

SCRIPT

####################
#  Vagrant Config  #
####################

Vagrant.configure("2") do |config|

  if Vagrant.has_plugin?("vagrant-vbguest")
    config.vbguest.auto_update = false
  end

  config.vm.define "testbed" do |testbed|

    # VirtualBox-specific configuration
    testbed.vm.provider "virtualbox" do |vb|
      vb.name = VM_NAME
      vb.cpus = CPUS
      vb.memory = RAM
      # MARK: The CPU should enable SSE3 or SSE4 to compile DPDK applications.
      vb.customize ["setextradata", :id, "VBoxInternal/CPUM/SSE4.1", "1"]
      vb.customize ["setextradata", :id, "VBoxInternal/CPUM/SSE4.2", "1"]
    end

    testbed.vm.box = BOX
    testbed.vm.hostname = "testbed"
    testbed.vm.box_check_update = true
    testbed.vm.post_up_message = '
VM already started! Run "$ vagrant ssh testbed" to ssh into the runnung VM.
    '

    # Workaround for vbguest plugin issue
    testbed.vm.provision "shell", run: "always", inline: <<-WORKAROUND
    modprobe vboxsf || true
    WORKAROUND

    testbed.vm.provision :shell, inline: $bootstrap, privileged: true
    testbed.vm.provision :shell, inline: $setup_x11_server, privileged: true
    testbed.vm.provision :shell, inline: $install_comnetsemu, privileged: false

    # Make the maketerm of Mininet works in VirtualBox.
    testbed.vm.provision :shell, privileged: true, run: "always", inline: <<-SHELL
      sed -i 's/X11UseLocalhost no/X11UseLocalhost yes/g' /etc/ssh/sshd_config
      systemctl restart sshd.service
    SHELL

    testbed.vm.provision :shell, inline: $post_installation, privileged: true

    testbed.vm.network "forwarded_port", guest: 8080, host: 8080, host_ip: "127.0.0.1"

    # Enable X11 forwarding
    testbed.ssh.forward_agent = true
    testbed.ssh.forward_x11 = true

    # Always run this when use `vagrant up`
    testbed.vm.provision :shell, privileged: true, run: "always", inline: <<-SHELL
      echo 3 | tee /proc/sys/vm/drop_caches
      cd /vagrant || exit
      bash ./setup_always.sh
      
    SHELL
  end
end
