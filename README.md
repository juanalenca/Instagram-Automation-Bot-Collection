# Instagram Automation Bot Collection 🤖📸

Um conjunto robusto de ferramentas escritas em Python desenvolvidas para automatizar a criação algorítmica de mídia por IA, upload e postagem no Instagram de forma autônoma (Headless / Selenium).

Este repositório visa aumentar a escala de geração e publicações orgânicas reduzindo o atrito de postagem manual diária, construindo uma linha de montagem programática e utilizando integrações neurais da API da *Pollinations* para modelagem de imagem e texto.

---

## 🏗️ Estrutura do Projeto

Os arquivos estáticos isolaram-se do ambiente de scripts, alinhando a arquitetura global a uma execução limpa:

```text
/
├── assets/
│   └── 1.png, 2.png, ..., 20.png, 3.jpeg   # Galeria de mídia bruta ou resultados testados.
├── src/
│   ├── v1_image_generator.py   # Bot autônomo V1: Gera descrições, imagens e legendas visuais via IA (Flux) e emposta no Feed.
│   ├── v2_video_creator.py     # Bot autônomo V2: Especializado em geração local ou em massa de curtas e automações de Reels.
│   └── v3_local_media.py       # Bot autônomo V3: Omitificador simplificado para extração de banco de folders logais ao invés de prompts dinâmicos.
└── README.md
```

---

## ⚙️ Core Technologies & Requisitos

O arsenal do software utiliza interdependências que lidam entre drivers de navegador e conexões abertas de machine learning público.

- **[Python](https://www.python.org/)** - Base linguística do ambiente local.
- **[Selenium WebDriver](https://www.selenium.dev/)** - O executor fantasma focado em manobrar e estressar seletores da interface Web do Instagram passando ileso pelo Shadow DOM.
- **[Pollinations AI](https://pollinations.ai/)** - Usado ativamente em scripts (ex. *v1*) para delegar cargas de processamento gerativo de artes de qualidade profissional que escalam o engajamento através da engine `Flux`.
- **[Pyperclip](https://pypi.org/project/pyperclip/)** - Estratégia nativa via *cross-clipboard* para saltar restrições anti-bot em text-inputs de legendas dinâmicas pesadas (lidar com emojis e chars Unicode não ASCII).

### Instalação

As dependências são fundamentais. Utilize um terminal para injetar o ecossistema python local:
```bash
pip install selenium pollinations pyperclip
```

O ambiente necessita obrigatoriamente do navegador [Google Chrome](https://www.google.com/chrome) instalado.

---

## 🚀 Desdobrando os Robôs

Ao escolher o modelo do bot desejado no pacote `src/`, atente-se às credenciais restritas do seu perfil de destino.

### Configuração de Criptografia (.env / Ambient)
Nos métodos de injeção dos bots, é requisitado os acessos da rede social. Defina as variáveis de ambiente a nível de Sistema Operacional de forma segura para não engatilhar as credenciais *raw text* no repositório público:

O bot consome nativamente:
- `INSTAGRAM_USERNAME`
- `INSTAGRAM_PASSWORD`

Se você não expôs como variáveis globais ou em `.env`, terá que substituir `os.getenv(...)` no código diretamente por *String literals* (Não recomendado e altamente propenso a vazamento de dados).

### Disparo e Execução
Na raiz do código do terminal, deflagre o worker escolhido:
```bash
python src/v1_image_generator.py
```

1. **A injeção do sistema entrará em ação.** O código construirá o prompt, consumirá a IA gerando artes inéditas, salvando as *assets* na máquina em tempo real.
2. O **Webdriver** assumirá o controle do seu Chrome, logando no Instagram e desviando dos sub-popups obstrusivos (`Not Now`/ `Agora Não`).
3. Uma complexa rotina de fallback de clipboard e javascript puro (`js_complete_script`) vai forçar a quebra do DOM do Instagram (React/Lexical nodes) impulsionando o texto nativo validado por unicode na área de *Caption* (legendas).
4. Publicação final concluída pelo botão "Share".

---
*Atenção: A política de uso da Meta lida vigorosamente contra robôs. Insira um atraso `time.sleep` considerável e humanizado entre instâncias nos loopings caso resolva empacotar os scripts, a fim de evitar `Shadow Bans` definitivos nos IPs da infraestrutura e em sua conta.*
