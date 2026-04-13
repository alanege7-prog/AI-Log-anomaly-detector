import os
import anthropic

_client = None


def _get_client():
    global _client
    if _client is None:
        api_key = os.environ.get('ANTHROPIC_API_KEY')
        if not api_key:
            raise RuntimeError(
                'ANTHROPIC_API_KEY is not set. '
                'Copy .env.example to .env and add your key.'
            )
        _client = anthropic.Anthropic(api_key=api_key)
    return _client


def explain(alert) -> str:
    """
    Generate a plain-language explanation for a flagged alert using Claude.
    Returns explanation string, or a fallback message if the API call fails.
    """
    prompt = (
        f"You are a network security analyst. A rule-based IDS flagged this event:\n\n"
        f"Rule: {alert.alert_type}\n"
        f"Source IP: {alert.src_ip}\n"
        f"Destination IP: {alert.dst_ip}\n"
        f"Port: {alert.port}\n"
        f"Event count: {alert.count}\n"
        f"Raw log sample: {alert.raw_log[:300]}\n\n"
        f"In 2-3 sentences, explain what this event likely means, why it was flagged, "
        f"and what a security analyst should investigate next. Be direct and concise."
    )
    try:
        msg = _get_client().messages.create(
            model='claude-haiku-4-5-20251001',
            max_tokens=200,
            messages=[{'role': 'user', 'content': prompt}],
        )
        return msg.content[0].text.strip()
    except Exception as e:
        return f'[Explanation unavailable: {e}]'
