# Browser Console Debugging Guide

## How to Open Browser Console
1. Press `F12` on your keyboard
2. Click on the "Console" tab
3. You'll see any error messages or console.log output

## What to Look For When Testing Login/Signup

### Expected Successful Login Sequence
You should see these messages in order:

```
handleLogin: Form submitted
handleLogin: Event object: SubmitEvent {isTrusted: true, ...}
handleLogin: Email = user@example.com , Password length = 8
handleLogin: Attempting to fetch /auth/login
handleLogin: Response received {success: true, message: "Login successful", ...}
handleLogin: Login successful, showing main app
showMainApp: Main app display set, calling setupEventListeners after delay
```

### If You See No Console Messages
- The form submit handler is not being called
- Check that button has `type="submit"`
- Check that button is inside the `<form>` tag
- Clear browser cache and reload the page

### Common Error Messages and Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| `Cannot GET /api/auth/login` | Flask server not running | Run `python app_api.py` in terminal |
| `Failed to fetch` | Server unreachable | Check if localhost:5000 is accessible |
| `Invalid email or password` | Wrong credentials | Check email/password spelling |
| `Email already registered` | Email exists in database | Use a different email or login |
| `CORS error` | Cross-origin request blocked | This should NOT happen - contact admin |

## Testing Without Form (Quick Test)

Open Console and type:
```javascript
// Test the API directly
fetch('http://localhost:5000/api/auth/register', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  credentials: 'include',
  body: JSON.stringify({
    name: 'Test',
    email: 'test@example.com',
    password: 'password123'
  })
})
.then(r => r.json())
.then(d => console.log('Result:', d))
.catch(e => console.error('Error:', e))
```

If this works, the API is fine. If it fails, there's a server issue.

## Checking Network Activity

1. Open Console
2. Click "Network" tab
3. Click Login button
4. You should see:
   - POST request to `/api/auth/login` with status `200` (success) or `401` (wrong password)
   - Look for the request in the list and click it to see details

## Checking Storage

To verify session is being saved:
1. Open Console
2. Right-click page → Inspect
3. Click "Application" tab
4. Look under "Cookies" for `session` cookie
5. After successful login, there should be a session cookie

## Browser DevTools Shortcuts

| Action | Shortcut |
|--------|----------|
| Open DevTools | F12 |
| Open Console | F12 then click Console tab |
| Toggle element inspector | Ctrl+Shift+C (Windows) or Cmd+Shift+C (Mac) |
| Reload hard cache | Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac) |

## Still Stuck?

Try these steps:
1. Hard refresh: Ctrl+Shift+R (or Cmd+Shift+R on Mac)
2. Clear browser cookies for localhost:5000
3. Close and reopen browser
4. Run `python test_auth_api.py` to verify backend works
5. Check that Flask server shows "Running on http://127.0.0.1:5000"
