import os
import sys
import socket  # Used to get the computer hostname
from dotenv import load_dotenv

# Flag to indicate whether environment variables have already been loaded
ENV_LOADED = False

def load_platform_specific_env():
    """
    Dynamically load different .env.common files based on the operating system
    and hostname, and prevent duplicate loading.
    """
    global ENV_LOADED

    # Check if environment variables have already been loaded
    if ENV_LOADED:
        return

    # Get project root directory path (modify as needed)
    project_root = os.path.abspath(os.path.dirname(__file__) + "/..")

    # Change working directory to the project root
    os.chdir(project_root)
    print(f"Changed working directory to project root: {project_root}")

    hostname = socket.gethostname()  # Get the hostname
    print(f"Current hostname: {hostname}")

    # Load the common .env.common file
    load_dotenv(os.path.join(project_root, "env_config/.env.common"))
    print(f"Loaded environment variables from env_config/.env.common")

    # Load environment-specific file based on OS and hostname
    if sys.platform == "darwin":  # macOS
        env_file = os.path.join(project_root, "env_config/.env.dev")
    elif sys.platform.startswith("linux"):  # Linux
        if hostname == "fengwenlyu-OptiPlex-5050":
            env_file = os.path.join(project_root, "env_config/.env.test")
        else:
            env_file = os.path.join(project_root, "env_config/.env.prod")
    else:
        raise EnvironmentError("Unsupported platform or hostname")

    # Load the specified environment file
    load_dotenv(env_file, override=False)
    print(f"Loaded environment variables from {env_file}")

    # Set the flag to indicate environment variables have been loaded
    ENV_LOADED = True
