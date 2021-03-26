from fabric.api import *
from fabric.context_managers import cd
from fabric.contrib.files import exists

env.hosts = [
        'ubuntu@pi1.lan',
        'ubuntu@pi2.lan',
        'ubuntu@pi3.lan',
        'ubuntu@pi4.lan',
        'ubuntu@pi5.lan',
        'ubuntu@pi6.lan',
        'ubuntu@pi7.lan',
        'ubuntu@pi8.lan',
        'ubuntu@pi9.lan',
        'ubuntu@pi10.lan',
        'ubuntu@pi11.lan',
        'ubuntu@pi12.lan',
        'ubuntu@pi13.lan',
        'ubuntu@pi14.lan',
        'ubuntu@pi15.lan',
        'ubuntu@pi16.lan',
        'ubuntu@pi17.lan',
        'ubuntu@pi18.lan',
        'ubuntu@pi19.lan',
        'ubuntu@pi20.lan',
#        'ubuntu@pitest',
        ]

env.password = '*****'

@parallel
def didwegetone():
    if exists('/home/ubuntu/results.txt'):
        print('%s|YEP' %env.host_string)
    else:
        print('%s|NOPE' %env.host_string)

@parallel
def scmd(command):
    sudo(command)

#@parallel
def cmd(command):
    with settings(colorize_errors=True,skip_bad_hosts=True,timeout=60):
        with hide('running'):
            run(command)

@parallel
def temps():
    with settings(colorize_errors=True,skip_bad_hosts=True,timeout=60,):
        with hide('running'):
            run("cat /sys/class/thermal/thermal_zone0/temp")

@parallel
def speedz():
    with settings(
        hide('running'),
        #warn_only=True,
        colorize_errors=True,
        skip_bad_hosts=True,timeout=60
    ):
        sudo("cat /sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_cur_freq")

@parallel
def updatepi():
    # updates
    sudo('apt update')
    sudo('apt upgrade -y')
    # overclocking - skip this step for PI3
    #sudo('echo "over_voltage=2\narm_freq=1750\n" >> /boot/firmware/usercfg.txt')
    # Reboot
    sudo('reboot')

@parallel
def prepstats():
    sudo('apt install python3-pip -y')
    sudo('pip3 install redis')
    put('/home/ianm/fabric/redis-push.py', '/home/ubuntu', use_sudo=False)
    sudo('chmod +x /home/ubuntu/redis-push.py')
    put('/home/ianm/fabric/crontab.txt', '/tmp', use_sudo=False)
    sudo('crontab < /tmp/crontab.txt')

def prepmemorydormants():
    # copy over the dormants file
    #put('/home/ianm/Downloads/dormants-btc.txt','/home/ubuntu/')
    put('/home/ianm/Downloads/rp4-2gb-btc-list-top-with-dormants.txt','/home/ubuntu/')
    # Make sure the golang directories exists
    run('mkdir -p /home/ubuntu/go/src/github.com/user')
    run('mkdir /home/ubuntu/go/bin')
    run('mkdir /home/ubuntu/go/pkg')
    # Put our files in place
    put('/home/ianm/work/src/github.com/btcsuite', '/home/ubuntu/go/src/github.com')
    put('/usr/local/go/src/github.com/btcsuite', '/home/ubuntu/go/src/github.com')
    put('/home/ianm/work/src/github.com/user/memory-dormants', '/home/ubuntu/go/src/github.com/user')
    # Place systemd file
    put('/home/ianm/fabric/memory-dormant.service', '/etc/systemd/system', use_sudo=True)
    sudo('systemctl daemon-reload')
    # install golang
    sudo('apt install golang -y')

@parallel
def buildmemorydormants():
    with cd('/home/ubuntu/go/src/github.com/user/memory-dormants'):
        run('go get')
        run('go build memory-dormants.go')
        run('cp memory-dormants /home/ubuntu')

@parallel
def updategocode():
    mdstop()
    put('/home/ianm/work/src/github.com/user/memory-dormants/memory-dormants.go', '/home/ubuntu/go/src/github.com/user/memory-dormants')
    buildmemorydormants()
    #put('/home/ianm/fabric/memory-dormant.service', '/etc/systemd/system', use_sudo=True)
    #sudo('systemctl daemon-reload')
    mdstart()

@parallel
def mdstart():
    sudo('systemctl start memory-dormant.service')

@parallel
def mdstatus():
    with settings(
        hide('running'),
        #warn_only=True,
        colorize_errors=True,
        skip_bad_hosts=False,timeout=20
    ):
        sudo('systemctl status memory-dormant.service')

@parallel
def mdstop():
    sudo('systemctl stop memory-dormant.service')


@parallel
def findresults():
    run('ls -ltr results.txt')

@parallel
def removevscode():
    # updates
    sudo('rm /etc/apt/sources.list.d/vscode.list')
    sudo('rm /etc/apt/trusted.gpg.d/microsoft.gpg')
    sudo('apt update')

@parallel
def disableDailyAPT():
    sudo('systemctl stop apt-daily.timer')
    sudo('systemctl disable apt-daily.timer')
    sudo('systemctl stop apt-daily-upgrade.timer')
    sudo('systemctl disable apt-daily-upgrade.timer')

@parallel
def upreboot():
    # updates
    sudo('apt update')
    sudo('apt upgrade -y')
    # Reboot
    sudo('reboot')

@parallel
def poweroff():
    # updates
    sudo('poweroff')

@parallel
def localAPT():
    put('/home/ianm/fabric/sources.list-local', '/etc/apt/sources.list', use_sudo=True)
    sudo('chmod 644 /etc/apt/sources.list')
    sudo('chown root:root /etc/apt/sources.list')

@parallel
def remoteAPT():
    put('/home/ianm/fabric/sources.list-remote', '/etc/apt/sources.list', use_sudo=True)
    sudo('chmod 644 /etc/apt/sources.list')
    sudo('chown root:root /etc/apt/sources.list')

#@parallel
#def updatedormants():
    # Push a new dormant file to each pi
#    mdstop()
    #put('/home/ianm/Downloads/rich-and-dormants-btc.txt','/home/ubuntu/dormants-btc.txt')
#    put('/home/ianm/Downloads/rp4-2gb-btc-list-top-with-dormants.txt','/home/ubuntu/')
#    mdstart()
#    mdstatus()

@parallel
def offWifiBt():
    sudo('echo "\ndtoverlay=disable-wifi\ndtoverlay=disable-bt\n" >> /boot/firmware/config.txt')


def setupNewPi():
    localAPT()
    sudo('apt update')
    sudo('apt upgrade -y')
    disableDailyAPT()
    offWifiBt()
    prepmemorydormants()
    buildmemorydormants()
    prepstats()
    sudo('echo "over_voltage=2\narm_freq=1750\n" >> /boot/firmware/usercfg.txt')
    updatepi()


def wipeSD():
    print('Not today Satan!')
    #sudo('blkdiscard -v /dev/mmcblk0')


@parallel
def missedone():
    #put('/usr/local/go/src/github.com/btcsuite', '/home/ubuntu/go/src/github.com')
    #run('mv work go')
    # Place systemd file
    #put('/home/ianm/fabric/memory-dormant.service', '/etc/systemd/system', use_sudo=True)
    put('/home/ianm/fabric/redis-push.py', '/home/ubuntu', use_sudo=False)
    sudo('chmod +x /home/ubuntu/redis-push.py')
    #put('/home/ianm/fabric/crontab.txt', '/tmp', use_sudo=False)
    #sudo('crontab < /tmp/crontab.txt')
    #updatedormants()
    #mdstop()
    #sudo('echo "over_voltage=2\narm_freq=1750\n" >> /boot/firmware/usercfg.txt')
    #sudo('echo "over_voltage=6\narm_freq=2000\n" >> /boot/firmware/usercfg.txt')
    #sudo('mv /home/ianm/Downloads/dormants-btc.txt /home/ubuntu')
    #sudo('mv /home/ianm/Downloads/dormants-btc.txt /home/ubuntu')
    #put('/home/ianm/fabric/memory-dormant.service', '/etc/systemd/system', use_sudo=True)
    #sudo('systemctl daemon-reload')
    #sudo('rm -rf /home/ianm')
    #sudo('apt update')
    #sudo('apt upgrade -y')
    # Reboot
    #sudo('reboot')
    # Place systemd file
    #put('/home/ianm/fabric/memory-dormant.service', '/etc/systemd/system', use_sudo=True)
