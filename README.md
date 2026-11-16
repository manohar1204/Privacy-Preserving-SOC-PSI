# CYB 599: Privacy-Preserving SOC Threat-Intelligence Matching

**Educational prototype only.** Semi-honest, SOC-output PSI using a blinded Ristretto255 OPRF and truncated SHA-256 comparison tokens. This is a custom teaching implementation, **not a reviewed PSI library**, not an RFC 9497-compliant implementation, and not production-safe. It runs both parties in one process for measurement; it does **not** implement TLS or network-isolated parties.

## Clean Ubuntu 22.04/24.04 setup

```bash
sudo apt-get update
sudo apt-get install -y python3 libsodium23
unzip CYB599_PSI_Implementation.zip
cd CYB599_PSI_Implementation
bash run.sh
```

No Python packages beyond the standard library are needed. A recent Linux installation with `libsodium.so.23` is required. For an existing checkout, omit `unzip`. To run a quick evaluation: `python3 src/benchmark.py --sizes 100 1000 --repeats 3`.

## Files and outputs

- `src/psi.py`: validated SHA-256 hex inputs, Ristretto255 blinded OPRF PSI, baseline, byte accounting.
- `src/benchmark.py`: deterministic synthetic fixtures (10% overlap), repeated benchmarks, CSV and environment metadata.
- `tests/test_psi.py`: no/full/partial overlap, duplicates, case, malformed data, empty inputs, randomized blinding.
- `run.sh`: reproducible tests + benchmark (100, 1,000, 5,000, 10,000 per party, 5 repeats, 16/32-byte tokens).
- `results/benchmark.csv`: measured time, baseline time, byte sizes, matches, per-run metadata. Recreated by `run.sh`.

## Protocol and measurement caveats

For each SOC digest x, the receiver computes B=r*H(x), server returns E=k*B, receiver unblinds U=r^-1*E. Provider sends shuffled tokens SHA256(domain||k*H(y)) truncated to 16 or 32 bytes. SOC compares tokens. The provider is not sent the intersection. The provider receives blinded group elements; no plaintext indicators are sent. Counts, timing, token list, and provider membership probing remain leakage concerns. This demo **does not authenticate provider evaluations, provide a formal malicious-security guarantee, or enforce query limits**. SHA-256 input hashes are often guessable from public malware samples. A real deployment should use a vetted, formally analyzed PSI library and authenticated transport.

`seconds` measures in-process cryptographic computation and comparison, excluding process startup, file I/O, network, and TLS. `baseline_seconds` measures in-process Python set intersection. `soc_to_provider_bytes` and `provider_to_soc_bytes` are calculated application-message payload lengths, not captured network traffic. No ciphertext or ZK proof is used; proof size is zero. The 16-byte token setting changes comparison-token length and collision bound, **not** the ~128-bit group security target. The 32-byte setting has a larger token collision margin. Results depend on CPU and environment.

## Publishing

Create an empty GitHub repository, then in this folder run `git init && git add . && git commit -m "CYB599 PSI prototype" && git branch -M main && git remote add origin YOUR_REPOSITORY_URL && git push -u origin main`. Replace the placeholder with your own repository URL. Do not claim a repository exists until pushed.
