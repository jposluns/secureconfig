# Ollama: it has no built-in authentication or TLS

Ollama's API binds to `127.0.0.1:11434` by default. Setting `OLLAMA_HOST=0.0.0.0` exposes the full API (model execution, pull, delete) to the network with **no authentication and no TLS**; the self-hosted server provides neither (per the Ollama FAQ as of September 2026; verify against current docs before relying on this). Thousands of Ollama instances exposed this way are indexed by internet scanners. That loopback default belongs to the standalone binary: the official `ollama/ollama` Docker image sets `ENV OLLAMA_HOST=0.0.0.0:11434`, so inside a container Ollama already listens on every interface, and under the default bridge networking a bare `-p 11434:11434` republishes it to every host interface by default without your ever setting the variable. The fix there is the published address, not `OLLAMA_HOST`: publish to loopback only with `-p 127.0.0.1:11434:11434` and reach it through a host-run proxy as below, or leave the port unpublished and put the proxy on the same Docker network, addressing Ollama by its container name (a proxy's own `127.0.0.1` will not reach it). With `--network host` there is no publication to bind, since Docker ignores `-p`, so the bind address is the only control: set `OLLAMA_HOST` to loopback or a private interface instead.

Rules:

1. Leave `OLLAMA_HOST` at its loopback default unless a protective layer is in front.
2. Never set `OLLAMA_HOST=0.0.0.0` on a machine with a public interface. "It is just a model server" still means free compute, model tampering, and data exfiltration for anyone who finds it.
3. Expose it only through an authenticated TLS proxy or tunnel, as below.

## Option A: reverse proxy with TLS and basic auth

Keep Ollama on loopback; publish only the proxy. nginx (full context in [nginx.md](nginx.md)):

```nginx
server {
    listen 443 ssl;
    server_name ollama.example.com;

    ssl_certificate     /etc/letsencrypt/live/ollama.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/ollama.example.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;

    location / {
        auth_basic           "Ollama";
        auth_basic_user_file /etc/nginx/.htpasswd;      # htpasswd -B
        proxy_pass http://127.0.0.1:11434;
        proxy_set_header Host localhost:11434;
        proxy_read_timeout 300s;        # model responses can be slow
    }
}
```

Caddy equivalent ([caddy.md](caddy.md)):

```caddyfile
ollama.example.com {
    basic_auth {
        admin $2a$14$REPLACE_WITH_HASH_FROM_caddy_hash-password
    }
    reverse_proxy 127.0.0.1:11434
}
```

Clients then call `https://ollama.example.com` with the basic-auth credentials. For clients that only send bearer tokens, enforce the token at the proxy:

```nginx
    location / {
        if ($http_authorization != "Bearer REPLACE_WITH_LONG_RANDOM_TOKEN") { return 401; }
        proxy_pass http://127.0.0.1:11434;
        proxy_set_header Host localhost:11434;
        proxy_read_timeout 300s;        # as above: model responses can be slow
    }
```

Generate the token per [authentication.md](authentication.md) and keep it out of the repository.

## Option B: Cloudflare Tunnel with Access

Follow [cloudflare.md](cloudflare.md) with the tunnel route pointed at `http://localhost:11434` and an Access policy (or service token for API clients) on the hostname. The Ollama FAQ itself documents fronting the server with a tunnel; adding Access is what makes it authenticated.

MFA: Ollama has no login of its own, so a second factor can only come from the fronting layer: an Access policy backed by an MFA-enforcing identity provider, or an [Authelia](https://www.authelia.com/)-protected proxy. Options in [mfa.md](mfa.md).

## Verify

```bash
ss -tlnp                                               # read every listener: 11434 on 127.0.0.1 only (or absent, behind an unpublished Docker port), nothing unexpected
# from another machine. Read err, not the number: it must name a refusal or timeout reaching YOUR
# address. An HTTP code means the port answered. A resolver failure, a local socket error, or a
# timeout that did not come from the remote address is inconclusive, never a pass.
(                                                      # a subshell, so your own script arguments are untouched
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_YOUR_PUBLIC_IP'   # replace inside the quotes, keeping them
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit; }
  shift
  [ "$#" -eq 1 ] || { echo "the set -- line needs exactly 1 value; not probing"; exit; }
  case "$1" in
    *REPLACE_WITH_*|*YOUR_PUBLIC_IP*|"") echo "substitute your own address on the set -- line above; not probing" ;;
    *) curl -q -g -s -o /dev/null --noproxy '*' --connect-timeout 5 --max-time 20 \
         -w 'http=%{http_code} exit=%{exitcode} err=%{errormsg}\n' "http://$1:11434/api/tags" ;;
  esac
)
curl -q -s https://ollama.example.com/api/tags            # 401 without credentials
curl -q -su admin https://ollama.example.com/api/tags     # model list with credentials
```

## Sources (checked September 2026)

- Ollama FAQ (bind address, `OLLAMA_HOST`, proxy examples): https://docs.ollama.com/faq
- Ollama repository: https://github.com/ollama/ollama
- Ollama Docker image (`ENV OLLAMA_HOST=0.0.0.0:11434` in the official Dockerfile; checked 2026-09-14): https://github.com/ollama/ollama/blob/main/Dockerfile
- curl manual (the `exitcode` and `errormsg` write-out variables, both added in curl 7.75.0): https://curl.se/docs/manpage.html
