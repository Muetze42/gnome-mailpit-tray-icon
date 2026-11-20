#!/usr/bin/python3
"""Install for the current user; never run with sudo."""
import argparse
import os
from pathlib import Path
import shutil
import subprocess


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mailpit', help='Path to an existing Mailpit executable')
    parser.add_argument('--no-start', action='store_true', help='Install without enabling or starting the service')
    args = parser.parse_args()
    if os.getuid() == 0:
        parser.error('Run as your desktop user, without sudo.')
    binary = shutil.which(args.mailpit or 'mailpit')
    if not binary:
        parser.error('Install Mailpit first or pass --mailpit /absolute/path/to/mailpit')
    subprocess.run(['/usr/bin/python3', '-c', 'import gi; gi.require_version("Gtk", "3.0"); gi.require_version("AyatanaAppIndicator3", "0.1"); from gi.repository import Gtk, AyatanaAppIndicator3'], check=True)
    for command in ('systemctl', 'xdg-open', 'notify-send', 'xdg-user-dir'):
        if not shutil.which(command):
            parser.error(f'Missing dependency: {command}')
    source = Path(__file__).resolve().parent
    home = Path.home()
    config = Path(os.environ.get('XDG_CONFIG_HOME', home / '.config'))
    app = home / '.local/bin/mailpit-tray'
    icons = home / '.local/share/icons/hicolor/scalable/status'
    applications = home / '.local/share/applications'
    unit = config / 'systemd/user/mailpit.service'
    autostart = config / 'autostart/mailpit-tray.desktop'
    desktop_dir = Path(subprocess.check_output(['xdg-user-dir', 'DESKTOP'], text=True).strip())
    if not desktop_dir.is_absolute() or desktop_dir == home:
        desktop_dir = home / 'Desktop'
    desktop = desktop_dir / 'mailpit-tray.desktop'
    # Keep pre-existing files so a repeated installation is recoverable.
    def write(path, data, executable=False):
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            shutil.copy2(path, str(path) + '.bak')
        path.write_bytes(data)
        if executable:
            path.chmod(0o755)
    write(app, (source / 'mailpit-tray').read_bytes(), True)
    for icon in (source / 'icons').glob('*.svg'):
        write(icons / icon.name, icon.read_bytes())
    def quote(value):
        return '"' + str(value).replace('\\', '\\\\').replace('"', '\\"').replace('$', '\\$').replace('`', '\\`') + '"'
    launcher = (source / 'mailpit-tray.desktop').read_text().replace('@EXEC@', quote(app).replace('%', '%%').replace('\\', '\\\\'))
    write(applications / desktop.name, launcher.encode())
    write(desktop, launcher.encode(), True)
    write(autostart, (launcher + 'X-GNOME-Autostart-enabled=true\nX-GNOME-Autostart-Delay=3\n').encode())
    executable = str(Path(binary).resolve()).replace('\\', '\\\\').replace('"', '\\"').replace('%', '%%').replace('$', '$$')
    service = (source / 'mailpit.service').read_text().replace('@MAILPIT@', '"' + executable + '"')
    write(unit, service.encode())
    subprocess.run(['systemctl', '--user', 'daemon-reload'], check=True)
    if not args.no_start:
        subprocess.run(['systemctl', '--user', 'enable', '--now', 'mailpit.service'], check=True)
    print(f'Installed. Start {app} or open the Mailpit launcher. Desktop shortcut: {desktop}')
    print('GNOME may require right-click → Allow Launching on the desktop shortcut.')


if __name__ == '__main__':
    main()
