
##### Análise Temporal Dashboard

Dashboard interativo em **Python** para análise operacional e temporal do processo de imóveis cadastrados em um sistema interno da empresa. Foi construído com **Dash**, **Plotly** e **Flask**, com suporte a **Docker**.  A aplicação transforma dados operacionais brutos (Excel) em **indicadores estratégicos**, reduzindo esforço manual, padronizando métricas e aumentando a confiabilidade das análises.

---
##### Projeto
Este projeto tem como objetivo automatizar o fluxo de análise de relatórios de um setor no ramo imobiliário, reduzindo atividades manuais e padronizando o tratamento dos dados. O desenvolvimento é realizado em Python, com foco na transformação de dados operacionais brutos em indicadores estratégicos, aumentando a confiabilidade e agilidade das análises. Originalmente desenvolvido em Jupyter Lab, o projeto evoluiu para uma aplicação web única, modular e integrada, empacotada e executada em containers Docker, garantindo portabilidade, padronização do ambiente e facilidade de deploy. A aplicação executada internamente em um ambiente de máquina virtual Linux.

**Funcionalidades Principais:**
A aplicação conta com:
- Tela de login personalizada e controle de acesso por usuário
- Upload seguro de arquivos Excel com limite de tamanho, processando os dados sem armazenar informações sensíveis no repositório
- Menu de navegação centralizado, com abas interativas para diferentes análises
- Visualização de gráficos interativos usando Plotly
- Processamento automático das etapas do processo, cálculo de tempos e indicadores chave.
- Armazenamento seguro de sessões e dados temporários, evitando vazamento de informações sensíveis. 
- Tabelas interativas com os gráficos
- Exportação do arquivo para .xlsx

**Atenção:**  
Os nomes de colunas refletem fluxos internos do processo de desocupação e **não representam dados reais** neste repositório.  
Este script processa dados internos contendo **informações operacionais e dados pessoais** (ex.: contatos), devendo ser executado **apenas em ambiente controlado e não público**.

---
##### Estrutura  
```
NIA_Desoc/  
├─ app/  
│ ├─ app.py                         #Aplicação principal  
│ ├─ arq.py                         #Lógica, leitura, normalização e cálculo
│ ├─ processar_arquivo.py           #Processamento do arquivo 
│ ├─ pages/                         #Layouts e callbacks das páginas  
│ ├─ templates/                     #HTML/CSS de login e upload  
│ ├─ static/                        #Imagens, ícones e assets visuais  
│ ├─ uploads/                       #Diretório temporário para arquivos enviados
│ ├─ flask_session/                 #Sessões do Flask
├─ docker/  
│ ├─ entrypoint.sh                  #Script de inicialização do container
├─ Dockerfile                       #Imagem 
├─ docker-compose.yml               #Orquestração de serviços
├─ requirements.txt                 #Bibliotecas necessárias
├─ .dockerignore                    #Arquivos ignorados pelo Docker 
├─ .gitignore                       #Arquivos ignorados pelo Git 
```
---
##### Variáveis de Ambiente

Para segurança, todas as credenciais e chaves são configuradas via variáveis de ambiente. Nenhuma credencial está hardcoded no código.
- USER_ADMIN → usuário administrador do sistema
- PASS_ADMIN → senha do usuário administrador
- FLASK_SECRET_KEY → chave secreta do Flask para sessões

> Apenas as **chaves devem ser definidas no ambiente**, sem valores no repositório.
---
##### Tecnologias utilizadas:
- Python
- Pandas
- NumPy
- Dash / Plotly
- Flask/ Flask-Login/ Flask-Session
- HTML / CSS customizado
- openpyxl /html5lib / lxml
- Docker / Docker Compose
-  Linux (VM)    
- SSH (PuTTY)
---
##### Segurança e LGPD

- Não versionar arquivos de Excel ou dados reais.
- Sessões e uploads são armazenados localmente e devem ser gerenciados em ambiente controlado.
- Cache e arquivos temporários são desabilitados via cabeçalhos HTTP.
- O sistema deve ser usado apenas em ambientes corporativos internos.

---
##### Boas Práticas

- Limpar periodicamente uploads/ e flask_session/ para evitar retenção desnecessária de dados.
- Não expor a aplicação em rede pública sem autenticação.
- Documentar variáveis de ambiente sem inserir valores no repositório.

---
##### Dependências

Principais bibliotecas utilizadas:

- **Web / Autenticação:** Flask, Flask-Login, Flask-Session, Werkzeug
- **Dashboard / Visualização:** dash, plotly
- **Dados:** pandas, numpy
- **Excel / Parsing:** openpyxl, html5lib, lxml, python-dateutil

> Todas são open source e amplamente utilizadas. Nenhuma biblioteca contém dados sensíveis.
---
##### Ambiente

Criação do ambiente virtual:
```
python -m venv venv
source venv/bin/activate  
venv\Scripts\activate   
```

Instala as dependências necessárias:
```
pip install -r requirements.txt
```

Definir variáveis de ambiente:
```
export USER_ADMIN=seu_usuario
export PASS_ADMIN=sua_senha
export FLASK_SECRET_KEY=sua_chave
```

Rodando a aplicação:
```
python app.py
```

Acessando pelo navegador:
```
http://localhost:****
```

---
##### Deploy do projeto para o Container

Pré-requisitos:
- Docker e Docker Compose instalados
- Python 3.11 (opcional, caso queira rodar sem container)

No terminal, dentro da sua pasta do projeto:
```
docker compose up -d                    #Subir o container

docker ps                               #Conferir se o container está rodando
```

A aplicação ficará disponível em:
```
http://localhost:****
```

Caso queira parar o container, execute o comando abaixo:
```
docker compose down
```
Para reativa-lo use:
```
docker compose up -d
```
**Atenção:** A infraestrutura Docker não é versionada neste repositório.  
O processo de build e deploy é documentado para reprodução em ambiente controlado.

---
##### Deploy do projeto em Máquina Virtual (VM)

Esse procedimento tem como objetivo disponibilizar a aplicação para acesso dentro da mesma rede, permitindo que múltiplos usuários utilizem o sistema simultaneamente. Ao executar a aplicação em uma máquina virtual Linux, o acesso deixa de ser realizado via localhost e passa a utilizar o endereço IP da VM, conforme mapeamento de portas definido no arquivo docker-compose.yml.
##### Pré-requisitos na VM 

O acesso à máquina virtual é realizado via SSH, utilizando o PuTTY.
Antes de iniciar o processo de deploy, é necessário garantir que o Docker e o Docker Compose estejam corretamente instalados na VM. 

Verificação no terminal (PuTTY):
```
docker --version
docker-compose --version
```
##### Acessar o projeto no ambiente local (WSL)

No terminal do WSL, navegue até a pasta raiz do projeto: 
```
cd /mnt/c/Users/caminho_do_projeto
```
##### Transferência dos arquivos para a VM (SCP)

O comando abaixo deve ser executado a partir do WSL e realiza a transferência apenas dos arquivos essenciais para execução da aplicação em produção:
```
scp -r app Dockerfile docker-compose.yml requirements.txt .dockerignore robo@IP_DA_VM:/home/robo/nome_pasta_raiz_do_projeto
```
- Na primeira conexão com a VM, será solicitada a confirmação da chave SSH. 
  Digite ```yes``` para continuar. 
##### Acessar o diretório do projeto na VM

Após a transferência, acesse a VM via PuTTY e navegue até o diretório do projeto:
```
cd ~/nome_pasta_raiz_do_projeto
```
##### Ajuste de permissões do entrypoint

Garante que o script de inicialização tenha permissão de execução:
```
chmod +x docker/entrypoint.sh
```
##### Build da aplicação 

Realize o build da imagem Docker:
```
docker-compose build --no-cache
```
##### Subir aplicação

Inicie o container em segundo plano:
```
docker-compose up -d
```
##### Verificação do container

Verifique se o container está em execução:
```
docker ps
```

- O container deverá estar com status Up e a porta mapeada:
```
0.0.0.0:**** -> ****
```

##### Acesso à aplicação 

A aplicação estará disponível para acesso a partir de qualquer máquina na mesma rede, utilizando o IP da VM: 
```
http://IP_DA_VM:****
```
##### Parar a aplicação na VM
```
docker-compose down
```
##### Reiniciar a aplicação
```
docker compose up -d
```

---
##### Considerações Finais

Este projeto entrega uma solução integrada, segura e eficiente para transformar dados operacionais brutos em indicadores estratégicos claros, confiáveis e acionáveis. A automação do processamento de arquivos Excel, aliada ao cálculo de tempos de permanência em cada fase do processo e à apresentação de métricas por meio de gráficos interativos, reduz significativamente o esforço manual, padroniza as análises e aumenta a confiabilidade das informações.

A aplicação combina a robustez do Python com frameworks modernos como Dash, Plotly e Flask, oferecendo uma interface web intuitiva, modular e centralizada. O sistema conta com controle de acesso por usuário, upload seguro de arquivos e armazenamento temporário de sessões, garantindo uma experiência consistente e segura para os usuários.

A utilização de Docker assegura que o ambiente de execução seja isolado, reproduzível e facilmente implantável em diferentes máquinas, mantendo consistência entre os ambientes de desenvolvimento, teste e produção. Além disso, o projeto foi estruturado seguindo boas práticas de desenvolvimento e deploy, evitando o versionamento de dados sensíveis e reforçando a segurança e confidencialidade das informações.

Em síntese, esta solução integra automação, confiabilidade e visualização interativa, proporcionando uma visão abrangente do desempenho do processo de desocupação. Isso permite decisões mais rápidas, embasadas e estratégicas, além de abrir espaço para futuras evoluções, como integrações com sistemas corporativos e expansão das análises disponíveis.
