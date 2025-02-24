ARG VARIANT="3.11"
FROM mcr.microsoft.com/devcontainers/python:${VARIANT}

# Install task
RUN sh -c "$(curl --location https://taskfile.dev/install.sh)" -- -d -b /usr/local/bin

# Install uv
# RUN sh -c "$(curl --location https://taskfile.dev/install.sh)" -- -d -b /usr/local/bin

# # Auto-activate virtualenv
# ENV VIRTUAL_ENV=/workspaces/asyncio-gevent/.venv
# ENV PATH="$VIRTUAL_ENV/bin:$PATH"

