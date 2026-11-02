# mobile-code-reviewer

A minimal web app for reviewing code changes on a phone.

It lists every git repository next to this one (the sibling folders in its parent directory). Tap a repository to see its `git diff`.

## Usage

```sh
make build   # build the Docker image
make start   # start the container in the background
make stop    # stop and remove the container
```

Then open `http://<tailscale-hostname>:8043` on a device in your tailnet.

The port is bound only to the host's Tailscale IPv4 address, so the app is not reachable from the local network or the internet. Tailscale must be running when you run `make start`.

The parent directory of this repository is mounted read-only into the container at `/repos`.

## Interface

- **Home** (top left): back to the repository list.
- **Fullscreen** (top right): enter or leave fullscreen.
- **Orientation lock**: entering fullscreen locks the page to portrait.

## Browser support

Fullscreen and the orientation lock currently work only in **Chrome on Android**. Other browsers, notably iOS Safari, don't support the Screen Orientation lock API. There, a CSS fallback rotates the page back to portrait when the phone is turned, but this is best effort.

## Security

There is no authentication of its own. Access is limited to devices in your tailnet, which can see the diffs of all sibling repositories. Your tailnet's access rules decide which devices those are.
