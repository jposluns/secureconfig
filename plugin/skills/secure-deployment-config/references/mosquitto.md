# Mosquitto (MQTT): no anonymous clients, TLS listener

MQTT brokers back IoT and agent projects, and open brokers leak live telemetry and accept injected commands. Mosquitto's defaults are sane on version 2.0 and later (with a listener defined, anonymous access is off; without any listener it binds the loopback interface only); the job is to keep them sane while adding real listeners.

## 1. Credentials per device

```bash
sudo mosquitto_passwd -c /etc/mosquitto/passwd device-01     # -c only the first time
sudo mosquitto_passwd /etc/mosquitto/passwd device-02
```

`/etc/mosquitto/conf.d/secure.conf`:

```
per_listener_settings false
allow_anonymous false
password_file /etc/mosquitto/passwd
```

One credential per device, so a leaked unit can be revoked alone; add an `acl_file` to limit each identity to its own topics.

## 2. TLS listener

```
listener 8883
cafile   /etc/mosquitto/tls/ca.pem
certfile /etc/mosquitto/tls/server.pem
keyfile  /etc/mosquitto/tls/server.key
# mutual TLS: clients must present certificates
# require_certificate true
```

Port 8883 is the conventional MQTT-over-TLS port. Certificates per [self-signed.md](self-signed.md) (an internal CA suits device fleets) or [free-certificates.md](free-certificates.md). `require_certificate true` makes a client certificate a possession factor for the connecting device, stronger than a password alone but not MFA for a person ([mfa.md](mfa.md)). Remove or firewall any plaintext `listener 1883` that is not strictly local. These snippets take effect only if the running broker loads `/etc/mosquitto/conf.d/` (confirm `include_dir` in the active config); a `listener` change is not applied on a reload signal, so restart the broker and check its startup log after editing.

## 3. Verify

```bash
# These are MANUAL checks: read the -d CONNACK output, not the exit status. mosquitto_sub exits 27 on a
# -W timeout even after a successful connect, and nonzero on a refusal, so each is wrapped to capture its
# status without aborting under set -e. Keep the client config clean: a default mosquitto client config
# (e.g. ~/.config/mosquitto_sub) can carry credentials, a SOCKS proxy, or an --insecure setting, so run
# these where there is none, or inspect it first. If require_certificate true is set, TLS rejects before
# the password check, so add --cert 'client.pem' --key 'client.key' (your paths, inside the quotes) to BOTH controls below and test a
# missing-client-certificate connection separately. -x sets MQTT session expiry (NOT a TLS bypass) and
# --insecure disables hostname verification; use neither here.
# Positive control: a valid device connects. Expect "received CONNACK (0)" in the output; the command
# then exits 27 when -W 2 elapses, which is the accepted-and-idle case, not a failure.
if mosquitto_sub -d -W 2 -h mq.example.com -p 8883 --cafile ca.pem -t 'test' -u device-01 -P 'REPLACE_WITH_DEVICE_PASSWORD'
then echo "connected and stayed (accepted)"; else echo "exit $? (27 = connected then -W timeout = accepted; confirm CONNACK (0) above)"; fi
# Negative control: NO credentials must be refused AT CONNECT, not merely denied the subscription.
# Expect "received CONNACK (5)" (MQTT 3.1.1 not authorized) or "(135)" (MQTT 5). An anonymous CONNECT
# that succeeds (CONNACK (0)) and only fails the SUBSCRIBE (e.g. under an acl_file) means the broker
# still accepts anonymous clients: that is a finding.
if mosquitto_sub -d -W 2 -h mq.example.com -p 8883 --cafile ca.pem -t 'test'
then echo "FINDING: anonymous CONNECT accepted"; else echo "exit $? (expected: CONNACK 5/135 refusal - confirm above, NOT a SUBACK denial)"; fi
ss -tlnp   # inventory the listeners (needs sudo for the process column); ss shows a local BIND, not a
           # firewall or external reachability. There must be no 1883 listener on ANY non-loopback
           # address - 0.0.0.0, ::, or a specific external IP, IPv4 or IPv6 - unless it is firewalled to
           # localhost. The plaintext 1883 listener is the main exposure (section 2), so also probe each
           # public address from ANOTHER host, using the corpus guard so an unsubstituted target cannot
           # masquerade as a pass:
(                              # a subshell, so your own script arguments are untouched
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_THE_BROKER_PUBLIC_HOST'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit; }
  shift
  [ "$#" -eq 1 ] || { echo "the set -- line needs exactly 1 value; not probing"; exit; }
  case "$1" in
    *REPLACE_WITH_*|"") echo "substitute the broker's public host on the set -- line above; not probing" ;;
    *) nc -vz -w 5 "$1" 1883 || true ;;   # refused/timeout = TCP 1883 unreachable from here (the pass); a completed connect means TCP 1883 is reachable off-host. nc sends no MQTT, so this shows reachability, not the service or its encryption; the positive control against the intended endpoint must have succeeded first
  esac
)
```

## Sources (checked September 2026)

- mosquitto.conf manual (allow_anonymous defaults, password_file, listener, certfile/keyfile/cafile, require_certificate): https://mosquitto.org/man/mosquitto-conf-5.html
- mosquitto_sub manual (`-d` debug/CONNACK, `-W` timeout, `-u`/`-P`, `--cafile`, `--cert`/`--key`, `-x` session expiry, `--insecure`): https://mosquitto.org/man/mosquitto_sub-1.html
- mosquitto_passwd manual (`-c` creates/overwrites the password file): https://mosquitto.org/man/mosquitto_passwd-1.html
