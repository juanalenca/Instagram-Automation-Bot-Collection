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

class InstagramVideoBot:
    def __init__(self, target_post_time=None):
        # CONFIGURAÇÕES DIRETAS
        self.username = 'xxxxxx'
        self.password = 'xxxxxx'
        self.target_post_time = target_post_time
        
        # API Keys - DEFINIDAS DIRETAMENTE
        self.replicate_api_key = None  # Desabilitado por enquanto
        self.groq_api_key = 'xxxxxx'
        
        # Verificar configurações
        logging.info(f"✅ Username configurado: {self.username}")
        logging.info(f"✅ Password configurado: {'*' * len(self.password)}")
        logging.info(f"✅ GROQ_API_KEY configurada: {self.groq_api_key[:8]}...")

    def clean_text_for_selenium(self, text):
        """Remove ou substitui caracteres que podem causar problemas no Selenium, mantendo emojis."""
        # Remover caracteres de controle
        text = ''.join(char for char in text if unicodedata.category(char) != 'Cc')
        
        # 🛠️ MUDANÇA: Remoção da substituição de emojis. Agora eles são mantidos.
        # O novo método de inserção de legenda lida bem com emojis.
        
        # Remover qualquer caractere fora do BMP (Basic Multilingual Plane) - opcional, mas seguro
        text = ''.join(char for char in text if ord(char) <= 0xFFFF)
        
        # Remover caracteres especiais problemáticos, mas mantendo os básicos para legendas
        # Esta regex foi ajustada para ser menos agressiva
        text = re.sub(r'[^\w\s.,!?@#\-_()+=<>:;"\'/\\]', '', text)
        
        return text.strip()

    def create_video_with_runwayml(self):
        """Cria vídeo usando API RunwayML"""
        try:
            logging.info("🎬 Criando vídeo com RunwayML...")
            
            # Prompts criativos para vídeo
            video_prompts = [
                "Abstract flowing liquid colors in motion, vibrant neon colors, smooth transitions, vertical format 9:16, modern aesthetic",
                "Geometric shapes morphing and flowing, bright colors, dynamic movement, vertical video format, contemporary design",
                "Particle systems creating beautiful patterns, colorful explosions of light, smooth animations, portrait orientation",
                "Fluid art in motion, rainbow colors mixing and flowing, mesmerizing patterns, vertical format for social media",
                "Digital wave patterns, electric blue and purple colors, smooth flowing motion, modern abstract art style"
            ]
            
            selected_prompt = random.choice(video_prompts)
            
            # Usar API Replicate (gratuita para vídeos simples)
            url = "https://api.replicate.com/v1/predictions"
            headers = {
                "Authorization": f"Token {self.replicate_api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "version": "anotherjesse/zeroscope-v2-xl:9f747673945c62801b13b84701c783929c0ee784e4748ec062204894dda1a351",
                "input": {
                    "prompt": selected_prompt,
                    "width": 576,
                    "height": 1024,
                    "num_frames": 120,  # ~4 segundos a 30fps
                    "num_inference_steps": 20
                }
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 201:
                prediction = response.json()
                prediction_id = prediction['id']
                
                logging.info(f"✅ Vídeo iniciado! ID: {prediction_id}")
                return self.wait_for_replicate_video(prediction_id)
            else:
                logging.warning(f"⚠️ RunwayML/Replicate falhou: {response.status_code}")
                return None
                
        except Exception as e:
            logging.error(f"❌ Erro na API RunwayML/Replicate: {str(e)}")
            return None

    def wait_for_replicate_video(self, prediction_id):
        """Aguarda processamento do vídeo Replicate"""
        logging.info("⏳ Aguardando processamento Replicate...")
        
        max_attempts = 20
        for attempt in range(max_attempts):
            try:
                url = f"https://api.replicate.com/v1/predictions/{prediction_id}"
                headers = {"Authorization": f"Token {self.replicate_api_key}"}
                
                response = requests.get(url, headers=headers, timeout=15)
                
                if response.status_code == 200:
                    data = response.json()
                    status = data.get('status', 'unknown')
                    
                    if status == 'succeeded':
                        video_url = data.get('output')
                        if video_url:
                            return self.download_video(video_url)
                    elif status == 'failed':
                        logging.error("❌ Replicate falhou no processamento")
                        break
                    else:
                        logging.info(f"⏳ Status: {status}...")
                
                time.sleep(15)
                
            except Exception as e:
                logging.warning(f"⚠️ Erro ao verificar status: {str(e)}")
                time.sleep(15)
        
        logging.warning("⚠️ Timeout no Replicate, usando fallback...")
        return None

    def create_enhanced_video_with_opencv(self):
        """Cria vídeo mais elaborado usando OpenCV"""
        try:
            import cv2
            import numpy as np
            
            logging.info("🎬 Criando vídeo aprimorado com OpenCV...")
            os.makedirs('videos', exist_ok=True)
            
            # Configurações do vídeo (9:16 format) - 45 segundos
            width, height = 720, 1280
            fps = 30
            duration = 45  # 45 segundos
            total_frames = fps * duration
            
            video_path = 'videos/enhanced_opencv_video.mp4'
            fourcc = cv2.VideoWriter_fourcc(*'avc1')
            out = cv2.VideoWriter(video_path, fourcc, fps, (width, height))
            
            # Cores vibrantes
            color_palettes = [
                [(255, 100, 150), (100, 255, 200), (200, 150, 255)],  # Rosa, Verde, Roxo
                [(255, 150, 100), (100, 200, 255), (255, 255, 100)],  # Laranja, Azul, Amarelo
                [(200, 100, 255), (100, 255, 150), (255, 200, 100)],  # Roxo, Verde, Pêssego
            ]
            
            for frame_num in range(total_frames):
                progress = frame_num / total_frames
                
                # Mudar paleta de cores periodicamente
                palette_index = int(progress * 3) % len(color_palettes)
                current_palette = color_palettes[palette_index]
                
                # Criar frame base
                frame = np.zeros((height, width, 3), dtype=np.uint8)
                
                # Gradiente dinâmico
                for y in range(height):
                    color_progress = (y / height + progress) % 1.0
                    color_index = int(color_progress * len(current_palette))
                    next_color_index = (color_index + 1) % len(current_palette)
                    
                    blend_factor = (color_progress * len(current_palette)) % 1.0
                    
                    color1 = np.array(current_palette[color_index])
                    color2 = np.array(current_palette[next_color_index])
                    blended_color = color1 * (1 - blend_factor) + color2 * blend_factor
                    
                    frame[y, :] = blended_color.astype(np.uint8)
                
                # Adicionar múltiplos elementos animados
                num_circles = 5
                for i in range(num_circles):
                    # Círculos com movimento orbital
                    angle = (frame_num * 0.05 + i * (2 * np.pi / num_circles))
                    center_x = int(width/2 + (150 + i*20) * np.cos(angle))
                    center_y = int(height/2 + (100 + i*15) * np.sin(angle))
                    radius = int(30 + 20 * np.sin(frame_num * 0.08 + i))
                    
                    # Cores dinâmicas para círculos
                    circle_color = current_palette[i % len(current_palette)]
                    
                    cv2.circle(frame, (center_x, center_y), radius, (255, 255, 255), 3)
                    cv2.circle(frame, (center_x, center_y), radius-8, circle_color, -1)
                
                # Adicionar ondas
                wave_amplitude = 50
                wave_frequency = 0.02
                for x in range(0, width, 10):
                    wave_y = int(height/2 + wave_amplitude * np.sin(x * wave_frequency + frame_num * 0.1))
                    cv2.circle(frame, (x, wave_y), 8, (255, 255, 255), -1)
                
                # Adicionar partículas em movimento
                num_particles = 15
                for p in range(num_particles):
                    particle_x = int((frame_num * 3 + p * 50) % (width + 100))
                    particle_y = int(height * 0.3 + 200 * np.sin((frame_num + p * 20) * 0.05))
                    particle_size = abs(int(3 + 5 * np.sin(frame_num * 0.1 + p)))
                    
                    if 0 <= particle_x < width and 0 <= particle_y < height:
                        cv2.circle(frame, (particle_x, particle_y), particle_size, (255, 255, 255), -1)
                
                # Adicionar texto dinâmico
                texts = ['CREATIVE', 'VIRAL', 'AMAZING', 'TRENDING', 'ARTISTIC']
                if frame_num % 180 == 0:  # Mudar texto a cada 6 segundos
                    current_text_index = (frame_num // 180) % len(texts)
                else:
                    current_text_index = (frame_num // 180) % len(texts)
                
                text = texts[current_text_index]
                font = cv2.FONT_HERSHEY_SIMPLEX
                text_size = cv2.getTextSize(text, font, 2, 3)[0]
                text_x = (width - text_size[0]) // 2
                text_y = int(height * 0.8)
                
                # Texto com efeito pulsante
                pulse = 1 + 0.3 * np.sin(frame_num * 0.2)
                scaled_font_size = 2 * pulse
                
                cv2.putText(frame, text, (text_x, text_y), font, scaled_font_size, (0, 0, 0), 6)
                cv2.putText(frame, text, (text_x, text_y), font, scaled_font_size, (255, 255, 255), 3)
                
                out.write(frame)
                
                # Log de progresso
                if frame_num % (fps * 5) == 0:
                    seconds_done = frame_num // fps
                    logging.info(f"⏳ Criando vídeo: {seconds_done}s/{duration}s")
            
            out.release()
            cv2.destroyAllWindows()
            
            logging.info(f"✅ Vídeo aprimorado criado: {video_path}")
            return video_path
            
        except ImportError:
            logging.warning("⚠️ OpenCV não instalado")
            return None
        except Exception as e:
            logging.error(f"❌ Erro com OpenCV: {str(e)}")
            return None

    def create_simple_fallback_video(self):
        """Cria vídeo simples como último recurso usando MoviePy"""
        try:
            from moviepy.editor import ColorClip, TextClip, CompositeVideoClip, concatenate_videoclips
            
            logging.info("🎬 Criando vídeo simples com MoviePy...")
            os.makedirs('videos', exist_ok=True)
            
            # Configurações do vídeo (9:16 format)
            width, height = 720, 1280
            duration = 45
            
            # Cores vibrantes
            colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FECA57', '#FF9FF3', '#54A0FF']
            selected_colors = random.sample(colors, 5)
            
            clips = []
            segment_duration = duration / len(selected_colors)
            
            for i, color in enumerate(selected_colors):
                # Criar clip colorido
                color_clip = ColorClip(size=(width, height), color=color, duration=segment_duration)
                
                # Adicionar texto dinâmico
                texts = ['CREATIVE', 'VIRAL', 'AMAZING', 'TRENDING', 'ARTISTIC']
                text = TextClip(texts[i % len(texts)], 
                               fontsize=80, color='white', font='Arial-Bold')
                text = text.set_position('center').set_duration(segment_duration)
                
                # Compor clip
                final_clip = CompositeVideoClip([color_clip, text])
                clips.append(final_clip)
            
            # Concatenar todos os clips
            final_video = concatenate_videoclips(clips, method="compose")
            
            video_path = 'videos/simple_moviepy_video.mp4'
            final_video.write_videofile(video_path, fps=24, codec='libx264', audio_codec='aac', verbose=False, logger=None)
            
            logging.info(f"✅ Vídeo simples criado: {video_path}")
            return video_path
            
        except ImportError:
            logging.warning("⚠️ MoviePy não instalado")
            return None
        except Exception as e:
            logging.error(f"❌ Erro com MoviePy: {str(e)}")
            return None

    def create_basic_video_with_pillow(self):
        """Cria vídeo básico usando Pillow + ffmpeg"""
        try:
            from PIL import Image, ImageDraw, ImageFont
            import subprocess
            
            logging.info("🎬 Criando vídeo básico com Pillow...")
            os.makedirs('videos', exist_ok=True)
            os.makedirs('temp_frames', exist_ok=True)
            
            width, height = 720, 1280
            fps = 24
            duration = 45
            total_frames = fps * duration
            
            # Cores
            colors = [
                (255, 100, 150), (100, 255, 200), (200, 150, 255),
                (255, 150, 100), (100, 200, 255), (255, 255, 100)
            ]
            
            texts = ['CREATIVE', 'VIRAL', 'AMAZING', 'TRENDING', 'ARTISTIC']
            
            for frame_num in range(total_frames):
                # Criar imagem
                img = Image.new('RGB', (width, height), colors[frame_num % len(colors)])
                draw = ImageDraw.Draw(img)
                
                # Adicionar texto
                text = texts[(frame_num // (fps * 9)) % len(texts)]
                
                try:
                    # Tentar fonte do sistema
                    font = ImageFont.truetype("arial.ttf", 60)
                except:
                    # Fonte padrão
                    font = ImageFont.load_default()
                
                # Posição do texto
                bbox = draw.textbbox((0, 0), text, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                text_x = (width - text_width) // 2
                text_y = (height - text_height) // 2
                
                # Desenhar texto com contorno
                for dx, dy in [(-2, -2), (-2, 2), (2, -2), (2, 2)]:
                    draw.text((text_x + dx, text_y + dy), text, font=font, fill=(0, 0, 0))
                draw.text((text_x, text_y), text, font=font, fill=(255, 255, 255))
                
                # Salvar frame
                img.save(f'temp_frames/frame_{frame_num:06d}.png')
                
                if frame_num % (fps * 5) == 0:
                    logging.info(f"⏳ Gerando frames: {frame_num // fps}s/{duration}s")
            
            # Criar vídeo com ffmpeg
            video_path = 'videos/pillow_video.mp4'
            cmd = [
                'ffmpeg', '-y', '-r', str(fps),
                '-i', 'temp_frames/frame_%06d.png',
                '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
                video_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # Limpar frames temporários
            import shutil
            shutil.rmtree('temp_frames', ignore_errors=True)
            
            if result.returncode == 0:
                logging.info(f"✅ Vídeo básico criado: {video_path}")
                return video_path
            else:
                logging.error(f"❌ Erro no ffmpeg: {result.stderr}")
                return None
                
        except Exception as e:
            logging.error(f"❌ Erro com Pillow: {str(e)}")
            return None
    def generate_video_with_fallbacks(self):
        """Gera vídeo com múltiplos fallbacks"""
        logging.info("🎬 Iniciando geração de vídeo...")
        
        # Tentar RunwayML/Replicate primeiro (se API key válida)
        if self.replicate_api_key and self.replicate_api_key != 'r8_YOUR_REPLICATE_TOKEN':
            video_path = self.create_video_with_runwayml()
            if video_path and os.path.exists(video_path):
                return video_path
        
        # Fallback 1: OpenCV aprimorado
        video_path = self.create_enhanced_video_with_opencv()
        if video_path and os.path.exists(video_path):
            return video_path
        
        # Fallback 2: MoviePy simples
        video_path = self.create_simple_fallback_video()
        if video_path and os.path.exists(video_path):
            return video_path
        
        # Fallback 3: Pillow + ffmpeg
        video_path = self.create_basic_video_with_pillow()
        if video_path and os.path.exists(video_path):
            return video_path
        
        logging.error("❌ Todas as opções de geração de vídeo falharam")
        return None

    def download_video(self, video_url):
        """Baixa vídeo da URL"""
        try:
            logging.info("📥 Baixando vídeo...")
            response = requests.get(video_url, timeout=120)
            
            if response.status_code == 200:
                os.makedirs('videos', exist_ok=True)
                video_path = f'videos/downloaded_video_{datetime.now().strftime("%Y%m%d_%H%M%S")}.mp4'
                
                with open(video_path, 'wb') as f:
                    f.write(response.content)
                
                logging.info(f"✅ Vídeo baixado: {video_path}")
                return video_path
                
        except Exception as e:
            logging.error(f"❌ Erro no download: {str(e)}")
        
        return None

    def generate_description_with_groq(self, video_prompt):
        """Gera descrição usando API Groq"""
        logging.info("📝 Gerando descrição com Groq...")
        
        fallback_descriptions = [
            "Conteúdo incrível esperando por você! #VideoArt #Creative #Instagram #Viral",
            "Arte em movimento que hipnotiza! #ArtisticVideo #VisualArt #CreativeContent", 
            "Quando a criatividade encontra a tecnologia! #Innovation #DigitalArt #Amazing",
            "Vídeo que desperta emoções! #EmotionalContent #ArtLovers #InstagramReel",
            "Magia visual em cada frame! #MagicMoments #VisualMagic #ContentCreator"
        ]
        
        try:
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.groq_api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "llama3-8b-8192",
                "messages": [
                    {
                        "role": "system",
                        "content": "Você é um criador de conteúdo especialista em Instagram Reels. Crie descrições curtas, envolventes e criativas para reels."
                    },
                    {
                        "role": "user",
                        "content": f"Crie uma descrição curta e envolvente para Instagram Reel (máximo 150 caracteres) para um vídeo que mostra: {video_prompt}. Inclua hashtags relevantes e emojis adequados."
                    }
                ],
                "max_tokens": 200,
                "temperature": 0.8
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
                time.sleep(random.uniform(90, 100))  # Mais tempo para processamento do reel
                #wait_long = WebDriverWait(driver, 90)

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

def job_with_timing(target_time_str, preparation_minutes):
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
    schedule_next_day(target_time_str, preparation_minutes)

def schedule_next_day(post_time_str, preparation_minutes):
    """Reagenda para próximo dia"""
    schedule.clear()
    
    post_time = datetime.strptime(post_time_str, "%H:%M").time()
    post_datetime = datetime.combine(datetime.now().date(), post_time)
    start_datetime = post_datetime - timedelta(minutes=preparation_minutes)
    start_time_str = start_datetime.strftime("%H:%M")
    
    schedule.every().day.at(start_time_str).do(job_with_timing, post_time_str, preparation_minutes)
    
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
    POST_TIME = "17:50"  # Horário de postagem
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
    
    # MODO TESTE: Executar imediatamente (remova estas 3 linhas para modo normal)
    logging.info("🧪 MODO TESTE: Executando agora...")
    job_with_timing(POST_TIME, PREPARATION_MINUTES)
    return
    
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