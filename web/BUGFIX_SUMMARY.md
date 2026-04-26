# Bug Fix Summary - 2026-04-26

## Issue: Usage Display Not Working

### Problem
The "检查账号使用情况" (Check Account Usage) feature was not displaying usage data correctly. The frontend was trying to access incorrect field names from the API response.

### Root Cause
The frontend code was attempting to read fields like `usage_usd`, `total_usage`, and `total_granted` from the usage data, but the actual CPA API returns a different structure:

```javascript
// Actual structure from CPA API:
{
  "rate_limit": {
    "primary_window": {
      "used_percent": 45.2  // Percentage (0-100)
    },
    "limit_reached": false
  }
}
```

### Solution
Updated `web/templates/base.html` in the `checkUsage()` function to:

1. **Use correct data structure**:
   ```javascript
   const rateLimit = usage.rate_limit || {};
   const primaryWindow = rateLimit.primary_window || {};
   const usedPercent = primaryWindow.used_percent || 0;
   const limitReached = rateLimit.limit_reached || false;
   ```

2. **Display percentage instead of dollar amounts**:
   ```javascript
   usageInfo = `${usedPercent.toFixed(1)}%`;
   ```

3. **Add status icons based on usage**:
   - 🟢 Green: < 50% usage
   - 🟡 Yellow: ≥ 50% usage
   - 🔴 Red: Limit reached

4. **Improved detail display**:
   ```javascript
   detailInfo = `${statusIcon} 使用率: ${usedPercent.toFixed(1)}% | 限额: ${limitReached ? '已达' : '未达'}`;
   ```

### Files Modified
- `web/templates/base.html` - Fixed checkUsage() function (lines ~678-700)
- `web/CHANGELOG.md` - Added v1.0.1 release notes

### Testing
To test the fix:
1. Start the web application
2. Navigate to "账号管理" (Account Management)
3. Select a server
4. Click "检查使用情况" (Check Usage)
5. Verify that usage is displayed as percentage (e.g., "45.2%")
6. Verify status icons appear correctly

### Reference
The correct data structure was confirmed by examining:
- `shell/manage_accounts.py` (lines 545-570) - Shows how Shell version handles usage data
- `web/utils/cpa_client.py` - Shows raw API response structure
- `web/routes/accounts.py` - Shows backend passes through raw usage data

### Additional Improvements
- Removed debug `console.log()` statements
- Cleaned up code comments
- Aligned with Shell version's display format
