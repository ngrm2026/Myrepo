# Receiving enquiries from the website

The **Contact Us** form posts to `/api/enquiry`. The server checks every field again,
blocks spam (hidden "honeypot" field, too-fast submissions, rate limit, other-site requests)
and then forwards the enquiry to **email**, a **webhook**, or both.

Until one of them is set up, the form tells the customer to send the same details on
WhatsApp (one tap — the message is pre-filled), so no lead is lost.

## Option A — Email (Resend)

1. Create a free account at <https://resend.com> and create an API key.
2. (Recommended) Verify your domain in Resend so emails come from your own address.
3. Add these environment variables (Vercel → Project → Settings → Environment Variables):
   - `RESEND_API_KEY` – your API key
   - `ENQUIRY_TO_EMAIL` – where enquiries go (comma-separate several addresses)
   - `ENQUIRY_FROM_EMAIL` – e.g. `Website Enquiry <enquiry@your-domain.com>`
4. Redeploy.

## Option B — Google Sheet (simple enquiry management)

Every enquiry becomes a new row — easy to track, filter, and share with your team.

1. Create a Google Sheet. In row 1 add the headings:
   `Received | Name | Mobile | Location | Requirement | Description | Page | Status`
2. Open **Extensions → Apps Script**, replace the code with:

   ```js
   function doPost(e) {
     const d = JSON.parse(e.postData.contents);
     const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheets()[0];
     sheet.appendRow([d.receivedAt, d.name, "'" + d.mobile, d.location, d.requirement, d.description, d.page, "New"]);
     return ContentService.createTextOutput("ok");
   }
   ```

3. Click **Deploy → New deployment → Web app**. Set *Execute as*: **Me**, *Who has access*: **Anyone**. Copy the Web app URL.
4. Set `ENQUIRY_WEBHOOK_URL` to that URL and redeploy.
5. Use the **Status** column (New / Called / Quoted / Done) to manage leads.

You can also point `ENQUIRY_WEBHOOK_URL` at Zapier, Make, or any service that accepts JSON.

## What the webhook receives

```json
{
  "name": "Ravi Kumar",
  "mobile": "+919876543210",
  "location": "Adyar, Chennai",
  "requirement": "Automatic Phase Changeover Switches",
  "description": "Need automatic changeover for 3-phase house",
  "receivedAt": "9/11/2026, 3:10:17 pm",
  "page": "https://www.your-domain.com/contact?product=...",
  "source": "website"
}
```
