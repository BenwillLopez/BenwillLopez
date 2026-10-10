# altsource

One AltStore/SideStore source that merges all the sources in `sources.txt`.
A GitHub Action rebuilds it every day.

**Add this URL to the app:**

```
https://raw.githubusercontent.com/benwilllopez/altsource/main/source.json
```

## Setup (one time)

1. Create a **public** repo named `altsource` on GitHub.
2. Upload everything in this folder to it, including the hidden `.github` folder.
3. Open **Actions**, then enable workflows if GitHub asks.
4. Open **Actions → Build source → Run workflow**. Wait for the green check.
5. Add the URL above in AltStore or SideStore.

## Changing sources

Edit `sources.txt`: one URL per line, lines starting with `#` are ignored.
Saving it starts a rebuild. When two sources list the same app (same bundle ID),
the source higher in the list wins.

If a source is down during a build, its apps from the last good build are kept
(from `cache/`). The Action log shows each source as `ok`, `cached` or `FAILED`.
