import json
from pathlib import Path

from app.pipeline import write_manifest
from app.simulation import build_starter_spec, compile_bundle, validate_spec


def _runtime_static_dir() -> Path:
    return Path(__file__).resolve().parents[1] / 'app' / 'static'


def test_validate_and_compile_bundle(tmp_path: Path):
    session_dir = tmp_path / 'session'
    session_dir.mkdir()
    manifest = {
        'id': 'abc123',
        'topic': 'Raft leader election',
        'target_level': 'practitioner',
        'learning_outcome': 'Predict leader election outcomes',
        'media': [],
        'status': 'prepared',
    }
    write_manifest(session_dir, manifest)

    raw_spec = {
        'title': 'Raft Leader Election',
        'objective': 'Understand how leader election progresses and fails.',
        'visual_grammar': 'state-machine',
        'entities': [
            {'id': 'node_a', 'label': 'Node A', 'kind': 'node'},
            {'id': 'node_b', 'label': 'Node B', 'kind': 'node'},
        ],
        'state': {'term': 1, 'leader': 'none'},
        'scenarios': [{'id': 'baseline', 'label': 'Baseline', 'state_overrides': {}}],
        'stages': [
            {
                'id': 'timeout', 'label': 'Election timeout', 'summary': 'A follower times out.',
                'focus_entities': ['node_a'],
                'state_patch': {'term': 2, 'candidate': 'node_a'},
                'questions': [{
                    'prompt': 'What happens next?',
                    'choices': ['Request votes', 'Append entries'],
                    'answer_index': 0,
                    'explanation': 'Candidates request votes in a new term.'
                }],
                'provenance': []
            },
            {
                'id': 'majority', 'label': 'Majority vote', 'summary': 'Node A gains a majority.',
                'focus_entities': ['node_a', 'node_b'],
                'state_patch': {'leader': 'node_a'},
                'questions': [],
                'provenance': []
            }
        ],
        'fidelity_ledger': [
            {'element': 'Timeout values', 'classification': 'SCALED', 'detail': 'Compressed for teaching.', 'confidence': 0.9}
        ]
    }

    spec = validate_spec(raw_spec)
    result = compile_bundle(session_dir, spec, _runtime_static_dir())
    assert result['stage_count'] == 2
    assert (session_dir / 'compiled' / 'index.html').exists()
    assert (session_dir / 'compiled' / 'simulation-spec.json').exists()
    compiled_manifest = json.loads((session_dir / 'manifest.json').read_text())
    assert compiled_manifest['status'] == 'compiled'
    assert compiled_manifest['compiled']['visual_grammar'] == 'state-machine'


def test_build_starter_spec_contains_stages():
    manifest = {'topic': 'Transformer attention', 'target_level': 'practitioner', 'learning_outcome': 'Explain attention', 'media': []}
    starter = build_starter_spec(manifest, {'pipeline': ['a', 'b']})
    assert starter['title'] == 'Transformer attention'
    assert len(starter['stages']) >= 3
    assert starter['fidelity_ledger'][0]['classification'] == 'ASSUMED'
