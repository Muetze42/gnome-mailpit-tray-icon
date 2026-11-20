# GNOME Mailpit Tray Icon

Python/GTK tray controller for a local [Mailpit](https://mailpit.axllent.org/) instance. Start/stop the service, open the web UI, and monitor service status through four state icons.

Tested with **GNOME 50 on Ubuntu 26**.

## AI Disclosure

Developed with AI assistance using **OpenAI Codex**.

## Requirements

- GNOME with AppIndicator support and a systemd user session.
- System Python 3 (`/usr/bin/python3`).
- PyGObject, GTK 3, Ayatana AppIndicator, `notify-send`, and XDG utilities.
- [Mailpit](https://mailpit.axllent.org/docs/install/) installed separately, on `PATH` or supplied via `--mailpit`. The service references its absolute path.

### Ubuntu — Python runtime:

```sh
sudo apt install python3
```

### Desktop dependencies:

```sh
sudo apt install python3-gi gir1.2-gtk-3.0 gir1.2-ayatanaappindicator3-0.1 libnotify-bin xdg-utils gnome-shell-extension-appindicator
```

## Install

```sh
python3 install.py
# Explicit Mailpit executable:
python3 install.py --mailpit /path/to/mailpit
```

Installation enables and starts `mailpit.service`. `--no-start` skips service enable/start; it still installs tray autostart and leaves existing service enablement unchanged.

| Component | Destination |
|----------------------|--------------------------------------------------------------|
| Tray executable | `~/.local/bin/mailpit-tray` |
| Status icons | `~/.local/share/icons/hicolor/scalable/status/mailpit-*.svg` |
| User service | `$XDG_CONFIG_HOME/systemd/user/mailpit.service` |
| Tray autostart | `$XDG_CONFIG_HOME/autostart/mailpit-tray.desktop` |
| Application launcher | `~/.local/share/applications/mailpit-tray.desktop` |

`XDG_CONFIG_HOME` defaults to `~/.config`. Existing files are backed up as `.bak` (replaced on subsequent installs).

## Runtime

- **Server:** systemd user service, starts at login.
- **Tray:** GNOME autostart, starts at graphical login. Launch immediately with `~/.local/bin/mailpit-tray`.
- **Web:** http://127.0.0.1:8025/
- **SMTP:** `127.0.0.1:1025`, no authentication or TLS.

Both listeners bind to loopback. Status polling runs every three seconds. Only one tray instance runs per user; quitting it leaves Mailpit running. Startup before login is not configured.

## Diagnostics

```sh
systemctl --user status mailpit.service
journalctl --user -u mailpit.service -n 50
systemctl --user restart mailpit.service
```

For a missing tray icon, check the GNOME AppIndicator extension. Run `~/.local/bin/mailpit-tray` in a terminal for GTK/Python errors. Service startup failures may indicate occupied ports or an invalid Mailpit executable path.

## Uninstall

Quit the tray, then:

```sh
systemctl --user disable --now mailpit.service
```

Remove the files listed under **Install**, then run `systemctl --user daemon-reload`. Restore `.bak` files if needed. The separately installed Mailpit executable is unaffected.

## License

[MIT](LICENSE)
