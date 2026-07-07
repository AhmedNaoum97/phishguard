# Model Investigation: Diagnosing a 100%-Accurate Model That Failed in Production

## Summary

The phishing-detection model scored a perfect 1.00 precision, recall, and F1 on both
classes, with an ROC-AUC of 1.0000 — a result that should be treated as a warning, not a
success. After building the live prediction endpoint, every real-world URL tested was
flagged as phishing, including `github.com` and `google.com`. Investigation traced the
cause to how the training dataset was constructed: its *legitimate* class contains almost
exclusively bare homepages, so the model learned the shortcut "any URL with a path is
phishing." This is a train/serve distribution mismatch — the model generalizes perfectly
to the dataset's own test split and not at all to real traffic.

---

## 1. The signal: perfect metrics

Both Random Forest and XGBoost produced identical, flawless results on the held-out 20%
test set (47,159 URLs):

| Metric              | Phishing | Legitimate |
| ------------------- | -------- | ---------- |
| Precision           | 1.00     | 1.00       |
| Recall              | 1.00     | 1.00       |
| F1-score            | 1.00     | 1.00       |
| ROC-AUC             | 1.0000   | —          |

Confusion matrix (Random Forest), zero misclassifications in either direction:

```
                 Predicted Phishing   Predicted Legitimate
Actual Phishing        20,189                  0
Actual Legitimate           0             26,970
```

In real-world binary classification — especially adversarial domains like phishing, where
attackers actively try to look legitimate — a model that never makes a single mistake on
tens of thousands of held-out samples is almost never a genuinely strong model. It is far
more often a sign that the data makes the two classes trivially separable in a way that
will not hold up outside the dataset. That was the working hypothesis going in.

---

## 2. Ruling out the obvious causes

Before blaming the dataset, I eliminated the mechanical explanations:

- **Label inversion** — verified against the notebook that `label == 1` is *legitimate* and
  `label == 0` is *phishing*, and that the serving code's `is_phishing = (pred_class == 0)`
  matches. Correct.
- **Feature-order mismatch** — compared the notebook's `URL_ONLY_FEATURES` list against the
  live extractor's `FEATURE_ORDER`, position by position. Identical across all 17 features.
  (This matters because scikit-learn models key on column *position*, not name — a mismatch
  would silently feed the wrong value into every slot.)
- **Corrupted model file** — confirmed the serialized `.pkl` was untouched by any failed
  notebook run.
- **Data leakage / duplicates** — highest single-feature correlation with the label was
  0.86 (not high enough to explain perfect separation); duplicate rows were 0.34% (too few
  to matter). A deliberately weak Logistic Regression baseline also scored 99.99%, which
  rules out "the model is too powerful" and points squarely at the data.

None of these accounted for the result. The problem was upstream, in the data itself.

---

## 3. The production test

Once the feature extractor and `/api/predict` endpoint were live, I tested a spread of
real URLs — a mix of obviously legitimate, obviously malicious, and realistic-phishing
shapes:

| URL                                                        | Expected   | is_phishing | confidence |
| ---------------------------------------------------------- | ---------- | ----------- | ---------- |
| `https://github.com`                                       | Legitimate | true        | 0.74       |
| `https://www.google.com/search?q=python`                   | Legitimate | true        | 0.70       |
| `https://en.wikipedia.org/wiki/Python`                     | Legitimate | true        | 0.69       |
| `https://www.amazon.com/gp/product/B08N5WRWNW/ref=ppx_yo_dt_b` | Legitimate | true    | 0.99       |
| `http://secure-paypal-login-verify.tk/account/update?id=12345` | Phishing | true      | 0.99       |
| `http://192.168.1.1@paypal-secure.tk/verify`               | Phishing   | true        | 1.00       |
| `http://mybank-secure-update.info/login.php`               | Phishing   | true        | 1.00       |

**Every URL was classified as phishing.** The genuinely malicious ones were caught — but so
was everything else. A detector that flags 100% of inputs, including `github.com`, has no
discriminative value; in a SOC context it would generate constant false positives and cause
immediate alert fatigue.

---

## 4. Root cause: what the "legitimate" class actually looks like

Sampling ten random URLs from the legitimate class (`label == 1`) made the problem obvious:

```
https://www.levelup.com
https://www.notjusttoyz.com
https://www.discover-suriname.com
https://www.ecolabelindex.com
https://www.cinematheque.fr
https://www.necclassicmotorshow.com
https://www.ringling.org
https://www.hlcommission.org
https://www.divx-digest.com
https://www.smartgecko.co.za
```

Every legitimate example is a **bare homepage**: `https://www.` + domain + TLD, with no
path, no query string, no parameters. The phishing class, by contrast, is full of deep URLs
with paths and query strings (`/account/update?id=...`, `/login.php`, and so on).

The model never learned what phishing *is*. It learned a proxy that happens to separate this
particular dataset perfectly: **"a URL with a path or query string is phishing; a bare
homepage is legitimate."**

This is confirmed by the feature values. For `google.com/search?q=python`, the extracted
`TLDLegitimateProb` for `.com` was only 0.51 — barely a coin flip — because `.com` is used
just as heavily by the phishing class as the legitimate class in this data. The dataset
simply does not encode the signal the feature name implies.

---

## 5. Why the model still scored 100%

The shortcut and the test set are drawn from the *same* biased distribution. Because every
legitimate URL in the dataset is a bare homepage and every phishing URL has a path, the rule
"path ⇒ phishing" separates the held-out test split with zero errors too. The perfect score
is real — it just measures the model's ability to exploit a dataset artifact, not its
ability to detect phishing.

The moment a real legitimate URL with a path (`google.com/search`, `wikipedia.org/wiki/...`)
is introduced, the shortcut misfires, and the model confidently calls it phishing. This is
the textbook definition of a **train/serve distribution mismatch**: the training data does
not represent the data the model sees in production.

---

## 6. The fix (planned: Sprint 2.5)

1. **Augment the legitimate class** with realistic URLs that include paths and query strings
   — e.g. deep links crawled from top-traffic sites — so the legitimate distribution matches
   what the model will actually encounter.
2. **Retrain** through the existing pipeline (no code changes needed downstream; the API,
   extractor, and DB layers are model-agnostic by design).
3. **Validate against a fixed real-world benchmark set** — the seven URLs above, plus more —
   as an explicit acceptance gate, rather than trusting the dataset's own test split. A model
   that scores well on its own split but fails the benchmark is not shippable.

---

## 7. Lesson

A classification accuracy above ~98–99% on a real-world task should be treated as a red flag
to investigate first, not a result to celebrate. The most valuable check cost nothing: pull
ten raw examples from each class and read them. That single step would have surfaced the
bare-homepage bias before any modeling work — and it is now the first thing I do when a model
looks too good.
