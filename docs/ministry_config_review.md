# Ministry Deployment Configuration Review

The current configuration defaults are tuned for the UNICEF BMA deployment on
Azure. Review and replace the following settings before running the system on
the ministry's on-premise infrastructure:

- **Database connection** – Update `DATABASE_URL` so it points to the ministry
  PostgreSQL cluster instead of the UNICEF Azure host.
- **File storage** – Replace the Azure Blob Storage credentials or configure an
  alternative backend for exported files and media uploads.
- **Identity service integrations** – Update the `UNIQUE_ID_*` endpoints once
  the ministry exposes its own CLM/MSCC identity service gateway.
- **Docker production domain** – Replace `compiler.uniceflebanon.org` and the
  UNICEF contact email in `production.yml` with the ministry's domain and
  operations contact prior to obtaining TLS certificates.
- **Export pipeline helpers** – Switch the Azure-backed exporters in
  `student_registration.backends` to whichever object storage or file share will
  be used on-prem.

Each affected file now includes `TODO(MoE)` comments to make the required edits
visible in the codebase.
