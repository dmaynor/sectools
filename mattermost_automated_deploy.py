#!/usr/bin/env python3

import os
import subprocess
import shutil
import json

# Define the necessary commands and configurations
commands = [
    "git clone https://github.com/mattermost/docker",
    "cd docker",
    "cp env.example .env"
]

# Define the directories to be created
directories = [
    "./volumes/app/mattermost/config",
    "./volumes/app/mattermost/data",
    "./volumes/app/mattermost/logs",
    "./volumes/app/mattermost/plugins",
    "./volumes/app/mattermost/client/plugins",
    "./volumes/app/mattermost/bleve-indexes"
]

def run_command(command):
    result = subprocess.run(command, shell=True)
    if result.returncode != 0:
        raise Exception(f"Command failed: {command}")

def update_env_file(version, use_team_edition):
    with open('.env', 'r') as file:
        data = file.readlines()
    
    for i, line in enumerate(data):
        if line.startswith("MATTERMOST_IMAGE_TAG="):
            data[i] = f"MATTERMOST_IMAGE_TAG={version}\n"
        elif line.startswith("MATTERMOST_IMAGE=mattermost-enterprise-edition") and use_team_edition:
            data[i] = "MATTERMOST_IMAGE=mattermost-team-edition\n"

    with open('.env', 'w') as file:
        file.writelines(data)

def update_config_json():
    config_path = "./volumes/app/mattermost/config/config.json"
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"{config_path} does not exist. Make sure the Mattermost configuration directory is correctly set up.")
    
    with open(config_path, 'r') as file:
        config_data = json.load(file)
    
    config_data['PluginSettings']['Enable'] = True
    
    with open(config_path, 'w') as file:
        json.dump(config_data, file, indent=4)

def setup_mattermost():
    # Clone the repository and navigate to the directory
    run_command(commands[0])
    os.chdir('docker')

    # Create and configure the .env file
    shutil.copy('env.example', '.env')
    
    # Prompt for Mattermost version and update .env file
    version = input("Enter the Mattermost version you want to use: ").strip()
    use_team_edition = input("Do you want to use the Team Edition? (yes/no): ").strip().lower() == 'yes'
    update_env_file(version, use_team_edition)

    print("Please edit the .env file to set the DOMAIN value for your Mattermost server.")
    input("Press Enter to continue after editing the .env file...")

    # Create the required directories and set their permissions
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    run_command("sudo chown -R 2000:2000 ./volumes/app/mattermost")

    # Optional: Configure TLS for NGINX if needed
    configure_tls = input("Do you want to configure TLS for NGINX? (yes/no): ").strip().lower()
    if configure_tls == "yes":
        create_certificate = input("Do you want to create a new certificate? (yes/no): ").strip().lower()
        if create_certificate == "yes":
            domain = input("Enter your Mattermost domain: ").strip()
            run_command(f"bash scripts/issue-certificate.sh -d {domain} -o {os.getcwd()}/certs")
            print("Please uncomment and set CERT_PATH and KEY_PATH in the .env file to point to the appropriate files.")
        else:
            pre_existing_cert = input("Enter the path to your pre-existing certificate (.pem file): ").strip()
            pre_existing_key = input("Enter the path to your pre-existing key (.pem file): ").strip()
            os.makedirs("./volumes/web/cert", exist_ok=True)
            shutil.copy(pre_existing_cert, "./volumes/web/cert/cert.pem")
            shutil.copy(pre_existing_key, "./volumes/web/cert/key-no-password.pem")
            with open('.env', 'a') as env_file:
                env_file.write("\nCERT_PATH=./volumes/web/cert/cert.pem")
                env_file.write("\nKEY_PATH=./volumes/web/cert/key-no-password.pem")

    # Deploy Mattermost
    use_nginx = input("Do you want to use the included NGINX reverse proxy? (yes/no): ").strip().lower()
    if use_nginx == "yes":
        run_command("sudo docker compose -f docker-compose.yml -f docker-compose.nginx.yml up --no-start")
        print("Mattermost deployment is set up with NGINX.")
    else:
        run_command("sudo docker compose -f docker-compose.yml -f docker-compose.without-nginx.yml up --no-start")
        print("Mattermost deployment is set up without NGINX.")

    # Update config.json to enable PluginSettings
    update_config_json()

    # Ask if the images should be started
    start_images = input("Do you want to start the Mattermost containers? (yes/no): ").strip().lower() == 'yes'
    if start_images:
        detached_mode = input("Do you want to start the containers in detached mode? (yes/no): ").strip().lower() == 'yes'
        if use_nginx == "yes":
            if detached_mode:
                run_command("sudo docker compose -f docker-compose.yml -f docker-compose.nginx.yml up -d")
            else:
                run_command("sudo docker compose -f docker-compose.yml -f docker-compose.nginx.yml up")
        else:
            if detached_mode:
                run_command("sudo docker compose -f docker-compose.yml -f docker-compose.without-nginx.yml up -d")
            else:
                run_command("sudo docker compose -f docker-compose.yml -f docker-compose.without-nginx.yml up")

    print("Mattermost deployment is complete. Please create your first Mattermost System Admin user, invite more users, and explore the Mattermost platform.")

if __name__ == "__main__":
    setup_mattermost()

