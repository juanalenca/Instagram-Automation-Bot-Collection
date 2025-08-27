# Coleção de Bots de Automação do Instagram

Uma coleção de scripts Python para automação de postagens no Instagram, apresentando três versões progressivamente aprimoradas com diferentes capacidades de geração de conteúdo.

## Visão Geral

Este repositório contém três estágios evolutivos de um bot de automação do Instagram:

1. **v1-image-generator.py** - Geração básica de imagens e postagem
2. **v2-video-creator.py** - Criação avançada de vídeos com múltiplos fallbacks
3. **v3-local-media.py** - Conversor de imagem local para vídeo com foco em promoção de ebook

## Funcionalidades

### Funcionalidades Comuns (Todas as Versões)
- **Login Automático no Instagram** - Tratamento seguro de credenciais
- **Agendamento Inteligente de Posts** - Direcionamento para horários específicos de postagem
- **Detecção Robusta de Elementos** - Múltiplos seletores de fallback para mudanças na interface
- **Geração de Legendas** - Descrições com IA usando API Groq
- **Tratamento de Erros** - Log abrangente e captura de screenshots
- **Gerenciamento de Pop-ups** - Tratamento automático de diálogos do Instagram

### Funcionalidades Específicas por Versão

#### v1 - Gerador de Imagens
- Geração de imagens com IA usando API Pollinations
- Automação básica de postagem no Instagram
- Limpeza de texto para caracteres especiais
- Geração aleatória de prompts criativos

#### v2 - Criador de Vídeos
- **Múltiplos Métodos de Geração de Vídeo:**
  - Integração com API RunwayML/Replicate
  - Animações aprimoradas com OpenCV
  - Vídeos simples com MoviePy
  - Fallback com Pillow + FFmpeg
- Duração de 45 segundos otimizada para Instagram Reels
- Efeitos de animação avançados (partículas, ondas, texto dinâmico)
- Conversão automática para proporção 9:16

#### v3 - Mídia Local (Promoção de Ebook)
- **Processamento de Imagens Locais** - Converte imagens da pasta `imgs/` para vídeos
- **Foco em Marketing de Ebook** - Prompts especializados para "100 Maneiras de Ganhar Dinheiro"
- **Geração Simples de Vídeo** - Conversão de imagem estática para MP4
- **Conteúdo Promocional** - Legendas e descrições focadas em desconto

## Instalação

### Pré-requisitos
```bash
# Dependências principais
pip install selenium opencv-python requests pyperclip schedule

# Opcionais para recursos avançados
pip install moviepy pillow

# ChromeDriver necessário (garantir que o ChromeDriver esteja no PATH)
```

### Configuração
1. Clone o repositório
```bash
git clone <url-do-repositorio>
cd instagram-automation-bot
```

2. Instale as dependências
```bash
pip install -r requirements.txt
```

3. Configure as credenciais no script:
```python
self.username = 'seu_usuario'
self.password = 'sua_senha'
self.groq_api_key = 'sua_chave_groq_api'
```

## Como Usar

### Início Rápido
```bash
# Executar v1 - Gerador de Imagens
python v1-image-generator.py

# Executar v2 - Criador de Vídeos  
python v2-video-creator.py

# Executar v3 - Mídia Local (requer imagens na pasta imgs/)
python v3-local-media.py
```

### Configuração de Agendamento
Modifique o horário de postagem na função principal:
```python
POST_TIME = "17:50"  # Formato 24 horas
PREPARATION_MINUTES = 10  # Iniciar processo X minutos antes
```

### Modo de Teste
Descomente as linhas do modo de teste para executar imediatamente:
```python
logging.info("🧪 MODO TESTE: Executando agora...")
job_with_timing(POST_TIME, PREPARATION_MINUTES)
return
```

## Estrutura de Arquivos

```
instagram-automation-bot/
├── v1-image-generator.py      # Bot básico de geração de imagens
├── v2-video-creator.py        # Bot avançado de criação de vídeos  
├── v3-local-media.py          # Bot de processamento de imagens locais
├── imgs/                      # Pasta de imagens locais (para v3)
├── videos/                    # Saída de vídeos gerados
├── generated_videos/          # Saída alternativa de vídeos (v3)
├── temp_frames/              # Armazenamento temporário de frames
├── requirements.txt          # Dependências Python
└── README.md                # Este arquivo
```

## Configuração

### Chaves de API Necessárias
- **API Groq** - Para geração de legendas (todas as versões)
- **API Replicate** - Para geração avançada de vídeos (apenas v2)
- **API Pollinations** - Para geração de imagens (apenas v1)

### Configuração do Instagram
- Certifique-se de que a 2FA esteja desabilitada ou adequadamente tratada
- Use senhas específicas de aplicação se disponível
- Teste o login manualmente antes da automação

## Detalhes Técnicos

### Especificações de Vídeo
- **Resolução**: 720x1280 (proporção 9:16)
- **Duração**: 5-45 segundos (dependendo da versão)
- **Formato**: MP4 com codificação H.264
- **Taxa de Quadros**: 24-30 FPS

### Configuração do Selenium
- Chrome WebDriver com opções headless disponíveis
- Espera robusta de elementos e recuperação de erros
- Captura de screenshots para depuração de falhas
- Múltiplas estratégias de seletores para mudanças na interface

### Geração de Legendas
- Alimentado por IA usando modelo Llama do Groq
- Fallback para templates predefinidos
- Integração de emojis e hashtags
- Otimização de limite de caracteres para Instagram

## Solução de Problemas

### Problemas Comuns
1. **Falhas de Login**
   - Verifique as credenciais
   - Verifique desafios de segurança do Instagram
   - Desabilite temporariamente a 2FA

2. **Erros de Elemento Não Encontrado**
   - A interface do Instagram muda frequentemente
   - Verifique os logs para seletores específicos
   - Atualize os seletores conforme necessário

3. **Falhas na Geração de Vídeo**
   - Certifique-se de que todas as dependências estão instaladas
   - Verifique o espaço em disco para arquivos temporários
   - Verifique a instalação do FFmpeg (para v2/v3)

4. **Problemas de Inserção de Legenda**
   - Múltiplas estratégias implementadas
   - Verifique a funcionalidade da área de transferência
   - Verifique a codificação do texto

### Modo de Depuração
Habilite log detalhado:
```python
logging.basicConfig(level=logging.DEBUG)
```

## Aviso Legal

**Considerações Legais e Éticas Importantes:**

- Esta ferramenta é apenas para fins educacionais e uso pessoal
- Respeite os Termos de Serviço do Instagram e limites de taxa da API
- Não use para spam ou fins comerciais não autorizados
- Sempre cumpra as leis e regulamentações locais sobre automação
- Os autores não são responsáveis por qualquer uso indevido ou penalidades na conta

### Conformidade com Políticas do Instagram
- Implemente atrasos razoáveis entre ações
- Evite frequência excessiva de postagem
- Use padrões de interação semelhantes aos humanos
- Monitore a saúde da conta e métricas de engajamento

## Linha do Tempo da Evolução

**v1 → v2**: Capacidades aprimoradas de geração de vídeo, múltiplos sistemas de fallback, animações avançadas

**v2 → v3**: Simplificado para processamento de mídia local, especializado em marketing de ebook, criação de vídeo simplificada

## Contribuindo

1. Faça um fork do repositório
2. Crie uma branch de feature
3. Implemente melhorias com tratamento adequado de erros
4. Adicione log abrangente
5. Teste minuciosamente com a interface atual do Instagram
6. Envie um pull request com descrição detalhada

## Licença

Este projeto é fornecido como está para fins educacionais. Os usuários são responsáveis por garantir a conformidade com todos os termos de serviço e leis aplicáveis.

---

**Dica Rápida**: Comece com v3 se você tem imagens locais para promover, use v2 para conteúdo de vídeo avançado, ou v1 para automação básica de postagem de imagens.
