"""
This is the server version. client version doesn't affect anymore.
This enables us to toggle between CS strategies i.e. experiments, and deploy the server only.
"""

version_details = {
    # '2.1.0_0_p': 'Rule Based navigator Bot - experiment #1',
    # '2.1.0_p': 'GPT based navigator bot - experiment #1. the human had 5 minutes timer',
    # '2.1.1_p': 'GPT based navigator bot - experiment #2. the human had 7 minutes timer',
    # '2.2.2_p': 'GPT based instructor bot - experiment #1. the human had 7 minutes timer',
    # '2.2.3_p': 'GPT based instructor bot - experiment #2. step by step prompt. the human had 7 minutes timer',
    # '2.2.4_p': 'Ins,Nav,Ins,Nav - 4 maps. English new instructions',  # +retry mechanism when calling API
    # '2.2.5_p': 'Ins,Nav,Ins,Nav - 4 maps. Mixed new instructions - prolific failed to filter correct spanish',
    # '2.2.6_p': 'First - Spanish, Fluent - English. Mixed new instructions. (LOC - US)',
    # '2.2.7_p': 'First - English, Fluent - Spanish. Mixed new instructions. (LOC - US)',
    # '2.3.0_p': 'GPT 4 + informal prompts. Fluent - ES || EN. Mixed new instructions. prolific add in ES only. (LOC - US). new Navigation mechanism.',
    '2.3.1_p': 'BASELINE (Alternation #6 - fix to ES only, in US)',
    '2.3.2_p': 'Random Code-switch alternation strategy - switch on the turn level; no-dep on human utter',
    '2.3.3_p': 'Short-context based Code-switch alternation strategy - switch on the utterance level; no-dep on human utter',
    '2.3.4_p': 'Switch Last User based Code-switch alternation strategy - switch on the turn level; dep on last human utter',
    '2.3.5_p': 'Align Last User based Code-switch alternation strategy - switch on the turn level; dep on last human utter',
    '2.4.0_p': 'Insertional Spanish Congruent',
    '2.4.1_p': 'Insertional Spanish InCongruent1',
    '2.4.2_p': 'Insertional Spanish InCongruent2',
    '2.4.3_p': 'Insertional Spanish Baseline'
}

experiments_short_names = {
    # '2.1.0_0_p': 'RB navigator #1',
    # '2.1.0_p': 'GPT navigator #1',
    # '2.1.1_p': 'GPT navigator #2',
    # '2.2.2_p': 'GPT instructor #1',
    # '2.2.3_p': 'GPT instructor #2',
    # '2.2.4_p': 'Alternation #1',
    # '2.2.5_p': 'Alternation #2',
    # '2.2.6_p': 'Alternation #3',
    # '2.2.7_p': 'Alternation #4',
    # '2.3.0_p': 'Alternation #5',
    '2.3.1_p': 'Alternation Baseline',
    '2.3.2_p': 'Alternation Random CS',
    '2.3.3_p': 'Alternation Short-context CS',
    '2.3.4_p': 'Alternation Adversarial CS',
    '2.3.5_p': 'Alternation Alignment CS',
    '2.4.0_p': 'Insertional Spanish Congruent',
    '2.4.1_p': 'Insertional Spanish Masculine InCongruent',
    '2.4.2_p': 'Insertional Spanish Feminine InCongruent',
    '2.4.3_p': 'Insertional Spanish Baseline'
}


def time_success_metric(version: str) -> int:
    if version == '2.1.0_0_p' or version == '2.1.0_p':
        return 300
    return 420


root_folder = r"data/prolific_lang_ids"
