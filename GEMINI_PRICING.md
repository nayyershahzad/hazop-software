# Gemini API Pricing Calculator

**Last Updated**: October 13, 2025
**Model Used**: Gemini 2.5 Flash

---

## 📊 Gemini 2.5 Flash Pricing (Current Model)

### Official Pricing (as of October 2025):

**Input (Prompts)**:
- Up to 128K tokens: **$0.075 per 1 million tokens**
- Over 128K tokens: **$0.15 per 1 million tokens**

**Output (Responses)**:
- Up to 128K tokens: **$0.30 per 1 million tokens**
- Over 128K tokens: **$0.60 per 1 million tokens**

**Free Tier**:
- 1,500 requests per day (RPD)
- 1 million tokens per minute (TPM)
- 10 million tokens per day

---

## 💰 Cost per AI Insight Call

### Typical Token Usage per Call:

Based on our HAZOP implementation:

#### 1. Suggest Causes:
```
Input tokens:  ~500 tokens (prompt with context)
Output tokens: ~800 tokens (5 causes with reasoning)
Total:         ~1,300 tokens per call
```

#### 2. Suggest Consequences:
```
Input tokens:  ~550 tokens (prompt with context + cause)
Output tokens: ~700 tokens (4 consequences with metadata)
Total:         ~1,250 tokens per call
```

#### 3. Suggest Recommendations (Safeguards):
```
Input tokens:  ~600 tokens (prompt with context + cause + consequence)
Output tokens: ~900 tokens (5 safeguards with details)
Total:         ~1,500 tokens per call
```

#### 4. Contextual Knowledge:
```
This uses backend logic, NOT Gemini API
Cost: $0 (no API call)
```

---

## 💵 Cost Calculation for 1000 Calls

### Scenario 1: 1000 Cause Suggestions

**Token Usage**:
- Input:  1,000 calls × 500 tokens = 500,000 tokens
- Output: 1,000 calls × 800 tokens = 800,000 tokens

**Cost**:
- Input:  500,000 tokens × $0.075 / 1,000,000 = **$0.0375**
- Output: 800,000 tokens × $0.30 / 1,000,000  = **$0.24**
- **Total: $0.2775 (~$0.28)**

### Scenario 2: 1000 Consequence Suggestions

**Token Usage**:
- Input:  1,000 calls × 550 tokens = 550,000 tokens
- Output: 1,000 calls × 700 tokens = 700,000 tokens

**Cost**:
- Input:  550,000 tokens × $0.075 / 1,000,000 = **$0.04125**
- Output: 700,000 tokens × $0.30 / 1,000,000  = **$0.21**
- **Total: $0.25125 (~$0.25)**

### Scenario 3: 1000 Recommendation Suggestions

**Token Usage**:
- Input:  1,000 calls × 600 tokens = 600,000 tokens
- Output: 1,000 calls × 900 tokens = 900,000 tokens

**Cost**:
- Input:  600,000 tokens × $0.075 / 1,000,000 = **$0.045**
- Output: 900,000 tokens × $0.30 / 1,000,000  = **$0.27**
- **Total: $0.315 (~$0.32)**

### Scenario 4: Complete HAZOP Analysis (1000 Full Workflows)

Assuming each HAZOP node uses:
- 1 cause suggestion call
- 1 consequence suggestion call
- 1 recommendation suggestion call

**Token Usage per Workflow**:
- Total tokens: 1,300 + 1,250 + 1,500 = 4,050 tokens

**For 1000 Complete Workflows**:
- Total tokens: 4,050 × 1,000 = 4,050,000 tokens
- Input:  1,650,000 tokens × $0.075 / 1,000,000 = **$0.124**
- Output: 2,400,000 tokens × $0.30 / 1,000,000  = **$0.72**
- **Total: $0.844 (~$0.85)**

---

## 📈 Summary Table

| Operation | Calls | Est. Cost | Cost per Call |
|-----------|-------|-----------|---------------|
| **Causes Only** | 1,000 | $0.28 | $0.00028 |
| **Consequences Only** | 1,000 | $0.25 | $0.00025 |
| **Recommendations Only** | 1,000 | $0.32 | $0.00032 |
| **Complete Workflow** | 1,000 | $0.85 | $0.00085 |
| **Contextual Knowledge** | 1,000 | $0.00 | $0.00000 |

---

## 🎯 Practical Usage Examples

### Small Project (50 HAZOP nodes):
- 50 nodes × 3 calls each = 150 API calls
- Estimated cost: **$0.13**

### Medium Project (200 HAZOP nodes):
- 200 nodes × 3 calls each = 600 API calls
- Estimated cost: **$0.51**

### Large Project (500 HAZOP nodes):
- 500 nodes × 3 calls each = 1,500 API calls
- Estimated cost: **$1.28**

### Very Large Project (1000 HAZOP nodes):
- 1,000 nodes × 3 calls each = 3,000 API calls
- Estimated cost: **$2.55**

---

## 🆓 Free Tier Coverage

**Free Tier Limits**:
- 1,500 requests per day
- 10 million tokens per day

**What You Can Do for Free**:
- **Daily**: ~500 complete HAZOP node analyses (1,500 API calls / 3)
- **Monthly**: ~15,000 complete analyses

**Token Usage Check**:
- 500 nodes × 4,050 tokens = 2,025,000 tokens
- ✅ Well within 10M token limit

**Conclusion**: For most HAZOP projects, you'll stay within the free tier!

---

## 💡 Cost Optimization Tips

### 1. Batch Processing
Instead of 3 separate calls, use the `/complete-analysis` endpoint:
- Saves ~20% on tokens (less repeated context)
- Single API call instead of 3

### 2. Context Management
Only provide relevant context:
- ❌ Don't: Include entire P&ID description (1000+ tokens)
- ✅ Do: Include concise process description (200 tokens)

### 3. Cache Results
Store AI suggestions in database:
- Reuse suggestions for similar deviations
- Avoid re-generating same content

### 4. Smart Refresh
Only refresh when needed:
- Don't auto-refresh on every page load
- Let users manually trigger suggestions

### 5. Quality Over Quantity
Request 3-5 suggestions instead of 10:
- Less output tokens
- Higher quality, more relevant results

---

## 📊 Comparison with Other Models

### Gemini 2.5 Flash (Current):
- Cost: **$0.85 per 1000 workflows**
- Speed: **Fast** (1-2 seconds)
- Quality: **High**
- ✅ **Best value**

### Gemini 2.5 Pro:
- Input: $1.25 per 1M tokens
- Output: $5.00 per 1M tokens
- Cost: **~$13 per 1000 workflows**
- Speed: Slower (3-5 seconds)
- Quality: Highest
- Use case: Critical safety analysis only

### Gemini Flash Lite:
- Free tier only
- Speed: Fastest (<1 second)
- Quality: Lower
- Use case: Testing/development

---

## 🔍 Real-World Cost Analysis

### Typical HAZOP Study:
- **Number of nodes**: 50-100
- **API calls**: 150-300
- **Monthly cost**: $0.13 - $0.26
- **Annual cost**: $1.56 - $3.12

### Large Facility HAZOP:
- **Number of nodes**: 500-1000
- **API calls**: 1,500-3,000
- **Monthly cost**: $1.28 - $2.55
- **Annual cost**: $15.36 - $30.60

### Enterprise (Multiple Facilities):
- **Number of nodes**: 5,000-10,000/year
- **API calls**: 15,000-30,000
- **Annual cost**: $12.75 - $25.50

---

## 📞 Billing & Monitoring

### Check Your Usage:
1. Visit: https://console.cloud.google.com/apis/api/generativelanguage.googleapis.com/quotas
2. Monitor: Request count, token usage, costs
3. Set alerts for unexpected spikes

### Budget Planning:
- **Small company**: $5-10/month budget covers 5,000+ analyses
- **Medium company**: $50/month covers 50,000+ analyses
- **Enterprise**: $500/month covers 500,000+ analyses

---

## ⚠️ Important Notes

1. **Prices may change**: Check official Gemini pricing page for updates
2. **Free tier is generous**: Most users won't exceed it
3. **Contextual Knowledge is free**: Uses backend logic, not Gemini API
4. **Token estimates are approximate**: Actual usage varies by content length

---

## 📚 Official Resources

- **Pricing Page**: https://ai.google.dev/pricing
- **API Limits**: https://ai.google.dev/gemini-api/docs/models/gemini#model-variations
- **Documentation**: https://ai.google.dev/docs

---

## ✅ Summary

**For 1000 API calls** (your question):

| Type | Cost |
|------|------|
| Causes only | **$0.28** |
| Consequences only | **$0.25** |
| Recommendations only | **$0.32** |
| Complete workflow (causes + consequences + recommendations) | **$0.85** |
| Contextual Knowledge | **$0.00** (no API call) |

**Bottom line**: Gemini 2.5 Flash is **extremely cost-effective** for HAZOP analysis. Most projects will stay within the free tier, and even large-scale usage costs less than $1 per 1000 complete analyses.

---

**Last Updated**: October 13, 2025
**Model**: Gemini 2.5 Flash
**Pricing Source**: https://ai.google.dev/pricing
