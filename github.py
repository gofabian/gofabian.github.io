import os
import subprocess

from log import log


def git_commit_and_push():
    if os.getenv("GITHUB_ACTIONS") != "true":
        log("No Github Actions context -> skip 'git commit and push'")
        return

    # Prüfen, ob wir in einem Git-Repo sind
    subprocess.run(["git", "rev-parse", "--is-inside-work-tree"], check=True, capture_output=True)

    # Git-Config setzen
    subprocess.run(["git", "config", "--global", "user.name", "github-actions[bot]"], check=True)
    subprocess.run(["git", "config", "--global", "user.email", "github-actions[bot]@users.noreply.github.com"],
                   check=True)

    # Änderungen hinzufügen und committen
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", "Apply automatic changes"],
                   check=False)  # kein Fehler, falls keine Änderungen

    # Falls in der Zwischenzeit neuere Commits existieren
    try:
        subprocess.run(["git", "pull"], check=True, text=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        log("Git failed with message:\n", e.stderr)
    # Push zum Remote
    subprocess.run(["git", "push"], check=True)

    log("✅ Änderungen wurden erfolgreich gepusht.")
