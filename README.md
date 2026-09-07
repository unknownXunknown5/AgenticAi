# AgenticAi


# what i learn 

dekho mera yeh workflow chal nahi raha tha twitter ke  api ke issue ke karna then maine cookie ka idea apna kar ai ko bola ki make the publisher.py such that ki usko cookie se login karke post kar de 


then scheduler ka yeh tha ki mujhe baar baar run karke chalana padta so i decided to just make a github workflow tu automate the work on github cloud enviroment so ki humsea run hote rahe 


# AgenticAi

## What I learned

My first workflow was not working because the X API authentication was a problem. I learned that I can use a browser session cookie instead: Playwright opens X, loads the saved session cookies, and publishes through the normal X website. This project still needs the Gemini API to generate and evaluate text, but it does not need the X posting API.

This is a learning note for running the project locally and on GitHub Actions. Never put real API keys or cookies in this README or commit them to GitHub.

## How the project works

The graph runs in this order:

```text
choose topic -> generate post with Gemini -> evaluate post -> improve if needed -> publish on X with Playwright
```

The main files are:

- `01/nodes/main.py`: runs the pipeline once.
- `01/nodes/publisher.py`: loads cookies and posts through the X website.
- `01/scheduler.py`: keeps a local computer process alive and runs posts at set times.
- `.github/workflows/daily_tweets.yml`: lets GitHub Actions run the pipeline in the cloud.
- `01/data/topics.json`: topics used by the generator.

## Important lesson: API versus cookies

There are two different login requirements:

1. `GEMINI_API_KEY` is required for Gemini to generate and score the post.
2. X authentication can use either `01/data/cookies.json` or the fallback values `X_AUTH_TOKEN` and `X_CT0`.

The preferred X method in this project is `data/cookies.json` because it uses an already logged-in browser session. Cookies can expire or be invalidated, so they must occasionally be exported again.

### Cookie method: local setup

1. Log in to `https://x.com` in your browser.
2. Export the cookies for the X domain as JSON using a trusted cookie-export tool.
3. Save the exported JSON as:

	 ```text
	 01/data/cookies.json
	 ```

4. Make sure the file contains a JSON array. A cookie normally looks like this:

	 ```json
	 [
		 {
			 "name": "auth_token",
			 "value": "YOUR_PRIVATE_COOKIE_VALUE",
			 "domain": ".x.com",
			 "path": "/",
			 "secure": true,
			 "httpOnly": true
		 },
		 {
			 "name": "ct0",
			 "value": "YOUR_PRIVATE_CSRF_VALUE",
			 "domain": ".x.com",
			 "path": "/",
			 "secure": true,
			 "httpOnly": false
		 }
	 ]
	 ```

The exporter may include additional cookies. Keep the complete exported array; `publisher.py` converts the common browser cookie fields into the format Playwright needs. Do not paste real cookie values into chat, README files, screenshots, or GitHub commits. A cookie can provide access to your account like a password.

The code first tries `data/cookies.json`. If that file is missing or invalid, it falls back to this smaller `.env` setup:

```env
X_AUTH_TOKEN=your_auth_token
X_CT0=your_ct0_value
```

If X redirects to a login page, the session is expired or the cookie file is invalid. Export fresh cookies and replace `01/data/cookies.json`.

## Local setup

Open PowerShell and run these commands from the `01` directory. The working directory matters because the code reads `data/topics.json` and `data/cookies.json` using relative paths.

```powershell
cd C:\Users\hp\Desktop\ProjectLangchian\01
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
playwright install chromium
```

Create `01/.env`:

```env
GEMINI_API_KEY=your_gemini_key
TIMEZONE=Asia/Kolkata
POST_HOURS=10,15,20
POST_MINUTE=0

# Optional fallback if cookies.json is unavailable.
X_AUTH_TOKEN=your_auth_token
X_CT0=your_ct0_value
```

Test one complete run:

```powershell
python -m nodes.main
```

Before using a real account, confirm that the generated text, account, and browser session are correct. The publisher posts to the account represented by the session cookies.

## Local scheduler

The local scheduler is a process that must remain running. It is useful on a personal computer or server, but it stops when the terminal, computer, or process stops.

Run once immediately and then keep waiting for scheduled times:

```powershell
python scheduler.py --now
```

Only wait for scheduled times:

```powershell
python scheduler.py
```

Stop it with `Ctrl+C`. The default schedule is 10:00, 15:00, and 20:00 in `Asia/Kolkata`. Change it with `POST_HOURS`, `POST_MINUTE`, and `TIMEZONE` in `.env`.

## Run it in the cloud with GitHub Actions

The cloud method does not keep `scheduler.py` running. GitHub starts a fresh Ubuntu machine for each scheduled workflow run, installs the project, creates the cookie file from a secret, and runs `python -m nodes.main` once.

### 1. Put the project on GitHub

1. Create or open a GitHub repository.
2. Push this project to the repository.
3. Confirm that `.gitignore` excludes `.env` and `data/cookies.json`.
4. Confirm that the workflow exists at `.github/workflows/daily_tweets.yml`.

Never push `.env` or `data/cookies.json`. If either was pushed, remove it from the repository history and immediately rotate the exposed keys/cookies.

### 2. Add GitHub Actions secrets

In the repository on GitHub, open **Settings -> Secrets and variables -> Actions -> New repository secret**. Add these names exactly:

```text
GEMINI_API_KEY
X_COOKIES_JSON
X_AUTH_TOKEN
X_CT0
```

Use the following values:

- `GEMINI_API_KEY`: the Gemini API key.
- `X_COOKIES_JSON`: the complete contents of the local `01/data/cookies.json` file, including the opening `[` and closing `]`.
- `X_AUTH_TOKEN`: optional fallback X auth token.
- `X_CT0`: optional fallback X CSRF token.

The cookie secret is the main X login method. The token secrets are kept as a fallback in case the cookie secret is absent or cannot be loaded.

### 3. Test the workflow manually

1. Open the repository's **Actions** tab.
2. Select **Agentic AI Daily Tweet Publisher**.
3. Click **Run workflow**.
4. Select the branch and click **Run workflow** again.
5. Open the new job and inspect each step.
6. The final step should show the generated post and a successful publish message.

If it fails, open the failed step's log. Common causes are an expired cookie, a missing Gemini key, an incorrectly copied JSON secret, or a changed X website selector.

### 4. Understand the cloud schedule

GitHub Actions cron uses UTC, not `TIMEZONE`. This workflow currently runs at:

```text
04:30 UTC = 10:00 Asia/Kolkata
09:30 UTC = 15:00 Asia/Kolkata
14:30 UTC = 20:00 Asia/Kolkata
```

The schedule is stored in `.github/workflows/daily_tweets.yml`. GitHub scheduled jobs can start a little late, so the cron time is the start request, not a guaranteed exact posting second.

## Troubleshooting checklist

### Gemini/API error

- Check that `GEMINI_API_KEY` exists and is valid.
- Check that the key has access to the Gemini model used by the code.
- Run `python -m nodes.main` locally to see the full error.

### X login or cookie error

- Confirm `01/data/cookies.json` is valid JSON.
- Confirm the secret `X_COOKIES_JSON` contains the complete JSON array, not a file path.
- Export fresh cookies after logging in again.
- Do not use cookies from a different account or domain.

### Playwright error

Run this from `01`:

```powershell
playwright install chromium
```

GitHub Actions already runs `playwright install chromium --with-deps` for Ubuntu.

### Scheduler appears not to work

- Run it from `01`, not the repository root.
- Use `python scheduler.py --now` to test immediately.
- Keep the terminal open while `python scheduler.py` is running.
- For cloud execution, use the GitHub Actions workflow; do not expect the local scheduler process to run on GitHub.

## Security reminders

- Treat Gemini keys, X tokens, and X cookies as passwords.
- Keep `.env` and `data/cookies.json` private.
- Store cloud credentials only in GitHub Actions Secrets.
- Rotate credentials if they are exposed.
- Review GitHub Actions logs and never print secret values.
