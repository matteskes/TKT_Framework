# -*- coding: utf-8 -*-
import platform
import distro
import os
import dulwich.porcelain as porcelain
import shutil

"""
Created on 2025-08-14

@author: M. Eskes - (C) 2025. All rights reserved.
@license: GNU General Public License v2-only (GPLv2)
@version: 0.0.1
@project: TKT Framework Project
@title: TKT Python Application
@contact: https://github.com/matteskes/TKT_Framework
@description: Python application for the TKT
"""
# PROTOTYE FRAMEWORK # This script sets up the build environment for the TKT Framework on Linux systems.

# We want to get and set the current working directory for the build.
current_dir = os.getcwd()
print(f"Current working directory: {current_dir}")
# Ensure the system.config file exists
if not os.path.isfile("system.config"):
    with open("system.config", "w") as f:
        pass
# Function to prepare the build environment
def prepare_build_environment():
    if platform.system() == "Linux":
        distro_name = distro.name(pretty=True)
        with open("system.config", "w") as config_file:
            config_file.write(distro_name)
    else:
        print("This script is intended for Linux systems only.")
        return False
    return True
# Function to set environment variables for the build environment. May be better to pull these from the config file.
def set_build_environment_variables():
        env_vars = {
            "CC": "/usr/bin/clang",
            "CPP": "/usr/bin/clang-cpp",
            "CXX": "/usr/bin/clang++",
            "LD": "lld",
            "CC_LD": "lld",
            "CXX_LD": "lld",
            "AR": "llvm-ar",
            "NM": "llvm-nm",
            "STRIP": "llvm-strip",
            "OBJCOPY": "llvm-objcopy",
            "OBJDUMP": "llvm-objdump",
            "READELF": "llvm-readelf",
            "RANLIB": "llvm-ranlib",
            "HOSTCC": "/usr/bin/clang",
            "HOSTCXX": "/usr/bin/clang++",
            "HOSTAR": "llvm-ar",
            "HOSTLD": "lld",
            "LLVM_VERSION": "21"
        }
        for key, value in env_vars.items():
            os.environ[key] = value
        print("Environment variables set for build tools.")
# Function to set build variable flags. Maybe better to pull these from the config file.
def set_build_variable_flags():
    build_flags = {
        "CFLAGS": "$CPPFLAGS -O3 -flto -pthread -g1 -fno-plt -fvisibility=hidden -fomit-frame-pointer -ffunction-sections -fdata-sections",
        "CXXFLAGS": "$CFLAGS",
        "LDFLAGS": "-Wl,-O3 -Wl,--as-needed -Wl,--gc-sections -fuse-ld=lld -flto -O3 -pthread" ,
        "RUSTFLAGS": "-C link-dead-code=off -C opt-level=3 -C target-cpu=native -C codegen-units=16 -C linker-plugin-lto -C panic=abort -C debuginfo=1" ,
        "DEBUG_CFLAGS": "-fasynchronous-unwind-tables -g2" ,
        "DEBUG_CXXFLAGS": "$DEBUG_CFLAGS",
        "DEBUG_RUSTFLAGS": "$RUSTFLAGS -C debuginfo=2",
    }
    for key, value in build_flags.items():
        os.environ[key] = value
        print(f"Build variable {key} set to: {value}")
# This script sets up the build environment for the TKT Framework on Linux systems.
def main():
    if prepare_build_environment():
        set_build_environment_variables()
        set_build_variable_flags()
        print("Build environment prepared successfully.")
    else:
        print("Failed to prepare build environment.")
if __name__ == "__main__":
    main()
##Put function here for interactive use giving the user the choice of kernel version and branch
##possibly by having it poll remote server with available kernel versions to install.
##This will most likely be something we add later on, as we are currently using a fixed version defined in the config file.

# Clone the stable linux kernel repository using dulwich.
def clone_linux_kernel_repo(current_dir):
    github_com = "https://github.com"
    repo_url = f"{github_com}/gregkh/linux"
    repo = None  # Initialize repo outside try block
    try:
        # Ensure the current_dir exists
        os.makedirs(current_dir, exist_ok=True)        
        # Clone the Linux kernel repository
        repo = porcelain.clone(repo_url, current_dir)
        print(f"Successfully cloned {repo_url} to {current_dir}")
        return repo
    except Exception as e:
        raise Exception(f"Failed to clone repository: {str(e)}")
    finally:
        print("Clone operation complete (success or failure). Performing any necessary cleanup...")
        # If the repository was not cloned successfully, remove the directory
        # This is a placeholder for any cleanup logic you might want to implement.
        # if repo is None and os.path.exists(current_dir):
        #     shutil.rmtree(current_dir)
        # But for now, just a print for demonstration