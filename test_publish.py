from NewsTools import publish_to_wordpress

title = "Test Post from REST API"
content = "<p>This is a <strong>test</strong> post published using REST API.</p>"
category = "Automation"

result = publish_to_wordpress(title, content, image_url=None, category_name=category)
try:
    print(f"\nResulting Post URL: {result.json().get('link')}")
except Exception:
    print(f"\nResult: {result.text}")

# Add this to always print the full response JSON for debugging:
print("\nFull response JSON:", result.json())