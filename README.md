## SensorDataAPI
Criação de uma API em python que trata as informações de sensores presentes nos equipamentos de uma empresa em tempo real. Os payloads são realizados em formato JSON. Enquanto isso, as enventuais lacunas de informações são tratadas por meio de arquivos CSV. Por fim, realiza-se a exibição do valor médio de cada sensor nas últimas 24h, 48h, 1 semana ou 1 mês.

## Bibliotecas
Para a execução correta do código, é necessária a instalação (pip install) das seguintes bibliotecas:
````python 
pip install Flask
````
````python 
pip install Flask-SQLAlchemy
```` 
````python 
pip install pandas
```` 
````python 
pip install numpy
````
````python 
pip install mysql-connector-python
````

## Instruções de Compilação
1- Para o código seja executado plenamente, certifique-se de instalar o servidor MySQL corretamente. Acesse seu root desta forma:
````pyhton
mysql -u root -p
````
Basta inserir sua senha, caso tudo esteja certo, estará logado no banco de dados

2- Agora, execute as seguintes linhas de código:
````pyhton
CREATE USER 'adm'@'localhost' IDENTIFIED BY 'admpassword';
GRANT ALL PRIVILEGES ON SensorData.* TO 'adm'@'localhost';
FLUSH PRIVILEGES;
````
Assim, você irá criar um novo usuário para estabelecer a conexão

3-Por fim, execute as seguintes linhas para criar o banco de dados:
````pyhton
CREATE SCHEMA IF NOT EXISTS `SensorData` DEFAULT CHARACTER SET utf8 ;
USE `SensorData` ;

CREATE TABLE IF NOT EXISTS `SensorData`.`Sensor_data` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `equipmentId` VARCHAR(45) NOT NULL,
  `timestamp` DATETIME NOT NULL,
  `value` DECIMAL(10,2) NULL,
  PRIMARY KEY (`id`)
) ENGINE = InnoDB;
````
Agora poderá executar a aplicação

## OBS
Em caso de falha na criação do banco pelo método acima, utilize o script do banco na pasta 'scripts'.

## Padrão de Commit
Utiliza-se tipos de commit para padronizar as mensagens de commit neste projeto. A seguir, estão os tipos de commit a serem utilizados, juntamente com exemplos de sumários correspondentes:

## ADD
Use o tipo "ADD" quando estiver adicionando um novo recurso ou funcionalidade ao código.

Exemplo:

"Adiciona funcionalidade de autenticação de usuário"

## DROP
O tipo "DROP" é usado para indicar a remoção de um recurso ou funcionalidade do código.

Exemplo:

"Remove o módulo de gráficos legados"

## FIX
Utilize "FIX" ao realizar correções de bugs e resolver problemas.

Exemplo:

"Corrige o erro de formatação na página de perfil do usuário"

## REFACTOR
Use "REFACTOR" quando estiver realizando refatorações no código, melhorando sua estrutura ou desempenho sem alterar sua funcionalidade.

Exemplo:

"Refatora a classe de manipulação de dados para melhorar a legibilidade"

## DOCS
O tipo "DOCS" é aplicado a alterações relacionadas à documentação, como adição ou atualização de comentários no código ou no README.

Exemplo:

"Adiciona documentação de código para o método de autenticação"