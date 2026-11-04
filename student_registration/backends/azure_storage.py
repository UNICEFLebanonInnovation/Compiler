"""Azure storage with bounded HTTP range downloads for media and exports."""

from azure.storage.blob import BlobServiceClient
from storages.backends.azure_storage import AzureStorage


class ChunkedAzureStorage(AzureStorage):
    # Azure normally fetches up to 32 MiB in its first response. Keep both the
    # initial and subsequent requests below the observed 4 MiB interruption.
    download_chunk_size = 2 * 1024 * 1024

    def _get_service_client(self, use_custom_domain):
        options = {
            'max_single_get_size': self.download_chunk_size,
            'max_chunk_get_size': self.download_chunk_size,
        }
        if self.api_version:
            options['api_version'] = self.api_version
        if self.connection_string is not None:
            return BlobServiceClient.from_connection_string(self.connection_string, **options)

        domain = (self.custom_domain if self.custom_domain and use_custom_domain else
                  '{}.blob.{}'.format(self.account_name, self.endpoint_suffix))
        credential = None
        if self.account_key:
            credential = {'account_name': self.account_name, 'account_key': self.account_key}
        elif self.sas_token:
            credential = self.sas_token
        elif self.token_credential:
            credential = self.token_credential
        return BlobServiceClient(
            '{}://{}'.format(self.azure_protocol, domain), credential=credential, **options)
