# GitHub Repository Manager for MicroPython

This project allows you to manage GitHub repositories directly from a MicroPython device. Through an interactive console interface, you can create, list, update, delete repositories, upload files from the device, and more.

## Main Features

- Automatic Wi-Fi connection
- Create, list, update, and delete repositories
- Upload files from a local folder on the device
- Download files from a repository
- Create folders within the repository
- Works with authentication via GitHub token

## Requirements

- MicroPython-enabled device (e.g., ESP32, ESP8266)
- Access to a Wi-Fi network
- GitHub personal access token (with repository permissions)
- Auxiliary libraries:
  - `github_lib.py`: GitHub API handler
  - `network_iot.py`: Wi-Fi connection handler for the device

## Project Structure

```
.
├── main_git.py          # Main script of the program
├── github_lib.py        # GitHub API management module
├── network_iot.py       # Module to manage Wi-Fi connection
├── proyecto/            # Default folder with files to upload
└── README.md            # This file
```

## Usage

1. **Configure the `main_git.py` file:**
   - Add your GitHub token to the `TOKEN` variable.
   - Set your Wi-Fi `ssid` and `password`.

2. **Upload the project to your device** (e.g., using ampy or mpremote).

3. **Run the main script:**
   ```python
   import main_git
   main_git.main()
   ```

4. **Follow the interactive menu** to perform the desired actions.

## Available Menu

```
=== GITHUB REPOSITORY MANAGER ===
1. Create new repository
2. List my repositories
3. Update existing repository
4. Delete repository
5. List another user's repositories
6. Upload files to a repository
7. Create repository and upload files automatically
8. Download file from a repository
9. Create folder in a repository
0. Exit
```

## Notes

- The script expects to find files to upload in the `proyecto/` folder. You can change this in the `CARPETA_PROYECTO` constant.
- Some functions expect `github_lib.py` to implement methods such as `create_repository`, `upload_file`, `list_repositories`, `delete_repository`, etc.
