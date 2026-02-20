from flask_restx import Namespace, Resource, fields
from app.services import facade

# Création du Namespace 'users'.
api = Namespace('users', description='Opérations liées à la gestion des utilisateurs')

# Ce modèle définit quels champs sont renvoyés au client (frontend) lors d'une requête GET.
user_model = api.model('User', {
    'id': fields.String(readonly=True, description='Identifiant unique de l\'utilisateur'),
    'first_name': fields.String(required=True, description='Prénom'),
    'last_name': fields.String(required=True, description='Nom de famille'),
    'email': fields.String(required=True, description='Adresse email'),
    'city': fields.String(description='Ville de résidence'),
    'bio': fields.String(description='Biographie courte'),
    'is_admin': fields.Boolean(readonly=True, description='Statut administrateur'),
    'created_at': fields.String(readonly=True, description='Date d\'inscription')
})

# Ce modèle définit les données attendues lors d'une requête PUT.
user_update_model = api.model('UserUpdate', {
    'first_name': fields.String(description='Nouveau prénom'),
    'last_name': fields.String(description='Nouveau nom de famille'),
    'city': fields.String(description='Nouvelle ville'),
    'bio': fields.String(description='Nouvelle biographie')
})


@api.route('/<string:user_id>')
@api.response(404, 'Utilisateur non trouvé')
class UserResource(Resource):
    """
    Classe gérant les opérations sur un utilisateur spécifique via son ID.
    """

    @api.doc('get_user')
    @api.marshal_with(user_model)
    def get(self, user_id):
        """
        Récupérer les détails d'un utilisateur par son ID.
        
        Cette méthode appelle la façade pour obtenir les données et utilise
        le décorateur @api.marshal_with pour formater la réponse JSON selon le user_model.
        """
        # Appel à la couche Business Logic
        user = facade.get_user(user_id)

        # Gestion d'erreur si l'utilisateur n'existe pas
        if not user:
            api.abort(404, "User not found")
        
        # Retourne l'objet
        return user.to_dict(), 200

    @api.doc('update_user')
    @api.expect(user_update_model, validate=True)
    @api.marshal_with(user_model) # Formate la réponse avec le modèle complet
    def put(self, user_id):
        """
        Mettre à jour les informations d'un utilisateur.
        
        Attend un objet JSON contenant les champs à modifier (first_name, last_name, city, bio).
        """
        # Récupération des données envoyées dans le corps de la requête
        user_data = api.payload
        
        # Appel à la façade pour effectuer la modification
        updated_user = facade.update_user(user_id, user_data)
        
        # Si la façade retourne None, c'est que l'utilisateur n'existe pas
        if not updated_user:
            api.abort(404, "User not found")
            
        return updated_user.to_dict(), 200
    