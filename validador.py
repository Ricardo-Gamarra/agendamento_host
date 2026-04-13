from playwright.sync_api import sync_playwright

def testar_login_sync(usuario, senha):
    with sync_playwright() as p:
        # headless=False para você ver o robô trabalhando
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            page.goto("https://host.globalhitss.com/", timeout=60000)
            page.locator("#UserName").fill(usuario)
            page.locator("#Password").fill(senha)
            page.get_by_role("button", name="Iniciar Sesión").click()
            
            page.get_by_role("row", name="Menu HitssId deazevedor").get_by_role("link").click()

            # Seletor de erro que você identificou
            selector_erro = "div.ui-dialog.ui-widget-content"
            
            # Verificamos se o erro aparece em até 5 segundos
            try:
                page.wait_for_selector(selector_erro, state="visible", timeout=5000)
                return False, "Usuário ou senha inválidos no site."
            except:
                # Se não apareceu erro, checamos se logou (URL mudou)
                if "Home" in page.url or page.url != "https://host.globalhitss.com/":
                    return True, "Sucesso"
                else:
                    return False, "Não foi possível confirmar o login."
        except Exception as e:
            return False, f"Erro de conexão: {str(e)}"
        finally:
            browser.close()