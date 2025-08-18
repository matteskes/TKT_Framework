# -*- coding: utf-8 -*-
"""
Created on 2025-08-14

@author: M. Eskes and contributors- (C) 2025. All respective rights reserved.
@license: GNU General Public License v2-only (GPLv2)
@version: 0.0.1
@project: TKT Framework Project
@title: TKT Python Application
@contact: https://github.com/matteskes/TKT_Framework
@description: Python application for the TKT
"""
# PROTOTYE FRAMEWORK # This script sets up the build environment for the TKT Framework on Linux systems.

# Prepares the environment, sets necessary environment variables, and configures build flags.
# We want to get and set the current working directory for the build.
# Get and print the initial current working directory.
# Note about dev environment variables and flags: I'm wondering if we should set them here or pull from a config file.
# I would like to have prepare_build_environment() function that checks the Distro and pulls a .config file that parses the distro specifics like version, package manager build routines, etc. 
# Maybe we could write a custom lib or libs that contains all the necessary functions to set up the environments for the build, per distro. So basically have it parse distro_name
# and then set the environment variables and flags accordingly. Maybe then have it compiled as bytecode and then have it run as a subprocess to set the environment variables to improve performance.


import os
import platform

import configparser
import importlib

from textual.app import App
from textual.widgets import Label, Button


def get_like_distro():
    info = platform.freedesktop_os_release()
    ids = [info["ID"]]
    if "ID_LIKE" in info:
    # ids are space separated and ordered by precedence
        ids.extend(info["ID_LIKE"].split())
    return ids


def get_distribution_name():
# Return the primary distribution name (first ID in the list)
    return get_like_distro()[0]

#User interface for the Kernel Toolkit application using Textual.
class KernelToolkitApp(App):
    title = "Kernel Toolkit"

    def compose(self):
        welcome_message = "Welcome to The Kernel Toolkit. This program will help users compile and install your custom Linux kernel."
        yield Label(welcome_message)
        distro = get_distribution_name()
        yield Label(f"Detected distribution: {distro}")
# Source a distribution-specific library (assuming modules like kernel_lib_ubuntu.py exist)
        try:
            lib_module = importlib.import_module(f"kernel_lib_{distro}")
            yield Label(f"Sourced distribution-specific library for {distro}")
        except ImportError:
            yield Label(f"No distribution-specific library found for {distro}")
# For example: install_binary = lib_module.generate_install_binary()
        except ImportError:
# If the import fails, we yield a label indicating that no library was found
            yield Label(f"No distribution-specific library found for {distro}")
# Read the list of available kernels from settings.config
        config_path = os.path.join(os.path.dirname(__file__), "settings.config")
            
        config = configparser.ConfigParser()
        config.read(config_path)

        kernels = []
        try:
            available_kernels_str = config.get('kernels', 'available')
            kernels = [k.strip() for k in available_kernels_str.split(',')]
        except (configparser.NoSectionError, configparser.NoOptionError):
            yield Label("No available kernels found in settings.config")
        else:
            yield Label("Available kernels for installation:")
            for kernel in kernels:
                yield Label(f"- {kernel}")
        yield Button("Exit", id="exit")


    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "exit":
            self.exit()
        else:
            self.exit(f"Button {event.button.id} pressed, but no action defined.")
# Here you can add more actions for other buttons if needed.

if __name__ == "__main__":
    KernelToolkitApp().run()


# Will be removing commented code as it is replaced by reimplemented code.

#def get_current_working_directory():
#    return os.getcwd()


#print("Initial Current Working Directory:", os.getcwd())
#new_directory = "/tmp/build"
#if not os.path.exists(new_directory):
#    os.makedirs(new_directory)
#os.chdir(new_directory)
#print("Changed Current Working Directory to:", os.getcwd())
#config_files = ["system.config", "build.config"]
#for config_file in config_files:
#    if os.path.exists(config_file):
#        shutil.copy(config_file, new_directory)
#        print(f"Copied {config_file} to {new_directory}")
#    else:
#        print(f"{config_file} does not exist, skipping copy.")
#print("Final Current Working Directory:", os.getcwd())


#def set_build_environment_variables():
#        env_vars = {
#            "CC": "/usr/bin/clang",
#            "CPP": "/usr/bin/clang-cpp",
#            "CXX": "/usr/bin/clang++",
#            "LD": "lld",
#            "CC_LD": "lld",
#            "CXX_LD": "lld",
#            "AR": "llvm-ar",
#            "NM": "llvm-nm",
#            "STRIP": "llvm-strip",
#            "OBJCOPY": "llvm-objcopy",
#            "OBJDUMP": "llvm-objdump",
#            "READELF": "llvm-readelf",
#            "RANLIB": "llvm-ranlib",
#            "HOSTCC": "/usr/bin/clang",
#            "HOSTCXX": "/usr/bin/clang++",
#            "HOSTAR": "llvm-ar",
#            "HOSTLD": "lld",
#            "LLVM_VERSION": "21"
#        }
#        for key, value in env_vars.items():
#            os.environ[key] = value
#        print("Environment variables set for build tools.")


#def set_build_variable_flags():
#    build_flags = {
#        "CFLAGS": "$CPPFLAGS -O3 -flto -pthread -g1 -fno-plt -fvisibility=hidden -fomit-frame-pointer -ffunction-sections -fdata-sections",
#        "CXXFLAGS": "$CFLAGS",
#        "LDFLAGS": "-Wl,-O3 -Wl,--as-needed -Wl,--gc-sections -fuse-ld=lld -flto -O3 -pthread" ,
#        "RUSTFLAGS": "-C link-dead-code=off -C opt-level=3 -C target-cpu=native -C codegen-units=16 -C linker-plugin-lto -C panic=abort -C debuginfo=1" ,
#        "DEBUG_CFLAGS": "-fasynchronous-unwind-tables -g2" ,
#        "DEBUG_CXXFLAGS": "$DEBUG_CFLAGS",
#        "DEBUG_RUSTFLAGS": "$RUSTFLAGS -C debuginfo=2",
#    }
#    for key, value in build_flags.items():
#        os.environ[key] = value
#        print(f"Build variable {key} set to: {value}")


#def init():
#    if prepare_build_environment():
#        get_current_working_directory()
#        set_build_environment_variables()
#        set_build_variable_flags()
#        print("Build environment prepared successfully.")
#    else:
#        print("Failed to prepare build environment.")


#if __name__ == "__init__":
#    init()
##Put function here for interactive use giving the user the choice of kernel version and branch
##possibly by having it poll our gh for a the patch versions available, and based on that, let the user choose which version to install.
##This will probably be something we add later on, as we are most likely using a fixed version defined in the config file for now.


# Clone the stable linux kernel repository using dulwich. This all should probably in included in the init function.
#def clone_linux_kernel_repo(current_dir):
#    github_com = "https://github.com"
#    repo_url = f"{github_com}/gregkh/linux"
#    repo = None  
#    try:
#        os.makedirs(current_dir, exist_ok=True)        
#        repo = porcelain.clone(repo_url, current_dir)
#        print(f"Successfully cloned {repo_url} to {current_dir}")
#        return repo
#    except Exception as e:
#        raise Exception(f"Failed to clone repository: {str(e)}")
#    finally:
#        print("Clone operation complete (success or failure). Performing any necessary cleanup...")
#        if repo is None and os.path.exists(current_dir):
#            shutil.rmtree(current_dir)
#            print(f"Removed directory {current_dir} due to failed clone operation.")
#        else:
#            print(f"Repository cloned successfully, no cleanup needed for {current_dir}.")


# Patch the kernel source code with the latest patches from the TKT Framework.
#def patch_kernel_source(repo, patch_dir):
#    if not os.path.exists(patch_dir):
#        raise FileNotFoundError(f"Patch directory {patch_dir} does not exist.")
#    try:
#        porcelain.apply(repo, patch_dir)
#        print(f"Successfully applied patches from {patch_dir} to the kernel source.")
#    except Exception as e:
#        raise Exception(f"Failed to apply patches: {str(e)}")
#    finally:
#        print("Patch operation complete (success or failure).")


# This function is used to build the kernel and modules.
#def build_kernel_and_modules(repo, build_dir):
#    if not os.path.exists(build_dir):
#        raise FileNotFoundError(f"Build directory {build_dir} does not exist.")
#    try:
#        porcelain.build(repo, build_dir)
#        print(f"Successfully built the kernel and modules in {build_dir}.")
#    except Exception as e:
#        raise Exception(f"Failed to build kernel and modules: {str(e)}")
#    finally:
#        print("Build operation complete (success or failure).")


# This function is used to install the kernel and modules.
#def install_kernel_and_modules(repo, install_dir):
#    if not os.path.exists(install_dir):
#        raise FileNotFoundError(f"Install directory {install_dir} does not exist.")
#    try:
#        porcelain.install(repo, install_dir)
#        print(f"Successfully installed the kernel and modules to {install_dir}.")
#    except Exception as e:
#        raise Exception(f"Failed to install kernel and modules: {str(e)}")
#    finally:
#        print("Install complete (success or failure).")


# This function is used to clean up the build environment.
#def cleanup_build_environment(build_dir):
#    if os.path.exists(build_dir):
#        shutil.rmtree(build_dir)
#        print(f"Successfully cleaned up the build environment at {build_dir}.")
#    else:
#        print(f"Build directory {build_dir} does not exist, nothing to clean up.")
#    print("Cleanup operation complete (success or failure).")


# This function is used to run the entire build process.
#def run_build_process():
#    current_dir = get_current_working_directory()
#    try:
#        repo = clone_linux_kernel_repo(current_dir)
#        patch_dir = os.path.join(current_dir, "patches")
#        patch_kernel_source(repo, patch_dir)
#        build_dir = os.path.join(current_dir, "build")
#        build_kernel_and_modules(repo, build_dir)
#        install_dir = os.path.join(current_dir, "install")
#        install_kernel_and_modules(repo, install_dir)
#    except Exception as e:
#        raise Exception(f"An error occurred during the build process: {str(e)}")
#    finally:
#        cleanup_build_environment(build_dir)


#if __name__ == "__main__":
#    run_build_process()
#    print("Build process completed successfully.")
#else:
#    print("This script is intended to be run as a standalone program.")
#    print("Please run it directly to execute the build process.")
# End of file