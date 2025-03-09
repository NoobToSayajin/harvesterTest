import logging
import mariadb
from pprint import pprint

class DBConnect():
    """
    Connecte et interagie avec une base de donnee.
    """
    logger: logging.Logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    formater = logging.Formatter('%(asctime)s:%(levelname)s:%(name)s:ligne_%(lineno)d -> %(message)s')

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formater)

    logger.addHandler(stream_handler)

    def __init__(self, user: str, password: str, host: str, port: str, database: str) -> None:
        self.user: str = user
        self.password: str = password
        self.host: str = host
        self.port: str = port
        self.database: str = database
        self.connection: mariadb.Connection | None = None
        self._connectDB()

    def __str__(self) -> str:
        return f"Database: {self.database}; Host: {self.host}:{self.port}; User: {self.user};"

    def _connectDB(self) -> mariadb.Connection:
        """
        Connection a la base de donnees.
        """
        try:
            self.connection: mariadb.Connection = mariadb.connect(
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port,
                database=self.database
            )
            DBConnect.logger.info(f"Nouvelle connection => {self}")
            # return self.connection
        except mariadb.Error as e:
            DBConnect.logger.error(f"Erreur de connexion à MariaDB : {e}")

    def ShowVersion(self) -> str:
        """
        :return str: version de MariaDB
        """
        if self.connection:
            try:
                _cursor: mariadb.Cursor = self.connection.cursor()
                _cursor.execute("SELECT version();")
                _version = _cursor.fetchone() # type: ignore
                return f"Version de MariaDB: {_version[0]}"
            except mariadb.Error as e:
                DBConnect.logger.error(f"Erreur lors de la récupération de la version : {e}")
                return "Impossible d'obtenir la version."

    def CreateTable(self, table: str, **kwargs: dict) -> None:
        """
        Selectionne les champs dans la table.
        
        :param str table: nom de la table
        :param dict kwargs: paire cle valeur des champs
        """
        if self.connection:
            try:
                _table: str = f"CREATE TABLE IF NOT EXISTS {table} ("
                _list: str = "".join(f"{key} {value}, " for key, value in kwargs.items())
                _end: str = ");"
                _cmd: str = _table+_list[:len(_list)-2]+_end
                
                _cursor: mariadb.Cursor = self.connection.cursor()
                _cursor.execute(_cmd)
                self.connection.commit()
                DBConnect.logger.info(f"Table créée : {table} -> {_cmd}")
            except mariadb.Error as e:
                DBConnect.logger.error(f"Erreur lors de la création de la table {table} : {e}")
        

    def Insert(self, table: str, **kwargs: dict) -> None:
        """
        Selectionne les champs dans la table.
        
        :param str table: nom de la table
        :param dict kwargs: paire cle valeur de l'insertion
        """
        if self.connection:
            try:
                _key: str = "".join(f"{key}, " for key, _ in kwargs.items())
                values: list = []
                for value in kwargs.values():
                    values.append(value)
                _cmd: str = f"INSERT INTO {table} ("+_key[:len(_key)-2]+") VALUES (%s,%s)"
                
                _cursor: mariadb.Cursor = self.connection.cursor()
                _cursor.execute(_cmd, values)
                self.connection.commit()
                DBConnect.logger.info(f"Enregistrement ajouté : {_cmd} -> {values}")
            except mariadb.Error as e:
                DBConnect.logger.error(f"Erreur lors de l'insertion dans {table} : {e}")

    def Select(self, table: str, *args: tuple) -> list:
        """
        Selectionne les champs dans la table.
        
        :param str table: nom de la table
        :param list args: champs a selectionner
        
        :return: 
        """
        if self.connection:
            try:
                _arg: str = "".join(f"{arg}, " for arg in args)
                _cmd: str = f"SELECT {_arg[:-2]} FROM {table};"
                _cursor: mariadb.Cursor = self.connection.cursor()
                _cursor.execute(_cmd)

                DBConnect.logger.info(f"Requête exécutée : {_cmd}")
                return _cursor.fetchall()
            except mariadb.Error as e:
                DBConnect.logger.error(f"Erreur lors de la récupération des données de {table} : {e}")
                return []

    def Close(self) -> None:
        """
        Ferme la connexion à la base de données.
        """
        if self.connection:
            self.connection.close()
            DBConnect.logger.info("Connexion fermée.")

if __name__=="__main__":
    exo: DBConnect = DBConnect("root", "root", "192.168.126.150", "3306", "test")
    tableUser: str = "users"
    
    # try:
    version: str = exo.ShowVersion()
    pprint(version)
    exo.CreateTable(tableUser,id="SERIAL PRIMARY KEY", name="VARCHAR(100)", email="VARCHAR(100)")
    exo.Insert(tableUser, name="John Doe", email="john@example.com")
    users:list = exo.Select(tableUser, "*")
    pprint(users)
    # except Exception as e:
    #     print(e)
    # finally:
    #     exo.Close()