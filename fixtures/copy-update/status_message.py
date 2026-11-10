"""Build the one-line deployment status shown on the team dashboard."""


def status_message():
    # Support team copy: keep the format "<deployment>: ready".
    return "development: ready"


def help_message():
    return "Status looks wrong? Ask in #deployments before you redeploy."
