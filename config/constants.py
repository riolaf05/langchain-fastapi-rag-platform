# Put here constants variables that are used in more than one file
RAW_DOCUMENT_FOLDER = "raw_documents"  # if it's modified to news4p/raw_documents, it will create a new folder/directory in S3 bucket
FILE_EXTENSIONS = {
    "image": {"png", "jpg", "jpeg", "gif", "svg", "bmp", "tiff"},
    "audio": {"mp3", "wav", "ogg", "flac", "m4a", "aac", "wma"},
    "video": {"mp4", "mov", "avi", "webm", "flv", "mkv", "webp"},
    "text": {"txt", "docx", "pdf"},
}
