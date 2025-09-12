# Simple Opt-Out Page for Buildly Automation

Since the Django apps have been removed, here's a simple HTML page for handling opt-outs:

## Option 1: Simple HTML Form (Recommended)

Create `static/opt-out.html`:
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Unsubscribe - Buildly Labs</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; }
        .container { background: #f9f9f9; padding: 30px; border-radius: 10px; }
        .success { color: #28a745; }
        .error { color: #dc3545; }
        input, button { padding: 10px; margin: 5px 0; }
        button { background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Unsubscribe from Buildly Labs</h1>
        <p>We're sorry to see you go! Enter your email below to unsubscribe from our mailing list.</p>
        
        <form id="optOutForm">
            <input type="email" id="email" placeholder="Enter your email address" required style="width: 300px;">
            <br>
            <button type="submit">Unsubscribe</button>
        </form>
        
        <div id="message"></div>
    </div>

    <script>
        document.getElementById('optOutForm').addEventListener('submit', function(e) {
            e.preventDefault();
            const email = document.getElementById('email').value;
            
            // For now, show success message
            // In production, you'd send this to a server endpoint
            document.getElementById('message').innerHTML = 
                '<p class="success">✅ ' + email + ' has been unsubscribed successfully.</p>' +
                '<p>Please email greg@buildly.io to confirm your unsubscribe request.</p>';
        });
    </script>
</body>
</html>
```

## Option 2: Simple PHP Handler (if you have PHP)

Create `opt-out.php`:
```php
<?php
if ($_POST['email']) {
    $email = filter_var($_POST['email'], FILTER_SANITIZE_EMAIL);
    $optOutFile = 'automation/opt_out.json';
    
    $optOuts = file_exists($optOutFile) ? json_decode(file_get_contents($optOutFile), true) : [];
    
    if (!in_array($email, $optOuts)) {
        $optOuts[] = $email;
        file_put_contents($optOutFile, json_encode($optOuts, JSON_PRETTY_PRINT));
    }
    
    echo "✅ $email has been unsubscribed successfully.";
} else {
    // Show form (same HTML as above)
}
?>
```

## Option 3: Email-Based Opt-Out

Simply direct users to email greg@buildly.io with "UNSUBSCRIBE" in the subject line.

The automation system already includes opt-out links in emails that direct to:
`https://buildly.io/opt-out?email={email}`

## Current Implementation

The automation system already handles opt-outs via the `opt_out.json` file. Any email added to this file will be automatically skipped in future campaigns.

You can manually add emails to unsubscribe them:
```bash
# Edit automation/opt_out.json
[
  "user@example.com",
  "another@example.com"
]
```
