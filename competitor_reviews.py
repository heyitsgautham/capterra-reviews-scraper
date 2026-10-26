"""Pull Capterra reviews for a list of competing products into one CSV, and compare them.

For every product it prints Capterra's own figures (rating, the four sub-ratings,
recommend share, 1 and 2 star share, starting price), then two things from the
reviews it collected: how many were incentivized or vendor-referred, and how
those rate against the rest, and which products reviewers say they switched from.

Usage:
    export APIFY_TOKEN=...
    python competitor_reviews.py examples/products.txt --max 50
    python competitor_reviews.py examples/products.txt --max 200 --only-new   # weekly, new reviews only

products.txt holds one product per line, a name such as "monday.com" or a
capterra.com product URL. Blank lines and lines starting with # are skipped.
"""

import argparse
import csv
import os
import sys
from collections import Counter, defaultdict
from decimal import Decimal
from pathlib import Path

from apify_client import ApifyClient

ACTOR = "heyitsgautham/software-reviews-scraper"
PRICE_PER_REVIEW = Decimal("0.001")
COLUMNS = [
    "productName", "reviewDate", "rating", "easeOfUseRating", "customerSupportRating",
    "functionalityRating", "valueForMoneyRating", "recommendationScore", "title", "pros", "cons",
    "reviewerJobTitle", "reviewerIndustry", "reviewerCompanySize", "timeUsedProduct",
    "isVerified", "isIncentivized", "isVendorReferred", "switchedFrom", "vendorReplied", "reviewId",
]


def avg(values):
    values = [v for v in values if v is not None]
    return sum(values) / len(values) if values else None


def fmt(value, spec=".2f", empty="-"):
    return empty if value is None else format(value, spec)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("products", help="text file, one Capterra product name or URL per line")
    parser.add_argument("--max", type=int, default=100, help="newest reviews per product (default 100)")
    parser.add_argument("--only-new", action="store_true", help="only reviews not returned on an earlier run")
    parser.add_argument("--out", default="capterra_reviews.csv")
    args = parser.parse_args()

    token = os.environ.get("APIFY_TOKEN")
    if not token:
        sys.exit("Set APIFY_TOKEN first. Get one at https://console.apify.com/settings/integrations")

    lines = [l.strip() for l in Path(args.products).read_text().splitlines()]
    lines = [l for l in lines if l and not l.startswith("#")]
    urls = [l for l in lines if l.startswith("http")]
    names = [l for l in lines if not l.startswith("http")]

    run_input = {
        "startUrls": urls,
        "productNames": names,
        "maxReviewsPerProduct": args.max,
        "sortBy": "newest",
        "productSummary": True,
        "compareProducts": True,
        "onlyNewSinceLastRun": args.only_new,
    }
    cap = PRICE_PER_REVIEW * args.max * len(lines)
    print(f"Reading up to {args.max} reviews for {len(lines)} products, at most ${cap:.3f}\n")

    client = ApifyClient(token)
    run = client.actor(ACTOR).call(run_input=run_input, max_total_charge_usd=cap, logger=None)
    if run is None or run.status != "SUCCEEDED":
        sys.exit(f"Run did not succeed: {run.status if run else 'no run'}")

    reviews, comparison, problems = defaultdict(list), None, []
    for item in client.dataset(run.default_dataset_id).iterate_items():
        status = item.get("status")
        if status == "ok":
            reviews[item["productName"]].append(item)
        elif status == "comparison":
            comparison = item
        elif status not in ("summary", "no_reviews"):
            problems.append(item)

    out = Path(args.out)
    new_file = not out.exists()
    with out.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS, extrasaction="ignore")
        if new_file:
            writer.writeheader()
        for rows in reviews.values():
            for r in rows:
                writer.writerow({**r, "switchedFrom": "; ".join(r.get("switchedFrom") or []),
                                 "vendorReplied": bool(r.get("vendorResponse"))})
    total = sum(len(v) for v in reviews.values())
    print(f"{total} reviews {'appended to' if not new_file else 'written to'} {out}\n")

    if comparison:
        print(f"{'Product':28} {'Rating':>6} {'Ease':>5} {'Supp':>5} {'Func':>5} {'Value':>5} "
              f"{'Recom':>6} {'1-2*':>5} {'From':>8}")
        for p in comparison["products"]:
            price = f"{p['currency'] or ''}{p['startingPrice']}" if p.get("startingPrice") else "-"
            print(f"{p['productName'][:28]:28} {fmt(p.get('productRatingExact')):>6} "
                  f"{fmt(p.get('easeOfUse'), '.1f'):>5} {fmt(p.get('customerSupport'), '.1f'):>5} "
                  f"{fmt(p.get('functionality'), '.1f'):>5} {fmt(p.get('valueForMoney'), '.1f'):>5} "
                  f"{fmt(p.get('recommendPercent'), '.0f'):>5}% {fmt(p.get('negativePercent'), '.1f'):>4}% "
                  f"{price:>8}")
        leaders = ", ".join(f"{k} {'/'.join(v)}" for k, v in (comparison.get("leaders") or {}).items())
        print(f"\nLeaders: {leaders}\n")

    for product, rows in reviews.items():
        paid = [r for r in rows if r.get("isIncentivized") or r.get("isVendorReferred")]
        organic = [r for r in rows if r not in paid]
        switched = Counter(s for r in rows for s in (r.get("switchedFrom") or []))
        print(f"## {product}, {len(rows)} newest reviews")
        print(f"  incentivized or vendor-referred: {len(paid)} of {len(rows)}, "
              f"avg {fmt(avg(r['rating'] for r in paid))} against {fmt(avg(r['rating'] for r in organic))} for the rest")
        if switched:
            print(f"  switched from: {', '.join(f'{name} ({n})' for name, n in switched.most_common(5))}")

    for item in problems:
        print(f"\nSkipped {item.get('input')}: {item.get('status')}, {item.get('message')}")


if __name__ == "__main__":
    main()
