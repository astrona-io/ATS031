# Disable Profiling And Raise The API Server TLS Minimum

A penetration test of the API server reports two findings: the profiling endpoint answers, and the server accepts TLS 1.0. The API server runs with profiling on (the default) and with `--tls-min-version=VersionTLS10`. Close both findings.

1. Run the API server with `--profiling=false`.
2. A request to `/debug/pprof/` with administrator credentials returns HTTP `404`.
3. Run the API server with `--tls-min-version=VersionTLS12` or `--tls-min-version=VersionTLS13`.

Node files belong to root; use `sudo`. The API server must be ready again and both `probe` replicas in `starfleet-031-020-03-02` must stay available.
