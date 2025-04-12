# Firewall Viewer

## English

### Description

Firewall Viewer is a tool designed to visualize firewall data from a Firepower Management Center (FMC). It provides a web interface to display access control policies and dynamic objects, making it easier to understand and manage your firewall configurations.

### Installation

1.  Clone the repository:
```
bash
    git clone https://github.com/gamarchetti/Firewall_viewer.git
    cd Firewall_viewer
    
```
2.  Create a virtual environment (recommended):
```
bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows use: venv\Scripts\activate
    
```
3.  Install the required dependencies:
```
bash
    pip install Flask requests
    pip install Flask-WTF
    
```
### Execution

1.  Run the application:
```
bash
    python app.py
    
```
2.  Open your web browser and go to `http://localhost:443` (or the address shown in the terminal).

**Note:** The application writes data files to a `data` subdirectory within the project.

### Usage

1.  **Add Firewall:** The first step is to add your firewall details by clicking the "Add Firewall" button and providing the FMC IP/FQDN, username, and password. This information is stored for subsequent data synchronization.

2.  **Synchronize Data:** After adding the firewall, you can synchronize data from the FMC using the appropriate buttons in the web interface. This will retrieve the latest access control policies and dynamic objects.

3.  **View Data:** Once the data is synchronized, you can view the access control policies and dynamic objects through the provided links on the homepage.

### Contributing

Contributions are welcome! Please fork the repository and submit a pull request with your changes.

## Portuguese

### Descrição

Firewall Viewer é uma ferramenta projetada para visualizar dados de firewall de um Firepower Management Center (FMC). Ele fornece uma interface web para exibir políticas de controle de acesso e objetos dinâmicos, tornando mais fácil entender e gerenciar as configurações do seu firewall.

### Instalação

1.  Clone o repositório:
```
bash
    git clone https://github.com/gamarchetti/Firewall_viewer.git
    cd Firewall_viewer
    
```
2.  Crie um ambiente virtual (recomendado):
```
bash
    python3 -m venv venv
    source venv/bin/activate  # No Windows use: venv\Scripts\activate
    
```
3.  Instale as dependências necessárias:
```
bash
    pip install Flask requests
    pip install Flask-WTF
    
```
### Execução

1.  Execute a aplicação:
```
bash
    python app.py
    
```
2.  Abra seu navegador web e acesse `http://localhost:443` (ou o endereço exibido no terminal).

**Observação:** A aplicação escreve os arquivos de dados em um subdiretório `data` dentro do projeto.

### Uso

1.  **Adicionar Firewall:** O primeiro passo é adicionar os detalhes do seu firewall clicando no botão "Add Firewall" e fornecendo o IP/FQDN, nome de usuário e senha do FMC. Essas informações são armazenadas para a sincronização de dados subsequente.

2.  **Sincronizar Dados:** Após adicionar o firewall, você pode sincronizar os dados do FMC usando os botões apropriados na interface web. Isso irá recuperar as políticas de controle de acesso e objetos dinâmicos mais recentes.

3.  **Visualizar Dados:** Uma vez que os dados são sincronizados, você pode visualizar as políticas de controle de acesso e objetos dinâmicos através dos links fornecidos na página inicial.

### Contribuindo

Contribuições são bem-vindas! Por favor, faça um fork do repositório e envie um pull request com suas alterações.