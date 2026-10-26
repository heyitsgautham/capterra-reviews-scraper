# Capterra reviews scraper

Get Capterra software reviews as JSON or CSV, with all four sub-ratings, pros and cons, the reviewer's role and company size, and Capterra's incentive flags.
There's a Python script here that compares a set of competitors in one command, and can run weekly for new reviews only.

The scraping runs on my [Capterra Reviews Scraper on Apify](https://apify.com/heyitsgautham/software-reviews-scraper).
I built it, and it's paid per result, $1 per 1,000 reviews, down to $0.70 on Apify's Gold tier.
Name lookups, products with no reviews, failures, and the summary and comparison rows are free.

## Is there a Capterra API?

Not one I could use for reading reviews.
When I searched "capterra api" in October 2026, page 1 was Capterra's own category pages for API software, third-party wrappers, and an API directory page saying it didn't have enough information about a Capterra API.
So this goes the other way round.
The scraper reads the same public review pages any visitor sees, with no login, and hands you rows through Apify's API.

## Compare competitors

`competitor_reviews.py` takes a file of products, by name or URL, and does three things.

- It writes every review to one CSV, with the overall rating, ease of use, customer support, functionality, value for money and the 0 to 10 recommend score in their own columns.
- It prints Capterra's figures for each product side by side, from the scraper's free comparison row.
- It reads the reviews it collected for two things Capterra's headline numbers hide, how many were incentivized or vendor-referred, and which products reviewers say they switched from.

```bash
pip install -r requirements.txt
export APIFY_TOKEN=your_token_here
python competitor_reviews.py examples/products.txt --max 30
```

`examples/products.txt` mixes names and a URL.

```
Asana
monday.com
ClickUp
https://www.capterra.com/p/135003/Slack/
```

My run on 26 Oct 2026:

```
Reading up to 30 reviews for 4 products, at most $0.120

120 reviews written to capterra_reviews.csv

Product                      Rating  Ease  Supp  Func Value  Recom  1-2*     From
Slack                          4.66   4.6   4.4   4.6   4.5    86%  0.7%    $8.75
Asana                          4.49   4.4   4.3   4.4   4.4    77%  1.7%   $10.99
monday AI Work Platform        4.57   4.5   4.4   4.5   4.3    77%  1.2%       $9
ClickUp                        4.63   4.3   4.5   4.6   4.6    84%  1.1%      $10

Leaders: productRating Slack, easeOfUse Slack, customerSupport ClickUp, functionality Slack/ClickUp, valueForMoney ClickUp, recommendPercent Slack, productReviewCount Slack, fewestNegative Slack

## monday AI Work Platform, 30 newest reviews
  incentivized or vendor-referred: 15 of 30, avg 4.33 against 4.60 for the rest
  switched from: Workbooks (1), Streak (1), 10xBeast (1)
## ClickUp, 30 newest reviews
  incentivized or vendor-referred: 14 of 30, avg 4.64 against 4.56 for the rest
  switched from: Trello (2), Asana (2), Google Sheets (1)
## Asana, 30 newest reviews
  incentivized or vendor-referred: 26 of 30, avg 4.88 against 5.00 for the rest
  switched from: monday AI Work Platform (1), Trello (1), Wrike (1), Jira (1)
## Slack, 30 newest reviews
  incentivized or vendor-referred: 9 of 30, avg 4.78 against 4.81 for the rest
  switched from: SkypeTime (1), Google Workspace (1), Microsoft Teams (1), Google Chat (1)
```

The top table is Capterra's figures over every review of each product.
"Recom" is the share who'd recommend it at 8 to 10 out of 10, "1-2*" the share of 1 and 2 star reviews, and "From" the starting price Capterra lists.
A product only leads a figure when 20 or more reviews stand behind it.

The part I find most useful is underneath.
26 of Asana's 30 newest reviews came with a gift card or a vendor invite, against 9 of Slack's.
Thirty reviews is a small sample, so raise `--max` before you quote any of it.
`monday.com` found "monday AI Work Platform", the product sold by monday.com, through Capterra's own search.

The script caps the run's charge at `--max` times the number of products times $0.001, and prints that cap first.

## Weekly: new reviews only

Add `--only-new` and each run returns only reviews you haven't had before, appended to the same CSV.

```bash
python competitor_reviews.py examples/products.txt --max 10 --only-new --out weekly.csv
```

I ran that twice in a row on 26 Oct 2026.
The first run returned 17 reviews, because the scraper's memory in my account already held these products from earlier tests.
The second returned 1, Asana's 11th newest review, which the first run's cap of 10 had left out.
No review came back twice.
A product with nothing new comes back as a free row, so a quiet week costs almost nothing.

The memory is a key-value store in your own Apify account, one record per product and star filter.
It looks 14 days behind the newest review it returned, because Capterra checks reviews before publishing them and some appear days after their date.
Put the command in cron or a scheduled GitHub Action to get it every week.

## One review row

A ClickUp review from the comparison run.
`reviewerName` is the first name and initial Capterra shows publicly.

```json
{
  "status": "ok",
  "site": "capterra",
  "productId": "158833",
  "productName": "ClickUp",
  "vendorName": "ClickUp",
  "productRating": 4.6,
  "productReviewCount": 4640,
  "productCategory": "Project Management",
  "productUrl": "https://www.capterra.com/p/158833/ClickUp/",
  "reviewId": "7210156",
  "title": "Good for keeping finance deadlines and follow ups in one place",
  "rating": 5,
  "easeOfUseRating": 4,
  "customerSupportRating": 5,
  "functionalityRating": 5,
  "valueForMoneyRating": 4,
  "recommendationScore": 10,
  "pros": "Recurring tasks are very useful for things like month end checklists, reconciliations and regular reporting. We also use dashboards to get a quick view of overdue items instead of going through each task one by one. Comments inside the task help as well because the discussion stays within one place",
  "cons": "There are so many features that it can feel a bit confusing at first. We tried some automations but didnt really need anything advanced. Pricing can also get a bit expensive when more users are added.",
  "overall": "We use ClickUp mainly for finance team tasks and recurring month end and year end work. It helps a lot when there are many deadlines at the same time. I can quickly see what is done, what is overdue and who is working on what.",
  "reviewDate": "2026-09-07",
  "reviewerName": "Davis M.",
  "reviewerJobTitle": "Head of Finance",
  "reviewerIndustry": "Mechanical or Industrial Engineering",
  "reviewerCompanySize": "1,001-5,000 employees",
  "timeUsedProduct": "1-2 years",
  "isVerified": true,
  "verificationMethods": ["LinkedIn", "ProofOfLink"],
  "isIncentivized": true,
  "isVendorReferred": false,
  "incentive": "NominalGift",
  "reviewSource": "Nominal Gift Card: This reviewer was invited by us to submit an honest review and was offered a nominal incentive as a thank you.",
  "switchedFrom": ["Trello"],
  "alternativesConsidered": null,
  "vendorResponse": null,
  "nameMatch": {"name": "ClickUp", "matchType": "exact", "otherMatches": []},
  "input": "ClickUp"
}
```

No emails, phone numbers or profile photos are collected.

## Python

```python
import os
from apify_client import ApifyClient

client = ApifyClient(os.environ["APIFY_TOKEN"])
run = client.actor("heyitsgautham/software-reviews-scraper").call(run_input={
    "startUrls": ["https://www.capterra.com/p/135003/Slack/reviews/"],
    "productNames": ["ClickUp"],
    "maxReviewsPerProduct": 100,
    "sortBy": "newest",
})
for review in client.dataset(run.default_dataset_id).iterate_items():
    if review["status"] == "ok":
        print(review["productName"], review["rating"], review["title"])
```

## curl

The two lowest-rated reviews of Notion:

```bash
curl -X POST "https://api.apify.com/v2/acts/heyitsgautham~software-reviews-scraper/run-sync-get-dataset-items?fields=productName,rating,reviewDate,title,cons" \
  -H "Authorization: Bearer $APIFY_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"productNames": ["Notion"], "maxReviewsPerProduct": 2, "sortBy": "lowest_rated", "starRatings": ["1", "2"]}'
```

What came back for me:

```json
[{
  "productName": "Notion",
  "rating": 1,
  "reviewDate": "2023-04-14",
  "title": "Good",
  "cons": "Don't really have too much bad to say about notion"
},
{
  "productName": "Notion",
  "rating": 1,
  "reviewDate": "2025-02-15",
  "title": "Pas fiable. A fuir.",
  "cons": "Pas fiable. Si vous voulez perdre vos données, c'est le bon programme."
}]
```

The first is a 1-star review titled "Good", which is a fair warning about trusting star ratings alone.
The second is in French, because review text comes back in the reviewer's language.

## Inputs

| Input | What it does |
|---|---|
| `startUrls` | capterra.com product or review page links |
| `productNames` | Names such as `Asana` or `monday.com`, matched through Capterra's search. The lookup is free |
| `maxReviewsPerProduct` | 100 by default, up to 100,000 for every review |
| `sortBy` | `newest`, `most_helpful`, `highest_rated` or `lowest_rated` |
| `starRatings` | Any of `"1"` to `"5"` |
| `productSummary` | A free row per product with star counts, sub-ratings, recommend share, Capterra's pros and cons themes and pricing |
| `compareProducts` | A free row comparing every product in the run, with `leaders` per figure |
| `onlyNewSinceLastRun`, `publishedAfter` | Only reviews you haven't had, or a date cutoff such as `7 days` |

## Price

| Apify tier | Per 1,000 reviews |
|---|---|
| No discount | $1.00 |
| Bronze | $0.90 |
| Silver | $0.80 |
| Gold | $0.70 |

No start fee.
In the final test, 63 of 63 products returned reviews, 1,860 in total, and a separate run collected 3,000 Slack reviews in under 3 minutes.
On 90 software names, 82 returned reviews of the product they name.

## Where it stops

- capterra.com only. Country sites such as capterra.co.uk aren't supported, and G2 links come back as a free `unsupported_site` row.
- Names rely on Capterra's search. A name that matches two products about equally, such as `HubSpot`, returns a free `ambiguous` row with candidates, so pass the full name or the URL.
- Capterra shows small products without a vendor name, so `vendorName` is empty for them.
- If Capterra changes its site, sorting and star filters may stop working until the scraper is updated. The default order keeps working through a fallback.

## License

MIT for the code in this repo.
