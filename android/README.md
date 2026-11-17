# UALP Android private TEST wrapper (not a standalone/offline backend)

This small Android WebView APK opens the exact existing UALP FastAPI/Vercel TEST hostname, in an app-specific persistent WebView cookie store. Work Values, RIASEC, profile, history and incomplete drafts continue to use the existing web TEST runtime. A network connection is required. This is **not** an independent mobile database, not a public release, and not evidence of psychometric validity.

- Stable URL: `https://ualp-app-git-feature-ualp-mvp-006-draft-6b4814-vahram-sargsyan.vercel.app/`.
- APK package: `am.ualp.privatepilot`; Android 8+.
- Allowlisted first-party HTTPS navigation only; external HTTPS links open in the system browser; arbitrary schemes blocked.
- CookieManager stores the existing 30-day Secure/HttpOnly/Strict owner cookie. You may have to enter the key ONCE within the APK because Chrome and WebView have different cookie stores. **Do not copy credentials into APK source or app storage.** Cookies expire, a TEST key rotation invalidates sessions, and explicit Logout removes them.
- In-app "На главную" only switches the existing single-page UI; it does not log the user out. Android Back returns to an existing WebView page or minimizes the app, rather than creating new browser contexts.
- The debug APK is intended for a single owner's isolated TEST, not public distribution. A new CI debug APK uses an ephemeral development signing key; it **cannot be updated in-place** if its signing certificate differs. Stable repeatable signed releases would require an approved private signing-key workflow. Do not commit a signing key.
- Download the `ualp-android-test-apk` artifact ZIP from the matching GitHub Actions PR run, extract `app-debug.apk`, install on the owner's Android phone (the OS might ask to enable installs from that source). **Do not publish** or promote the APK to PROD.
- Test: open APK, sign in once with Remember enabled, go to Profile then "На главную", repeat, minimize/reopen the installed app, and verify Profile opens without the password. Run existing test scenarios for history and form submission only with explicit consent.
- Rollback: uninstall the TEST wrapper APK only. The server, Neon saved results and Chrome installation remain untouched. Do not clear server data.
