#!/bin/bash

WORK_DIR="$(dirname "$0")"
<<<<<<< HEAD
OS_REQUIREMENTS_FILENAME="$WORK_DIR/requirements.apt"

VER=$(lsb_release -sr)
if [ "$VER" == "16.04" ]; then
  OS_REQUIREMENTS_FILENAME="requirements.apt.xenial"
else
  OS_REQUIREMENTS_FILENAME="requirements.apt"
fi
# Handle call with wrong command
function wrong_command()
{
  echo "${0##*/} - unknown command: '${1}'"
  usage_message
=======
DISTRO_NAME=$(lsb_release -sc)
OS_REQUIREMENTS_FILENAME="requirements-$DISTRO_NAME.apt"

cd $WORK_DIR

# Check if a requirements file exist for the current distribution.
if [ ! -r "$OS_REQUIREMENTS_FILENAME" ]; then
    cat <<-EOF >&2
		There is no requirements file for your distribution.
		You can see one of the files listed below to help search the equivalent package in your system:
		$(find ./ -name "requirements-*.apt" -printf "  - %f\n")
	EOF
    exit 1;
fi

# Handle call with wrong command
function wrong_command()
{
    echo "${0##*/} - unknown command: '${1}'" >&2
    usage_message
>>>>>>> 3b9073c012bcdfc49afcb1d105deb56123ab5be1
}

# Print help / script usage
function usage_message()
{
<<<<<<< HEAD
  echo "usage: ./${0##*/} <command>"
  echo "available commands are:"
  echo -e "\tlist\t\tPrint a list of all packages defined on ${OS_REQUIREMENTS_FILENAME} file"
  echo -e "\thelp\t\tPrint this help"
  echo -e "\n\tCommands that require superuser permission:"
  echo -e "\tinstall\t\tInstall packages defined on ${OS_REQUIREMENTS_FILENAME} file. Note: This\n\t\t\t   does not upgrade the packages already installed for new\n\t\t\t   versions, even if new version is available in the repository."
  echo -e "\tupgrade\t\tSame that install, but upgrate the already installed packages,\n\t\t\t   if new version is available."

=======
    cat <<-EOF
		Usage: $WORK_DIR/${0##*/} <command>
		Available commands are:
		    list        Print a list of all packages defined on ${OS_REQUIREMENTS_FILENAME} file
		    help        Print this help

		Commands that require superuser permission:
		    install     Install packages defined on ${OS_REQUIREMENTS_FILENAME} file. Note: This
		                does not upgrade the packages already installed for new versions, even if
		                new version is available in the repository.
		    upgrade     Same that install, but upgrade the already installed packages, if new
		                version is available.
	EOF
>>>>>>> 3b9073c012bcdfc49afcb1d105deb56123ab5be1
}

# Read the requirements.apt file, and remove comments and blank lines
function list_packages(){
<<<<<<< HEAD
     grep -v "#" ${OS_REQUIREMENTS_FILENAME} | grep -v "^$";
}

function install()
=======
    grep -v "#" "${OS_REQUIREMENTS_FILENAME}" | grep -v "^$";
}

function install_packages()
>>>>>>> 3b9073c012bcdfc49afcb1d105deb56123ab5be1
{
    list_packages | xargs apt-get --no-upgrade install -y;
}

<<<<<<< HEAD
function upgrade()
=======
function upgrade_packages()
>>>>>>> 3b9073c012bcdfc49afcb1d105deb56123ab5be1
{
    list_packages | xargs apt-get install -y;
}

<<<<<<< HEAD

=======
>>>>>>> 3b9073c012bcdfc49afcb1d105deb56123ab5be1
function install_or_upgrade()
{
    P=${1}
    PARAN=${P:-"install"}

    if [[ $EUID -ne 0 ]]; then
<<<<<<< HEAD
        echo -e "\nYou must run this with root privilege" 2>&1
        echo -e "Please do:\n" 2>&1
        echo "sudo ./${0##*/} $PARAN" 2>&1
        echo -e "\n" 2>&1

=======
        cat <<-EOF >&2
			You must run this script with root privilege
			Please do:
			sudo $WORK_DIR/${0##*/} $PARAN
		EOF
>>>>>>> 3b9073c012bcdfc49afcb1d105deb56123ab5be1
        exit 1
    else

        apt-get update

        # Install the basic compilation dependencies and other required libraries of this project
        if [ "$PARAN" == "install" ]; then
<<<<<<< HEAD
            install;
        else
            upgrade;
=======
            install_packages;
        else
            upgrade_packages;
>>>>>>> 3b9073c012bcdfc49afcb1d105deb56123ab5be1
        fi

        # cleaning downloaded packages from apt-get cache
        apt-get clean

        exit 0
    fi
<<<<<<< HEAD


}


=======
}

>>>>>>> 3b9073c012bcdfc49afcb1d105deb56123ab5be1
# Handle command argument
case "$1" in
    install) install_or_upgrade;;
    upgrade) install_or_upgrade "upgrade";;
    list) list_packages;;
<<<<<<< HEAD
    help) usage_message;;
    *) wrong_command $1;;
=======
    help|"") usage_message;;
    *) wrong_command "$1";;
>>>>>>> 3b9073c012bcdfc49afcb1d105deb56123ab5be1
esac
