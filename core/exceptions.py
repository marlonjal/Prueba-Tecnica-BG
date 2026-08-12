"""Infrastructure failures kept separate from functional assertions."""


class EnvironmentUnavailable(RuntimeError):
    """The shared test environment cannot currently serve the request."""
