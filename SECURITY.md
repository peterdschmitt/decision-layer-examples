# Keys and secrets

- The only secret these examples use is an API key, read from the `TYPESAFE_API_KEY` environment variable at the moment a request is sent.
- No key, token or password is ever committed here. `.gitignore` blocks `.env` files, and a check on every push and pull request looks for the key name set to a value.
- The code never prints, logs or echoes the key. Error messages show the HTTP status, not the request headers.
- Sample inputs are made up. Never put real claims, submissions or customer details in an issue or pull request.

If you spot a secret in this repo, please email info@converselyai.com rather than opening a public issue.
