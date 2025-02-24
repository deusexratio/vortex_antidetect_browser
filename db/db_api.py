from db.models import db, Profile, Wallets, Extension


def load_profiles(sqlite_query: bool = False) -> list[Profile]:
    if sqlite_query:
        return db.execute('SELECT * FROM profiles')
    return db.all(entities=Profile)


def get_profile(name: str, sqlite_query: bool = False) -> Profile | None:
    if sqlite_query:
        return db.execute('SELECT * FROM profiles WHERE name = ?', (name,), True)
    return db.one(Profile, Profile.name == name)


def delete_profile(name: str, sqlite_query: bool = False):
    if sqlite_query:
        return db.delete('DELETE * FROM profiles WHERE name = ?', (name,), True)
    return db.delete(Profile)

def get_wallets_by_name(name: str, sqlite_query: bool = False) -> Wallets | None:
    if sqlite_query:
        return db.execute('SELECT * FROM wallets WHERE name = ?', (name,), True)
    return db.one(Wallets, Wallets.name == name)

def load_wallets(sqlite_query: bool = False) -> list[Wallets]:
    if sqlite_query:
        return db.execute('SELECT * FROM wallets')
    return db.all(entities=Wallets)

def flush_wallets():
    all_wallets = load_wallets()
    for wallets in all_wallets:
        db.delete(wallets)

def get_extension_id(extension_name: str):
    extensions = db.all(entities=Extension)
    for extension in extensions:
        if extension_name.lower() in extension.name.lower():
            return extension.extension_id

def get_extension_instance(extension_name: str | None = None, extension_id: str | None = None):
    if extension_name:
        return db.one(Extension, Extension.name == extension_name)
    elif extension_id:
        return db.one(Extension, Extension.extension_id == extension_id)
    else:
        print('Specify arguments in get_extension_instance')

def get_all_extensions_from_db():
    return db.all(entities=Extension)
