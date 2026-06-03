from playwright.sync_api import sync_playwright
import os

def haal_scores_op():
    email = os.environ.get('SPOULE_EMAIL')
    wachtwoord = os.environ.get('SPOULE_WACHTWOORD')

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Log in
        page.goto("https://app.sportspoule.com/login")
        page.fill("input[type='email']", email)
        page.fill("input[type='password']", wachtwoord)
        
        # In plaats van zoeken naar de knop, drukken we op Enter!
        page.keyboard.press("Enter")

        # Wacht tot we ingelogd zijn en ga naar de poule
        page.wait_for_url("**/tabs/**", timeout=15000)
        page.goto("https://app.sportspoule.com/tabs/groups/4285")

        # Geef de pagina even tijd om de data in te laden
        page.wait_for_timeout(5000)

        # Haal de hele inhoud van het scherm op
        html_content = page.content()

        # Sla op als webpagina
        webpagina = f"""
        <html>
            <head>
                <title>ProActive Scorebord</title>
                <style>
                    body {{ font-family: sans-serif; background: #eef2f5; padding: 20px; }}
                    h1 {{ color: #333; text-align: center; }}
                    .container {{ background: white; padding: 20px; border-radius: 10px; max-width: 800px; margin: 0 auto; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>ProActive World Cup Poule</h1>
                    <p>De laatste stand wordt hier getoond. (We moeten de precieze tabel nog filteren!)</p>
                </div>
            </body>
        </html>
        """

        with open("index.html", "w", encoding="utf-8") as file:
            file.write(webpagina)

        browser.close()

if __name__ == "__main__":
    haal_scores_op()
