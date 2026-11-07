"""Batch03 preserves PR5's complete 17 entries and tests additions separately."""
import copy,json,subprocess,unittest
from pathlib import Path
from integrity import same_fields
from validation import validate_record, FIELDS
BASE=Path(__file__).resolve().parent
DATA=json.loads((BASE/'eikyouki_records.json').read_text())['records']
class Batch03(unittest.TestCase):
    def test_existing17_unchanged(self):
        old=json.loads(subprocess.check_output(['git','show','c4c69c1079af74d2dd5fc7ba1b8b6272f0488cbb:prototype/eikyouki/eikyouki_records.json'],cwd=BASE))['records']
        same_fields(old,DATA[:17],'PR5 existing17')
    def test_new_articles(self):
        self.assertGreaterEqual(len(DATA),19)
        for r,id,day,j,g in zip(DATA[17:19],['EK-0018','EK-0019'],[29,24],['1438-10-18','1438-10-13'],['1438-10-27','1438-10-22']):
            self.assertEqual((id,day,j,g),(r['id'],r['lunar_day'],r['julian_start'],r['gregorian_start']))
            self.assertEqual('provisional',r['date_conversion_status']);self.assertIsNone(r['full_original_text'])
            self.assertIsNone(r['research_date_start']);validate_record(r)
            for field in FIELDS:
                changed=copy.deepcopy(r);changed[field]='CORRUPTED' if r[field] is None else None
                with self.subTest(id=id,field=field):
                    with self.assertRaises(ValueError):same_fields([r],[changed],'batch03 individual field')
