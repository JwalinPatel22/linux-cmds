### Disable SSH root login
```bash
sudo vi /etc/ssh/sshd_config

# set PermitRootLogin no

sudo systemctl restart sshd
sudo cat vi /etc/ssh/sshd_config | grep -i "PermitRootLogin"
```

