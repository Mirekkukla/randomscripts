############
# Keylogging
############

print_klog_dest() { echo "written to /var/log/keystroke.log"; }

sneaky_keylogger() {
    trap 'print_klog_dest' SIGINT
    echo 'KLOG running, dont forget to kill'
    sudo keylogger > /dev/null
    trap - SIGINT
}

alias klog=sneaky_keylogger


#####################
# Pausing steam games
#####################

pause_pid() {
    echo "About to pause $1"
    kill -STOP $1
}

# pass the PID as the arg
resume_pid() {
    echo "About to resume $1"
    kill -CONT $1
}

# echos the PIDs as a string (bash / zsh functions can't return arrays)
echo_steam_pids() {
    echo `ps aux | grep -i Steam | grep -v grep | grep -v ipcserver | awk '{print $2}'`
}

pause_steam() {
    # zsh doesn't do word splitting like bash
    # see https://stackoverflow.com/questions/23157613/how-to-iterate-through-string-one-word-at-a-time-in-zsh
    echo "Pausing steam"
    local pids=$(echo_steam_pids)
    local pid
    for pid in ${(z)pids}; do
        pause_pid $pid
    done
}

resume_steam() {
    echo "Resume steam"
    local pids=$(echo_steam_pids)
    local pid
    for pid in ${(z)pids}; do
        resume_pid $pid
    done
}

echo_divinity_pid() {
    echo `ps aux | grep Divinity | grep -v grep | awk '{print $2}'`
} 

test_divinity_running() {
    if [ -z `echo_divinity_pid` ]; then
        echo "Divinity isn't running, quiting"
        return 1
    else
        echo "Divinity running, presumably about to pause / resume"
    fi
}

pause_divinity() {
    test_divinity_running && pause_pid `echo_divinity_pid` && pause_steam
}

resume_divinity() {
    test_divinity_running && resume_pid `echo_divinity_pid` && resume_steam 
}

# these aliases need to wrap a function so that we don't hard-code the divinity pid
alias pdiv=pause_divinity
alias rdiv=resume_divinity
