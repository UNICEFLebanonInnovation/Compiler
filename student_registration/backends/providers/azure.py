

class Azure:

    def send_file(self, data):
        from azure.storage import CloudStorageAccount
        from azure.storage.file import ContentSettings

        settings = ContentSettings(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                                   content_language='ar')

        storage_client = CloudStorageAccount('compiler', 'dfY79hBWV9JlsN6EGfaWi5UOsTbYiXkUHksb3E0VW7CowcdOiGErV8k8rcCEMmyizGDmsasO5I8djej2W+UY3Q==')
        blob_service = storage_client.create_block_blob_service()

        blob_service.create_blob_from_bytes(
            'exports',
            'enrolment_data.xlsx',
            data,
            content_settings=settings
        )

        return blob_service.make_blob_url('exports', 'enrolment_data.xlsx')
