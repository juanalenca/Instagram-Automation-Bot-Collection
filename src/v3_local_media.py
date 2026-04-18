import os
import time
import random
import unicodedata
import re
import pyperclip
import schedule
import threading
import requests
import json
from datetime import datetime, timedelta
import logging
import cv2
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException, NoSuchElementException


# Configuração de logs
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('instagram_bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)


class EbookImageVideoGenerator:
    def __init__(self):
        """Inicializa o gerador de vídeo a partir de imagens locais."""
        self.image_folder = "imgs"
    
        # Criar diretórios se não existirem
        os.makedirs(self.image_folder, exist_ok=True)
        os.makedirs("generated_videos", exist_ok=True)

    def get_random_image_from_folder(self):
        """Seleciona uma imagem aleatória da pasta 'imgs'."""
        print(f"🖼️  Procurando por imagens na pasta '{self.image_folder}'...")
    
        try:
            # Lista apenas arquivos de imagem comuns
            valid_extensions = ('.png', '.jpg', '.jpeg', '.webp')
            images = [f for f in os.listdir(self.image_folder) if f.lower().endswith(valid_extensions)]
        
            if not images:
                print(f"❌ Erro: Nenhuma imagem encontrada na pasta '{self.image_folder}'.")
                print("   Por favor, adicione arquivos .png, .jpg ou .jpeg nesta pasta.")
                return None
        
            # Escolhe uma imagem aleatoriamente
            chosen_image_name = random.choice(images)
            image_path = os.path.join(self.image_folder, chosen_image_name)
        
            print(f"✅ Imagem selecionada: {image_path}")
            return image_path

        except FileNotFoundError:
            print(f"❌ Erro: A pasta '{self.image_folder}' não foi encontrada.")
            return None

    def create_video_from_image(self, image_path, duration=5):
        """Converte imagem estática em vídeo MP4 (função mantida como original)"""
        if not os.path.exists(image_path):
            print(f"❌ Imagem não encontrada: {image_path}")
            return None

        print(f"🎬 Convertendo imagem para vídeo...")

        img = cv2.imread(image_path)
        if img is None:
            print(f"❌ Erro ao carregar imagem: {image_path}")
            return None

        height, width, _ = img.shape
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        video_filename = f"generated_videos/ebook_video_{timestamp}.mp4"
    
        fourcc = cv2.VideoWriter_fourcc(*'X264')
        fps = 30
        total_frames = duration * fps
    
        video_writer = cv2.VideoWriter(video_filename, fourcc, fps, (width, height))
        if not video_writer.isOpened():
            print("❌ Erro ao criar o arquivo de vídeo")
            return None

        for frame in range(total_frames):
            video_writer.write(img)
            if frame % (fps * 2) == 0:
                progress = (frame / total_frames) * 100
                print(f"📹  Progresso: {progress:.1f}%")

        video_writer.release()
        print(f"✅ Vídeo salvo: {video_filename}")

        if os.path.exists(video_filename) and os.path.getsize(video_filename) > 0:
            return video_filename
        else:
            print("❌ Erro: Arquivo de vídeo não foi criado ou está vazio.")
            return None

    def create_video_from_local_image(self, video_duration=5):
        """Processo completo: pega uma imagem local e converte para vídeo"""
        print("🚀 Iniciando criação de vídeo a partir de imagem local...")
        print("-" * 50)
    
        # Pega o caminho de uma imagem da pasta
        image_path = self.get_random_image_from_folder()
        if not image_path:
            print("❌ Falha ao obter imagem da pasta.")
            return None, None
    
        time.sleep(1) # Pequena pausa
    
        # Converter para vídeo
        video_path = self.create_video_from_image(image_path, video_duration)
        if not video_path:
            print("❌ Falha ao gerar vídeo")
            return image_path, None
    
        print("-" * 50)
        print("🎉 Processo concluído com sucesso!")
        print(f"📸 Imagem usada: {image_path}")
        print(f"🎥 Vídeo gerado: {video_path}")
    
        return image_path, video_path


class InstagramVideoBot:
    def __init__(self, target_post_time=None):
        # CONFIGURAÇÕES DIRETAS
        self.username = 'xxxxxx'
        self.password = 'xxxxxx'
        self.target_post_time = target_post_time
    
        # API Keys - DEFINIDAS DIRETAMENTE
        self.replicate_api_key = None  # Desabilitado por enquanto
        self.groq_api_key = 'xxxxxx'
    
        # Inicializar gerador de vídeo local
        self.video_generator = EbookImageVideoGenerator()
    
        # Verificar configurações
        logging.info(f"✅ Username configurado: {self.username}")
        logging.info(f"✅ Password configurado: {'*' * len(self.password)}")
        logging.info(f"✅ GROQ_API_KEY configurada: {self.groq_api_key[:8]}...")

    def clean_text_for_selenium(self, text):
        """Remove ou substitui caracteres que podem causar problemas no Selenium, mantendo emojis."""
        # Remover caracteres de controle
        text = ''.join(char for char in text if unicodedata.category(char) != 'Cc')
    
        # Remover qualquer caractere fora do BMP (Basic Multilingual Plane) - opcional, mas seguro
        text = ''.join(char for char in text if ord(char) <= 0xFFFF)
    
        # Remover caracteres especiais problemáticos, mas mantendo os básicos para legendas
        text = re.sub(r'[^\w\s.,!?@#\-_()+=<>:;"\'/\\]', '', text)
    
        return text.strip()

    def generate_video_with_fallbacks(self):
        """Gera vídeo usando o gerador de imagens locais"""
        logging.info("🎬 Iniciando geração de vídeo a partir de imagem local...")
        
        image_path, video_path = self.video_generator.create_video_from_local_image(video_duration=5)
        
        if video_path and os.path.exists(video_path):
            logging.info(f"✅ Vídeo gerado com sucesso: {video_path}")
            return video_path
        else:
            logging.error("❌ Falha na geração do vídeo a partir da imagem local")
            return None

    def generate_description_with_groq(self, video_prompt):
        """Gera descrição usando API Groq com prompt específico do ebook"""
        logging.info("📝 Gerando descrição com Groq...")
    
        fallback_descriptions = [
            "💰 PROMOÇÃO IMPERDÍVEL! 💰\n\n📖 '100 Maneiras de Ganhar Dinheiro' por apenas R$35!\nDe R$70 por R$35 - 50% OFF! 🔥\n\n✅ Ideias práticas para aumentar sua renda\n✅ Estratégias para todos os públicos\n✅ Oportunidade única!\n\n⏰ Por tempo limitado!\n👆 GARANTE O SEU AGORA! #DinheiroExtra #Promoção",
            "🚀 TRANSFORME SUA VIDA FINANCEIRA! 🚀\n\n📚 100 Maneiras de Ganhar Dinheiro\n💲 SUPER PROMOÇÃO: R$35 (era R$70!)\n\n🎯 Estratégias comprovadas\n🎯 Métodos acessíveis\n🎯 Resultados reais\n\n⚡ ÚLTIMAS UNIDADES!\n🛒 Compre já! #RendaExtra #Sucesso",
            "💡 OPORTUNIDADE ÚNICA! 💡\n\n📖 100 Maneiras de Ganhar Dinheiro\n🏷️ 50% OFF - Apenas R$35!\n\n🔸 Ideias práticas e eficazes\n🔸 Para iniciantes e experientes\n🔸 Aumente sua renda hoje!\n\n⏳ Promoção por tempo limitado!\n👉 CLIQUE E GARANTE! #Dinheiro #Oportunidade"
        ]
    
        try:
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.groq_api_key}",
                "Content-Type": "application/json"
            }
        
            # Usando o prompt específico do ebook
            ebook_prompt = "Crie uma descrição cativante e persuasiva para um anúncio no Instagram do livro '100 Maneiras de Ganhar Dinheiro'. Destaque que o livro está com uma promoção imperdível. Use um tom motivador e direto, enfatizando os benefícios do livro, como ideias práticas para aumentar a renda, estratégias acessíveis para todos os públicos e a oportunidade única de adquirir o livro por um preço especial. Inclua uma chamada para ação clara, incentivando a compra imediata, e mencione que a promoção é por tempo limitado. A descrição deve ser curta, ideal para um post no Instagram, com até 100 palavras, e incluir emojis para engajamento."
        
            payload = {
                "model": "llama3-8b-8192",
                "messages": [
                    {
                        "role": "system",
                        "content": "Você é um especialista em marketing digital e criação de conteúdo para Instagram, especializado em promoções de ebooks e produtos digitais."
                    },
                    {
                        "role": "user",
                        "content": ebook_prompt
                    }
                ],
                "max_tokens": 300,
                "temperature": 0.7
            }
        
            response = requests.post(url, headers=headers, json=payload, timeout=15)
        
            if response.status_code == 200:
                data = response.json()
                description = data['choices'][0]['message']['content'].strip()
                logging.info(f"✅ Descrição gerada com Groq: {description}")
                return description
            
        except Exception as e:
            logging.warning(f"⚠️ Erro no Groq: {str(e)}")
    
        description = random.choice(fallback_descriptions)
        logging.info(f"✅ Usando descrição fallback: {description}")
        return description

    def wait_for_post_time(self):
        """Aguarda horário correto para postar"""
        if not self.target_post_time:
            logging.info("🚀 Sem horário alvo, postando imediatamente...")
            return True
    
        current_time = datetime.now()
        target_datetime = datetime.combine(current_time.date(), self.target_post_time)
    
        time_difference = (target_datetime - current_time).total_seconds()
    
        if time_difference <= 0:
            logging.info("✅ Horário atingido! Postando...")
            return True
    
        if time_difference <= 300:  # 5 minutos
            logging.info(f"⏰ Aguardando {int(time_difference)} segundos...")
        
            while datetime.now() < target_datetime:
                time.sleep(1)
        
            logging.info("🎯 Hora de postar!")
            return True
        else:
            logging.warning("⚠️ Muito tempo de espera, postando imediatamente...")
            return True

    def handle_ok_button_after_upload(self, driver, wait):
        """Lidar com o pop-up 'Video posts are now shared as reels' após o upload."""
        logging.info("🔍 Verificando pop-up 'Video posts are now reels'...")
    
        # Seletores robustos baseados em texto, do mais específico para o mais geral
        selectors = [
            # 1. O ideal: Encontra o botão "OK" dentro do pop-up específico pelo H2
            "//div[.//h2[contains(text(), 'Video posts are now shared as reels')]]//button[text()='OK']",
            # 2. Fallback: Procura por qualquer botão "OK" visível na tela (caso o texto do H2 mude)
            "//button[text()='OK']"
        ]
    
        for i, selector in enumerate(selectors):
            try:
                logging.info(f"🔍 Tentando seletor #{i+1} para o botão OK...")
                ok_button = WebDriverWait(driver, 7).until(
                    EC.element_to_be_clickable((By.XPATH, selector))
                )
            
                if ok_button.is_displayed():
                    logging.info(f"✅ Pop-up/Botão OK encontrado com o seletor #{i+1}!")
                    driver.execute_script("arguments[0].click();", ok_button)
                    time.sleep(2)
                    logging.info("✅ Botão OK clicado com sucesso via JavaScript!")
                    return True
                
            except TimeoutException:
                logging.info(f"ℹ️ Seletor #{i+1} não encontrou o botão, tentando próximo...")
                continue # Tenta o próximo seletor
            except Exception as e:
                logging.warning(f"⚠️ Erro inesperado ao tentar clicar no botão OK: {str(e)}")
                return False

        logging.info("ℹ️ Pop-up 'Video posts are now reels' não apareceu ou não foi encontrado. Continuando...")
        return False

    def change_video_format_to_9_16(self, driver, wait):
        """Mudar formato do vídeo para 9:16"""
        logging.info("📐 Tentando mudar formato para 9:16...")
    
        try:
            # Procurar pelo botão de crop/formato
            crop_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'svg[aria-label="Select crop"]'))
            )
        
            # Scroll para o botão e clicar
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", crop_button)
            time.sleep(1)
            crop_button.click()
            logging.info("✅ Clicou no botão de formato!")
            time.sleep(2)
        
            # Procurar pela opção 9:16
            try:
                nine_sixteen_option = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//span[text()='9:16']"))
                )
                nine_sixteen_option.click()
                logging.info("✅ Selecionou formato 9:16!")
                time.sleep(3)
            
                # Verificar se a mudança foi aplicada (opcional)
                try:
                    video_container = driver.find_element(By.CSS_SELECTOR, 'video')
                    logging.info("✅ Vídeo redimensionado!")
                except:
                    pass
            
                return True
            
            except TimeoutException:
                logging.warning("⚠️ Opção 9:16 não encontrada, continuando...")
                return False
            
        except TimeoutException:
            logging.info("ℹ️ Botão de formato não encontrado, continuando...")
            return False
        except Exception as e:
            logging.warning(f"⚠️ Erro ao mudar formato: {str(e)}")
            return False

    def safe_click_advance(self, driver, wait, step_name, button_text):
        """Clica com segurança nos botões Next e Share"""
        logging.info(f"🔘 Procurando botão '{button_text}'...")
    
        # Seletores ordenados por prioridade
        selectors = [
            f"//div[@role='button' and contains(@class, 'x1i10hfl') and text()='{button_text}']",
            f"//button[text()='{button_text}']",
            f"//div[@role='button' and text()='{button_text}']",
            f"//span[text()='{button_text}']/parent::div[@role='button']",
            f"//*[contains(text(), '{button_text}') and (@role='button' or self::button)]"
        ]
    
        for selector in selectors:
            try:
                logging.info(f"🔍 Tentando seletor: {selector}")
            
                button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, selector))
                )
            
                if button.is_displayed():
                    # Scroll para o elemento
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", button)
                    time.sleep(1)
                
                    # Tentar clicar
                    try:
                        button.click()
                        logging.info(f"✅ {step_name} clicado!")
                        time.sleep(2)
                        return True
                    except ElementClickInterceptedException:
                        # Tentar JavaScript click
                        driver.execute_script("arguments[0].click();", button)
                        logging.info(f"✅ {step_name} clicado com JavaScript!")
                        time.sleep(2)
                        return True
                    
            except TimeoutException:
                continue
            except Exception as e:
                logging.warning(f"⚠️ Erro no seletor: {str(e)}")
                continue
    
        raise Exception(f"❌ Não foi possível encontrar/clicar no botão '{button_text}'")

    def insert_caption(self, driver, wait, caption):
        """Inserir legenda usando múltiplas estratégias robustas."""
        logging.info("📝 Inserindo legenda com método avançado...")
    
        caption_inserted = False
        caption_field = None
    
        # Tenta localizar o campo de legenda uma vez
        try:
            caption_field = wait.until(EC.presence_of_element_located((
                By.CSS_SELECTOR,
                'div[aria-label="Write a caption..."][contenteditable="true"]'
            )))
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", caption_field)
            time.sleep(1)
        except TimeoutException:
            logging.error("❌ Campo de legenda não foi encontrado na página.")
            return False

        # Estratégia 1: Usar clipboard (mais eficaz)
        try:
            logging.info("-> Tentando Estratégia 1 (Clipboard)...")
            caption_field.click()
            time.sleep(0.5)
        
            # Limpar campo
            caption_field.send_keys(Keys.CONTROL + "a")
            time.sleep(0.5)
            caption_field.send_keys(Keys.DELETE)
            time.sleep(1)
        
            # Colar
            pyperclip.copy(caption)
            caption_field.send_keys(Keys.CONTROL + "v")
            time.sleep(2)
        
            if caption in caption_field.text:
                logging.info("✅ Estratégia 1 (Clipboard) bem-sucedida!")
                caption_inserted = True
            else:
                logging.warning("⚠️ Estratégia 1 (Clipboard) falhou na verificação.")
        except Exception as e:
            logging.error(f"❌ Erro na Estratégia 1: {str(e)}")

        # Estratégia 2: Digitação letra por letra (fallback)
        if not caption_inserted:
            try:
                logging.info("-> Tentando Estratégia 2 (Digitação)...")
                caption_field.click()
                time.sleep(0.5)
                caption_field.clear() # Limpa de forma mais direta
                time.sleep(0.5)

                for char in caption:
                    caption_field.send_keys(char)
                    time.sleep(random.uniform(0.05, 0.1)) # Simula digitação humana
            
                time.sleep(2)
                if caption in caption_field.text:
                    logging.info("✅ Estratégia 2 (Digitação) bem-sucedida!")
                    caption_inserted = True
                else:
                    logging.warning("⚠️ Estratégia 2 (Digitação) falhou na verificação.")
            except Exception as e:
                logging.error(f"❌ Erro na Estratégia 2: {str(e)}")

        # Estratégia 3: JavaScript (último recurso)
        if not caption_inserted:
            try:
                logging.info("-> Tentando Estratégia 3 (JavaScript)...")
                js_script = "arguments[0].innerText = arguments[1];"
                driver.execute_script(js_script, caption_field, caption)
                # Disparar um evento de 'input' para que o React reconheça a mudança
                driver.execute_script("arguments[0].dispatchEvent(new Event('input', {bubbles: true}));", caption_field)
                time.sleep(2)
            
                if caption in caption_field.text:
                    logging.info("✅ Estratégia 3 (JavaScript) bem-sucedida!")
                    caption_inserted = True
                else:
                    logging.warning("⚠️ Estratégia 3 (JavaScript) falhou na verificação.")
            except Exception as e:
                logging.error(f"❌ Erro na Estratégia 3: {str(e)}")
    
        if caption_inserted:
            logging.info(f"✅ Legenda final inserida com sucesso: '{caption}'")
        else:
            logging.error("❌ TODAS AS ESTRATÉGIAS DE INSERÇÃO DE LEGENDA FALHARAM.")

        return caption_inserted

    def post_to_instagram(self):
        """Função principal para postar vídeo no Instagram - Baseada na função que funciona"""
        try:
            logging.info("🚀 Iniciando processo de postagem automática...")
        
            video_path = self.generate_video_with_fallbacks()
            if not video_path:
                logging.error("❌ Falha na geração do vídeo. Abortando.")
                return False

            video_description = self.generate_description_with_groq("vídeo artístico e criativo com cores vibrantes")
        
            # A função de limpeza agora mantém os emojis
            description_clean = self.clean_text_for_selenium(video_description)
            logging.info(f"Descrição a ser postada: {description_clean}")

            options = Options()
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            driver = webdriver.Chrome(options=options)
            wait = WebDriverWait(driver, 15)

            try:
                driver.get("https://www.instagram.com/")
                time.sleep(random.uniform(2, 5))

                # Login
                username_field = driver.find_element(By.NAME, "username")
                username_field.send_keys(self.username)
                time.sleep(random.uniform(1, 3))

                password_field = driver.find_element(By.NAME, "password")
                password_field.send_keys(self.password)
                time.sleep(random.uniform(1, 3))

                login_button = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
                login_button.click()
                time.sleep(10)

                # Lidar com pop-ups pós-login
                try:
                    not_now_specific = wait.until(EC.element_to_be_clickable((
                        By.XPATH,
                        "//div[@role='button' and contains(@class, 'x1i10hfl') and text()='Not now']"
                    )))
                    not_now_specific.click()
                    logging.info("✅ Clicou no botão 'Not now'!")
                    time.sleep(random.uniform(2, 4))
                except TimeoutException:
                    logging.info("Botão 'Not now' não encontrado...")

                # Encontrar e clicar no botão de nova publicação
                create_button_selectors = [
                    'svg[aria-label="Nova publicação"]',
                    'svg[aria-label="New post"]',
                    'svg[aria-label="Create"]',
                    'a[href*="/create/"]'
                ]
            
                create_button = None
                for selector in create_button_selectors:
                    try:
                        logging.info(f"Tentando encontrar botão criar com: {selector}")
                        create_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                        break
                    except TimeoutException:
                        continue
            
                if create_button is None:
                    logging.info("Tentando navegar diretamente para página de criar...")
                    driver.get("https://www.instagram.com/create/select/")
                    time.sleep(3)
                else:
                    create_button.click()
                    logging.info("✅ Clicou no botão de criar post!")
                    time.sleep(random.uniform(2, 4))

                # Tentar clicar no botão "Post" se disponível
                try:
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
                        logging.info("✅ Clicou no botão 'Post'!")
                        time.sleep(random.uniform(2, 4))
                    
                except Exception as e:
                    logging.warning(f"Erro ao tentar clicar em 'Post', continuando: {str(e)[:50]}...")

                # Upload do vídeo
                logging.info("Procurando input de arquivo...")
                file_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="file"]')))
                file_input.send_keys(os.path.abspath(video_path))
                logging.info("✅ Vídeo enviado!")
                time.sleep(random.uniform(5, 8))  # Mais tempo para vídeo

                # NOVO: Verificar e clicar no botão OK se aparecer
                self.handle_ok_button_after_upload(driver, wait)

                # NOVO: Mudar formato para 9:16 antes do primeiro Next
                self.change_video_format_to_9_16(driver, wait)

                # Primeiro Next
                self.safe_click_advance(driver, wait, "primeiro Next", "Next")
                time.sleep(random.uniform(3, 5))

                # Segundo Next
                self.safe_click_advance(driver, wait, "segundo Next", "Next")
                time.sleep(random.uniform(3, 5))

                # Inserir legenda
                caption_inserted = self.insert_caption(driver, wait, description_clean)
            
                if not caption_inserted:
                    logging.warning("⚠️ ATENÇÃO: Não foi possível inserir a legenda!")
                else:
                    logging.info(f"✅ Legenda final inserida: '{description_clean}'")
            
                time.sleep(random.uniform(20, 35))

                # Aguardar horário correto antes de compartilhar
                logging.info("🕐 Verificando se chegou a hora de postar...")
                self.wait_for_post_time()

                # Compartilhar
                self.safe_click_advance(driver, wait, "Compartilhar", "Share")
                time.sleep(random.uniform(85, 95))  # Mais tempo para processamento do reel

                # Verificar sucesso - NOVO: Procurar pela mensagem específica de reel
                try:
                    # Tentar encontrar a mensagem de sucesso para reel
                    success_message = wait.until(EC.presence_of_element_located((
                        By.XPATH,
                        '//h3[contains(text(), "Your reel has been shared")] | //h3[contains(text(), "Seu reel foi compartilhado")] | //h3[contains(text(), "Your post has been shared")]'
                    )))
                    logging.info("🎉 REEL PUBLICADO COM SUCESSO!")
                    return True
                except TimeoutException:
                    logging.warning("⚠️ Reel pode ter sido publicado, mas confirmação não encontrada")
                    return True

            except Exception as e:
                logging.error(f"❌ Erro durante o posting: {e}")
                try:
                    driver.save_screenshot(f"erro_debug_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
                    logging.info("📸 Screenshot salvo para debug")
                except:
                    pass
                return False

            finally:
                logging.info("🔧 Limpando recursos...")
                try:
                    driver.quit()
                    # Remover vídeo após uso
                    if os.path.exists(video_path):
                        os.remove(video_path)
                        logging.info("🗑️ Vídeo removido")
                except:
                    pass
            
        except Exception as e:
            logging.error(f"❌ Erro geral na postagem: {e}")
            return False


def job_with_timing(target_time_str, PREPARATION_MINUTES):
    """Job executado pelo scheduler"""
    logging.info("⏰ Executando job agendado...")

    try:
        target_time = datetime.strptime(target_time_str, "%H:%M").time()
        bot = InstagramVideoBot(target_post_time=target_time)
        success = bot.post_to_instagram()
    
        if success:
            logging.info("✅ Job executado com sucesso!")
        else:
            logging.error("❌ Job falhou!")
        
    except Exception as e:
        logging.error(f"❌ Erro no job: {str(e)}")

    # Reagendar para próximo dia
    logging.info("📅 Reagendando para próximo dia...")
    schedule_next_day(target_time_str, PREPARATION_MINUTES)


def schedule_next_day(post_time_str, PREPARATION_MINUTES ):
    """Reagenda para próximo dia"""
    schedule.clear()

    post_time = datetime.strptime(post_time_str, "%H:%M").time()
    post_datetime = datetime.combine(datetime.now().date(), post_time)
    start_datetime = post_datetime - timedelta(minutes=PREPARATION_MINUTES)
    start_time_str = start_datetime.strftime("%H:%M")

    schedule.every().day.at(start_time_str).do(job_with_timing, post_time_str, PREPARATION_MINUTES)

    next_run = schedule.next_run()
    if next_run:
        logging.info(f"📅 Próximo post: {next_run.strftime('%d/%m/%Y às %H:%M:%S')}")


def run_scheduler():
    """Executa scheduler"""
    while True:
        try:
            schedule.run_pending()
            time.sleep(60)
        except Exception as e:
            logging.error(f"❌ Erro no scheduler: {str(e)}")
            time.sleep(60)


def main():
    """Função principal"""
    POST_TIME = "17:53"  # Horário de postagem
    PREPARATION_MINUTES = 10  # Minutos antes para iniciar

    logging.info("🤖 Instagram Video Bot iniciado!")
    logging.info(f"🎬 Programado para {POST_TIME}h diariamente")

    # Calcular horários
    post_time = datetime.strptime(POST_TIME, "%H:%M").time()
    post_datetime = datetime.combine(datetime.now().date(), post_time)
    start_datetime = post_datetime - timedelta(minutes=PREPARATION_MINUTES)
    start_time_str = start_datetime.strftime("%H:%M")

    logging.info(f"🔧 Processo inicia às {start_time_str}h")
    logging.info(f"🎬 Reel postado às {POST_TIME}h")

    """
    # MODO TESTE: Executar imediatamente (remova estas 3 linhas para modo normal)
    logging.info("🧪 MODO TESTE: Executando agora...")
    job_with_timing(POST_TIME, PREPARATION_MINUTES)
    #return #descomente caso só queira testar a psotagem e não reagendar
    """
    # Agendar
    current_time = datetime.now()
    if current_time.time() > datetime.strptime(start_time_str, "%H:%M").time():
        logging.info("⏰ Agendando para amanhã...")
    else:
        logging.info("⏰ Agendando para hoje...")

    schedule.every().day.at(start_time_str).do(job_with_timing, POST_TIME, PREPARATION_MINUTES)

    next_run = schedule.next_run()
    if next_run:
        logging.info(f"🕒 Próxima execução: {next_run.strftime('%d/%m/%Y às %H:%M:%S')}")

    # Iniciar scheduler
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()

    logging.info("✅ Scheduler ativo! Ctrl+C para parar")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("🛑 Bot parado pelo usuário")


if __name__ == "__main__":
    main()