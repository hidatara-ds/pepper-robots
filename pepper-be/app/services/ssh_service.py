"""
SSH Service for Pepper Robot Communication
Handles SSH connections and file transfers to Pepper robot
"""

import os
import logging
import paramiko
import subprocess
from typing import Tuple, Optional
from dotenv import load_dotenv

load_dotenv()

# Configuration from environment variables with fallback defaults
PEPPER_IP = os.getenv('PEPPER_IP', '192.168.43.15')
USERNAME = os.getenv('PEPPER_SSH_USERNAME', 'nao')
PASSWORD = os.getenv('PEPPER_SSH_PASSWORD', 'changeme')
SSH_TIMEOUT = int(os.getenv('PEPPER_SSH_TIMEOUT', '10'))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SSHService:
    @staticmethod
    def send_ssh_command(command: str) -> Tuple[str, str]:
        """
        Send SSH command to Pepper robot
        
        Args:
            command: Command string to execute on Pepper robot
            
        Returns:
            Tuple of (output, error) strings from command execution
        """
        client = None
        try:
            logger.info(f"Connecting to Pepper robot at {PEPPER_IP} to execute command: {command}")
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            client.connect(
                PEPPER_IP,
                username=USERNAME,
                password=PASSWORD,
                look_for_keys=False,
                allow_agent=False,
                auth_timeout=SSH_TIMEOUT,
                timeout=SSH_TIMEOUT
            )

            stdin, stdout, stderr = client.exec_command(command)
            output = stdout.read().decode()
            error = stderr.read().decode()
            
            if error:
                logger.warning(f"Command execution returned error: {error}")
            else:
                logger.info(f"Command executed successfully. Output length: {len(output)} chars")
            
            return output, error
            
        except paramiko.AuthenticationException:
            logger.error(f"Authentication failed for {USERNAME}@{PEPPER_IP}")
            return "", "Authentication failed"
        except paramiko.SSHException as e:
            logger.error(f"SSH connection error: {e}")
            return "", str(e)
        except Exception as e:
            logger.error(f"Unexpected error executing SSH command: {e}")
            return "", str(e)
        finally:
            if client:
                client.close()

    @staticmethod
    def send_file_to_pepper(local_file_path: str, remote_directory: str = "/home/nao/audio/") -> bool:
        """
        Send file to Pepper robot via SFTP
        
        Args:
            local_file_path: Path to local file to upload
            remote_directory: Remote directory path on Pepper robot (default: /home/nao/audio/)
            
        Returns:
            True if upload successful, False otherwise
        """
        client = None
        sftp = None
        try:
            if not local_file_path or not os.path.exists(local_file_path):
                raise ValueError(f"Local file path is invalid or file does not exist: {local_file_path}")

            logger.info(f"Uploading file {local_file_path} to {PEPPER_IP}:{remote_directory}")
            
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            client.connect(
                PEPPER_IP,
                username=USERNAME,
                password=PASSWORD,
                look_for_keys=False,
                allow_agent=False,
                auth_timeout=SSH_TIMEOUT,
                timeout=SSH_TIMEOUT
            )

            sftp = client.open_sftp()
            filename = os.path.basename(local_file_path)
            remote_path = os.path.join(remote_directory, filename).replace('\\', '/')

            sftp.put(local_file_path, remote_path)
            logger.info(f"File uploaded successfully to {remote_path}")
            
            return True
            
        except paramiko.AuthenticationException:
            logger.error(f"Authentication failed for {USERNAME}@{PEPPER_IP}")
            return False
        except paramiko.SSHException as e:
            logger.error(f"SSH/SFTP error: {e}")
            return False
        except Exception as e:
            logger.error(f"Error uploading file to Pepper: {e}")
            return False
        finally:
            if sftp:
                sftp.close()
            if client:
                client.close()
        
    @staticmethod
    def send_bytes_to_pepper(audio_bytes: bytes, remote_filename: str, remote_directory: str = "/home/nao/audio/") -> bool:
        """
        Send bytes data (e.g., audio) directly to Pepper robot via SFTP
        
        Args:
            audio_bytes: Bytes data to upload
            remote_filename: Filename for the remote file
            remote_directory: Remote directory path on Pepper robot (default: /home/nao/audio/)
            
        Returns:
            True if upload successful, False otherwise
        """
        client = None
        sftp = None
        try:
            if not audio_bytes:
                raise ValueError("audio_bytes is None or empty")
            
            if not remote_filename:
                raise ValueError("remote_filename is required")

            logger.info(f"Uploading {len(audio_bytes)} bytes as {remote_filename} to {PEPPER_IP}:{remote_directory}")
            
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            client.connect(
                PEPPER_IP,
                username=USERNAME,
                password=PASSWORD,
                look_for_keys=False,
                allow_agent=False,
                auth_timeout=SSH_TIMEOUT,
                timeout=SSH_TIMEOUT
            )

            sftp = client.open_sftp()
            remote_path = os.path.join(remote_directory, remote_filename).replace('\\', '/')

            with sftp.open(remote_path, 'wb') as remote_file:
                remote_file.write(audio_bytes)

            logger.info(f"Bytes uploaded successfully to {remote_path}")
            return True
            
        except paramiko.AuthenticationException:
            logger.error(f"Authentication failed for {USERNAME}@{PEPPER_IP}")
            return False
        except paramiko.SSHException as e:
            logger.error(f"SSH/SFTP error: {e}")
            return False
        except Exception as e:
            logger.error(f"Error uploading bytes to Pepper: {e}")
            return False
        finally:
            if sftp:
                sftp.close()
            if client:
                client.close()    

