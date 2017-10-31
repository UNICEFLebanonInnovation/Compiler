

def get_default_provider():
    from .providers.azure import Azure

    return Azure()


def store_file(data, file_name):

    # provider = get_default_provider()
    # file_link = provider.send_file(data)
    # send_email(file_link)

    from django.conf import settings
    from azure.storage import CloudStorageAccount
    from azure.storage.blob import ContentSettings

    file_name = '{}.{}'.format(file_name, settings.DEFAULT_FILE_FORMAT)

    file_settings = ContentSettings(content_type=settings.DEFAULT_FILE_CONTENT_TYPE,
                                    content_language=settings.DEFAULT_FILE_CONTENT_LANGUAGE)

    storage_client = CloudStorageAccount(settings.AZURE_ACCOUNT_NAME,
                                         settings.AZURE_ACCOUNT_KEY)
    blob_service = storage_client.create_block_blob_service()

    blob_service.create_blob_from_bytes(
        settings.AZURE_CONTAINER,
        file_name,
        data,
        content_settings=file_settings
    )

    file_link = blob_service.make_blob_url(settings.AZURE_CONTAINER, file_name)
    # send_email(file_link, file_name)
    create_record(file_link, file_name)


def create_record(url, file_name):
    from .models import Exporter
    instance = Exporter.objects.create(name=file_name, file_url=url)
    instance.save()


def send_email(url, file_name):
    from django.core.mail import send_mail
    send_mail(
        file_name+' extraction',
        url,
        'achamseddine@unicef.org',
        ['achamseddine@unicef.org'],
        fail_silently=False,
    )
