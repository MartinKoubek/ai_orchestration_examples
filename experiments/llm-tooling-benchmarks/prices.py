
# ------------- PRICING (USD per 1,000,000 tokens) -------------
# Only input and output prices are used (no cached pricing).
PRICES = {
    "grok-3-fast": (0.3, 0.5), # grok-3-mini
    #openai price list
    "gpt-5": (1.25, 10.00),
    "gpt-5-mini": (0.25, 2.00),
    "gpt-5-nano": (0.05, 0.40),
    "gpt-5-chat-latest": (1.25, 10.00),
    "gpt-5-codex": (1.25, 10.00),
    "gpt-5-pro": (15.00, 120.00),
    "gpt-4.1": (2.00, 8.00),
    "gpt-4.1-mini": (0.40, 1.60),
    "gpt-4.1-nano": (0.10, 0.40),
    "gpt-4o": (2.50, 10.00),
    "gpt-4o-2024-05-13": (5.00, 15.00),
    "gpt-4o-mini": (0.15, 0.60),
    "gpt-realtime": (4.00, 16.00),
    "gpt-realtime-mini": (0.60, 2.40),
    "gpt-4o-realtime-preview": (5.00, 20.00),
    "gpt-4o-mini-realtime-preview": (0.60, 2.40),
    "gpt-audio": (2.50, 10.00),
    "gpt-audio-mini": (0.60, 2.40),
    "gpt-4o-audio-preview": (2.50, 10.00),
    "gpt-4o-mini-audio-preview": (0.15, 0.60),
    "o1": (15.00, 60.00),
    "o1-pro": (150.00, 600.00),
    "o3-pro": (20.00, 80.00),
    "o3": (2.00, 8.00),
    "o3-deep-research": (10.00, 40.00),
    "o4-mini": (1.10, 4.40),
    "o4-mini-deep-research": (2.00, 8.00),
    "o3-mini": (1.10, 4.40),
    "o1-mini": (1.10, 4.40),
    "codex-mini-latest": (1.50, 6.00),
    "gpt-5-search-api": (1.25, 10.00),
    "gpt-4o-mini-search-preview": (0.15, 0.60),
    "gpt-4o-search-preview": (2.50, 10.00),
    "computer-use-preview": (3.00, 12.00),
    "gpt-image-1": (5.00, 0.00),        # output N/A -> treat as 0
    "gpt-image-1-mini": (2.00, 0.00),   # output N/A -> treat as 0
}