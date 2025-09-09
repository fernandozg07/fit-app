BACKUP_DIR="/mnt/c/Users/User/Desktop/foco/fit-app/backups"   # Diretório onde o backup será salvo#!/bin/bash

# Variáveis de configuração
DB_HOST="yamabiko.proxy.rlwy.net"         # Host do seu banco de dados
DB_USER="postgres"                         # Usuário do banco de dados
DB_NAME="railway"                          # Nome do banco de dados
BACKUP_DIR="/mnt/c/Users/User/Desktop/foco/fit-app/backups"   # Diretório onde os backups serão salvos

# Criação do nome do arquivo de backup com data e hora
BACKUP_FILE="$BACKUP_DIR/backup_$(date +%Y%m%d%H%M%S).dump"

# Comando para fazer o backup
pg_dump -h $DB_HOST -U $DB_USER -d $DB_NAME > $BACKUP_FILE

# Exibe uma mensagem para confirmar que o backup foi feito
echo "Backup criado em $BACKUP_FILE"
