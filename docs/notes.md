```
python app.py --enable-background --subreddits BreakUps+DeadBedrooms+LongDistance+RelationshipsOver35+dating_advice+polyamory+relationship_advice+relationshipproblems --story-mode
```

## Using Dev Containers

A basic VSCode dev container has been made available to simplify local development.

### Pre-requisites

- Visual Studio Code
- Docker Desktop

### Configuring your local environment.

Open the repo folder locally when performing the below steps, don't do this
through a WSL remote connection, or the devcontainer build will fail. The
assumption is that Docker Desktop is configured to use the WSL2 based engine.

1. Install the **Dev Containers** Visual Studio Code extension.
2. Press **Ctrl+Shift+P** to open the command palette and run
   "Dev Containers: Open workspace in container".
3. Wait about 15mins for the devcontainer to be built. Don't worry, this is
   only slow the first time the image is built. It will:
    - Install ImageMagick and update the security policy.
    - Download the latest version of yt-dlp.
    - Initialize playwright, including downloading the Firefox browser.
    - Install python dependencies needed to run the application, as defined in
      `requirements.txt`.
    - Install python dependencies needed for local development, as defined in
      `requirements-dev.txt`.

### Future Improvements

- Pre-build the base image to reduce startup time.
- Add firstrun script to configure settings.py.
- Configure pre-commit to ensure static analysis/tests are executed during 
  commit process.