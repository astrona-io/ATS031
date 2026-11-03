---
draft: true
exam_objectives:
- Properly set up Ingress with TLS
---
# Self-Signed Certificate With openssl

The fastest way to get a certificate for a test is to create one that signs itself. One `openssl` command makes the key and the certificate together, and the exam often asks for exactly this. This part builds the command option by option, creates a certificate for `scout.example.test`, and then reads the result to prove that the name, the dates and the SAN are what you intended.

## The command and its options

The command `openssl req` creates certificate requests. With the option `-x509` it creates a certificate directly instead of a request, and signs it with the key it just made. These options matter:

- `-newkey rsa:2048` creates a new RSA key with 2048 bits together with the certificate.
- `-nodes` leaves the private key without a passphrase. A controller cannot type a passphrase, so a key in a TLS Secret must have none. Newer OpenSSL versions also accept `-noenc` for the same purpose.
- `-days 30` sets the validity to 30 days from now.
- `-keyout` and `-out` set the file names for the key and the certificate.
- `-subj /CN=scout.example.test` sets the subject without asking questions.
- `-addext subjectAltName=DNS:scout.example.test` adds the SAN extension. This option needs OpenSSL 1.1.1 or newer.

<!-- astrona:playground:renew -->

Run the command in an empty working folder on your own machine:

```sh
openssl req -x509 -nodes -newkey rsa:2048 -days 30 -keyout scout.key -out scout.crt -subj /CN=scout.example.test -addext subjectAltName=DNS:scout.example.test
```

The command writes two files and prints nothing important. If it reports that `-addext` is unknown, your `openssl` is too old or is LibreSSL. Install a current OpenSSL and run the command with its full path. You can create an elliptic-curve key instead of RSA with `-newkey ec -pkeyopt ec_paramgen_curve:prime256v1`, which gives a smaller key and a faster handshake.

## Read what you made

Never trust a certificate you have not read. Print the subject, the issuer and the dates, and then the extensions:

```sh
openssl x509 -in scout.crt -noout -subject -issuer -dates
openssl x509 -in scout.crt -noout -ext subjectAltName
```

The subject and the issuer are both `CN = scout.example.test`, which shows that the certificate is self-signed. The dates show that it starts now and ends 30 days later. The second command prints the SAN list with `DNS:scout.example.test`. If the SAN section is missing, the `-addext` option did not work and the certificate is useless for a modern client.

Two more reads help in the exam. The first checks whether the certificate is still valid for a number of seconds, and the exit status tells you the answer: zero means it will not expire in that time.

```sh
openssl x509 -in scout.crt -noout -checkend 86400 && echo "valid for at least one more day"
openssl x509 -in scout.crt -noout -fingerprint -sha256
```

The fingerprint is a hash of the certificate. You can compare it later with the fingerprint of the certificate that Traefik serves, to prove that it is the same file.

You now have a key and a self-signed certificate. A real client trusts only certificates signed by a CA it knows, so the next question is how to be your own CA and sign a server certificate.

## Common pitfalls

> [!WARNING]
> - **Forgetting `-addext`.** The certificate has a CN and no SAN, and clients reject it.
> - **A passphrase on the key.** Without `-nodes` or `-noenc`, `openssl` asks for a passphrase and the controller cannot load the key.
> - **A validity that is too short or too long.** Check the dates with `-dates` before you use the certificate.
> - **Using the system `openssl` on macOS without checking the version.** It can be LibreSSL, which lacks options used in the exam.
