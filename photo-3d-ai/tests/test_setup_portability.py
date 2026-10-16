"""Installation control flow uses temporary folders; no packages are downloaded here."""
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
spec=importlib.util.spec_from_file_location('portable_setup',Path(__file__).resolve().parents[1]/'setup.py')
setup=importlib.util.module_from_spec(spec);spec.loader.exec_module(setup)

class SetupPortabilityTests(unittest.TestCase):
    def test_copied_environment_is_preserved_and_new_install_is_reused(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);(root/'requirements.txt').write_text('numpy==1.26.4\n')
            old=root/'.venv';old.mkdir();(old/'.ls-install.json').write_text(json.dumps({'machine':'old-machine'}))
            (old/'user-marker').write_text('preserve')
            def build(folder):
                python=folder/('Scripts/python.exe' if sys.platform=='win32' else 'bin/python')
                python.parent.mkdir(parents=True);python.write_text('placeholder')
            report={'device':'cpu','name':'CPU','warning':'CPU only','cuda_tested':False}
            with patch.object(setup,'ROOT',root),patch.object(setup,'REPORT',root/'.runtime'/'hardware.json'),patch.object(setup,'fingerprint',return_value='new-machine'),patch.object(setup,'inventory',return_value={'nvidia':[],'displays':[]}),patch.object(setup.venv.EnvBuilder,'create',side_effect=build),patch.object(setup,'run') as install,patch.object(setup,'inspect_torch',return_value=report),patch.object(sys,'argv',['setup.py']),patch.object(sys,'version_info',(3,11,9)):
                setup.main()
                self.assertEqual(len(list(root.glob('.venv-old-*/user-marker'))),1)
                self.assertTrue((root/'.venv'/'.ls-install.json').is_file())
                self.assertGreater(install.call_count,0)
                install.reset_mock()
                setup.main()
                self.assertEqual(install.call_count,0,'Unchanged machine must not reinstall packages')
                self.assertEqual(json.loads((root/'.runtime'/'hardware.json').read_text())['device'],'cpu')

if __name__=='__main__':unittest.main()
