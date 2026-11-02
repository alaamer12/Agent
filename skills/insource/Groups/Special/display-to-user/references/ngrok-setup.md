# ngrok setup reference

Read this when `scripts/ngrok_tunnel.py check` reports `NOT_INSTALLED` or
`NOT_AUTHED`, so you can give the user precise remediation steps instead of
vague "go install ngrok" guidance.

## If NOT_INSTALLED

ngrok has no package-manager-free single command; installation differs by OS.
Tell the user to do ONE of the following, then re-run the skill:

**macOS (Homebrew):**
```
brew install ngrok/ngrok/ngrok
```

**Windows (winget or Chocolatey):**
```
winget install ngrok.ngrok
```
or
```
choco install ngrok
```

**Linux (apt, Debian/Ubuntu):**
```
curl -sSL https://ngrok-agent.s3.amazonaws.com/ngrok.asc \
  | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null \
  && echo "deb https://ngrok-agent.s3.amazonaws.com buster main" \
  | sudo tee /etc/apt/sources.list.d/ngrok.list \
  && sudo apt update && sudo apt install ngrok
```

**Any OS (manual download):**
Direct the user to https://ngrok.com/download — download the binary for
their OS/architecture, unzip it, and place it somewhere on their PATH.

Do not attempt to install ngrok yourself via bash_tool on the user's behalf —
you do not have access to the user's actual machine; you are only advising
them what to run locally.

## If NOT_AUTHED (installed but no authtoken configured)

ngrok requires a free account and an authtoken even for the free tier. Tell
the user:

1. Sign up (free) at https://dashboard.ngrok.com/signup
2. Copy their authtoken from https://dashboard.ngrok.com/get-started/your-authtoken
3. Run:
   ```
   ngrok config add-authtoken <THEIR_TOKEN>
   ```
4. Re-run the skill once that succeeds.

You can verify success yourself by re-running `scripts/ngrok_tunnel.py check`
— do not just assume it worked because the user said so; check should report
`OK` before proceeding to `start`.

## Custom domains / subdomains

By default, `scripts/ngrok_tunnel.py start` requests a random ngrok-assigned
URL (e.g. `https://a1b2c3.ngrok-free.app`), matching this skill's default
behavior of always using ngrok's default random URL. Only pass a custom
subdomain or reserved domain if the user explicitly asks for one — most
custom-domain features require a paid ngrok plan, and requesting one when
the user is on the free tier will make `ngrok http` fail outright. If the
user does ask for a specific subdomain, warn them ahead of time that it
requires a paid plan if you're not sure of their plan tier, and pass
`--subdomain <name>` to the start script accordingly.
