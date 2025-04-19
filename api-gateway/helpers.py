def extract_files_data(files):
    files_data = []
    for name, file_item in files.items():
        if name.endswith('[]'):
            for file in files.getlist(name):
                files_data.append(
                    (name, (file.filename, file.stream, file.content_type))
                )
        else:
            files_data.append(
                (name, (file_item.filename, file_item.stream, file_item.content_type))
            )
    return files_data