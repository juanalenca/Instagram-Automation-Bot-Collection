import os
import time
import random
import unicodedata
import re
import pyperclip
from pollinations import Text, Image
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException

# Função para limpar texto de caracteres problemáticos
def clean_text_for_selenium(text):
    """
    Remove ou substitui caracteres que podem causar problemas no Selenium
    """
    # Remover caracteres de controle
    text = ''.join(char for char in text if unicodedata.category(char) != 'Cc')
    
    # Converter emojis comuns para texto alternativo
    emoji_replacements = {
        '🔥': '[fire]',
        '💯': '[100]',
        '✨': '[sparkles]',
        '❤️': '[heart]',
        '😍': '[heart_eyes]',
        '🚀': '[rocket]',
        '🎉': '[party]',
        '💪': '[muscle]',
        '👏': '[clap]',
        '🌟': '[star]',
        '📸': '[camera]',
        '🎨': '[art]',
        '💝': '[gift_heart]',
        '🌈': '[rainbow]',
        '⭐': '[star]',
        '💎': '[diamond]',
        '🔴': '[red_circle]',
        '🟢': '[green_circle]',
        '🔵': '[blue_circle]',
        '⚡': '[lightning]',
        '🎯': '[target]',
        '💡': '[bulb]'
    }
    
    for emoji, replacement in emoji_replacements.items():
        text = text.replace(emoji, replacement)
    
    # Remover qualquer caractere fora do BMP (Basic Multilingual Plane)
    # Mantém apenas caracteres Unicode de U+0000 a U+FFFF
    text = ''.join(char for char in text if ord(char) <= 0xFFFF)
    
    # Remover caracteres especiais problemáticos, mas manter pontuação básica
    text = re.sub(r'[^\w\s\[\].,!?@#\-_()+=<>:;"\'/\\]', '', text)
    
    return text.strip()

# Passo 1: Gerar prompt para imagem
text_model = Text()
prompt_response = text_model("Gere uma descrição aleatória, criativa e detalhada para uma imagem gerada por IA. Torne-a única e adequada para Instagram.")
image_prompt = prompt_response.strip()

print(f"Prompt gerado para imagem: {image_prompt}")

# Passo 2: Gerar a imagem
image_model = Image(model="flux")
generated_image = image_model(image_prompt)
os.makedirs('images', exist_ok=True)
image_path = 'images/generated_image.jpeg'
generated_image.save(image_path)

print(f"Imagem salva em: {image_path}")

# Passo 3: Gerar legenda
caption_response = text_model(f"Gere uma legenda criativa e envolvente para Instagram para uma imagem descrita como: '{image_prompt}'. Mantenha curta, divertida e inclua hashtags relevantes.")
caption = caption_response.strip()

# Limpar a legenda para evitar problemas com caracteres especiais
caption_clean = clean_text_for_selenium(caption)

print(f"Legenda original: {caption}")
print(f"Legenda limpa: {caption_clean}")

# Passo 4: Automatizar post no Instagram
options = Options()
driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 15)

try:
    driver.get("https://www.instagram.com/")
    time.sleep(random.uniform(2, 5))

    # Login
    username = os.getenv('INSTAGRAM_USERNAME', 'xxxxxx')
    password = os.getenv('INSTAGRAM_PASSWORD', 'xxxxxx')

    username_field = driver.find_element(By.NAME, "username")
    username_field.send_keys(username)
    time.sleep(random.uniform(1, 3))

    password_field = driver.find_element(By.NAME, "password")
    password_field.send_keys(password)
    time.sleep(random.uniform(1, 3))

    login_button = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
    login_button.click()
    time.sleep(10)

    # Lidar com pop-ups pós-login
    print("Procurando pop-ups para dispensar...")
    try:
        print("Tentando clicar no botão 'Not now' específico...")
        not_now_specific = wait.until(EC.element_to_be_clickable((
            By.XPATH, 
            "//div[@role='button' and contains(@class, 'x1i10hfl') and text()='Not now']"
        )))
        not_now_specific.click()
        print("✅ Clicou no botão 'Not now' específico!")
        time.sleep(random.uniform(2, 4))
    except TimeoutException:
        print("Botão 'Not now' específico não encontrado...")

    # Função para clicar com segurança nos botões "Next" e "Share"
    def safe_click_advance(step_name, button_text):
        print(f"Clicando em {step_name}...")
        
        # Seletor baseado nas classes específicas que você forneceu
        specific_selector = f"//div[@role='button' and contains(@class, 'x1i10hfl') and contains(@class, 'xjqpnuy') and text()='{button_text}']"
        
        # Seletores de fallback
        fallback_selectors = [
            f"//div[@role='button' and text()='{button_text}']",
            f"//button[text()='{button_text}']",
            f"//div[contains(@class, 'x1i10hfl') and text()='{button_text}']"
        ]
        
        all_selectors = [specific_selector] + fallback_selectors
        
        for selector in all_selectors:
            try:
                # Encontrar elemento
                button = wait.until(EC.presence_of_element_located((By.XPATH, selector)))
                
                # Scroll até o elemento
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
                time.sleep(1)
                
                # Verificar se elemento está visível e clicável
                if button.is_displayed() and button.is_enabled():
                    # Tentar diferentes métodos de clique
                    click_methods = [
                        ("JavaScript click", lambda: driver.execute_script("arguments[0].click();", button)),
                        ("Normal click", lambda: button.click()),
                        ("Send ENTER", lambda: button.send_keys(Keys.RETURN))
                    ]
                    
                    for method_name, click_method in click_methods:
                        try:
                            print(f"  Tentando {method_name}...")
                            click_method()
                            print(f"✅ {step_name} sucesso com {method_name}!")
                            return True
                        except ElementClickInterceptedException:
                            print(f"  {method_name} interceptado, tentando próximo...")
                            time.sleep(1)
                            continue
                        except Exception as e:
                            print(f"  {method_name} falhou: {str(e)[:50]}...")
                            continue
                            
            except TimeoutException:
                print(f"  Seletor {selector} não encontrado...")
                continue
        
        raise Exception(f"Não foi possível clicar em {step_name}")

    # Encontrar e clicar no botão de nova publicação
    try:
        create_button_selectors = [
            'svg[aria-label="Nova publicação"]',
            'svg[aria-label="New post"]', 
            'svg[aria-label="Create"]',
            'a[href*="/create/"]'
        ]
        
        create_button = None
        for selector in create_button_selectors:
            try:
                print(f"Tentando encontrar botão criar com: {selector}")
                create_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                break
            except TimeoutException:
                continue
        
        if create_button is None:
            print("Tentando navegar diretamente para página de criar...")
            driver.get("https://www.instagram.com/create/select/")
            time.sleep(3)
        else:
            create_button.click()
            print("✅ Clicou no botão de criar post!")
            time.sleep(random.uniform(2, 4))

        # Tentar clicar no botão "Post" se disponível (pode aparecer após criar)
        try:
            print("Procurando botão 'Post' para clicar...")
            post_button_selectors = [
                "//div[contains(@class, 'xdj266r') and contains(@class, 'x14z9mp')]//span[text()='Post']",
                "//span[text()='Post']",
                "//div[@role='button']//span[text()='Post']"
            ]
            
            post_button = None
            for selector in post_button_selectors:
                try:
                    post_button = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    break
                except TimeoutException:
                    continue
            
            if post_button:
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", post_button)
                time.sleep(1)
                post_button.click()
                print("✅ Clicou no botão 'Post'!")
                time.sleep(random.uniform(2, 4))
            else:
                print("Botão 'Post' não encontrado, continuando normalmente...")
                
        except Exception as e:
            print(f"Erro ao tentar clicar em 'Post', continuando: {str(e)[:50]}...")

        # Upload da imagem
        print("Procurando input de arquivo...")
        file_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="file"]')))
        file_input.send_keys(os.path.abspath(image_path))
        print("✅ Imagem enviada!")
        time.sleep(random.uniform(3, 6))

        # Primeiro Next
        safe_click_advance("primeiro Next", "Next")
        time.sleep(random.uniform(3, 5))

        # Segundo Next
        safe_click_advance("segundo Next", "Next")
        time.sleep(random.uniform(3, 5))

        # Campo de legenda - versão com clipboard e múltiplas estratégias
        print("Inserindo legenda...")
        
        caption_inserted = False
        
        # Estratégia 1: Usar clipboard (mais eficaz para editores complexos)
        try:
            print("Tentando inserir legenda - Estratégia 1 (Clipboard)...")
            
            caption_field = wait.until(EC.presence_of_element_located((
                By.CSS_SELECTOR, 
                'div[aria-label="Write a caption..."][contenteditable="true"]'
            )))
            
            # Scroll e foco no elemento
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", caption_field)
            time.sleep(1)
            
            # Clicar múltiplas vezes para garantir foco
            for i in range(3):
                caption_field.click()
                time.sleep(0.5)
            
            # Limpar campo
            caption_field.send_keys(Keys.CONTROL + "a")
            time.sleep(0.5)
            caption_field.send_keys(Keys.DELETE)
            time.sleep(1)
            
            # Copiar texto para clipboard e colar
            pyperclip.copy(caption_clean)
            time.sleep(0.5)
            caption_field.send_keys(Keys.CONTROL + "v")
            time.sleep(2)
            
            # Verificar se colou
            try:
                verification_element = caption_field.find_element(By.CSS_SELECTOR, 'span[data-lexical-text="true"]')
                if verification_element.text.strip():
                    print(f"✅ Legenda inserida com clipboard! Texto: '{verification_element.text}'")
                    caption_inserted = True
                else:
                    print("⚠️ Clipboard colou mas sem texto visível")
            except:
                # Verificar pelo texto geral do campo
                if caption_field.text.strip():
                    print(f"✅ Legenda inserida com clipboard (fallback)! Texto: '{caption_field.text}'")
                    caption_inserted = True
                else:
                    print("❌ Clipboard não funcionou")
                    
        except Exception as e:
            print(f"❌ Estratégia 1 (Clipboard) falhou: {str(e)[:100]}...")
        
        # Estratégia 2: Digitação letra por letra (mais lenta mas eficaz)
        if not caption_inserted:
            try:
                print("Tentando inserir legenda - Estratégia 2 (Digitação letra por letra)...")
                
                caption_field = wait.until(EC.element_to_be_clickable((
                    By.CSS_SELECTOR, 
                    'div[aria-label="Write a caption..."][contenteditable="true"]'
                )))
                
                # Garantir foco
                caption_field.click()
                time.sleep(1)
                caption_field.send_keys(Keys.CONTROL + "a")
                time.sleep(0.5)
                caption_field.send_keys(Keys.DELETE)
                time.sleep(1)
                
                # Digitar letra por letra
                for char in caption_clean:
                    caption_field.send_keys(char)
                    time.sleep(0.05)  # Pequena pausa entre cada caractere
                
                time.sleep(2)
                
                # Verificar
                if caption_field.text.strip():
                    print(f"✅ Legenda inserida letra por letra! Texto: '{caption_field.text}'")
                    caption_inserted = True
                else:
                    print("❌ Digitação letra por letra não funcionou")
                    
            except Exception as e:
                print(f"❌ Estratégia 2 falhou: {str(e)[:100]}...")
        
        # Estratégia 3: JavaScript com eventos simulados
        if not caption_inserted:
            try:
                print("Tentando inserir legenda - Estratégia 3 (JavaScript + Eventos)...")
                
                caption_field = wait.until(EC.element_to_be_clickable((
                    By.CSS_SELECTOR, 
                    'div[aria-label="Write a caption..."][contenteditable="true"]'
                )))
                
                # Script JavaScript mais completo
                js_complete_script = """
                var field = arguments[0];
                var text = arguments[1];
                
                // Focar primeiro
                field.focus();
                field.click();
                
                // Limpar
                field.innerHTML = '';
                
                // Inserir texto diretamente
                field.textContent = text;
                
                // Criar estrutura Lexical se necessário
                if (field.textContent && !field.querySelector('p')) {
                    var p = document.createElement('p');
                    p.className = 'xdj266r x14z9mp xat24cr x1lziwak';
                    p.setAttribute('dir', 'ltr');
                    
                    var span = document.createElement('span');
                    span.setAttribute('data-lexical-text', 'true');
                    span.textContent = text;
                    
                    p.appendChild(span);
                    field.innerHTML = '';
                    field.appendChild(p);
                }
                
                // Simular digitação
                var inputEvent = new InputEvent('input', { 
                    inputType: 'insertText', 
                    data: text,
                    bubbles: true, 
                    cancelable: true 
                });
                field.dispatchEvent(inputEvent);
                
                // Outros eventos importantes
                field.dispatchEvent(new KeyboardEvent('keydown', { bubbles: true }));
                field.dispatchEvent(new KeyboardEvent('keyup', { bubbles: true }));
                field.dispatchEvent(new Event('change', { bubbles: true }));
                field.dispatchEvent(new FocusEvent('blur', { bubbles: true }));
                field.dispatchEvent(new FocusEvent('focus', { bubbles: true }));
                
                return field.textContent;
                """
                
                result = driver.execute_script(js_complete_script, caption_field, caption_clean)
                time.sleep(2)
                
                if result and result.strip():
                    print(f"✅ Legenda inserida com JavaScript! Resultado: '{result}'")
                    caption_inserted = True
                else:
                    print("❌ JavaScript não retornou texto")
                    
            except Exception as e:
                print(f"❌ Estratégia 3 falhou: {str(e)[:100]}...")
        
        # Estratégia 4: Combinação de métodos
        if not caption_inserted:
            print("Tentando inserir legenda - Estratégia 4 (Combinada)...")
            try:
                caption_field = wait.until(EC.element_to_be_clickable((
                    By.CSS_SELECTOR, 
                    'div[aria-label="Write a caption..."][contenteditable="true"]'
                )))
                
                # Método combinado: JavaScript + Clipboard + Interação
                caption_field.click()
                time.sleep(1)
                
                # JavaScript
                driver.execute_script("arguments[0].textContent = arguments[1];", caption_field, caption_clean)
                time.sleep(1)
                
                # Clipboard como backup
                pyperclip.copy(caption_clean)
                caption_field.send_keys(Keys.CONTROL + "a")
                time.sleep(0.5)
                caption_field.send_keys(Keys.CONTROL + "v")
                time.sleep(1)
                
                # Interação final
                caption_field.send_keys(Keys.END)
                caption_field.send_keys(" ")
                caption_field.send_keys(Keys.BACKSPACE)
                
                if caption_field.text.strip():
                    print("✅ Estratégia combinada funcionou!")
                    caption_inserted = True
                    
            except Exception as e:
                print(f"❌ Estratégia 4 falhou: {str(e)[:100]}...")
        
        if not caption_inserted:
            print("⚠️ TODAS AS ESTRATÉGIAS FALHARAM - continuando sem legenda")
        else:
            print(f"✅ Legenda final inserida: '{caption_clean}'")
        
        time.sleep(random.uniform(3, 5))

        # Verificação final da legenda antes de compartilhar
        print("Verificando legenda antes de compartilhar...")
        try:
            # Procurar o campo de legenda novamente
            caption_field = driver.find_element(By.CSS_SELECTOR, 'div[aria-label="Write a caption..."][contenteditable="true"]')
            
            # Verificar se há texto no campo
            current_text = ""
            try:
                text_span = caption_field.find_element(By.CSS_SELECTOR, 'span[data-lexical-text="true"]')
                current_text = text_span.text.strip()
            except:
                current_text = caption_field.text.strip()
            
            print(f"Texto atual no campo: '{current_text}'")
            
            # Se não há texto ou está diferente, tentar inserir novamente
            if not current_text or current_text != caption_clean.strip():
                print("⚠️ Legenda não está presente ou está incorreta. Re-inserindo...")
                
                # Focar no campo
                caption_field.click()
                time.sleep(1)
                
                # Método mais agressivo - usar JavaScript para forçar a inserção
                js_force_insert = """
                var field = arguments[0];
                var text = arguments[1];
                
                // Limpar completamente
                field.innerHTML = '';
                
                // Criar estrutura correta
                var p = document.createElement('p');
                p.className = 'xdj266r x14z9mp xat24cr x1lziwak';
                p.setAttribute('dir', 'ltr');
                
                var span = document.createElement('span');
                span.setAttribute('data-lexical-text', 'true');
                span.textContent = text;
                
                p.appendChild(span);
                field.appendChild(p);
                
                // Forçar eventos múltiplos
                field.focus();
                field.click();
                
                var events = ['input', 'change', 'keyup', 'keydown', 'blur', 'focus'];
                events.forEach(function(eventType) {
                    var event = new Event(eventType, { bubbles: true, cancelable: true });
                    field.dispatchEvent(event);
                });
                
                // Trigger change no documento também
                document.dispatchEvent(new Event('change', { bubbles: true }));
                
                return field.textContent;
                """
                
                result = driver.execute_script(js_force_insert, caption_field, caption_clean)
                time.sleep(2)
                
                print(f"Resultado da re-inserção forçada: '{result}'")
                
                # Simular interação humana
                caption_field.click()
                time.sleep(0.5)
                caption_field.send_keys(Keys.END)  # Ir para o final
                time.sleep(0.5)
                caption_field.send_keys(Keys.SPACE)  # Adicionar espaço
                time.sleep(0.5)
                caption_field.send_keys(Keys.BACKSPACE)  # Remover espaço
                time.sleep(1)
                
                print("✅ Re-inserção da legenda concluída!")
            else:
                print("✅ Legenda verificada - está presente no campo!")
                
        except Exception as e:
            print(f"⚠️ Erro na verificação final da legenda: {str(e)[:100]}...")
        
        # Pequena pausa antes de compartilhar
        time.sleep(random.uniform(2, 3))

        # Compartilhar - usando o método seguro
        safe_click_advance("Compartilhar", "Share")
        time.sleep(random.uniform(5, 8))

        # Verificar sucesso
        try:
            success_message = wait.until(EC.presence_of_element_located((
                By.XPATH, 
                '//h3[contains(text(), "Seu post foi compartilhado")] | //h3[contains(text(), "Your post has been shared")]'
            )))
            print("🎉 POST PUBLICADO COM SUCESSO!")
            time.sleep(5)
        except TimeoutException:
            print("⚠️ Post pode ter sido publicado, mas confirmação não encontrada")

    except Exception as e:
        print(f"❌ Erro durante o posting: {e}")
        # Salvar screenshot para debug
        driver.save_screenshot("erro_debug.png")
        print("Screenshot de erro salvo como 'erro_debug.png'")

finally:
    print("Fechando navegador...")
    driver.quit()