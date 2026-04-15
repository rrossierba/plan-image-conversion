#!/bin/bash
set -e

USER_ID=${USER_ID:-1000}
GROUP_ID=${GROUP_ID:-1000}
USERNAME=${USERNAME:-user}

echo "Run as user: ${USERNAME} (UID=${USER_ID}, GID=${GROUP_ID})"

if ! getent group ${GROUP_ID} > /dev/null 2>&1; then
    groupadd -g ${GROUP_ID} ${USERNAME}
fi

if ! getent passwd ${USER_ID} > /dev/null 2>&1; then
    useradd -u ${USER_ID} -g ${GROUP_ID} -m -s /bin/bash ${USERNAME}
fi

chown -R ${USER_ID}:${GROUP_ID} /app /result

exec gosu ${USERNAME} "$@"