"""Build the one-line deployment status shown on the team dashboard."""


def status_message():
    deployment = "staging"
    return f"{deployment}: ready"
