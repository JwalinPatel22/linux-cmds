#### Disable SSH root login

```bash
sudo vi /etc/ssh/sshd_config

# set PermitRootLogin no

sudo systemctl restart sshd
sudo cat vi /etc/ssh/sshd_config | grep -i "PermitRootLogin"
```

#### Granting executable permission to a script

```bash
sudo +x script.sh
sudo +r script.sh
```

#### Installing SELinux

```bash

# checking the os of the system
cat /etc/os-release

# installing selinux on centos
sudo yum install selinux-policy selinux-policy-targeted

# to check the status of selinux
sestatus

# edit the status of selinux
sudo vi /etc/selinux/config
# set SELINUX=disabled
```
