import paramiko
import subprocess

PEPPER_IP = "192.168.43.15"
USERNAME = "nao"
PASSWORD = "changeme"

class SSHService:
    @staticmethod
    def send_ssh_command(command):
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        client.connect(
            PEPPER_IP,
            username=USERNAME,
            password=PASSWORD,
            look_for_keys=False,
            allow_agent=False,
            auth_timeout=10
        )

        stdin, stdout, stderr = client.exec_command(command)
        output = stdout.read().decode()
        error = stderr.read().decode()
        client.close()

        return output, error

    @staticmethod
    def send_file_to_pepper(local_file_path: str, remote_directory: str = "/home/nao/audio/") -> bool:
        try:
            if not local_file_path:
                raise ValueError("local_file_path is None or empty")

            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            client.connect(
                PEPPER_IP,
                username=USERNAME,
                password=PASSWORD,
                look_for_keys=False,
                allow_agent=False,
                auth_timeout=10
            )

            sftp = client.open_sftp()
            filename = local_file_path.split('/')[-1]
            remote_path = remote_directory + filename

            sftp.put(local_file_path, remote_path)
            sftp.close()
            client.close()

            return True
        except Exception as e:
            print(f"[SCP ERROR]: {e}")
            return False
        
    @staticmethod
    def send_bytes_to_pepper(audio_bytes: bytes, remote_filename: str, remote_directory: str = "/home/nao/audio/") -> bool:
        try:
            if not audio_bytes:
                raise ValueError("audio_bytes is None or empty")

            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            client.connect(
                PEPPER_IP,
                username=USERNAME,
                password=PASSWORD,
                look_for_keys=False,
                allow_agent=False,
                auth_timeout=10
            )

            sftp = client.open_sftp()
            remote_path = remote_directory + remote_filename

            with sftp.open(remote_path, 'wb') as remote_file:
                remote_file.write(audio_bytes)

            sftp.close()
            client.close()

            return True
        except Exception as e:
            print(f"[SCP ERROR]: {e}")
            return False
        
    

        
    

