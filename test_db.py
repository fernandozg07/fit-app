import psycopg2

# URL do banco Railway (use a pública para rodar localmente)
DATABASE_URL = "postgresql://postgres:mXGgdDlzwypZOuaCKdZOUKlbCIjKzlvX@yamabiko.proxy.rlwy.net:29101/railway"

try:
    conn = psycopg2.connect(DATABASE_URL)
    print("Conexão bem-sucedida!")
    conn.close()
except Exception as e:
    print("Erro ao conectar:", e)
