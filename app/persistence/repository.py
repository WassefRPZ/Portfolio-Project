from abc import ABC, abstractmethod

class Repository(ABC):
    """Interface abstraite pour garantir que tous les repositories ont les mêmes méthodes."""
    @abstractmethod
    def add(self, obj): pass
    @abstractmethod
    def get(self, obj_id): pass
    @abstractmethod
    def get_all(self): pass
    @abstractmethod
    def update(self, obj_id, data): pass
    @abstractmethod
    def delete(self, obj_id): pass
    @abstractmethod
    def get_by_attribute(self, attr_name, attr_value): pass


class InMemoryRepository(Repository):
    """
    Implémentation d'un stockage en mémoire (dictionnaire Python).
    Utilisé pour le développement et les tests avant de passer à une base de données SQL.
    """
    def __init__(self):
        self._storage = {}  # Stockage temporaire {id: object}

    def add(self, obj):
        """Ajoute un nouvel objet au stockage."""
        self._storage[obj.id] = obj

    def get(self, obj_id):
        """Récupère un objet par son ID."""
        return self._storage.get(obj_id)

    def get_all(self):
        """Récupère tous les objets stockés."""
        return list(self._storage.values())

    def get_by_attribute(self, attr_name, attr_value):
        """
        Récupère le premier objet dont l'attribut correspond à la valeur donnée.
        Utile pour trouver un user par email, par exemple.
        """
        return next((obj for obj in self._storage.values() if getattr(obj, attr_name) == attr_value), None)

    def update(self, obj_id, data):
        """
        Met à jour un objet existant.
        Si l'objet possède une méthode 'update' (comme User), elle est appelée pour gérer 
        la logique interne (ex: updated_at). Sinon, mise à jour attribut par attribut.
        """
        obj = self.get(obj_id)
        if obj:
            # Si l'objet a sa propre méthode update, on l'utilise
            if hasattr(obj, 'update') and callable(obj.update):
                obj.update(data)
            else:
                # Sinon, méthode générique
                for key, value in data.items():
                    if hasattr(obj, key):
                        setattr(obj, key, value)
            return True
        return False

    def delete(self, obj_id):
        """Supprime un objet par son ID."""
        if obj_id in self._storage:
            del self._storage[obj_id]
            return True
        return False
