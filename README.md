# Smart Control

Smart Control é uma aplicação web que funciona como uma dashboard e plataforma centralizada para gerenciar soluções de automação predial.

## Pré-requisitos

- Python 3.8+
- Node.js
- npm

## Instalação

Siga as etapas abaixo para configurar o ambiente de desenvolvimento:

1. **Criar e ativar um ambiente Python**

```bash
python3 -m venv venv
source venv/bin/activate
```

2. **Instalar as dependências do Python**

```bash
pip install -r requirements.txt
```

3. **Instalar as dependências do Node.js**

```bash
npm install
```

## Execução

Para iniciar o servidor Flask e o servidor de desenvolvimento do Node.js, você precisará abrir dois terminais diferentes:

- No primeiro terminal, execute o comando:

```bash
npm run dev
```

- No segundo terminal, execute o comando:

```bash
flask run --debug
```

Agora você deve ser capaz de acessar a aplicação em `localhost:5000`.