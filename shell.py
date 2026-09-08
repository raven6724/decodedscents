"""
Shared layout shell for every generated page.   2026-08-07

The generators emit .container, .article-hero, .dupe-entry, .cta-btn, .top-nav and
friends, but NONE of those classes exist in the site stylesheet — they were invented
by the page templates and never defined. So all 173 static pages rendered as
unstyled full-width divs with browser-default blue links: text jammed against the
left edge, match counts stranded at the far right of the viewport.

This defines them, built on the stylesheet's own CSS variables (--gold, --bg2,
--text, --border) so the pages inherit the site's identity rather than introducing
a second one.

Import into every generator and inject alongside its page-specific EXTRA.
"""

SHELL = """
    /* ── layout primitives the templates assume ── */
    .container { width:100%; max-width:1040px; margin:0 auto; padding:0 24px; }
    @media (max-width:640px) { .container { padding:0 16px; } }

    main.container { padding-top:6px; padding-bottom:64px; }
    article { max-width:100%; }
    article p { line-height:1.65; color:var(--text-muted,#a9a396); margin:0 0 14px; }
    article h2 { font-size:1.25rem; letter-spacing:-0.01em; color:var(--text,#e8e4dc);
                 margin:38px 0 12px; }
    article h3 { font-size:1.05rem; margin:0 0 8px; color:var(--text,#e8e4dc); }
    article a { color:var(--gold-light,#e8c97a); text-decoration:none;
                border-bottom:1px solid rgba(201,168,76,0.28); transition:border-color .15s; }
    article a:hover { border-bottom-color:var(--gold,#c9a84c); }
    article a:focus-visible { outline:2px solid var(--gold,#c9a84c); outline-offset:2px; }

    /* ── top nav (Spanish pages use .top-nav; EN nav ships its own markup) ── */
    .top-nav { border-bottom:1px solid var(--border,rgba(255,255,255,0.08));
               background:rgba(10,10,15,0.92); backdrop-filter:blur(8px);
               position:sticky; top:0; z-index:60; }
    .top-nav .container { display:flex; align-items:center; justify-content:space-between;
                          gap:20px; height:60px; }
    .top-nav .nav-logo { font-family:Georgia,'Times New Roman',serif; font-size:1.05rem;
        letter-spacing:0.06em; color:var(--gold,#c9a84c); text-decoration:none; border:0; }
    .top-nav .nav-links { display:flex; gap:1.6rem; }
    .top-nav .nav-links a { color:var(--text-muted,#a9a396); text-decoration:none; border:0;
        font-size:0.78rem; letter-spacing:0.08em; text-transform:uppercase; }
    .top-nav .nav-links a:hover { color:var(--gold,#c9a84c); }
    @media (max-width:560px) { .top-nav .nav-links { gap:1rem; } .top-nav .nav-links a { font-size:0.7rem; } }

    /* ── page header ── */
    .article-hero { padding:46px 0 30px; border-bottom:1px solid var(--border,rgba(255,255,255,0.07));
                    margin-bottom:26px; }
    .article-hero h1 { font-family:Georgia,'Times New Roman',serif; font-weight:400;
        font-size:clamp(1.85rem,4.4vw,2.9rem); line-height:1.12; letter-spacing:-0.015em;
        margin:0 0 12px; color:var(--text,#e8e4dc); }
    .hero-meta { font-size:0.73rem; letter-spacing:0.14em; text-transform:uppercase;
                 color:var(--gold,#c9a84c); margin-bottom:14px; }
    .hero-byline { font-size:0.88rem; color:var(--text-dim,#7a756c); letter-spacing:0.01em; }
    @media (max-width:640px) { .article-hero { padding:30px 0 22px; } }

    /* ── entry cards ── */
    .dupe-entry { background:var(--bg2,#111118); border:1px solid var(--border,rgba(255,255,255,0.07));
                  border-left:3px solid rgba(201,168,76,0.3);
                  border-radius:10px; padding:20px 22px; margin:16px 0; }
    .dupe-entry h3 { display:flex; align-items:baseline; gap:2px; flex-wrap:wrap; }
    .dupe-entry.tier-callout { border-left-color:var(--gold,#c9a84c);
                               background:linear-gradient(180deg,rgba(201,168,76,0.06),transparent 60%),var(--bg2,#111118); }
    .dupe-entry.tier-real { border-left-color:#4ade80; }
    .dupe-entry.tier-inspired { border-left-color:#facc15; }
    .dupe-meta { font-size:0.86rem; color:var(--text-dim,#7a756c); margin:2px 0 10px; }
    @media (max-width:640px) { .dupe-entry { padding:16px 15px; } }

    /* ── buy buttons ── */
    .buying-options { display:flex; flex-wrap:wrap; gap:8px; margin-top:14px; }
    .cta-btn { display:inline-flex; align-items:center; gap:6px; padding:8px 14px;
        font-size:0.82rem; line-height:1; border-radius:7px; text-decoration:none;
        background:var(--bg4,#1c1c28); border:1px solid var(--border,rgba(255,255,255,0.09));
        color:var(--text-muted,#a9a396); transition:border-color .15s, color .15s; }
    .cta-btn:hover { border-color:var(--gold,#c9a84c); color:var(--gold-light,#e8c97a); }
    .cta-btn:focus-visible { outline:2px solid var(--gold,#c9a84c); outline-offset:2px; }
    article .cta-btn { border-bottom:1px solid var(--border,rgba(255,255,255,0.09)); }
    article .cta-btn:hover { border-bottom-color:var(--gold,#c9a84c); }


    .footer-disclosure { max-width:640px; margin:14px auto 0; padding:0 20px;
        font-size:0.76rem; line-height:1.6; color:var(--text-dim,#7a756c); }
    .footer-disclosure a { color:var(--text-muted,#a9a396); text-decoration:none;
                           border-bottom:1px solid rgba(255,255,255,0.14); }
    .footer-disclosure a:hover { color:var(--gold,#c9a84c); border-bottom-color:var(--gold,#c9a84c); }

    .visually-hidden { position:absolute; width:1px; height:1px; overflow:hidden;
                       clip:rect(0 0 0 0); white-space:nowrap; }

    @media (prefers-reduced-motion:reduce) {
      * { animation-duration:0.01ms !important; transition-duration:0.01ms !important; }
    }
"""
