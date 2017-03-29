# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure(2) do |config|

    config.vm.box = "ubuntu/trusty64"
    config.vm.network "forwarded_port", guest: 80, host: 8080
    config.vm.network :private_network, ip: "192.168.111.222"
    config.vm.hostname = 'default'

    config.vm.synced_folder "./", "/srv/www/imagery", :owner=>'vagrant', :group=>'vagrant'

    config.ssh.insert_key = false

    config.vm.provider "virtualbox" do |v|
        v.memory = 2048
    end

    config.vm.provision "shell" do |s|
        s.inline = <<-SCRIPT
            wget -q -O - http://apt-mirror.internal/parthenon-repo/key | sudo apt-key add -
            sudo rm /etc/apt/sources.list && sudo wget -q http://apt-mirror.internal/source-lists/$(lsb_release -c | awk '{print$2}').list -O /etc/apt/sources.list
        SCRIPT
    end

    config.vm.provision "ansible" do |ansible|
        ansible.limit = "all, localhost"
        ansible.inventory_path = "deployment/local"
        ansible.playbook = "deployment/local.yml"
    end

    pubkey = File.read("deployment/keys/vagrant.key.pub")
    config.vm.provision "shell" do |s|
        s.inline = "echo $1 >> ~vagrant/.ssh/authorized_keys"
        s.args = [pubkey]
    end

    config.vm.provision "shell" do |s|
        s.inline = "sudo apt-get update"
    end

    config.vm.provision "ansible" do |ansible|
        ansible.inventory_path = "deployment/dev"
        ansible.playbook = "deployment/site.yml"
        ansible.raw_arguments = ['--timeout=30']
        ansible.vault_password_file = 'vault_pass.py'
    end

end
