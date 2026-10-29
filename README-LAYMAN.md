# StegVerse SCW — plain-language guide

SCW (StegVerse Code Worker) is the repository that checks and coordinates other StegVerse
repositories. Most of it runs as automated checks on GitHub.

## The public page

The `ui/public/` folder is a small static website:

- `index.html` is the landing page, about private, resilient communication and the StegTalk beta.
- `stegtalk.html` is the StegTalk beta page. Phones can install it as an app through
  `manifest.json`, and it uses the icons in `ui/public/icons/`.
- `sw.js` keeps the main pages available offline after the first visit.
- `diag.html` is a diagnostics page.

It is hosted as a static site, with no server code. The host serves the `ui/public` folder as is.

## Where to read more

- `README.md` covers what SCW does and how its workflows are bounded.
- `README-DEV.md` covers how the UI is laid out and checked, for developers.
- `docs/` holds architecture, structure and governance documents.
