import pandas as pd


async def read_file(file_path, document):
    await document.download(
        destination_file=file_path,
    )

    def to_csv(encoding=None):
        file_to_encode = pd.read_csv(file_path, sep=';', encoding=encoding)
        if len(file_to_encode.columns) == 1:
            file_to_encode = pd.read_csv(file_path, sep=',', encoding=encoding)
        return file_to_encode

    try:
        file = to_csv('utf8')
    except UnicodeDecodeError:
        file = to_csv('cp1251')
    return file