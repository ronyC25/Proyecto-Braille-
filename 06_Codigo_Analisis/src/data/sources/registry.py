from pathlib import Path

from src.data.sources import angelina, dsbi


def iter_pages(source, root, **kwargs):
    if source == "angelina":
        return angelina.iter_pages(root, **kwargs)
    if source == "dsbi":
        return dsbi.iter_pages(root, **kwargs)
    raise ValueError(f"Fuente no soportada: {source}")


def load_page(source, image_path):
    if source == "angelina":
        return angelina.load_page(image_path)
    if source == "dsbi":
        return dsbi.load_page(image_path)
    raise ValueError(f"Fuente no soportada: {source}")


def audit_source(source, root):
    if source == "angelina":
        return angelina.audit(root)
    if source == "dsbi":
        return dsbi.audit(root)
    raise ValueError(f"Fuente no soportada: {source}")
