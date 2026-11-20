from src.data.sources.registry import audit_source
from src.utils.io import write_json


def audit(angelina_root, dsbi_root, report_json=None):
    result = {
        "angelina": audit_source("angelina", angelina_root),
        "dsbi": audit_source("dsbi", dsbi_root),
    }
    result["angelina"]["classes"] = sorted(result["angelina"]["classes"])
    result["dsbi"]["classes"] = sorted(result["dsbi"]["classes"])
    if report_json:
        write_json(report_json, result)
    return result
