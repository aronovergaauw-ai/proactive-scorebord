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

        # 2. Vang de onzichtbare data op
        with page.expect_response(lambda response: "api.sportspoule.com/groups/4285" in response.url and response.request.method == "GET") as response_info:
            page.goto("https://app.sportspoule.com/tabs/groups/4285")
        
        # 3. Lees de data
        data = response_info.value.json()
        deelnemers = data.get('users', [])
        
        # 4. Sorteer deelnemers op punten (hoogste eerst)
        deelnemers.sort(key=lambda x: x.get('points', 0), reverse=True)

        # --- NIEUW: Splits de groep in tweeën voor de 2 kolommen ---
        midden = (len(deelnemers) + 1) // 2
        groep1 = deelnemers[:midden]
        groep2 = deelnemers[midden:]

        def bouw_rij(user, positie):
            # Achternaam wegfilteren door alleen het eerste woord te pakken
            volledige_naam = user.get('name', 'Onbekend')
            voornaam = volledige_naam.split()[0]
            punten = user.get('points', 0)
            
            icoon = ""
            rij_class = ""
            
            # Geef de top 3 een speciale opmaak
            if positie == 1: 
                icoon = "🏆 "
                rij_class = ' class="podium-1"'
            elif positie == 2: 
                icoon = "🥈 "
                rij_class = ' class="podium-2"'
            elif positie == 3: 
                icoon = "🥉 "
                rij_class = ' class="podium-3"'
            
            return f"<tr{rij_class}><td>{positie}</td><td>{icoon}{voornaam}</td><td><strong>{punten}</strong></td></tr>\n"

        # Bouw de twee losse tabellen op
        tabel1_rijen = ""
        for i, user in enumerate(groep1, start=1):
            tabel1_rijen += bouw_rij(user, i)
            
        tabel2_rijen = ""
        for i, user in enumerate(groep2, start=midden + 1):
            tabel2_rijen += bouw_rij(user, i)

        # 6. Bouw de HTML (Twee kolommen & Breedbeeld TV Modus!)
        webpagina = f"""
        <html>
            <head>
                <title>ProActive Scorebord</title>
                <meta http-equiv="refresh" content="900"> 
                <style>
                    body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #eef2f5; margin: 0; padding: 2vh 2vw; color: #333; overflow: hidden; }}
                    h1 {{ text-align: center; color: #2c3e50; font-size: 6vh; margin: 1vh 0 3vh 0; }}
                    .container {{ background: white; padding: 3vh 3vw; border-radius: 20px; width: 95vw; margin: 0 auto; box-shadow: 0 10px 30px rgba(0,0,0,0.1); box-sizing: border-box; }}
                    
                    /* Layout voor de twee tabellen naast elkaar */
                    .twee-kolommen {{ display: flex; gap: 4vw; justify-content: space-between; }}
                    
                    table {{ width: 48%; border-collapse: collapse; font-size: 3.5vh; }}
                    th, td {{ padding: 1.5vh 1.5vw; text-align: left; border-bottom: 2px solid #eee; }}
                    th {{ background-color: #004b87; color: white; font-size: 4vh; }}
                    tr:nth-child(even) {{ background-color: #f9f9fc; }}
                    
                    /* Styling top 3 */
                    .podium-1 td {{ font-weight: bold; background-color: #fff8e1; color: #b8860b; font-size: 3.8vh; }}
                    .podium-2 td {{ font-weight: bold; color: #7f8c8d; font-size: 3.6vh; }}
                    .podium-3 td {{ font-weight: bold; color: #d35400; font-size: 3.6vh; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>⚽ ProActive WK Poule ⚽</h1>
                    <div class="twee-kolommen">
                        <table>
                            <thead>
                                <tr>
                                    <th>#</th>
                                    <th>Naam</th>
                                    <th>Punten</th>
                                </tr>
                            </thead>
                            <tbody>
                                {tabel1_rijen}
                            </tbody>
                        </table>
                        
                        <table>
                            <thead>
                                <tr>
                                    <th>#</th>
                                    <th>Naam</th>
                                    <th>Punten</th>
                                </tr>
                            </thead>
                            <tbody>
                                {tabel2_rijen}
                            </tbody>
                        </table>
                    </div>
                </div>
            </body>
        </html>
        """

        with open("index.html", "w", encoding="utf-8") as file:
            file.write(webpagina)

        browser.close()

if __name__ == "__main__":
    haal_scores_op()
