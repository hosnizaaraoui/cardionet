from textual.theme import Theme

cardionet_neon = Theme(
    name="cardionet_neon",
    primary="#00ffff",
    secondary="#ff00ff",
    accent="#00ff99",
    foreground="#c8f7ff",
    background="#05060d",
    surface="#0a0d1a",
    panel="#101324",
    success="#00ff99",
    warning="#ffcc00",
    error="#ff3366",
    dark=True,
    variables={
        "input-selection-background": "#00ffff 30%",
        "footer-key-foreground": "#00ffff",
        "shadow": "#00ffff40",
        "text-muted": "#6a7a8c",
        "text-strong": "#ffffff",
    },
)
