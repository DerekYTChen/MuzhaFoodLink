# -*- coding: utf-8 -*-
"""Order-of-magnitude sizing for the winter pilot.

Every input is either measured (zoo admissions) or an openly stated guess
(party size, spend, conversion). The output is a band, not a number,
because the conversion rate is genuinely unknown and a single figure would
imply precision that does not exist.
"""
from zoo_data import MEAN

JANFEB   = MEAN[0] + MEAN[1]   # measured: mean Jan+Feb admissions, 2024-25
PARTY    = 3.1                 # guess: people per family group
SPEND    = 500                 # guess: NT$ per party, one modest family meal
SHOPS    = 6                   # midpoint of the 5-8 cohort
WEEKS    = 6                   # the pilot window
RATES    = [0.001, 0.005, 0.01]

parties = JANFEB / PARTY
rows = []
for r in RATES:
    n = parties * r
    rows.append((r, n, n * SPEND, n / (SHOPS * WEEKS)))

def frag():
    o = ['<table class="size-table">',
         '  <thead><tr>',
         '    <th data-i18n="size.h1"></th><th data-i18n="size.h2"></th>',
         '    <th data-i18n="size.h3"></th><th data-i18n="size.h4"></th>',
         '  </tr></thead>', '  <tbody>']
    for i, (r, n, rev, per) in enumerate(rows):
        cls = ' class="size-floor"' if i == 0 else ''
        o.append('    <tr%s><td>%s</td><td>%s</td><td>NT$%s</td><td>%s</td></tr>'
                 % (cls, ("%g%%" % (r * 100)), "{:,}".format(int(round(n))),
                    "{:,}".format(int(round(rev, -2))), int(round(per))))
    o += ['  </tbody>', '</table>']
    return "\n".join(o) + "\n"

if __name__ == "__main__":
    print("Jan+Feb admissions (measured, 2024-25 mean): %s" % "{:,}".format(int(JANFEB)))
    print("parties at %.1f people each:                  %s" % (PARTY, "{:,}".format(int(parties))))
    for r, n, rev, per in rows:
        print("  %4g%% -> %7s parties   NT$%9s   %4.1f per shop per week"
              % (r * 100, "{:,}".format(int(round(n))), "{:,}".format(int(round(rev, -2))), per))
    open("sizing_frag.html", "w", encoding="utf-8").write(frag())
    print("wrote sizing_frag.html")
