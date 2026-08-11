#!/usr/bin/env python3
from __future__ import annotations
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

SCRIPT=Path(__file__).resolve().parents[1]/"scripts/sync-agent-content.py"
spec=importlib.util.spec_from_file_location("sync_agent_content",SCRIPT); module=importlib.util.module_from_spec(spec); assert spec.loader; spec.loader.exec_module(module)

def contract(name,category_field,category,purpose):
    return f"# {name}\n\n## Agent Contract\n\n- Agent name: {name}\n- {category_field}: {category}\n- Purpose: {purpose}\n\n## Use This Agent When\n\n- Use it.\n"

class SyncTests(unittest.TestCase):
    def test_scoped_sync_preserves_other_set_and_removes_only_owned_stale(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)/"kujo-agents"; output=Path(tmp)/"content/agents"; output.mkdir(parents=True)
            for set_id,field,value,slug in (("chain-of-command","Rank/layer","Strategic","general-commander"),("webops","Category","Quality Operations","site-qa-operator")):
                folder=root/set_id/slug; folder.mkdir(parents=True); (folder/"AGENT.md").write_text(contract(slug.replace("-"," ").title(),field,value,"A meaningful source-grounded purpose."))
            (root/"chain-of-command/README.md").write_text("chain"); (root/"webops/README.md").write_text("webops")
            (root/"webops/webops-catalog.json").write_text(json.dumps({"agents":[{"slug":"site-qa-operator"}]}))
            old_chain=output/"general-commander.md"; old_chain.write_text('categories: ["Chain of Command"]\n')
            stale_webops=output/"old-webops.md"; stale_webops.write_text('categories: ["WebOps"]\n')
            module.OUTPUT_ROOT=output; module.STATE_PATH=output/".sync-state.json"
            state={"sets":{"chain-of-command":["general-commander"],"webops":["old-webops"]}}
            count,slugs=module.sync_set(root,"webops",state)
            self.assertEqual(1,count); self.assertEqual(["site-qa-operator"],slugs); self.assertTrue(old_chain.is_file()); self.assertFalse(stale_webops.exists()); self.assertTrue((output/"site-qa-operator.md").is_file())

if __name__=="__main__": unittest.main(verbosity=2)
