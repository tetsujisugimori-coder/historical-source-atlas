"""Explicit editing command; verification never calls this or rewrites outputs."""
import json
import re
from pathlib import Path
from validation import validate_data


def embed(html, data):
    records = validate_data(data)
    # Prevent arbitrary text (including </script>) from ending the HTML script element.
    payload = json.dumps(records, ensure_ascii=False).replace('<', '\\u003c')
    result, count = re.subn(r'(<script id="payload" type="application/json">).*?(</script>)',
                            lambda m: m[1]+payload+m[2], html, flags=re.S)
    if count != 1:
        raise ValueError('expected exactly one payload element')
    additional = {k:data.get(k, {} if k == 'publication' else []) for k in ['publication','article_relationships']}
    extra = json.dumps(additional, ensure_ascii=False).replace('<', '\\u003c')
    result, count = re.subn(r'(<script id="provenance" type="application/json">).*?(</script>)',
                            lambda m:m[1]+extra+m[2], result, flags=re.S)
    if count != 1: raise ValueError('expected exactly one provenance element')
    return result


if __name__ == '__main__':
    base=Path(__file__).resolve().parent
    html=base/'index.html'
    data=json.loads((base/'eikyouki_records.json').read_text(encoding='utf8'))
    html.write_text(embed(html.read_text(encoding='utf8'),data),encoding='utf8')
