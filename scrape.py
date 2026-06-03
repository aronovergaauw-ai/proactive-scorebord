from playwright.sync_api import sync_playwright
import os
import json

def haal_scores_op():
    email = os.environ.get('SPOULE_EMAIL')
    wachtwoord = os.environ.get('SPOULE_WACHTWOORD')

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # 1. Log in
        page.goto("https://app.sportspoule.com/login")
        page.fill("input[type='email']", email)
        page.fill("input[type='password']", wachtwoord)
        page.keyboard.press("Enter")
        page.wait_for_url("**/tabs/**", timeout=15000)

        # 2. Ga naar de poule en VANG de onzichtbare data op!
        with page.expect_response(lambda response: "groups/4285" in response.url) as response_info:
            page.goto("https://app.sportspoule.com/tabs/groups/4285")
        
        # 3. Lees de data
        data = response_info.value.json()
        deelnemers = data.get('users', [])
        
        # 4. Sorteer deelnemers op punten (hoogste eerst)
        deelnemers.sort(key=lambda x: x.get('points', 0), reverse=True)

        # 5. Bouw de rijen voor de tabel
        tabel_rijen = ""
        for positie, user in enumerate(deelnemers, start=1):
            naam = user.get('name', 'Onbekend')
            punten = user.get('points', 0)
            
            # Geef de top 3 een kroontje of medaille
            icoon = ""
            if positie == 1: icoon = "🏆 "
            elif positie == 2: icoon = "🥈 "
            elif positie == 3: icoon = "🥉 "
            
            tabel_rijen += f"<tr><td>{positie}</td><td>{icoon}{naam}</td><td><strong>{punten}</strong></td></tr>\n"

        # 6. Bouw de uiteindelijke HTML (Groot en opgemaakt voor een TV scherm!)
        webpagina = f"""
        <html>
            <head>
                <title>ProActive Scorebord</title>
                <meta http-equiv="refresh" content="900"> 
                <style>
                    body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #eef2f5; padding: 40px; color: #333; }}
                    h1 {{ text-align: center; color: #2c3e50; font-size: 4em; margin-bottom: 20px; }}
                    .container {{ background: white; padding: 40px; border-radius: 20px; max-width: 1000px; margin: 0 auto; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }}
                    table {{ width: 100%; border-collapse: collapse; font-size: 2em; }}
                    th, td {{ padding: 20px; text-align: left; border-bottom: 2px solid #eee; }}
                    th {{ background-color: #004b87; color: white; }}
                    tr:nth-child(even) {{ background-color: #f9f9fc; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>⚽ ProActive WK Poule ⚽</h1>
                    <table>
                        <thead>
                            <tr>
                                <th>#</th>
                                <th>Naam</th>
                                <th>Punten</th>
                            </tr>
                        </thead>
                        <tbody>
                            {tabel_rijen}
                        </tbody>
                    </table>
                </div>
            </body>
        </html>
        """

        with open("index.html", "w", encoding="utf-8") as file:
            file.write(webpagina)

        browser.close()

if __name__ == "__main__":
    haal_scores_op()
