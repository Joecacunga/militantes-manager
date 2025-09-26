# 📋 Sistema de Registo de Militantes

Este é um sistema simples e funcional de **gestão de militantes**, desenvolvido em [Streamlit](https://streamlit.io/).  
Permite carregar ficheiros Excel, identificar registos duplicados (Nomes, Telefones, Nº CAP) e exportar dados tratados.

---

## 🚀 Funcionalidades
- Upload de ficheiros Excel (`.xlsx`).
- Deteção automática de duplicados:
  - Primeiro Nome + Último Nome
  - Nº de Telefone
  - Nº de CAP
- Exportação de ficheiro Excel limpo.
- Interface web simples e intuitiva.

---

## 🌐 Aceder Online
Quando o deploy estiver concluído, podes abrir a aplicação diretamente aqui:  

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://JoeCacunga-militantes-manager.streamlit.app)

---

## 📂 Estrutura do repositório
- `app.py` → ficheiro principal da aplicação Streamlit.  
- `utils.py` → funções auxiliares (deteção de duplicados e exportação).  
- `requirements.txt` → dependências necessárias.  

---

## 🖥️ Executar localmente
1. Clonar o repositório:
   ```bash
   git clone https://github.com/JoeCacunga/militantes-manager.git
   cd militantes-manager
   ```
2. Instalar dependências:
   ```bash
   pip install -r requirements.txt
   ```
3. Executar a aplicação:
   ```bash
   streamlit run app.py
   ```
4. Aceder no navegador:  
   ```
   http://localhost:8501
   ```

---

## ✨ Autor
Desenvolvido por **Joe Cacunga** como protótipo profissional para gestão de militantes.  
