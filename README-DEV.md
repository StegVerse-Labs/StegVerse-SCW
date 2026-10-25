# StegVerse SCW — developer notes

The general overview and the workflow boundaries are in `README.md`. The repository tree is in `docs/STRUCTURE.md`.

## UI layout

```
ui/
  public/            static site root (served as is)
    index.html       landing page (served at /, precached by sw.js)
    stegtalk.html    StegTalk beta page (manifest start_url)
    diag.html        diagnostics page
    manifest.json    web app manifest; icons at /icons/icon-192.png and /icons/icon-512.png
    sw.js            service worker; precaches /, /stegtalk.html, /manifest.json
    icons/           icon-192.png, icon-512.png
  pages/index.js     Next.js page (ui/package.json: next build && next export)
```

The file names are case-sensitive. Static hosts on Linux serve `/` from `index.html`, so the landing
page must use that exact name.

## Hosting (Render static site `scw-ui`)

- Type: Static Site
- Root Directory: `ui/public`
- Publish Directory: `.`

## Checks

`.github/workflows/verify_ui.yml` asserts that the files above exist, together with this file and
`README-LAYMAN.md`. It needs no credential, and it reads the checked-out tree only.
