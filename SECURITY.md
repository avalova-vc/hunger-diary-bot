# Security notes

- Never commit `.env`, `deploy/secrets.env`, or private SSH keys.
- Rotate `BOT_TOKEN` in @BotFather if it was ever pasted into a chat or screenshot.
- Keep the repository private if you store personal health-related discussion in issues; the bot itself stores data only on the machine where it runs (SQLite), not on GitHub.
