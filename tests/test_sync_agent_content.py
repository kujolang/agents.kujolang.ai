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
    def test_collaboration_index_is_joined_by_id_and_only_qualified_setup_is_active(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp)
            (source / "agent-registry.json").write_text(json.dumps({"agents": [
                {"id": "chain.general-commander", "path": "chain-of-command/general-commander"},
                {"id": "videoops.producer", "path": "videoops/producer"},
            ]}))
            slack = {"agent_ids": ["chain.general-commander"], "platform": "slack",
                     "host": "reference", "protocol_major": 1, "status": "fixture-only",
                     "operations": ["message", "task.request"]}
            matrix = {**slack, "agent_ids": ["videoops.producer"], "platform": "matrix",
                      "status": "qualified", "setup_url": "https://agents.kujolang.ai/setup/matrix/",
                      "qualification_url": "https://github.com/kujolang/fixture/blob/main/proof.md"}
            index = source / "collaboration-integrations.json"
            payload = {"schema": "kujo.collaboration.compatibility/v1", "entries": [slack, matrix]}
            index.write_text(json.dumps(payload))
            chain = module.compatibility(source, "chain-of-command")
            self.assertEqual(list(chain), ["general-commander"])
            chain_options = module.connection_options(chain["general-commander"])
            self.assertEqual(chain_options[0], {"name": "Slack", "status": "fixture-only"})
            self.assertEqual(chain_options[1], {"name": "Vercel Board", "status": "unavailable"})
            video = module.connection_options(module.compatibility(source, "videoops")["producer"])
            self.assertEqual(video[-1], {"name": "Matrix", "status": "qualified",
                                        "url": matrix["setup_url"], "evidence": matrix["qualification_url"]})
            preview = {**slack, "agent_ids": ["chain.general-commander", "videoops.producer"],
                       "status": "experimental", "host": "local-setup",
                       "preview_url": "https://agents.kujolang.ai/connect-slack/"}
            payload["entries"].append(preview)
            index.write_text(json.dumps(payload))
            chain = module.compatibility(source, "chain-of-command")
            self.assertEqual(module.connection_options(chain["general-commander"])[0]["url"],
                             "/connect-slack/?agent=chain.general-commander")
            self.assertEqual(module.connection_options(module.compatibility(source, "videoops")["producer"])[0]["url"],
                             "/connect-slack/?agent=videoops.producer")
            matrix["setup_url"] = "https://agents.kujolang.ai/setup?token=secret"
            index.write_text(json.dumps(payload))
            with self.assertRaisesRegex(ValueError, "qualification link"):
                module.compatibility(source, "videoops")

    def test_scoped_sync_preserves_other_set_and_removes_only_owned_stale(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)/"kujo-agents"; output=Path(tmp)/"content/agents"; output.mkdir(parents=True)
            for set_id,field,value,slug in (("chain-of-command","Rank/layer","Strategic","general-commander"),("webops","Category","Quality Operations","site-qa-operator"),("publishing-house","Desk","Executive","publisher")):
                folder=root/set_id/slug; folder.mkdir(parents=True); (folder/"AGENT.md").write_text(contract(slug.replace("-"," ").title(),field,value,"A meaningful source-grounded purpose."))
            (root/"chain-of-command/README.md").write_text("chain"); (root/"webops/README.md").write_text("webops"); (root/"publishing-house/README.md").write_text("publishing")
            (root/"webops/webops-catalog.json").write_text(json.dumps({"agents":[{"slug":"site-qa-operator"}]}))
            (root/"publishing-house/publishing-house-catalog.json").write_text(json.dumps({"agents":[{"slug":"publisher"}]}))
            old_chain=output/"general-commander.md"; old_chain.write_text('categories: ["Chain of Command"]\n')
            stale_webops=output/"old-webops.md"; stale_webops.write_text('categories: ["WebOps"]\n')
            module.SITE_ROOT=Path(tmp); module.OUTPUT_ROOT=output; module.STATE_PATH=output/".sync-state.json"
            state={"sets":{"chain-of-command":["general-commander"],"webops":["old-webops"]}}
            count,slugs=module.sync_set(root,"webops",state)
            self.assertEqual(1,count); self.assertEqual(["site-qa-operator"],slugs); self.assertTrue(old_chain.is_file()); self.assertFalse(stale_webops.exists()); self.assertTrue((output/"site-qa-operator.md").is_file())

    def test_publishing_house_uses_catalog_order_and_desk_category(self):
        with tempfile.TemporaryDirectory() as tmp:
            site=Path(tmp); root=site/"kujo-agents"; output=site/"content/agents"; output.mkdir(parents=True)
            for slug,name,desk in (("publisher","Publisher","Executive"),("features-writer","Features Writer","Writing & Creative")):
                folder=root/"publishing-house"/slug; folder.mkdir(parents=True)
                (folder/"AGENT.md").write_text(contract(name,"Desk",desk,"A meaningful source-grounded purpose."))
            (root/"publishing-house/publishing-house-catalog.json").write_text(json.dumps({"agents":[{"slug":"features-writer"},{"slug":"publisher"}]}))
            module.SITE_ROOT=site; module.OUTPUT_ROOT=output; module.STATE_PATH=output/".sync-state.json"
            count,slugs=module.sync_set(root,"publishing-house",{"sets":{}})
            self.assertEqual(2,count); self.assertEqual(["features-writer","publisher"],slugs)
            generated=(output/"features-writer.md").read_text()
            self.assertIn('categories: ["Publishing House"]',generated)
            self.assertIn('tags: ["Writing & Creative"]',generated)
            self.assertIn('order: 1',generated)
            self.assertIn('featured_image: "assets/images/kujo-logomark.svg"',generated)

    def test_sync_uses_matching_agent_portrait_when_available(self):
        with tempfile.TemporaryDirectory() as tmp:
            site=Path(tmp); root=site/"kujo-agents"; output=site/"content/agents"
            folder=root/"webops/site-qa-operator"; folder.mkdir(parents=True)
            (folder/"AGENT.md").write_text(contract("Site QA Operator","Category","Quality Operations","A meaningful source-grounded purpose."))
            (root/"webops/webops-catalog.json").write_text(json.dumps({"agents":[{"slug":"site-qa-operator"}]}))
            portrait=site/"content/media/agents/site-qa-operator.webp"; portrait.parent.mkdir(parents=True); portrait.write_bytes(b"portrait")
            output.mkdir(parents=True)
            module.SITE_ROOT=site; module.OUTPUT_ROOT=output; module.STATE_PATH=output/".sync-state.json"
            module.sync_set(root,"webops",{"sets":{}})
            generated=(output/"site-qa-operator.md").read_text()
            self.assertIn('featured_image: "content/media/agents/site-qa-operator.webp"',generated)

    def test_videoops_prefix_avoids_cross_set_slug_collisions(self):
        with tempfile.TemporaryDirectory() as tmp:
            site=Path(tmp); root=site/"kujo-agents"; output=site/"content/agents"; output.mkdir(parents=True)
            folder=root/"videoops/creative-director"; folder.mkdir(parents=True)
            (folder/"AGENT.md").write_text(contract("Video Creative Director","Stage","Planning","Create a bounded timed production plan."))
            (root/"videoops/videoops-catalog.json").write_text(json.dumps({"agents":[{"slug":"creative-director"}]}))
            existing=output/"creative-director.md"; existing.write_text('categories: ["Publishing House"]\n')
            module.SITE_ROOT=site; module.OUTPUT_ROOT=output; module.STATE_PATH=output/".sync-state.json"
            count,slugs=module.sync_set(root,"videoops",{"sets":{}})
            self.assertEqual(1,count); self.assertEqual(["videoops-creative-director"],slugs)
            self.assertTrue(existing.is_file())
            generated=(output/"videoops-creative-director.md").read_text()
            self.assertIn('custom_url: "videoops-creative-director"',generated)
            self.assertIn('/videoops/creative-director/AGENT.md',generated)

if __name__=="__main__": unittest.main(verbosity=2)
