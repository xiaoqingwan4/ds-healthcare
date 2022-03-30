import os

MODELS_HOME = os.environ['MODELS_HOME']


def get_model_file_path(*parts: str) -> str:
    path = MODELS_HOME
    for part in parts:
        path = os.path.join(path, part)
    return path